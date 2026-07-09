"""
Cost Validation Service
Compares claimed costs against standard market rates
"""

from pricing_db import match_procedure


def validate_line_item_cost(description, claimed_price):
    """
    Validate a single line item cost against market rate
    """
    # Match to pricing database
    matched_procedure, price_data = match_procedure(description)
    
    if not price_data:
        # Procedure not in database
        return {
            'description': description,
            'claimed': claimed_price,
            'expected': 'Unknown',
            'max_reasonable': None,
            'deviation_pct': 0,
            'suspicious': False,
            'matched_procedure': None
        }
    
    standard_price = price_data['standard']
    max_price = price_data['max']
    
    # Calculate deviation
    deviation_pct = ((claimed_price - standard_price) / standard_price) * 100
    
    # Flag if exceeds 150% of standard rate
    is_suspicious = claimed_price > (standard_price * 1.5)
    
    return {
        'description': description,
        'claimed': claimed_price,
        'expected': standard_price,
        'max_reasonable': max_price,
        'deviation_pct': deviation_pct,
        'suspicious': is_suspicious,
        'matched_procedure': matched_procedure
    }


def validate_costs(line_items):
    """
    Validate all line items and calculate overall cost score
    """
    if not line_items:
        return {
            'cost_comparison': [],
            'cost_score': 0,
            'flagged_items': 0,
            'total_claimed': 0,
            'total_expected': 0
        }
    
    results = []
    total_deviation = 0
    flagged_items = 0
    total_claimed = 0
    total_expected = 0
    
    for item in line_items:
        description = item.get('description', '')
        claimed_price = item.get('price', 0)
        
        validation_result = validate_line_item_cost(description, claimed_price)
        results.append(validation_result)
        
        total_claimed += claimed_price
        
        if validation_result['suspicious']:
            flagged_items += 1
            total_deviation += abs(validation_result['deviation_pct'])
        
        if isinstance(validation_result['expected'], (int, float)):
            total_expected += validation_result['expected']
    
    # Calculate overall cost deviation score (0-100)
    if len(line_items) > 0:
        avg_deviation = total_deviation / len(line_items)
        cost_score = min(avg_deviation, 100)
    else:
        cost_score = 0
    
    return {
        'cost_comparison': results,
        'cost_score': float(cost_score),
        'flagged_items': flagged_items,
        'total_claimed': float(total_claimed),
        'total_expected': float(total_expected)
    }


def detect_round_number(amount):
    """
    Detect suspiciously round numbers
    """
    if amount >= 1000 and amount % 100 == 0:
        return True
    if amount >= 500 and amount % 50 == 0:
        return True
    return False