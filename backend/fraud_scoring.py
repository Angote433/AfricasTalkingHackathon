"""
Fraud Scoring Service
Combines all signals into a final explainable fraud score.
"""

from pricing_db import CURRENCY


def calculate_fraud_score(analysis_results):
    """
    Weighted fraud score — weights tuned for receipt fraud context.

    Component         Weight   Rationale
    ─────────────────────────────────────────────────────
    Image forensics    35%     Manipulation is strongest signal
    Cost deviation     35%     Overpricing is most common fraud vector
    Business rules     20%     Rule violations add strong context
    Screenshot flag    10%     Screenshots hide original metadata
    """
    manipulation = analysis_results.get('manipulation_score', 0)
    cost         = analysis_results.get('cost_score', 0)
    rules        = analysis_results.get('rule_violation_score', 0)
    screenshot   = 100 if analysis_results.get('is_screenshot', False) else 0

    fraud_score = (
        manipulation * 0.35 +
        cost         * 0.35 +
        rules        * 0.20 +
        screenshot   * 0.10
    )
    fraud_score = min(round(fraud_score, 1), 100)

    if fraud_score < 25:
        risk, action = 'LOW',      'APPROVE'
    elif fraud_score < 55:
        risk, action = 'MEDIUM',   'REVIEW'
    elif fraud_score < 80:
        risk, action = 'HIGH',     'INVESTIGATE'
    else:
        risk, action = 'CRITICAL', 'REJECT'

    return {
        'fraud_score':    fraud_score,
        'risk_category':  risk,
        'recommendation': action,
        'score_breakdown': {
            'image_forensics': round(manipulation * 0.35, 1),
            'cost_deviation':  round(cost         * 0.35, 1),
            'business_rules':  round(rules        * 0.20, 1),
            'screenshot_flag': round(screenshot   * 0.10, 1),
        }
    }


def generate_red_flags(analysis_results):
    red_flags = []

    if analysis_results.get('edited_with_software'):
        sw = analysis_results.get('software_used', 'image editing software')
        red_flags.append({
            'severity': 'CRITICAL',
            'category': 'Image Manipulation',
            'description': f'Receipt was edited using {sw}',
            'evidence': f'EXIF metadata reveals software: {sw}',
            'confidence': 'HIGH'
        })

    if analysis_results.get('manipulation_detected') and not analysis_results.get('edited_with_software'):
        red_flags.append({
            'severity': 'HIGH',
            'category': 'Image Manipulation',
            'description': 'Error Level Analysis detected digital tampering',
            'evidence': f'ELA score: {analysis_results.get("ela_score", 0):.2f} (threshold: 10.0)',
            'confidence': 'MEDIUM'
        })

    if analysis_results.get('is_screenshot'):
        red_flags.append({
            'severity': 'MEDIUM',
            'category': 'Document Authenticity',
            'description': 'Uploaded file is a screenshot, not an original receipt',
            'evidence': 'EXIF data absent; screen capture indicators present',
            'confidence': 'HIGH'
        })

    for item in analysis_results.get('cost_comparison', []):
        if item.get('suspicious'):
            red_flags.append({
                'severity': 'HIGH',
                'category': 'Cost Anomaly',
                'description': (
                    f'{item["description"]}: Billed {CURRENCY} {item["claimed"]:,.0f} '
                    f'vs expected {CURRENCY} {item["expected"]:,.0f}'
                ),
                'evidence': f'{item["deviation_pct"]:.0f}% above standard market rate',
                'confidence': 'HIGH'
            })

    red_flags.extend(analysis_results.get('rule_violations', []))

    order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    red_flags.sort(key=lambda x: order.get(x['severity'], 4))
    return red_flags


def compile_final_analysis(extracted_data, forensics_result, cost_validation, business_rules_result):
    analysis_results = {
        'manipulation_score':   forensics_result.get('manipulation_score', 0),
        'manipulation_detected':forensics_result.get('manipulation_detected', False),
        'edited_with_software': forensics_result.get('exif_data', {}).get('edited_with_software', False),
        'software_used':        forensics_result.get('exif_data', {}).get('software_used'),
        'is_screenshot':        forensics_result.get('is_screenshot', False),
        'ela_score':            forensics_result.get('ela_score', 0),
        'cost_score':           cost_validation.get('cost_score', 0),
        'cost_comparison':      cost_validation.get('cost_comparison', []),
        'rule_violation_score': business_rules_result.get('rule_violation_score', 0),
        'rule_violations':      business_rules_result.get('violations', []),
    }

    scoring  = calculate_fraud_score(analysis_results)
    red_flags = generate_red_flags(analysis_results)

    return {
        'claim_id':         None,
        'fraud_score':      scoring['fraud_score'],
        'risk_category':    scoring['risk_category'],
        'recommendation':   scoring['recommendation'],
        'score_breakdown':  scoring['score_breakdown'],
        'red_flags':        red_flags,
        'extracted_data':   extracted_data,
        'exif_data':        forensics_result.get('exif_data', {}),
        'is_screenshot':    forensics_result.get('is_screenshot', False),
        'manipulation_score': forensics_result.get('manipulation_score', 0),
        'ela_image_url':    None,
        'cost_comparison':  cost_validation.get('cost_comparison', []),
        'image_url':        None,
        'currency':         CURRENCY,
    }
