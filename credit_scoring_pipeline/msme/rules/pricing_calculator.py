"""Pricing calculator for interest rates and fees"""

from typing import Dict


def calculate_interest_rate(
    score: int,
    loan_amount: float,
    business_age_years: float,
    industry: str = 'general',
    base_rate: float = 10.0
) -> Dict[str, float]:
    """
    Calculate interest rate based on risk factors
    
    Formula:
    Final Rate = Base Rate + Score Premium + Vintage Premium + Industry Premium
    
    Args:
        score: Credit score (300-900)
        loan_amount: Loan amount requested
        business_age_years: Age of business
        industry: Industry sector
        base_rate: Base lending rate
        
    Returns:
        Dictionary with interest rate breakdown
    """
    # Score-based premium
    if score >= 800:
        score_premium = 0.0
    elif score >= 750:
        score_premium = 1.5
    elif score >= 700:
        score_premium = 2.5
    elif score >= 650:
        score_premium = 3.5
    elif score >= 600:
        score_premium = 5.0
    elif score >= 550:
        score_premium = 6.5
    elif score >= 500:
        score_premium = 8.0
    else:
        score_premium = 10.0
    
    # Business vintage premium (newer = higher risk)
    if business_age_years >= 5:
        vintage_premium = -0.5  # Discount
    elif business_age_years >= 3:
        vintage_premium = 0.0
    elif business_age_years >= 2:
        vintage_premium = 0.5
    elif business_age_years >= 1:
        vintage_premium = 1.0
    else:
        vintage_premium = 2.0
    
    # Industry risk premium
    industry_premiums = {
        'technology': -0.5,
        'healthcare': 0.0,
        'services': 0.0,
        'retail': 0.5,
        'manufacturing': 0.5,
        'trading': 0.5,
        'hospitality': 1.0,
        'construction': 1.5,
        'agriculture': 1.5,
        'general': 0.5
    }
    industry_premium = industry_premiums.get(industry.lower(), 0.5)
    
    # Loan amount premium (larger loans = lower rates)
    if loan_amount >= 5000000:  # ₹50L+
        amount_premium = -0.5
    elif loan_amount >= 2000000:  # ₹20L+
        amount_premium = 0.0
    elif loan_amount >= 1000000:  # ₹10L+
        amount_premium = 0.5
    else:
        amount_premium = 1.0
    
    # Calculate final rate
    final_rate = base_rate + score_premium + vintage_premium + industry_premium + amount_premium
    
    # Floor and cap
    final_rate = max(10.0, min(final_rate, 30.0))
    
    return {
        'final_interest_rate': round(final_rate, 2),
        'base_rate': base_rate,
        'score_premium': score_premium,
        'vintage_premium': vintage_premium,
        'industry_premium': industry_premium,
        'amount_premium': amount_premium,
        'total_premium': round(score_premium + vintage_premium + industry_premium + amount_premium, 2)
    }


def calculate_processing_fee(
    loan_amount: float,
    score: int,
    base_fee_percentage: float = 1.0
) -> Dict[str, float]:
    """
    Calculate processing fee based on loan amount and score
    
    Args:
        loan_amount: Loan amount
        score: Credit score
        base_fee_percentage: Base processing fee percentage
        
    Returns:
        Dictionary with processing fee details
    """
    # Score-based discount
    if score >= 750:
        discount = 0.50  # 50% discount
    elif score >= 650:
        discount = 0.25  # 25% discount
    else:
        discount = 0.0
    
    # Calculate fee
    fee_percentage = base_fee_percentage * (1 - discount)
    
    # Floor and cap
    fee_percentage = max(0.25, min(fee_percentage, 2.0))
    
    processing_fee = loan_amount * (fee_percentage / 100)
    
    # Minimum and maximum fee
    min_fee = 500  # ₹500
    max_fee = 50000  # ₹50,000
    
    processing_fee = max(min_fee, min(processing_fee, max_fee))
    
    return {
        'processing_fee': round(processing_fee, 2),
        'fee_percentage': round(fee_percentage, 2),
        'base_fee_percentage': base_fee_percentage,
        'discount': round(discount * 100, 2)  # In percentage
    }


def calculate_total_cost(
    loan_amount: float,
    interest_rate: float,
    tenure_months: int,
    processing_fee: float
) -> Dict[str, float]:
    """
    Calculate total cost of the loan
    
    Args:
        loan_amount: Principal amount
        interest_rate: Annual interest rate (%)
        tenure_months: Loan tenure in months
        processing_fee: One-time processing fee
        
    Returns:
        Dictionary with cost breakdown
    """
    monthly_rate = interest_rate / 12 / 100
    
    # Calculate EMI
    if monthly_rate > 0:
        emi = loan_amount * monthly_rate * \
              (1 + monthly_rate)**tenure_months / \
              ((1 + monthly_rate)**tenure_months - 1)
    else:
        emi = loan_amount / tenure_months
    
    total_payment = emi * tenure_months
    total_interest = total_payment - loan_amount
    total_cost = total_payment + processing_fee
    
    return {
        'monthly_emi': round(emi, 2),
        'total_payment': round(total_payment, 2),
        'total_interest': round(total_interest, 2),
        'processing_fee': round(processing_fee, 2),
        'total_cost': round(total_cost, 2),
        'effective_rate': round((total_cost / loan_amount - 1) * (12 / tenure_months) * 100, 2)
    }

