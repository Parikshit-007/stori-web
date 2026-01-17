"""Overdraft limit calculation based on business rules"""

from typing import Dict
import numpy as np


def calculate_overdraft_limit(
    score: int,
    monthly_revenue: float,
    annual_turnover: float = None,
    avg_bank_balance: float = 0,
    monthly_profit: float = None,
    existing_debt: float = 0,
    business_age_years: float = 1,
    method: str = 'combined'
) -> Dict[str, any]:
    """
    Calculate overdraft limit using industry-standard methods
    
    Methods:
    1. Turnover Method: 20-40% of annual turnover (based on score)
    2. MPBF Method: (Current Assets - Current Liabilities) * 0.75
    3. Cash Flow Method: Based on DSCR and repayment capacity
    4. Combined: Weighted average of above methods
    
    Args:
        score: Credit score (300-900)
        monthly_revenue: Average monthly revenue
        annual_turnover: Annual turnover (if None, estimated from monthly)
        avg_bank_balance: Average bank balance
        monthly_profit: Average monthly profit
        existing_debt: Existing debt obligations
        business_age_years: Age of business in years
        method: Calculation method ('turnover', 'mpbf', 'cashflow', 'combined')
        
    Returns:
        Dictionary with recommended limits and details
    """
    # Estimate annual turnover if not provided
    if annual_turnover is None:
        annual_turnover = monthly_revenue * 12
    
    # Estimate monthly profit if not provided
    if monthly_profit is None:
        monthly_profit = monthly_revenue * 0.10  # Assume 10% margin
    
    # Method 1: Turnover-based limit
    turnover_limit = _calculate_turnover_method(
        score, annual_turnover, business_age_years
    )
    
    # Method 2: MPBF (simplified - using bank balance as proxy for working capital)
    mpbf_limit = _calculate_mpbf_method(
        avg_bank_balance, monthly_revenue, existing_debt
    )
    
    # Method 3: Cash flow coverage method
    cashflow_limit = _calculate_cashflow_method(
        monthly_profit, existing_debt, score
    )
    
    # Combined recommendation (weighted average)
    if method == 'turnover':
        recommended_limit = turnover_limit
    elif method == 'mpbf':
        recommended_limit = mpbf_limit
    elif method == 'cashflow':
        recommended_limit = cashflow_limit
    else:  # combined
        # Weight: 50% turnover, 30% cashflow, 20% MPBF
        recommended_limit = (
            turnover_limit * 0.50 +
            cashflow_limit * 0.30 +
            mpbf_limit * 0.20
        )
    
    # Apply business vintage adjustment
    vintage_multiplier = _get_vintage_multiplier(business_age_years)
    recommended_limit *= vintage_multiplier
    
    # Calculate utilization metrics
    available_limit = max(0, recommended_limit - existing_debt)
    utilization = (existing_debt / recommended_limit * 100) if recommended_limit > 0 else 0
    
    return {
        'recommended_overdraft_limit': round(recommended_limit, 2),
        'available_limit': round(available_limit, 2),
        'existing_debt': existing_debt,
        'utilization_percentage': round(utilization, 2),
        'method_breakdown': {
            'turnover_method': round(turnover_limit, 2),
            'mpbf_method': round(mpbf_limit, 2),
            'cashflow_method': round(cashflow_limit, 2)
        },
        'adjustments': {
            'vintage_multiplier': round(vintage_multiplier, 2),
            'business_age_years': business_age_years
        }
    }


def _calculate_turnover_method(
    score: int,
    annual_turnover: float,
    business_age_years: float
) -> float:
    """
    Turnover-based limit: 20-40% of annual turnover
    
    Score-based multipliers:
    - 750+: 40% of turnover
    - 650-749: 30% of turnover
    - 550-649: 25% of turnover
    - 450-549: 15% of turnover
    - <450: 0% (not eligible)
    """
    if score >= 750:
        multiplier = 0.40
    elif score >= 650:
        multiplier = 0.30
    elif score >= 550:
        multiplier = 0.25
    elif score >= 450:
        multiplier = 0.15
    else:
        multiplier = 0.0
    
    return annual_turnover * multiplier


def _calculate_mpbf_method(
    avg_bank_balance: float,
    monthly_revenue: float,
    existing_debt: float
) -> float:
    """
    MPBF (Maximum Permissible Bank Finance) Method
    
    Simplified formula:
    Working Capital = (Current Assets - Current Liabilities)
    MPBF = Working Capital * 0.75
    
    Using bank balance as proxy for working capital
    """
    # Estimate current assets (bank balance + 1 month receivables)
    current_assets = avg_bank_balance + (monthly_revenue * 0.5)
    
    # Estimate current liabilities (existing debt + 1 month payables)
    current_liabilities = existing_debt + (monthly_revenue * 0.3)
    
    # Working capital
    working_capital = max(0, current_assets - current_liabilities)
    
    # MPBF = 75% of working capital
    mpbf = working_capital * 0.75
    
    return mpbf


def _calculate_cashflow_method(
    monthly_profit: float,
    existing_debt: float,
    score: int
) -> float:
    """
    Cash Flow Coverage Method
    
    Based on Debt Service Coverage Ratio (DSCR)
    
    Formula:
    Max Monthly EMI = Monthly Profit / Required DSCR
    Max Loan = Monthly EMI * Tenure / EMI Factor
    
    Required DSCR by score:
    - 750+: 1.10x
    - 650-749: 1.20x
    - 550-649: 1.30x
    - 450-549: 1.50x
    - <450: 2.00x
    """
    # Required DSCR by score
    if score >= 750:
        required_dscr = 1.10
        max_tenure = 36
    elif score >= 650:
        required_dscr = 1.20
        max_tenure = 24
    elif score >= 550:
        required_dscr = 1.30
        max_tenure = 18
    elif score >= 450:
        required_dscr = 1.50
        max_tenure = 12
    else:
        required_dscr = 2.00
        max_tenure = 6
    
    # Max EMI based on cashflow
    max_monthly_emi = monthly_profit / required_dscr
    
    # Assume average interest rate of 15% p.a.
    annual_rate = 0.15
    monthly_rate = annual_rate / 12
    
    # Calculate max loan using EMI formula
    if monthly_rate > 0:
        max_loan = max_monthly_emi * \
                   (((1 + monthly_rate)**max_tenure - 1) / \
                    (monthly_rate * (1 + monthly_rate)**max_tenure))
    else:
        max_loan = max_monthly_emi * max_tenure
    
    return max(0, max_loan)


def _get_vintage_multiplier(business_age_years: float) -> float:
    """
    Business vintage adjustment multiplier
    
    - <1 year: 0.50x
    - 1-2 years: 0.70x
    - 2-3 years: 0.85x
    - 3-5 years: 1.00x
    - 5-10 years: 1.10x
    - 10+ years: 1.20x
    """
    if business_age_years < 1:
        return 0.50
    elif business_age_years < 2:
        return 0.70
    elif business_age_years < 3:
        return 0.85
    elif business_age_years < 5:
        return 1.00
    elif business_age_years < 10:
        return 1.10
    else:
        return 1.20

