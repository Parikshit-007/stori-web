"""Eligibility checking based on business rules"""

from typing import Dict, List, Tuple


def check_eligibility(
    score: int,
    business_age_years: float,
    monthly_revenue: float,
    gst_verified: bool = False,
    kyc_complete: bool = False,
    fraud_flag: bool = False,
    legal_proceedings: bool = False
) -> Tuple[str, List[str]]:
    """
    Check eligibility for MSME lending
    
    Returns:
        Tuple of (eligibility_status, reasons)
        
    Eligibility statuses:
    - 'eligible': Auto-approve
    - 'conditionally_eligible': Approve with conditions
    - 'manual_review': Requires manual review
    - 'rejected': Auto-reject
    """
    reasons = []
    
    # Hard rejections
    if fraud_flag:
        return 'rejected', ['Fraud flag detected']
    
    if score < 300 or score > 900:
        return 'rejected', ['Invalid credit score']
    
    # Eligibility checks
    if score >= 750:
        status = 'eligible'
        reasons.append('Excellent credit score (750+)')
    elif score >= 650:
        status = 'eligible'
        reasons.append('Good credit score (650+)')
    elif score >= 550:
        status = 'conditionally_eligible'
        reasons.append('Fair credit score (550-649)')
    elif score >= 450:
        status = 'manual_review'
        reasons.append('Below average credit score (450-549)')
    else:
        status = 'rejected'
        reasons.append('Poor credit score (<450)')
        return status, reasons
    
    # Business age check
    if business_age_years < 1:
        if status == 'eligible':
            status = 'conditionally_eligible'
        reasons.append('New business (<1 year)')
    
    # Revenue check
    min_monthly_revenue = 50000  # ₹50,000
    if monthly_revenue < min_monthly_revenue:
        if status == 'eligible':
            status = 'manual_review'
        reasons.append(f'Low monthly revenue (<₹{min_monthly_revenue:,})')
    
    # GST verification
    if not gst_verified and monthly_revenue > 200000:  # > ₹2L/month
        reasons.append('GST verification required')
        if status == 'eligible':
            status = 'conditionally_eligible'
    
    # KYC check
    if not kyc_complete:
        reasons.append('KYC completion required')
        if status == 'eligible':
            status = 'conditionally_eligible'
    
    # Legal proceedings
    if legal_proceedings:
        reasons.append('Legal proceedings detected - requires review')
        if status == 'eligible':
            status = 'manual_review'
    
    # Add positive reasons
    if status == 'eligible':
        if gst_verified:
            reasons.append('✓ GST verified')
        if kyc_complete:
            reasons.append('✓ KYC complete')
        if monthly_revenue >= 500000:
            reasons.append('✓ Strong monthly revenue')
        if business_age_years >= 3:
            reasons.append('✓ Established business')
    
    return status, reasons


def get_eligibility_reasons(
    score: int,
    business_profile: Dict
) -> Dict[str, any]:
    """
    Get detailed eligibility analysis
    
    Args:
        score: Credit score
        business_profile: Dictionary with business details
        
    Returns:
        Dictionary with eligibility details
    """
    status, reasons = check_eligibility(
        score=score,
        business_age_years=business_profile.get('business_age_years', 0),
        monthly_revenue=business_profile.get('monthly_revenue', 0),
        gst_verified=business_profile.get('gst_verified', False),
        kyc_complete=business_profile.get('kyc_complete', False),
        fraud_flag=business_profile.get('fraud_flag', False),
        legal_proceedings=business_profile.get('legal_proceedings', False)
    )
    
    # Determine approval probability
    if status == 'eligible':
        approval_probability = 0.90
    elif status == 'conditionally_eligible':
        approval_probability = 0.70
    elif status == 'manual_review':
        approval_probability = 0.40
    else:
        approval_probability = 0.10
    
    # Determine collateral requirement
    if score >= 650:
        collateral_required = False
    elif score >= 550:
        collateral_required = True
        collateral_type = 'Personal guarantee or property'
    else:
        collateral_required = True
        collateral_type = 'Property or fixed assets'
    
    return {
        'eligibility_status': status,
        'approval_probability': approval_probability,
        'reasons': reasons,
        'collateral_required': collateral_required,
        'collateral_type': collateral_type if collateral_required else 'None',
        'recommendations': _get_recommendations(status, score, business_profile)
    }


def _get_recommendations(
    status: str,
    score: int,
    business_profile: Dict
) -> List[str]:
    """Generate recommendations based on eligibility"""
    recommendations = []
    
    if status == 'rejected':
        recommendations.append('Focus on improving credit score')
        recommendations.append('Build stronger business fundamentals')
        recommendations.append('Ensure timely tax payments')
        return recommendations
    
    if score < 650:
        recommendations.append('Work on improving credit score to get better terms')
    
    if not business_profile.get('gst_verified', False):
        recommendations.append('Complete GST verification for faster processing')
    
    if not business_profile.get('kyc_complete', False):
        recommendations.append('Complete KYC documentation')
    
    if business_profile.get('business_age_years', 0) < 2:
        recommendations.append('Build longer business track record')
    
    if business_profile.get('monthly_revenue', 0) < 200000:
        recommendations.append('Increase monthly revenue for higher limits')
    
    if status == 'eligible':
        recommendations.append('✓ Eligible for best interest rates and terms')
        recommendations.append('✓ No collateral required')
    
    return recommendations

