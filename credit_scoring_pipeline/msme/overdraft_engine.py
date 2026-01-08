"""
MSME Overdraft Limit Recommendation Engine
============================================

Industry-standard overdraft limit calculation based on:
1. Credit Score-based eligibility tiers
2. Turnover Method (20-40% of annual turnover)
3. MPBF (Maximum Permissible Bank Finance) method
4. Cash Flow Coverage (DSCR-based limits)
5. Debt Service Coverage Ratio (DSCR)
6. Business vintage and stability
7. Existing debt obligations
8. Collateral requirements

Reference Standards:
- RBI Guidelines for MSME Lending
- Basel III Capital Adequacy Norms
- CGTMSE (Credit Guarantee Trust for MSMEs) Guidelines
- Industry best practices from leading NBFC/Banks

Author: ML Engineering Team
Version: 1.0.0
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import json


# ============================================================================
# ENUMS AND CONSTANTS
# ============================================================================

class OverdraftEligibility(Enum):
    """Eligibility status for overdraft"""
    ELIGIBLE = "eligible"
    CONDITIONALLY_ELIGIBLE = "conditionally_eligible"
    MANUAL_REVIEW = "manual_review"
    NOT_ELIGIBLE = "not_eligible"


class RiskTier(Enum):
    """Risk tier based on credit score"""
    PRIME = "prime"                    # Score 750-900
    NEAR_PRIME = "near_prime"          # Score 650-749
    STANDARD = "standard"              # Score 550-649
    SUBPRIME = "subprime"              # Score 450-549
    HIGH_RISK = "high_risk"            # Score 300-449


class ProductType(Enum):
    """Types of overdraft products"""
    WORKING_CAPITAL_OD = "working_capital_od"      # Standard WC overdraft
    CASH_CREDIT = "cash_credit"                     # Cash credit facility
    DROPLINE_OD = "dropline_od"                     # Reducing balance OD
    FLEXI_OD = "flexi_od"                           # Flexible overdraft
    INVOICE_DISCOUNTING = "invoice_discounting"    # Against receivables


# ============================================================================
# INDUSTRY STANDARD PARAMETERS
# ============================================================================

# Score-based eligibility tiers
SCORE_TIERS = {
    RiskTier.PRIME: {
        'score_range': (750, 900),
        'eligibility': OverdraftEligibility.ELIGIBLE,
        'max_turnover_multiplier': 0.40,      # 40% of annual turnover
        'interest_rate_base': 10.5,            # Base rate %
        'processing_fee_pct': 0.50,            # Processing fee %
        'collateral_required': False,
        'personal_guarantee': False,
        'max_tenure_months': 36,
        'renewal_frequency_months': 12,
        'dscr_min': 1.10,
        'ltv_max': 0.90                        # Loan to value
    },
    RiskTier.NEAR_PRIME: {
        'score_range': (650, 749),
        'eligibility': OverdraftEligibility.ELIGIBLE,
        'max_turnover_multiplier': 0.30,
        'interest_rate_base': 13.0,
        'processing_fee_pct': 0.75,
        'collateral_required': False,
        'personal_guarantee': True,
        'max_tenure_months': 24,
        'renewal_frequency_months': 12,
        'dscr_min': 1.20,
        'ltv_max': 0.80
    },
    RiskTier.STANDARD: {
        'score_range': (550, 649),
        'eligibility': OverdraftEligibility.CONDITIONALLY_ELIGIBLE,
        'max_turnover_multiplier': 0.25,
        'interest_rate_base': 16.0,
        'processing_fee_pct': 1.00,
        'collateral_required': True,
        'personal_guarantee': True,
        'max_tenure_months': 18,
        'renewal_frequency_months': 6,
        'dscr_min': 1.30,
        'ltv_max': 0.70
    },
    RiskTier.SUBPRIME: {
        'score_range': (450, 549),
        'eligibility': OverdraftEligibility.MANUAL_REVIEW,
        'max_turnover_multiplier': 0.15,
        'interest_rate_base': 20.0,
        'processing_fee_pct': 1.50,
        'collateral_required': True,
        'personal_guarantee': True,
        'max_tenure_months': 12,
        'renewal_frequency_months': 6,
        'dscr_min': 1.50,
        'ltv_max': 0.60
    },
    RiskTier.HIGH_RISK: {
        'score_range': (300, 449),
        'eligibility': OverdraftEligibility.NOT_ELIGIBLE,
        'max_turnover_multiplier': 0.0,
        'interest_rate_base': 24.0,
        'processing_fee_pct': 2.00,
        'collateral_required': True,
        'personal_guarantee': True,
        'max_tenure_months': 0,
        'renewal_frequency_months': 0,
        'dscr_min': 2.00,
        'ltv_max': 0.50
    }
}

# Business vintage adjustments
VINTAGE_ADJUSTMENTS = {
    'less_than_1_year': {'limit_multiplier': 0.50, 'rate_adjustment': 2.0},
    '1_to_2_years': {'limit_multiplier': 0.70, 'rate_adjustment': 1.0},
    '2_to_3_years': {'limit_multiplier': 0.85, 'rate_adjustment': 0.5},
    '3_to_5_years': {'limit_multiplier': 1.00, 'rate_adjustment': 0.0},
    '5_to_10_years': {'limit_multiplier': 1.10, 'rate_adjustment': -0.5},
    'more_than_10_years': {'limit_multiplier': 1.20, 'rate_adjustment': -1.0}
}

# Industry risk adjustments
INDUSTRY_RISK_ADJUSTMENTS = {
    'technology': {'limit_multiplier': 1.10, 'rate_adjustment': -0.5},
    'healthcare': {'limit_multiplier': 1.05, 'rate_adjustment': 0.0},
    'manufacturing': {'limit_multiplier': 1.00, 'rate_adjustment': 0.0},
    'services': {'limit_multiplier': 1.00, 'rate_adjustment': 0.0},
    'retail': {'limit_multiplier': 0.95, 'rate_adjustment': 0.5},
    'trading': {'limit_multiplier': 0.90, 'rate_adjustment': 0.5},
    'logistics': {'limit_multiplier': 0.95, 'rate_adjustment': 0.5},
    'hospitality': {'limit_multiplier': 0.85, 'rate_adjustment': 1.0},
    'construction': {'limit_multiplier': 0.80, 'rate_adjustment': 1.5},
    'agriculture': {'limit_multiplier': 0.75, 'rate_adjustment': 1.5}
}

# MSME category limits (as per RBI guidelines)
MSME_LIMITS = {
    'micro': {'max_limit': 2500000, 'min_limit': 50000},      # Up to 25 Lakh
    'small': {'max_limit': 10000000, 'min_limit': 100000},    # Up to 1 Crore
    'medium': {'max_limit': 50000000, 'min_limit': 500000},   # Up to 5 Crore
    'not_registered': {'max_limit': 1000000, 'min_limit': 25000}
}

# Cash flow coverage requirements
CASH_FLOW_REQUIREMENTS = {
    'min_inflow_outflow_ratio': 1.05,
    'min_cash_buffer_days': 7,
    'max_negative_balance_days': 15,
    'min_avg_bank_balance_months': 1,  # 1 month GTV as min balance
}

# Existing debt constraints
DEBT_CONSTRAINTS = {
    'max_debt_to_turnover_ratio': 0.50,      # Max 50% of annual turnover as total debt
    'max_emi_to_cash_surplus_ratio': 0.40,   # EMI shouldn't exceed 40% of monthly surplus
    'max_total_exposure': 0.60               # Max 60% of annual turnover as total credit exposure
}


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class OverdraftRecommendation:
    """Complete overdraft recommendation"""
    eligibility: str
    risk_tier: str
    credit_score: int
    
    # Recommended limits
    recommended_limit: float
    min_limit: float
    max_limit: float
    
    # Methods used for calculation
    turnover_based_limit: float
    cash_flow_based_limit: float
    mpbf_based_limit: float
    final_adjusted_limit: float
    
    # Pricing
    interest_rate: float
    processing_fee_pct: float
    processing_fee_amount: float
    
    # Terms
    tenure_months: int
    renewal_frequency_months: int
    emi_amount: Optional[float]
    
    # Requirements
    collateral_required: bool
    collateral_value_required: float
    personal_guarantee_required: bool
    
    # Risk metrics
    dscr: float
    debt_to_turnover: float
    emi_coverage_ratio: float
    
    # Factors breakdown
    calculation_factors: Dict
    adjustment_factors: Dict
    conditions: List[str]
    recommendations: List[str]


# ============================================================================
# CALCULATION FUNCTIONS
# ============================================================================

def get_risk_tier(score: int) -> RiskTier:
    """Determine risk tier from credit score"""
    if score >= 750:
        return RiskTier.PRIME
    elif score >= 650:
        return RiskTier.NEAR_PRIME
    elif score >= 550:
        return RiskTier.STANDARD
    elif score >= 450:
        return RiskTier.SUBPRIME
    else:
        return RiskTier.HIGH_RISK


def get_vintage_category(business_age_years: float) -> str:
    """Categorize business vintage"""
    if business_age_years < 1:
        return 'less_than_1_year'
    elif business_age_years < 2:
        return '1_to_2_years'
    elif business_age_years < 3:
        return '2_to_3_years'
    elif business_age_years < 5:
        return '3_to_5_years'
    elif business_age_years < 10:
        return '5_to_10_years'
    else:
        return 'more_than_10_years'


def calculate_turnover_based_limit(
    annual_turnover: float,
    score: int,
    tier_params: Dict
) -> float:
    """
    Calculate limit using Turnover Method.
    Industry standard: 20-40% of annual turnover based on risk tier.
    """
    base_limit = annual_turnover * tier_params['max_turnover_multiplier']
    return max(0, base_limit)


def calculate_cash_flow_based_limit(
    monthly_cash_surplus: float,
    dscr_required: float,
    tenure_months: int
) -> float:
    """
    Calculate limit based on cash flow coverage.
    Limit = (Monthly Surplus / DSCR) * 12 months capacity
    """
    if monthly_cash_surplus <= 0:
        return 0
    
    serviceable_emi = monthly_cash_surplus / dscr_required
    # Assume EMI is ~3% of principal per month for OD (interest + principal repayment)
    limit = serviceable_emi / 0.03
    return max(0, limit)


def calculate_mpbf_limit(
    current_assets: float,
    current_liabilities: float,
    inventory: float,
    receivables: float,
    existing_debt: float
) -> float:
    """
    Calculate Maximum Permissible Bank Finance (MPBF).
    MPBF = 75% of (Current Assets - Current Liabilities) - Existing Bank Debt
    
    This is the Tandon Committee / RBI recommended method.
    """
    working_capital_gap = current_assets - current_liabilities
    
    # Method II of Tandon Committee
    # Borrower contributes 25% of working capital gap
    mpbf = working_capital_gap * 0.75 - existing_debt
    
    # Alternative: Based on inventory + receivables (more conservative)
    asset_based_limit = (inventory * 0.60 + receivables * 0.75) - existing_debt
    
    return max(0, min(mpbf, asset_based_limit))


def calculate_dscr(
    monthly_cash_inflow: float,
    monthly_cash_outflow: float,
    proposed_emi: float
) -> float:
    """
    Calculate Debt Service Coverage Ratio.
    DSCR = Net Cash Flow / Debt Service
    """
    net_cash_flow = monthly_cash_inflow - monthly_cash_outflow
    if proposed_emi <= 0:
        return 999.0  # No debt service
    return net_cash_flow / proposed_emi


def calculate_emi(
    principal: float,
    annual_rate: float,
    tenure_months: int
) -> float:
    """Calculate EMI using standard formula"""
    if tenure_months <= 0 or principal <= 0:
        return 0
    
    monthly_rate = annual_rate / 100 / 12
    
    if monthly_rate == 0:
        return principal / tenure_months
    
    emi = principal * monthly_rate * (1 + monthly_rate)**tenure_months / ((1 + monthly_rate)**tenure_months - 1)
    return emi


def apply_adjustments(
    base_limit: float,
    business_age_years: float,
    industry: str,
    cash_flow_health: float,
    payment_discipline: float
) -> Tuple[float, Dict]:
    """Apply various adjustments to base limit"""
    adjustments = {}
    adjusted_limit = base_limit
    
    # 1. Vintage adjustment
    vintage_cat = get_vintage_category(business_age_years)
    vintage_adj = VINTAGE_ADJUSTMENTS.get(vintage_cat, {'limit_multiplier': 1.0})
    adjusted_limit *= vintage_adj['limit_multiplier']
    adjustments['vintage'] = {
        'category': vintage_cat,
        'multiplier': vintage_adj['limit_multiplier']
    }
    
    # 2. Industry adjustment
    industry_adj = INDUSTRY_RISK_ADJUSTMENTS.get(
        industry.lower(), {'limit_multiplier': 1.0}
    )
    adjusted_limit *= industry_adj['limit_multiplier']
    adjustments['industry'] = {
        'industry': industry,
        'multiplier': industry_adj['limit_multiplier']
    }
    
    # 3. Cash flow health adjustment (0-1 score)
    cf_multiplier = 0.7 + (cash_flow_health * 0.4)  # Range: 0.7 to 1.1
    adjusted_limit *= cf_multiplier
    adjustments['cash_flow_health'] = {
        'score': cash_flow_health,
        'multiplier': cf_multiplier
    }
    
    # 4. Payment discipline adjustment (0-1 score)
    pd_multiplier = 0.8 + (payment_discipline * 0.3)  # Range: 0.8 to 1.1
    adjusted_limit *= pd_multiplier
    adjustments['payment_discipline'] = {
        'score': payment_discipline,
        'multiplier': pd_multiplier
    }
    
    return adjusted_limit, adjustments


def calculate_interest_rate(
    base_rate: float,
    business_age_years: float,
    industry: str,
    payment_discipline: float
) -> float:
    """Calculate final interest rate with adjustments"""
    rate = base_rate
    
    # Vintage adjustment
    vintage_cat = get_vintage_category(business_age_years)
    vintage_adj = VINTAGE_ADJUSTMENTS.get(vintage_cat, {'rate_adjustment': 0})
    rate += vintage_adj['rate_adjustment']
    
    # Industry adjustment
    industry_adj = INDUSTRY_RISK_ADJUSTMENTS.get(
        industry.lower(), {'rate_adjustment': 0}
    )
    rate += industry_adj['rate_adjustment']
    
    # Payment discipline discount (up to 1% reduction for excellent behavior)
    if payment_discipline >= 0.95:
        rate -= 1.0
    elif payment_discipline >= 0.90:
        rate -= 0.5
    elif payment_discipline < 0.70:
        rate += 1.0
    
    # Ensure rate is within bounds
    return max(10.0, min(rate, 26.0))


def check_debt_constraints(
    proposed_limit: float,
    existing_debt: float,
    annual_turnover: float,
    monthly_surplus: float,
    tenure_months: int,
    interest_rate: float
) -> Tuple[bool, List[str], float]:
    """
    Check if proposed limit meets debt constraints.
    Returns: (is_within_constraints, violations, adjusted_limit)
    """
    violations = []
    adjusted_limit = proposed_limit
    
    # 1. Check total debt to turnover
    total_debt = existing_debt + proposed_limit
    debt_to_turnover = total_debt / (annual_turnover + 1)
    
    if debt_to_turnover > DEBT_CONSTRAINTS['max_debt_to_turnover_ratio']:
        max_additional = annual_turnover * DEBT_CONSTRAINTS['max_debt_to_turnover_ratio'] - existing_debt
        adjusted_limit = min(adjusted_limit, max(0, max_additional))
        violations.append(f"Debt-to-turnover ratio {debt_to_turnover:.2f} exceeds max {DEBT_CONSTRAINTS['max_debt_to_turnover_ratio']}")
    
    # 2. Check EMI to surplus ratio
    if adjusted_limit > 0 and tenure_months > 0:
        emi = calculate_emi(adjusted_limit, interest_rate, tenure_months)
        emi_to_surplus = emi / (monthly_surplus + 1)
        
        if emi_to_surplus > DEBT_CONSTRAINTS['max_emi_to_cash_surplus_ratio']:
            max_emi = monthly_surplus * DEBT_CONSTRAINTS['max_emi_to_cash_surplus_ratio']
            # Back-calculate max limit from max EMI
            monthly_rate = interest_rate / 100 / 12
            if monthly_rate > 0:
                adjusted_limit = min(adjusted_limit, 
                    max_emi * ((1 + monthly_rate)**tenure_months - 1) / (monthly_rate * (1 + monthly_rate)**tenure_months))
            violations.append(f"EMI-to-surplus ratio {emi_to_surplus:.2f} exceeds max {DEBT_CONSTRAINTS['max_emi_to_cash_surplus_ratio']}")
    
    # 3. Check total exposure
    total_exposure = existing_debt + adjusted_limit
    exposure_ratio = total_exposure / (annual_turnover + 1)
    
    if exposure_ratio > DEBT_CONSTRAINTS['max_total_exposure']:
        max_exposure = annual_turnover * DEBT_CONSTRAINTS['max_total_exposure'] - existing_debt
        adjusted_limit = min(adjusted_limit, max(0, max_exposure))
        violations.append(f"Total exposure ratio {exposure_ratio:.2f} exceeds max {DEBT_CONSTRAINTS['max_total_exposure']}")
    
    is_within_constraints = len(violations) == 0
    return is_within_constraints, violations, adjusted_limit


def apply_msme_category_limits(
    limit: float,
    msme_category: str
) -> float:
    """Apply MSME category-based limits (RBI guidelines)"""
    category_limits = MSME_LIMITS.get(msme_category.lower(), MSME_LIMITS['not_registered'])
    
    return np.clip(limit, category_limits['min_limit'], category_limits['max_limit'])


# ============================================================================
# MAIN RECOMMENDATION ENGINE
# ============================================================================

class OverdraftRecommendationEngine:
    """
    Comprehensive overdraft recommendation engine following industry standards.
    
    Methods used:
    1. Turnover Method (RBI recommended)
    2. MPBF Method (Tandon Committee)
    3. Cash Flow Coverage Method
    4. Score-based eligibility
    
    Adjustments applied:
    - Business vintage
    - Industry risk
    - Cash flow health
    - Payment discipline
    - MSME category limits
    - Debt constraints
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.score_tiers = SCORE_TIERS
        self.vintage_adjustments = VINTAGE_ADJUSTMENTS
        self.industry_adjustments = INDUSTRY_RISK_ADJUSTMENTS
        self.msme_limits = MSME_LIMITS
    
    def calculate_recommendation(
        self,
        credit_score: int,
        # Business Profile
        business_age_years: float,
        industry: str,
        msme_category: str,
        # Financials
        monthly_gtv: float,
        annual_turnover: float = None,
        avg_bank_balance: float = 0,
        monthly_cash_inflow: float = None,
        monthly_cash_outflow: float = None,
        # Assets
        total_assets: float = 0,
        current_assets: float = 0,
        current_liabilities: float = 0,
        inventory_value: float = 0,
        receivables_value: float = 0,
        # Existing Debt
        existing_debt: float = 0,
        existing_emi: float = 0,
        # Behavioral Scores
        cash_flow_health_score: float = 0.5,
        payment_discipline_score: float = 0.5,
        # Override
        requested_amount: float = None
    ) -> OverdraftRecommendation:
        """
        Calculate comprehensive overdraft recommendation.
        
        Args:
            credit_score: MSME credit score (300-900)
            business_age_years: Years since business formation
            industry: Industry category
            msme_category: micro/small/medium
            monthly_gtv: Monthly gross transaction value
            annual_turnover: Annual turnover (defaults to monthly_gtv * 12)
            avg_bank_balance: Average bank balance
            monthly_cash_inflow: Monthly cash inflow
            monthly_cash_outflow: Monthly cash outflow
            total_assets: Total asset value
            current_assets: Current assets
            current_liabilities: Current liabilities
            inventory_value: Inventory value
            receivables_value: Receivables value
            existing_debt: Existing debt amount
            existing_emi: Existing EMI obligations
            cash_flow_health_score: Cash flow health (0-1)
            payment_discipline_score: Payment discipline (0-1)
            requested_amount: Specific amount requested by business
            
        Returns:
            OverdraftRecommendation with complete details
        """
        # Default calculations
        if annual_turnover is None:
            annual_turnover = monthly_gtv * 12
        
        if monthly_cash_inflow is None:
            monthly_cash_inflow = monthly_gtv * 1.1  # Assume 10% buffer
        
        if monthly_cash_outflow is None:
            monthly_cash_outflow = monthly_gtv * 0.85  # Assume 85% of inflow as outflow
        
        monthly_surplus = monthly_cash_inflow - monthly_cash_outflow - existing_emi
        
        # If current assets not provided, estimate from turnover
        if current_assets == 0:
            current_assets = annual_turnover * 0.25  # 3 months turnover
        
        if current_liabilities == 0:
            current_liabilities = annual_turnover * 0.15
        
        # Get risk tier
        risk_tier = get_risk_tier(credit_score)
        tier_params = self.score_tiers[risk_tier]
        
        # Check basic eligibility
        if tier_params['eligibility'] == OverdraftEligibility.NOT_ELIGIBLE:
            return self._create_ineligible_response(credit_score, risk_tier, tier_params)
        
        # ============================================================
        # STEP 1: Calculate limits using different methods
        # ============================================================
        
        # Method 1: Turnover-based limit
        turnover_limit = calculate_turnover_based_limit(
            annual_turnover, credit_score, tier_params
        )
        
        # Method 2: Cash flow-based limit
        cash_flow_limit = calculate_cash_flow_based_limit(
            monthly_surplus,
            tier_params['dscr_min'],
            tier_params['max_tenure_months']
        )
        
        # Method 3: MPBF-based limit
        mpbf_limit = calculate_mpbf_limit(
            current_assets,
            current_liabilities,
            inventory_value,
            receivables_value,
            existing_debt
        )
        
        # Take conservative approach: minimum of all methods
        base_limit = min(
            turnover_limit,
            cash_flow_limit if cash_flow_limit > 0 else float('inf'),
            mpbf_limit if mpbf_limit > 0 else float('inf')
        )
        
        if base_limit == float('inf'):
            base_limit = turnover_limit
        
        # ============================================================
        # STEP 2: Apply adjustments
        # ============================================================
        
        adjusted_limit, adjustment_factors = apply_adjustments(
            base_limit,
            business_age_years,
            industry,
            cash_flow_health_score,
            payment_discipline_score
        )
        
        # ============================================================
        # STEP 3: Calculate interest rate
        # ============================================================
        
        interest_rate = calculate_interest_rate(
            tier_params['interest_rate_base'],
            business_age_years,
            industry,
            payment_discipline_score
        )
        
        # ============================================================
        # STEP 4: Check debt constraints
        # ============================================================
        
        is_within_constraints, violations, constrained_limit = check_debt_constraints(
            adjusted_limit,
            existing_debt,
            annual_turnover,
            monthly_surplus,
            tier_params['max_tenure_months'],
            interest_rate
        )
        
        # ============================================================
        # STEP 5: Apply MSME category limits
        # ============================================================
        
        final_limit = apply_msme_category_limits(constrained_limit, msme_category)
        
        # Round to nearest 10000
        final_limit = round(final_limit / 10000) * 10000
        
        # ============================================================
        # STEP 6: Calculate EMI and DSCR
        # ============================================================
        
        emi = calculate_emi(
            final_limit,
            interest_rate,
            tier_params['max_tenure_months']
        )
        
        dscr = calculate_dscr(
            monthly_cash_inflow,
            monthly_cash_outflow,
            emi + existing_emi
        )
        
        # ============================================================
        # STEP 7: Calculate collateral requirements
        # ============================================================
        
        collateral_required = tier_params['collateral_required']
        collateral_value_required = 0
        
        if collateral_required:
            # Collateral = Limit / LTV
            collateral_value_required = final_limit / tier_params['ltv_max']
        
        # ============================================================
        # STEP 8: Generate conditions and recommendations
        # ============================================================
        
        conditions = []
        recommendations = []
        
        if tier_params['personal_guarantee']:
            conditions.append("Personal guarantee from promoter/director required")
        
        if collateral_required:
            conditions.append(f"Collateral worth ₹{collateral_value_required:,.0f} required")
        
        if business_age_years < 2:
            conditions.append("Additional documentation required for businesses < 2 years old")
        
        if dscr < 1.3:
            recommendations.append("Consider reducing requested amount for better DSCR")
        
        if len(violations) > 0:
            recommendations.extend([f"Constraint: {v}" for v in violations])
        
        if payment_discipline_score < 0.8:
            recommendations.append("Improve payment discipline for better rates")
        
        if cash_flow_health_score < 0.7:
            recommendations.append("Strengthen cash flow position for higher limits")
        
        # ============================================================
        # STEP 9: Create response
        # ============================================================
        
        msme_limits = self.msme_limits.get(msme_category.lower(), self.msme_limits['not_registered'])
        
        return OverdraftRecommendation(
            eligibility=tier_params['eligibility'].value,
            risk_tier=risk_tier.value,
            credit_score=credit_score,
            
            recommended_limit=final_limit,
            min_limit=msme_limits['min_limit'],
            max_limit=msme_limits['max_limit'],
            
            turnover_based_limit=round(turnover_limit),
            cash_flow_based_limit=round(cash_flow_limit),
            mpbf_based_limit=round(mpbf_limit),
            final_adjusted_limit=round(final_limit),
            
            interest_rate=round(interest_rate, 2),
            processing_fee_pct=tier_params['processing_fee_pct'],
            processing_fee_amount=round(final_limit * tier_params['processing_fee_pct'] / 100),
            
            tenure_months=tier_params['max_tenure_months'],
            renewal_frequency_months=tier_params['renewal_frequency_months'],
            emi_amount=round(emi) if emi > 0 else None,
            
            collateral_required=collateral_required,
            collateral_value_required=round(collateral_value_required),
            personal_guarantee_required=tier_params['personal_guarantee'],
            
            dscr=round(dscr, 2),
            debt_to_turnover=round((existing_debt + final_limit) / (annual_turnover + 1), 2),
            emi_coverage_ratio=round(monthly_surplus / (emi + 1), 2) if emi > 0 else 999,
            
            calculation_factors={
                'annual_turnover': annual_turnover,
                'monthly_surplus': round(monthly_surplus),
                'current_assets': current_assets,
                'current_liabilities': current_liabilities,
                'existing_debt': existing_debt,
                'business_age_years': business_age_years,
                'industry': industry,
                'msme_category': msme_category
            },
            adjustment_factors=adjustment_factors,
            conditions=conditions,
            recommendations=recommendations
        )
    
    def _create_ineligible_response(
        self, 
        credit_score: int, 
        risk_tier: RiskTier,
        tier_params: Dict
    ) -> OverdraftRecommendation:
        """Create response for ineligible applications"""
        return OverdraftRecommendation(
            eligibility=OverdraftEligibility.NOT_ELIGIBLE.value,
            risk_tier=risk_tier.value,
            credit_score=credit_score,
            
            recommended_limit=0,
            min_limit=0,
            max_limit=0,
            
            turnover_based_limit=0,
            cash_flow_based_limit=0,
            mpbf_based_limit=0,
            final_adjusted_limit=0,
            
            interest_rate=tier_params['interest_rate_base'],
            processing_fee_pct=tier_params['processing_fee_pct'],
            processing_fee_amount=0,
            
            tenure_months=0,
            renewal_frequency_months=0,
            emi_amount=None,
            
            collateral_required=True,
            collateral_value_required=0,
            personal_guarantee_required=True,
            
            dscr=0,
            debt_to_turnover=0,
            emi_coverage_ratio=0,
            
            calculation_factors={},
            adjustment_factors={},
            conditions=[
                "Credit score below minimum threshold (450)",
                "Application requires significant credit improvement"
            ],
            recommendations=[
                "Improve credit score to at least 450 for eligibility",
                "Clear any existing defaults or write-offs",
                "Establish consistent payment history for 6+ months",
                "Maintain positive cash flow for 3+ months"
            ]
        )
    
    def get_quick_estimate(
        self,
        credit_score: int,
        monthly_gtv: float,
        msme_category: str = 'micro'
    ) -> Dict:
        """
        Get quick overdraft estimate based on minimal inputs.
        
        Args:
            credit_score: Credit score (300-900)
            monthly_gtv: Monthly gross transaction value
            msme_category: micro/small/medium
            
        Returns:
            Quick estimate dict
        """
        risk_tier = get_risk_tier(credit_score)
        tier_params = self.score_tiers[risk_tier]
        
        if tier_params['eligibility'] == OverdraftEligibility.NOT_ELIGIBLE:
            return {
                'eligible': False,
                'reason': 'Credit score below minimum threshold',
                'min_score_required': 450
            }
        
        annual_turnover = monthly_gtv * 12
        estimated_limit = annual_turnover * tier_params['max_turnover_multiplier']
        
        # Apply MSME limits
        msme_limit = self.msme_limits.get(msme_category.lower(), self.msme_limits['not_registered'])
        estimated_limit = np.clip(estimated_limit, msme_limit['min_limit'], msme_limit['max_limit'])
        
        return {
            'eligible': True,
            'eligibility_type': tier_params['eligibility'].value,
            'risk_tier': risk_tier.value,
            'estimated_limit_min': round(estimated_limit * 0.7 / 10000) * 10000,
            'estimated_limit_max': round(estimated_limit / 10000) * 10000,
            'estimated_rate_range': f"{tier_params['interest_rate_base']}-{tier_params['interest_rate_base'] + 3}%",
            'collateral_required': tier_params['collateral_required'],
            'note': 'Final limit subject to detailed assessment'
        }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def calculate_overdraft_limit(
    credit_score: int,
    monthly_gtv: float,
    business_age_years: float = 3,
    industry: str = 'trading',
    msme_category: str = 'micro',
    existing_debt: float = 0,
    cash_flow_health_score: float = 0.7,
    payment_discipline_score: float = 0.8,
    **kwargs
) -> Dict:
    """
    Convenience function to calculate overdraft limit.
    
    Returns dict with limit and details.
    """
    engine = OverdraftRecommendationEngine()
    
    recommendation = engine.calculate_recommendation(
        credit_score=credit_score,
        business_age_years=business_age_years,
        industry=industry,
        msme_category=msme_category,
        monthly_gtv=monthly_gtv,
        existing_debt=existing_debt,
        cash_flow_health_score=cash_flow_health_score,
        payment_discipline_score=payment_discipline_score,
        **kwargs
    )
    
    return {
        'eligibility': recommendation.eligibility,
        'risk_tier': recommendation.risk_tier,
        'credit_score': recommendation.credit_score,
        'recommended_limit': recommendation.recommended_limit,
        'interest_rate': recommendation.interest_rate,
        'tenure_months': recommendation.tenure_months,
        'emi_amount': recommendation.emi_amount,
        'processing_fee': recommendation.processing_fee_amount,
        'collateral_required': recommendation.collateral_required,
        'collateral_amount': recommendation.collateral_value_required,
        'dscr': recommendation.dscr,
        'conditions': recommendation.conditions,
        'recommendations': recommendation.recommendations,
        'calculation_methods': {
            'turnover_method': recommendation.turnover_based_limit,
            'cash_flow_method': recommendation.cash_flow_based_limit,
            'mpbf_method': recommendation.mpbf_based_limit
        }
    }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("MSME OVERDRAFT RECOMMENDATION ENGINE DEMO")
    print("=" * 70)
    
    engine = OverdraftRecommendationEngine()
    
    # Test cases with different profiles
    test_cases = [
        {
            'name': 'Prime MSME (High Score)',
            'credit_score': 780,
            'monthly_gtv': 5000000,
            'business_age_years': 5,
            'industry': 'trading',
            'msme_category': 'small',
            'existing_debt': 500000,
            'cash_flow_health_score': 0.85,
            'payment_discipline_score': 0.92
        },
        {
            'name': 'Near-Prime MSME',
            'credit_score': 680,
            'monthly_gtv': 2500000,
            'business_age_years': 3,
            'industry': 'services',
            'msme_category': 'micro',
            'existing_debt': 200000,
            'cash_flow_health_score': 0.75,
            'payment_discipline_score': 0.85
        },
        {
            'name': 'New Business (Low Vintage)',
            'credit_score': 620,
            'monthly_gtv': 1500000,
            'business_age_years': 1,
            'industry': 'retail',
            'msme_category': 'micro',
            'existing_debt': 0,
            'cash_flow_health_score': 0.65,
            'payment_discipline_score': 0.78
        },
        {
            'name': 'High Risk Profile',
            'credit_score': 480,
            'monthly_gtv': 1000000,
            'business_age_years': 2,
            'industry': 'construction',
            'msme_category': 'micro',
            'existing_debt': 300000,
            'cash_flow_health_score': 0.50,
            'payment_discipline_score': 0.60
        },
        {
            'name': 'Ineligible (Very Low Score)',
            'credit_score': 380,
            'monthly_gtv': 800000,
            'business_age_years': 1.5,
            'industry': 'hospitality',
            'msme_category': 'micro',
            'existing_debt': 200000,
            'cash_flow_health_score': 0.40,
            'payment_discipline_score': 0.50
        }
    ]
    
    for case in test_cases:
        print(f"\n{'='*70}")
        print(f"Case: {case['name']}")
        print(f"{'='*70}")
        
        recommendation = engine.calculate_recommendation(
            credit_score=case['credit_score'],
            business_age_years=case['business_age_years'],
            industry=case['industry'],
            msme_category=case['msme_category'],
            monthly_gtv=case['monthly_gtv'],
            existing_debt=case['existing_debt'],
            cash_flow_health_score=case['cash_flow_health_score'],
            payment_discipline_score=case['payment_discipline_score']
        )
        
        print(f"\nCredit Score: {recommendation.credit_score}")
        print(f"Risk Tier: {recommendation.risk_tier}")
        print(f"Eligibility: {recommendation.eligibility}")
        print(f"\n--- RECOMMENDED LIMIT ---")
        print(f"Recommended Limit: ₹{recommendation.recommended_limit:,.0f}")
        print(f"  - Turnover Method: ₹{recommendation.turnover_based_limit:,.0f}")
        print(f"  - Cash Flow Method: ₹{recommendation.cash_flow_based_limit:,.0f}")
        print(f"  - MPBF Method: ₹{recommendation.mpbf_based_limit:,.0f}")
        print(f"\n--- PRICING ---")
        print(f"Interest Rate: {recommendation.interest_rate}% p.a.")
        print(f"Processing Fee: {recommendation.processing_fee_pct}% (₹{recommendation.processing_fee_amount:,.0f})")
        print(f"Tenure: {recommendation.tenure_months} months")
        if recommendation.emi_amount:
            print(f"EMI: ₹{recommendation.emi_amount:,.0f}/month")
        print(f"\n--- RISK METRICS ---")
        print(f"DSCR: {recommendation.dscr}")
        print(f"Debt-to-Turnover: {recommendation.debt_to_turnover}")
        print(f"\n--- REQUIREMENTS ---")
        print(f"Collateral Required: {recommendation.collateral_required}")
        if recommendation.collateral_required:
            print(f"Collateral Value: ₹{recommendation.collateral_value_required:,.0f}")
        print(f"Personal Guarantee: {recommendation.personal_guarantee_required}")
        
        if recommendation.conditions:
            print(f"\n--- CONDITIONS ---")
            for cond in recommendation.conditions:
                print(f"  • {cond}")
        
        if recommendation.recommendations:
            print(f"\n--- RECOMMENDATIONS ---")
            for rec in recommendation.recommendations:
                print(f"  • {rec}")


