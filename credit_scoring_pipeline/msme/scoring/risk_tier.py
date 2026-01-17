"""
Risk Tier Classification Module
================================

Classifies credit scores into risk tiers with associated parameters.

Author: ML Engineering Team
Version: 2.0.0
"""

from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class RiskTier:
    """Risk tier configuration"""
    name: str
    min_score: int
    max_score: int
    turnover_multiplier: float
    interest_rate_min: float
    interest_rate_max: float
    dscr_required: float
    max_tenure_months: int
    eligible: bool


# Risk tier definitions
RISK_TIERS = {
    'prime': RiskTier(
        name='Prime',
        min_score=750,
        max_score=900,
        turnover_multiplier=0.40,
        interest_rate_min=10.0,
        interest_rate_max=14.0,
        dscr_required=1.20,
        max_tenure_months=24,
        eligible=True
    ),
    'near_prime': RiskTier(
        name='Near Prime',
        min_score=650,
        max_score=749,
        turnover_multiplier=0.30,
        interest_rate_min=13.0,
        interest_rate_max=16.0,
        dscr_required=1.35,
        max_tenure_months=18,
        eligible=True
    ),
    'standard': RiskTier(
        name='Standard',
        min_score=550,
        max_score=649,
        turnover_multiplier=0.25,
        interest_rate_min=15.0,
        interest_rate_max=19.0,
        dscr_required=1.50,
        max_tenure_months=12,
        eligible=True
    ),
    'subprime': RiskTier(
        name='Subprime',
        min_score=450,
        max_score=549,
        turnover_multiplier=0.15,
        interest_rate_min=18.0,
        interest_rate_max=22.0,
        dscr_required=1.75,
        max_tenure_months=12,
        eligible=True
    ),
    'high_risk': RiskTier(
        name='High Risk',
        min_score=300,
        max_score=449,
        turnover_multiplier=0.00,
        interest_rate_min=22.0,
        interest_rate_max=26.0,
        dscr_required=2.00,
        max_tenure_months=6,
        eligible=False
    )
}


def get_risk_tier(score: int) -> RiskTier:
    """
    Get risk tier for a given credit score.
    
    Args:
        score: Credit score
        
    Returns:
        RiskTier object
    """
    for tier in RISK_TIERS.values():
        if tier.min_score <= score <= tier.max_score:
            return tier
    
    # Default to high risk
    return RISK_TIERS['high_risk']


def get_tier_name(score: int) -> str:
    """Get tier name for score"""
    return get_risk_tier(score).name


def is_eligible(score: int) -> bool:
    """Check if score is eligible for lending"""
    tier = get_risk_tier(score)
    return tier.eligible


def get_turnover_multiplier(score: int) -> float:
    """Get turnover multiplier for score"""
    return get_risk_tier(score).turnover_multiplier


def get_interest_rate_range(score: int) -> Dict[str, float]:
    """Get interest rate range for score"""
    tier = get_risk_tier(score)
    return {
        'min': tier.interest_rate_min,
        'max': tier.interest_rate_max,
        'mid': (tier.interest_rate_min + tier.interest_rate_max) / 2
    }


def get_dscr_required(score: int) -> float:
    """Get required DSCR for score"""
    return get_risk_tier(score).dscr_required


def get_max_tenure(score: int) -> int:
    """Get maximum tenure for score"""
    return get_risk_tier(score).max_tenure_months
