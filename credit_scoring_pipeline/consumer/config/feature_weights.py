"""
Consumer Credit Scoring - Feature Weights Configuration
========================================================

All parameter weights as per business requirements.
Total: 100%

Author: ML Engineering Team
Version: 1.0.0
"""

from typing import Dict

# Parameter weights (%) - Total = 100%
CONSUMER_FEATURE_WEIGHTS = {
    # Identity & Verification (7%)
    'name_dob_verified': 1.0,
    'phone_number_verified': 1.5,
    'email_verified': 1.0,
    'education_level': 1.5,
    'identity_matching': 2.0,
    
    # Employment & Income (14%)
    'employment_history_score': 3.0,
    'monthly_income_stability': 5.0,
    'income_source_verification': 3.0,
    'regular_p2p_upi_transactions': 3.0,
    
    # Cash Flow & Banking (24%)
    'monthly_outflow_burden': 4.0,
    'avg_account_balance': 4.0,
    'survivability_months': 4.0,
    'income_retention_ratio': 4.0,
    'expense_rigidity': 2.0,
    'inflow_time_consistency': 2.0,
    'emi_to_monthly_upi_amount': 4.0,
    
    # Financial Assets & Insurance (9%)
    'total_financial_assets': 6.0,
    'insurance_coverage': 3.0,
    
    # Debt Burden (11%)
    'emi_to_income_ratio': 4.0,
    'rent_to_income_ratio': 2.0,
    'utility_to_income_ratio': 2.0,
    'insurance_payment_discipline': 3.0,
    
    # Behavioral Patterns (17%)
    'spending_personality_score': 3.0,
    'spending_discipline_index': 4.0,
    'bill_payment_discipline': 5.0,
    'late_night_payment_behaviour': 3.0,
    'utility_payment_consistency': 2.0,
    
    # Risk & Fraud (18%)
    'risk_appetite_score': 4.0,
    'pin_code_risk_score': 3.0,
    'bank_statement_manipulation': 5.0,
    'synthetic_id_risk': 6.0,
}

# Validate total weight = 100%
TOTAL_WEIGHT = sum(CONSUMER_FEATURE_WEIGHTS.values())
assert abs(TOTAL_WEIGHT - 100.0) < 0.1, f"Total weight must be 100%, got {TOTAL_WEIGHT}%"

# Feature categories
FEATURE_CATEGORIES = {
    'A_identity_verification': [
        'name_dob_verified', 'phone_number_verified', 'email_verified',
        'education_level', 'identity_matching'
    ],
    'B_employment_income': [
        'employment_history_score', 'monthly_income_stability',
        'income_source_verification', 'regular_p2p_upi_transactions'
    ],
    'C_cash_flow_banking': [
        'monthly_outflow_burden', 'avg_account_balance',
        'survivability_months', 'income_retention_ratio',
        'expense_rigidity', 'inflow_time_consistency',
        'emi_to_monthly_upi_amount'
    ],
    'D_financial_assets': [
        'total_financial_assets', 'insurance_coverage'
    ],
    'E_debt_burden': [
        'emi_to_income_ratio', 'rent_to_income_ratio',
        'utility_to_income_ratio', 'insurance_payment_discipline'
    ],
    'F_behavioral_patterns': [
        'spending_personality_score', 'spending_discipline_index',
        'bill_payment_discipline', 'late_night_payment_behaviour',
        'utility_payment_consistency'
    ],
    'G_risk_fraud': [
        'risk_appetite_score', 'pin_code_risk_score',
        'bank_statement_manipulation', 'synthetic_id_risk'
    ]
}

# Category weights
CATEGORY_WEIGHTS = {
    'A_identity_verification': 7.0,
    'B_employment_income': 14.0,
    'C_cash_flow_banking': 24.0,
    'D_financial_assets': 9.0,
    'E_debt_burden': 11.0,
    'F_behavioral_patterns': 17.0,
    'G_risk_fraud': 18.0
}

