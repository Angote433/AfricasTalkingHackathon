"""
Business Rules Validation - Kenya/Nairobi context
"""

from datetime import datetime
from dateutil import parser as date_parser
from pricing_db import HIGH_TOTAL_THRESHOLD, LOW_TOTAL_THRESHOLD, CURRENCY


def validate_dates(extracted_data):
    violations, score = [], 0
    date_str = extracted_data.get('invoice_date')
    if not date_str:
        return violations, score
    try:
        invoice_date = date_parser.parse(date_str).date()
        today = datetime.now().date()
        if invoice_date > today:
            violations.append({
                'severity': 'CRITICAL',
                'category': 'Date Anomaly',
                'description': 'Invoice is dated in the future',
                'evidence': f'Invoice date: {invoice_date}, Today: {today}',
                'confidence': 'HIGH'
            })
            score += 35
        days_old = (today - invoice_date).days
        if days_old > 730:
            violations.append({
                'severity': 'MEDIUM',
                'category': 'Date Anomaly',
                'description': 'Invoice is over 2 years old',
                'evidence': f'Invoice date: {invoice_date} ({days_old} days ago)',
                'confidence': 'MEDIUM'
            })
            score += 10
    except Exception as e:
        print(f"Date validation error: {e}")
    return violations, score


def validate_amount(total_amount):
    violations, score = [], 0
    if not total_amount:
        return violations, score

    if total_amount > HIGH_TOTAL_THRESHOLD:
        violations.append({
            'severity': 'HIGH',
            'category': 'Amount Anomaly',
            'description': f'Unusually high outpatient bill',
            'evidence': f'Total: {CURRENCY} {total_amount:,.0f} (flag threshold: {CURRENCY} {HIGH_TOTAL_THRESHOLD:,})',
            'confidence': 'MEDIUM'
        })
        score += 15

    if total_amount < LOW_TOTAL_THRESHOLD:
        violations.append({
            'severity': 'LOW',
            'category': 'Amount Anomaly',
            'description': 'Suspiciously low total amount',
            'evidence': f'Total: {CURRENCY} {total_amount:,.0f}',
            'confidence': 'LOW'
        })
        score += 5

    # Round number heuristic (KES context)
    if total_amount >= 5000 and total_amount % 1000 == 0:
        violations.append({
            'severity': 'LOW',
            'category': 'Amount Anomaly',
            'description': 'Total is a suspiciously round number',
            'evidence': f'{CURRENCY} {total_amount:,.0f} — round totals can indicate fabrication',
            'confidence': 'LOW'
        })
        score += 8

    return violations, score


def validate_line_items(extracted_data):
    """Check for duplicate services and phantom line items."""
    violations, score = [], 0
    items = extracted_data.get('line_items', [])
    if not items:
        return violations, score

    # Duplicate service detection
    descriptions = [i.get('description', '').lower().strip() for i in items]
    seen, duplicates = set(), set()
    for d in descriptions:
        if d in seen:
            duplicates.add(d)
        seen.add(d)

    if duplicates:
        violations.append({
            'severity': 'HIGH',
            'category': 'Duplicate Services',
            'description': f'Same service billed multiple times',
            'evidence': f'Duplicated: {", ".join(duplicates)}',
            'confidence': 'HIGH'
        })
        score += 25

    # Too many line items (possible unbundling)
    if len(items) > 10:
        violations.append({
            'severity': 'MEDIUM',
            'category': 'Unbundling',
            'description': 'Unusually high number of billed services',
            'evidence': f'{len(items)} line items on a single receipt',
            'confidence': 'MEDIUM'
        })
        score += 12

    return violations, score


def validate_required_fields(extracted_data):
    violations, score = [], 0
    missing = []
    for field, label in [
        ('hospital_name', 'Hospital/Clinic Name'),
        ('invoice_date', 'Invoice Date'),
        ('total_amount', 'Total Amount'),
    ]:
        if not extracted_data.get(field):
            missing.append(label)

    if missing:
        violations.append({
            'severity': 'HIGH',
            'category': 'Missing Information',
            'description': 'Critical fields could not be extracted',
            'evidence': f'Missing: {", ".join(missing)}',
            'confidence': 'HIGH'
        })
        score += 15
    return violations, score


def validate_business_rules(extracted_data):
    all_violations, total_score = [], 0

    for fn in [validate_dates, validate_amount, validate_required_fields, validate_line_items]:
        v, s = fn(extracted_data) if fn != validate_amount else fn(extracted_data.get('total_amount'))
        all_violations.extend(v)
        total_score += s

    return {
        'violations': all_violations,
        'rule_violation_score': min(total_score, 100)
    }
