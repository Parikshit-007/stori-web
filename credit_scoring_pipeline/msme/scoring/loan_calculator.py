"""
Overdraft/Loan Limit Calculator
================================

Calculates recommended overdraft limits using multiple methodologies.

Author: ML Engineering Team
Version: 2.0.0
"""

import numpy as np
from typing import Dict, Optional


class OverdraftCalculator:
    """
    Overdraft limit calculation using industry-standard methods.
    """
    
    @staticmethod
    def turnover_method(
        annual_turnover: float,
        risk_tier_multiplier: float
    ) -> float:
        """
        RBI Recommended Turnover Method.
        
        Formula: OD Limit = Annual Turnover × Risk-Based Multiplier
        
        Args:
            annual_turnover: Annual gross turnover
            risk_tier_multiplier: Multiplier based on risk tier
            
        Returns:
            Maximum overdraft limit
        """
        return annual_turnover * risk_tier_multiplier
    
    @staticmethod
    def mpbf_tandon_method(
        current_assets: float,
        current_liabilities: float,
        existing_bank_debt: float
    ) -> float:
        """
        Maximum Permissible Bank Finance (MPBF) - Tandon Committee Method II.
        
        Formula: MPBF = 0.75 × (Current Assets - Current Liabilities) - Existing Debt
        
        Args:
            current_assets: Total current assets
            current_liabilities: Total current liabilities
            existing_bank_debt: Existing bank borrowings
            
        Returns:
            Maximum permissible bank finance
        """
        working_capital_gap = current_assets - current_liabilities
        mpbf = (working_capital_gap * 0.75) - existing_bank_debt
        return max(0, mpbf)
    
    @staticmethod
    def cash_flow_method(
        monthly_surplus: float,
        dscr_required: float
    ) -> float:
        """
        Cash Flow Coverage Method.
        
        Formula:
            Serviceable_EMI = Monthly_Surplus / DSCR_Required
            OD_Limit = Serviceable_EMI / 0.03
            
        Args:
            monthly_surplus: Monthly cash surplus after expenses
            dscr_required: Required DSCR
            
        Returns:
            Cash flow based limit
        """
        if monthly_surplus <= 0:
            return 0
        
        serviceable_emi = monthly_surplus / dscr_required
        limit = serviceable_emi / 0.03  # 3% EMI per month
        return max(0, limit)
    
    @staticmethod
    def dscr(
        net_operating_income: float,
        debt_service: float
    ) -> float:
        """
        Calculate Debt Service Coverage Ratio.
        
        Formula: DSCR = Net Operating Income / Total Debt Service
        
        Args:
            net_operating_income: NOI (EBITDA)
            debt_service: Total debt service
            
        Returns:
            DSCR value
        """
        if debt_service <= 0:
            return 999.0
        return net_operating_income / debt_service


def calculate_max_loan_limit(
    annual_turnover: float,
    monthly_surplus: float,
    risk_tier_multiplier: float,
    dscr_required: float,
    current_assets: Optional[float] = None,
    current_liabilities: Optional[float] = None,
    existing_debt: Optional[float] = None
) -> Dict[str, float]:
    """
    Calculate maximum loan limit using multiple methods.
    
    Args:
        annual_turnover: Annual turnover
        monthly_surplus: Monthly cash surplus
        risk_tier_multiplier: Risk-based multiplier
        dscr_required: Required DSCR
        current_assets: Current assets (optional)
        current_liabilities: Current liabilities (optional)
        existing_debt: Existing debt (optional)
        
    Returns:
        Dictionary with limits from each method and final recommendation
    """
    calc = OverdraftCalculator()
    
    # Method 1: Turnover
    turnover_limit = calc.turnover_method(annual_turnover, risk_tier_multiplier)
    
    # Method 2: Cash flow
    cash_flow_limit = calc.cash_flow_method(monthly_surplus, dscr_required)
    
    # Method 3: MPBF (if data available)
    mpbf_limit = None
    if all([current_assets, current_liabilities, existing_debt]):
        mpbf_limit = calc.mpbf_tandon_method(
            current_assets, current_liabilities, existing_debt
        )
    
    # Final recommendation: minimum of available methods
    limits = [turnover_limit, cash_flow_limit]
    if mpbf_limit is not None:
        limits.append(mpbf_limit)
    
    recommended_limit = min(limits)
    
    return {
        'turnover_method': turnover_limit,
        'cash_flow_method': cash_flow_limit,
        'mpbf_method': mpbf_limit,
        'recommended_limit': recommended_limit
    }
