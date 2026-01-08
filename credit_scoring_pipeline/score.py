"""
Credit Scoring Pipeline - Scoring Module
=========================================

This module provides:
1. score_user() function for real-time scoring
2. Persona subscore computation with exact weight mappings
3. Blending of GBM output with persona subscore
4. Probability to credit score mapping (300-900)
5. SHAP-based explanation generation

The persona subscore is computed as follows:
- Raw features are mapped to category-level normalized scores [0,1]
- Each category gets a weighted sum of normalized parameters using persona-specific weights
- Persona_subscore = Σ(category_score * category_weight) across categories A-G
- Higher persona_subscore = lower default risk

Blending formula:
  final_prob = alpha * gbm_pred_prob + (1-alpha) * (1 - persona_subscore)

Where:
- alpha = 0.7 (default, configurable)
- (1 - persona_subscore) converts the "good" score to a risk probability

Author: ML Engineering Team
Version: 1.0.0
"""

import numpy as np
import pandas as pd
import json
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
import joblib
import os

# ============================================================================
# PERSONA WEIGHT CONFIGURATION
# ============================================================================

# Default category weights (used when persona is not specified)
DEFAULT_CATEGORY_WEIGHTS = {
    'A_identity_stability_demographics': 0.10,
    'B_income_cashflow': 0.25,
    'C_assets_liabilities': 0.20,
    'D_spending_behavioral': 0.25,
    'E_transactions_repayments': 0.15,
    'F_fraud_identity': 0.05,
    'G_family_network': 0.05
}

# Persona-specific weight configurations
# These exactly match the specifications provided
PERSONA_WEIGHTS = {
    'new_to_credit': {
        'name': 'New-to-Credit (NTC)',
        'description': 'Users with limited or no credit history',
        'category_weights': {
            'A_identity_stability_demographics': 0.15,
            'B_income_cashflow': 0.35,
            'C_assets_liabilities': 0.05,
            'D_spending_behavioral': 0.30,
            'E_transactions_repayments': 0.09,
            'F_fraud_identity': 0.04,
            'G_family_network': 0.02
        },
        'intra_weights': {
            'A_identity_stability_demographics': {
                'name_dob': 0.02, 'phone': 0.02, 'email': 0.03,
                'location': 0.03, 'education': 0.03, 'employment_history': 0.02
            },
            'B_income_cashflow': {
                'income_proxies': 0.10, 'avg_balance': 0.04, 'income_stability': 0.07,
                'itr': 0.06, 'employability': 0.04, 'ppf_gov_schemes': 0.04
            },
            'C_assets_liabilities': {
                'lic_fd': 0.02, 'insurance_premium': 0.01, 'assets': 0.02,
                'current_loans': 0.0, 'credit_card_loan_data': 0.0
            },
            'D_spending_behavioral': {
                'spending_pattern': 0.10, 'subscription_cancellations': 0.03,
                'application_patterns': 0.04, 'impatience_credit': 0.04,
                'budgeting': 0.02, 'financial_literacy': 0.01,
                'recurring_payment_habit': 0.03, 'social_media': 0.02,
                'email_behaviour': 0.01, 'purchase_behaviour': 0.0
            },
            'E_transactions_repayments': {
                'upi_payment_transactions': 0.05, 'utility_payments': 0.02,
                'ecommerce': 0.02, 'repayment_behaviour': 0.0,
                'paid_subscriptions': 0.0, 'sip_investments_savings': 0.0
            },
            'F_fraud_identity': {
                'face_name_match': 0.02, 'location_device_intelligence': 0.01,
                'fraud_history': 0.01, 'income_source_verification': 0.0
            },
            'G_family_network': {
                'spouse_family_credit': 0.01, 'family_responsibility': 0.01
            }
        }
    },
    'gig_worker': {
        'name': 'Gig Worker / Freelancer',
        'description': 'Users with irregular income from gig/freelance work',
        'category_weights': {
            'A_identity_stability_demographics': 0.10,
            'B_income_cashflow': 0.40,
            'C_assets_liabilities': 0.08,
            'D_spending_behavioral': 0.25,
            'E_transactions_repayments': 0.14,
            'F_fraud_identity': 0.02,
            'G_family_network': 0.01
        },
        'intra_weights': {
            'A_identity_stability_demographics': {
                'name_dob': 0.01, 'phone': 0.02, 'email': 0.02,
                'location': 0.02, 'education': 0.01, 'employment_history': 0.02
            },
            'B_income_cashflow': {
                'income_proxies': 0.12, 'avg_balance': 0.10, 'income_stability': 0.10,
                'itr': 0.05, 'employability': 0.03, 'ppf_gov_schemes': 0.0
            },
            'C_assets_liabilities': {
                'current_loans': 0.03, 'credit_card_loan_data': 0.03,
                'insurance_premium': 0.01, 'assets': 0.01, 'lic_fd': 0.0
            },
            'D_spending_behavioral': {
                'spending_pattern': 0.08, 'subscription_cancellations': 0.03,
                'application_patterns': 0.02, 'impatience_credit': 0.04,
                'budgeting': 0.03, 'financial_literacy': 0.02,
                'recurring_payment_habit': 0.03, 'social_media': 0.0,
                'email_behaviour': 0.0, 'purchase_behaviour': 0.0
            },
            'E_transactions_repayments': {
                'upi_payment_transactions': 0.07, 'utility_payments': 0.05,
                'ecommerce': 0.02, 'repayment_behaviour': 0.0,
                'paid_subscriptions': 0.0, 'sip_investments_savings': 0.0
            },
            'F_fraud_identity': {
                'face_name_match': 0.01, 'location_device_intelligence': 0.01,
                'fraud_history': 0.0, 'income_source_verification': 0.0
            },
            'G_family_network': {
                'spouse_family_credit': 0.01, 'family_responsibility': 0.0
            }
        }
    },
    'salaried_professional': {
        'name': 'Salaried Professional',
        'description': 'Users with stable salaried employment',
        'category_weights': {
            'A_identity_stability_demographics': 0.10,
            'B_income_cashflow': 0.30,
            'C_assets_liabilities': 0.25,
            'D_spending_behavioral': 0.15,
            'E_transactions_repayments': 0.15,
            'F_fraud_identity': 0.03,
            'G_family_network': 0.02
        },
        'intra_weights': {
            'A_identity_stability_demographics': {
                'name_dob': 0.01, 'phone': 0.01, 'email': 0.02,
                'location': 0.01, 'education': 0.02, 'employment_history': 0.03
            },
            'B_income_cashflow': {
                'income_proxies': 0.05, 'avg_balance': 0.05, 'income_stability': 0.10,
                'itr': 0.06, 'employability': 0.03, 'ppf_gov_schemes': 0.01
            },
            'C_assets_liabilities': {
                'current_loans': 0.10, 'credit_card_loan_data': 0.10,
                'lic_fd': 0.02, 'insurance_premium': 0.02, 'assets': 0.01
            },
            'D_spending_behavioral': {
                'spending_pattern': 0.05, 'subscription_cancellations': 0.01,
                'application_patterns': 0.02, 'impatience_credit': 0.02,
                'budgeting': 0.02, 'financial_literacy': 0.02,
                'recurring_payment_habit': 0.01, 'social_media': 0.0,
                'email_behaviour': 0.0, 'purchase_behaviour': 0.0
            },
            'E_transactions_repayments': {
                'upi_payment_transactions': 0.03, 'utility_payments': 0.04,
                'repayment_behaviour': 0.06, 'ecommerce': 0.01,
                'sip_investments_savings': 0.01, 'paid_subscriptions': 0.0
            },
            'F_fraud_identity': {
                'face_name_match': 0.01, 'location_device_intelligence': 0.01,
                'fraud_history': 0.01, 'income_source_verification': 0.0
            },
            'G_family_network': {
                'spouse_family_credit': 0.02, 'family_responsibility': 0.0
            }
        }
    },
    'credit_experienced': {
        'name': 'Credit-Experienced Borrower',
        'description': 'Users with established credit history and multiple products',
        'category_weights': {
            'A_identity_stability_demographics': 0.05,
            'B_income_cashflow': 0.20,
            'C_assets_liabilities': 0.40,
            'D_spending_behavioral': 0.10,
            'E_transactions_repayments': 0.15,
            'F_fraud_identity': 0.05,
            'G_family_network': 0.05
        },
        'intra_weights': {
            'A_identity_stability_demographics': {
                'name_dob': 0.01, 'phone': 0.01, 'email': 0.01,
                'location': 0.01, 'education': 0.01, 'employment_history': 0.0
            },
            'B_income_cashflow': {
                'income_proxies': 0.02, 'avg_balance': 0.04, 'income_stability': 0.07,
                'itr': 0.03, 'employability': 0.02, 'ppf_gov_schemes': 0.02
            },
            'C_assets_liabilities': {
                'current_loans': 0.10, 'credit_card_loan_data': 0.10,
                'insurance_premium': 0.06, 'assets': 0.08, 'lic_fd': 0.06
            },
            'D_spending_behavioral': {
                'spending_pattern': 0.03, 'application_patterns': 0.02,
                'impatience_credit': 0.02, 'budgeting': 0.01,
                'financial_literacy': 0.02, 'subscription_cancellations': 0.0,
                'recurring_payment_habit': 0.0, 'social_media': 0.0,
                'email_behaviour': 0.0, 'purchase_behaviour': 0.0
            },
            'E_transactions_repayments': {
                'upi_payment_transactions': 0.03, 'utility_payments': 0.03,
                'repayment_behaviour': 0.05, 'sip_investments_savings': 0.04,
                'ecommerce': 0.0, 'paid_subscriptions': 0.0
            },
            'F_fraud_identity': {
                'face_name_match': 0.02, 'location_device_intelligence': 0.01,
                'fraud_history': 0.02, 'income_source_verification': 0.0
            },
            'G_family_network': {
                'spouse_family_credit': 0.05, 'family_responsibility': 0.0
            }
        }
    },
    'mass_affluent': {
        'name': 'Mass Affluent / High Asset',
        'description': 'High net worth users with significant assets',
        'category_weights': {
            'A_identity_stability_demographics': 0.03,
            'B_income_cashflow': 0.20,
            'C_assets_liabilities': 0.45,
            'D_spending_behavioral': 0.07,
            'E_transactions_repayments': 0.15,
            'F_fraud_identity': 0.05,
            'G_family_network': 0.05
        },
        'intra_weights': {
            'A_identity_stability_demographics': {
                'name_dob': 0.01, 'phone': 0.01, 'email': 0.01,
                'location': 0.0, 'education': 0.0, 'employment_history': 0.0
            },
            'B_income_cashflow': {
                'income_proxies': 0.04, 'avg_balance': 0.06, 'income_stability': 0.04,
                'itr': 0.03, 'employability': 0.02, 'ppf_gov_schemes': 0.01
            },
            'C_assets_liabilities': {
                'current_loans': 0.08, 'credit_card_loan_data': 0.10,
                'lic_fd': 0.05, 'insurance_premium': 0.05, 'assets': 0.17
            },
            'D_spending_behavioral': {
                'spending_pattern': 0.03, 'purchase_behaviour': 0.01,
                'subscription_cancellations': 0.01, 'budgeting': 0.01,
                'financial_literacy': 0.01, 'application_patterns': 0.0,
                'impatience_credit': 0.0, 'recurring_payment_habit': 0.0,
                'social_media': 0.0, 'email_behaviour': 0.0
            },
            'E_transactions_repayments': {
                'upi_payment_transactions': 0.02, 'utility_payments': 0.04,
                'repayment_behaviour': 0.05, 'sip_investments_savings': 0.04,
                'ecommerce': 0.0, 'paid_subscriptions': 0.0
            },
            'F_fraud_identity': {
                'face_name_match': 0.02, 'location_device_intelligence': 0.01,
                'fraud_history': 0.02, 'income_source_verification': 0.0
            },
            'G_family_network': {
                'spouse_family_credit': 0.05, 'family_responsibility': 0.0
            }
        }
    }
}

# ============================================================================
# FEATURE TO PARAMETER GROUP MAPPING
# ============================================================================

# Maps features to parameter groups for intra-category weighting
FEATURE_TO_PARAM_GROUP = {
    # Category A: Identity & Demographics
    'name_dob_verified': 'name_dob',
    'phone_verified': 'phone',
    'phone_age_months': 'phone',
    'email_verified': 'email',
    'email_age_months': 'email',
    'location_stability_score': 'location',
    'location_tier': 'location',
    'education_level': 'education',
    'employment_tenure_months': 'employment_history',
    'employment_type': 'employment_history',
    
    # Category B: Income & Cashflow
    'monthly_income': 'income_proxies',
    'income_growth_rate': 'income_proxies',
    'avg_account_balance': 'avg_balance',
    'min_account_balance': 'avg_balance',
    'income_stability_score': 'income_stability',
    'income_variance_coefficient': 'income_stability',
    'itr_filed': 'itr',
    'itr_income_declared': 'itr',
    'bank_statement_months_available': 'itr',
    'employability_score': 'employability',
    'ppf_balance': 'ppf_gov_schemes',
    'gov_schemes_enrolled': 'ppf_gov_schemes',
    
    # Category C: Assets & Liabilities
    'current_loan_count': 'current_loans',
    'current_loan_amount': 'current_loans',
    'debt_to_income_ratio': 'current_loans',
    'credit_card_count': 'credit_card_loan_data',
    'credit_card_utilization': 'credit_card_loan_data',
    'credit_card_limit': 'credit_card_loan_data',
    'lic_policy_count': 'lic_fd',
    'lic_premium_annual': 'lic_fd',
    'fd_total_amount': 'lic_fd',
    'total_assets_value': 'assets',
    'insurance_premium_paid_ratio': 'insurance_premium',
    'insurance_renewal_ontime_ratio': 'insurance_premium',
    
    # Category D: Spending & Behavioral
    'monthly_spending': 'spending_pattern',
    'spending_to_income_ratio': 'spending_pattern',
    'essential_spending_ratio': 'spending_pattern',
    'discretionary_spending_ratio': 'spending_pattern',
    'purchase_frequency': 'purchase_behaviour',
    'avg_purchase_value': 'purchase_behaviour',
    'subscription_cancellation_count': 'subscription_cancellations',
    'subscription_downgrade_count': 'subscription_cancellations',
    'impatience_score': 'impatience_credit',
    'impulse_buying_score': 'impatience_credit',
    'budgeting_score': 'budgeting',
    'financial_literacy_score': 'financial_literacy',
    'recurring_payment_habit_score': 'recurring_payment_habit',
    'loan_application_count_6m': 'application_patterns',
    'application_rejection_rate': 'application_patterns',
    'social_media_score': 'social_media',
    'email_response_time_score': 'email_behaviour',
    
    # Category E: Transactions & Repayments
    'upi_transaction_count_monthly': 'upi_payment_transactions',
    'upi_transaction_amount_monthly': 'upi_payment_transactions',
    'p2m_transaction_ratio': 'upi_payment_transactions',
    'utility_payment_ontime_ratio': 'utility_payments',
    'rent_payment_ontime_ratio': 'utility_payments',
    'phone_bill_ontime_ratio': 'utility_payments',
    'internet_bill_ontime_ratio': 'utility_payments',
    'repayment_ontime_ratio': 'repayment_behaviour',
    'max_dpd_ever': 'repayment_behaviour',
    'avg_dpd': 'repayment_behaviour',
    'ecommerce_transaction_count': 'ecommerce',
    'ecommerce_return_rate': 'ecommerce',
    'paid_subscription_count': 'paid_subscriptions',
    'sip_active_count': 'sip_investments_savings',
    'sip_monthly_amount': 'sip_investments_savings',
    'investment_portfolio_value': 'sip_investments_savings',
    'savings_rate': 'sip_investments_savings',
    
    # Category F: Fraud & Identity
    'face_recognition_match_score': 'face_name_match',
    'name_match_score': 'face_name_match',
    'location_mismatch_flag': 'location_device_intelligence',
    'device_anomaly_score': 'location_device_intelligence',
    'fraud_history_flag': 'fraud_history',
    'fraud_attempt_count': 'fraud_history',
    'income_source_verified': 'income_source_verification',
    
    # Category G: Family & Network
    'spouse_credit_score': 'spouse_family_credit',
    'spouse_credit_available': 'spouse_family_credit',
    'family_credit_score_avg': 'spouse_family_credit',
    'family_credit_available': 'spouse_family_credit',
    'family_financial_responsibility_score': 'family_responsibility',
    'dependents_count': 'family_responsibility'
}

# Parameter group to category mapping
PARAM_GROUP_TO_CATEGORY = {
    'name_dob': 'A_identity_stability_demographics',
    'phone': 'A_identity_stability_demographics',
    'email': 'A_identity_stability_demographics',
    'location': 'A_identity_stability_demographics',
    'education': 'A_identity_stability_demographics',
    'employment_history': 'A_identity_stability_demographics',
    'income_proxies': 'B_income_cashflow',
    'avg_balance': 'B_income_cashflow',
    'income_stability': 'B_income_cashflow',
    'itr': 'B_income_cashflow',
    'employability': 'B_income_cashflow',
    'ppf_gov_schemes': 'B_income_cashflow',
    'current_loans': 'C_assets_liabilities',
    'credit_card_loan_data': 'C_assets_liabilities',
    'lic_fd': 'C_assets_liabilities',
    'assets': 'C_assets_liabilities',
    'insurance_premium': 'C_assets_liabilities',
    'spending_pattern': 'D_spending_behavioral',
    'purchase_behaviour': 'D_spending_behavioral',
    'subscription_cancellations': 'D_spending_behavioral',
    'impatience_credit': 'D_spending_behavioral',
    'budgeting': 'D_spending_behavioral',
    'financial_literacy': 'D_spending_behavioral',
    'recurring_payment_habit': 'D_spending_behavioral',
    'application_patterns': 'D_spending_behavioral',
    'social_media': 'D_spending_behavioral',
    'email_behaviour': 'D_spending_behavioral',
    'upi_payment_transactions': 'E_transactions_repayments',
    'utility_payments': 'E_transactions_repayments',
    'repayment_behaviour': 'E_transactions_repayments',
    'ecommerce': 'E_transactions_repayments',
    'paid_subscriptions': 'E_transactions_repayments',
    'sip_investments_savings': 'E_transactions_repayments',
    'face_name_match': 'F_fraud_identity',
    'location_device_intelligence': 'F_fraud_identity',
    'fraud_history': 'F_fraud_identity',
    'income_source_verification': 'F_fraud_identity',
    'spouse_family_credit': 'G_family_network',
    'family_responsibility': 'G_family_network'
}


# ============================================================================
# NORMALIZATION BOUNDS
# ============================================================================

# Default normalization bounds (min, max) for converting raw values to [0, 1]
# Higher normalized value = better (lower risk)
NORMALIZATION_BOUNDS = {
    # Category A
    'name_dob_verified': (0, 1, True),
    'phone_verified': (0, 1, True),
    'phone_age_months': (0, 120, True),
    'email_verified': (0, 1, True),
    'email_age_months': (0, 120, True),
    'location_stability_score': (0, 1, True),
    'location_tier': None,  # Categorical - handled separately
    'education_level': (0, 5, True),
    'employment_tenure_months': (0, 240, True),
    'employment_type': None,  # Categorical
    
    # Category B
    'monthly_income': (0, 500000, True),  # Using 95th percentile as max
    'income_growth_rate': (-0.3, 0.5, True),
    'avg_account_balance': (0, 1000000, True),
    'min_account_balance': (0, 500000, True),
    'income_stability_score': (0, 1, True),
    'income_variance_coefficient': (0, 1, False),  # Higher is worse
    'itr_filed': (0, 1, True),
    'itr_income_declared': (0, 5000000, True),
    'employability_score': (0, 1, True),
    'ppf_balance': (0, 1000000, True),
    'gov_schemes_enrolled': (0, 5, True),
    'bank_statement_months_available': (0, 24, True),
    
    # Category C
    'current_loan_count': (0, 10, False),  # Higher is worse
    'current_loan_amount': (0, 5000000, False),
    'credit_card_count': (0, 5, True),  # Moderate is good
    'credit_card_utilization': (0, 1, False),  # Higher is worse
    'credit_card_limit': (0, 1000000, True),
    'lic_policy_count': (0, 5, True),
    'lic_premium_annual': (0, 200000, True),
    'fd_total_amount': (0, 2000000, True),
    'total_assets_value': (0, 10000000, True),
    'insurance_premium_paid_ratio': (0, 1, True),
    'insurance_renewal_ontime_ratio': (0, 1, True),
    'debt_to_income_ratio': (0, 2, False),  # Higher is worse
    
    # Category D
    'monthly_spending': (0, 200000, None),  # Neutral
    'spending_to_income_ratio': (0, 1, False),  # Higher is worse
    'essential_spending_ratio': (0, 1, True),
    'discretionary_spending_ratio': (0, 1, False),
    'purchase_frequency': (0, 200, None),  # Neutral
    'avg_purchase_value': (0, 10000, None),
    'subscription_cancellation_count': (0, 10, False),
    'subscription_downgrade_count': (0, 10, False),
    'impatience_score': (0, 1, False),
    'impulse_buying_score': (0, 1, False),
    'budgeting_score': (0, 1, True),
    'financial_literacy_score': (0, 1, True),
    'recurring_payment_habit_score': (0, 1, True),
    'loan_application_count_6m': (0, 10, False),
    'application_rejection_rate': (0, 1, False),
    'social_media_score': (0, 1, True),
    'email_response_time_score': (0, 1, True),
    
    # Category E
    'upi_transaction_count_monthly': (0, 200, None),
    'upi_transaction_amount_monthly': (0, 500000, None),
    'p2m_transaction_ratio': (0, 1, None),
    'utility_payment_ontime_ratio': (0, 1, True),
    'rent_payment_ontime_ratio': (0, 1, True),
    'phone_bill_ontime_ratio': (0, 1, True),
    'internet_bill_ontime_ratio': (0, 1, True),
    'repayment_ontime_ratio': (0, 1, True),
    'max_dpd_ever': (0, 90, False),  # Higher is worse
    'avg_dpd': (0, 30, False),
    'ecommerce_transaction_count': (0, 100, None),
    'ecommerce_return_rate': (0, 1, False),
    'paid_subscription_count': (0, 10, True),
    'sip_active_count': (0, 5, True),
    'sip_monthly_amount': (0, 100000, True),
    'investment_portfolio_value': (0, 5000000, True),
    'savings_rate': (0, 1, True),
    
    # Category F
    'face_recognition_match_score': (0, 1, True),
    'name_match_score': (0, 1, True),
    'location_mismatch_flag': (0, 1, False),
    'device_anomaly_score': (0, 1, False),
    'fraud_history_flag': (0, 1, False),
    'fraud_attempt_count': (0, 5, False),
    'income_source_verified': (0, 1, True),
    
    # Category G
    'spouse_credit_score': (300, 900, True),
    'spouse_credit_available': (0, 1, True),
    'family_credit_score_avg': (300, 900, True),
    'family_credit_available': (0, 1, True),
    'family_financial_responsibility_score': (0, 1, True),
    'dependents_count': (0, 5, False)
}


# ============================================================================
# SCORING FUNCTIONS
# ============================================================================

def normalize_feature(value: float, feature_name: str, 
                      bounds: Dict = None) -> float:
    """
    Normalize a feature value to [0, 1] range.
    
    Higher normalized value always means BETTER (lower risk).
    
    Args:
        value: Raw feature value
        feature_name: Name of the feature
        bounds: Optional custom bounds dict
        
    Returns:
        Normalized value in [0, 1] where higher = better
    """
    bounds = bounds or NORMALIZATION_BOUNDS
    
    if feature_name not in bounds or bounds[feature_name] is None:
        # For categorical or undefined features, return 0.5 (neutral)
        return 0.5
    
    min_val, max_val, higher_is_better = bounds[feature_name]
    
    # Handle missing values
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return 0.5  # Neutral for missing
    
    # Clip to bounds
    value = np.clip(value, min_val, max_val)
    
    # Normalize to [0, 1]
    if max_val == min_val:
        normalized = 0.5
    else:
        normalized = (value - min_val) / (max_val - min_val)
    
    # Invert if higher raw value means worse outcome
    if higher_is_better is False:
        normalized = 1 - normalized
    elif higher_is_better is None:
        # Neutral feature - map to 0.5 centered
        normalized = 0.5
    
    return float(np.clip(normalized, 0, 1))


def compute_param_group_score(features: Dict, param_group: str, 
                               norm_bounds: Dict = None) -> float:
    """
    Compute normalized score for a parameter group.
    
    Args:
        features: Dict of feature name -> value
        param_group: Name of the parameter group
        norm_bounds: Normalization bounds
        
    Returns:
        Weighted average normalized score for the parameter group
    """
    # Get features belonging to this param group
    group_features = [f for f, g in FEATURE_TO_PARAM_GROUP.items() 
                     if g == param_group]
    
    if not group_features:
        return 0.5
    
    scores = []
    for feat in group_features:
        if feat in features:
            score = normalize_feature(features[feat], feat, norm_bounds)
            scores.append(score)
    
    if not scores:
        return 0.5
    
    return float(np.mean(scores))


def compute_category_score(features: Dict, category: str,
                           intra_weights: Dict = None,
                           norm_bounds: Dict = None) -> Tuple[float, Dict]:
    """
    Compute score for a category using weighted parameter group scores.
    
    Args:
        features: Dict of feature name -> value
        category: Category name (e.g., 'A_identity_stability_demographics')
        intra_weights: Dict of param_group -> weight within category
        norm_bounds: Normalization bounds
        
    Returns:
        Tuple of (category_score, param_group_scores_dict)
    """
    # Get param groups for this category
    category_param_groups = [pg for pg, cat in PARAM_GROUP_TO_CATEGORY.items() 
                            if cat == category]
    
    if not category_param_groups:
        return 0.5, {}
    
    # Default equal weights if not provided
    if intra_weights is None:
        intra_weights = {pg: 1.0 / len(category_param_groups) 
                        for pg in category_param_groups}
    
    # Compute param group scores
    param_scores = {}
    weighted_sum = 0.0
    weight_sum = 0.0
    
    for pg in category_param_groups:
        pg_score = compute_param_group_score(features, pg, norm_bounds)
        param_scores[pg] = pg_score
        
        weight = intra_weights.get(pg, 0.0)
        weighted_sum += pg_score * weight
        weight_sum += weight
    
    # Compute weighted category score
    if weight_sum > 0:
        category_score = weighted_sum / weight_sum
    else:
        category_score = 0.5
    
    return float(category_score), param_scores


def compute_persona_subscore(features: Dict, persona: str,
                             norm_bounds: Dict = None) -> Tuple[float, Dict]:
    """
    Compute persona-specific subscore using the exact weight mappings.
    
    Args:
        features: Dict of feature name -> value
        persona: Persona identifier (e.g., 'new_to_credit', 'gig_worker')
        norm_bounds: Optional custom normalization bounds
        
    Returns:
        Tuple of (persona_subscore, category_contributions)
        - persona_subscore is in [0, 1] where higher = lower risk
        - category_contributions shows each category's contribution
    """
    if persona not in PERSONA_WEIGHTS:
        # Fall back to default weights
        category_weights = DEFAULT_CATEGORY_WEIGHTS
        intra_weights_by_cat = None
    else:
        persona_config = PERSONA_WEIGHTS[persona]
        category_weights = persona_config['category_weights']
        intra_weights_by_cat = persona_config['intra_weights']
    
    category_scores = {}
    category_contributions = {}
    total_score = 0.0
    
    for category, cat_weight in category_weights.items():
        # Get intra-category weights for this persona
        intra_weights = None
        if intra_weights_by_cat and category in intra_weights_by_cat:
            intra_weights = intra_weights_by_cat[category]
        
        # Compute category score
        cat_score, param_scores = compute_category_score(
            features, category, intra_weights, norm_bounds
        )
        
        category_scores[category] = {
            'score': cat_score,
            'weight': cat_weight,
            'weighted_contribution': cat_score * cat_weight,
            'param_scores': param_scores
        }
        
        category_contributions[category] = cat_score * cat_weight
        total_score += cat_score * cat_weight
    
    # Normalize to [0, 1] (should already be if weights sum to 1)
    persona_subscore = np.clip(total_score, 0, 1)
    
    return float(persona_subscore), category_contributions


def prob_to_score(prob: float, min_score: int = 300, max_score: int = 900) -> int:
    """
    Map default probability to credit score.
    
    Lower probability -> Higher score
    
    Uses a piecewise linear mapping calibrated on typical default distributions:
    - P < 0.02: Score 800-900 (Very Low Risk)
    - P 0.02-0.05: Score 700-800 (Low Risk)
    - P 0.05-0.10: Score 600-700 (Medium Risk)
    - P 0.10-0.20: Score 500-600 (High Risk)
    - P > 0.20: Score 300-500 (Very High Risk)
    
    Args:
        prob: Default probability in [0, 1]
        min_score: Minimum credit score
        max_score: Maximum credit score
        
    Returns:
        Credit score in [min_score, max_score]
    """
    prob = np.clip(prob, 0, 1)
    
    # Piecewise linear mapping
    # Define breakpoints (prob, score)
    breakpoints = [
        (0.00, 900),
        (0.02, 800),
        (0.05, 700),
        (0.10, 600),
        (0.20, 500),
        (0.35, 400),
        (0.50, 350),
        (1.00, 300)
    ]
    
    # Find segment
    for i in range(len(breakpoints) - 1):
        p1, s1 = breakpoints[i]
        p2, s2 = breakpoints[i + 1]
        
        if p1 <= prob <= p2:
            # Linear interpolation
            if p2 == p1:
                return int(s1)
            slope = (s2 - s1) / (p2 - p1)
            score = s1 + slope * (prob - p1)
            return int(np.clip(round(score), min_score, max_score))
    
    return min_score


def blend_scores(gbm_prob: float, persona_subscore: float, 
                 alpha: float = 0.7) -> float:
    """
    Blend GBM prediction with persona subscore.
    
    Formula: final_prob = alpha * gbm_prob + (1-alpha) * (1 - persona_subscore)
    
    Note: persona_subscore is constructed so higher = lower risk,
    so we use (1 - persona_subscore) to get a risk-like value.
    
    Args:
        gbm_prob: GBM model prediction (probability of default)
        persona_subscore: Persona-weighted subscore (higher = lower risk)
        alpha: Blending weight for GBM (default 0.7)
        
    Returns:
        Blended default probability
    """
    # Convert persona_subscore (goodness) to risk probability
    persona_risk = 1 - persona_subscore
    
    # Blend
    final_prob = alpha * gbm_prob + (1 - alpha) * persona_risk
    
    return float(np.clip(final_prob, 0, 1))


# ============================================================================
# MAIN SCORING CLASS
# ============================================================================

class CreditScorer:
    """
    Production-ready credit scorer that combines GBM predictions
    with persona-based subscores.
    """
    
    def __init__(self, model_path: str = None, 
                 preprocessor_path: str = None,
                 config_path: str = None,
                 alpha: float = 0.7):
        """
        Initialize the scorer.
        
        Args:
            model_path: Path to trained model (joblib)
            preprocessor_path: Path to fitted preprocessor
            config_path: Path to feature_config.json
            alpha: GBM weight in blending (default 0.7)
        """
        self.model = None
        self.preprocessor = None
        self.config = None
        self.alpha = alpha
        self.model_version = "unknown"
        
        if model_path and os.path.exists(model_path):
            self._load_model(model_path)
        
        if preprocessor_path and os.path.exists(preprocessor_path):
            self._load_preprocessor(preprocessor_path)
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
    
    def _load_model(self, path: str):
        """Load trained model"""
        from train import CreditScoringModel
        self.model = CreditScoringModel.load(path)
        self.model_version = self.model.model_version
    
    def _load_preprocessor(self, path: str):
        """Load fitted preprocessor"""
        from data_prep import CreditScoringPreprocessor
        self.preprocessor = CreditScoringPreprocessor()
        self.preprocessor.load(path)
    
    def score_user(self, features: Dict, persona: str = None,
                   alpha: float = None, include_explanation: bool = True) -> Dict:
        """
        Score a user based on features and persona.
        
        This is the main scoring function that:
        1. Preprocesses raw features
        2. Gets GBM model prediction
        3. Computes persona subscore
        4. Blends predictions
        5. Maps to credit score
        6. Generates explanation
        
        Args:
            features: Dict of raw feature values
            persona: Persona identifier (optional)
            alpha: Override default alpha for blending
            include_explanation: Whether to include SHAP explanation
            
        Returns:
            Dict with score, probabilities, and explanation
        """
        alpha = alpha if alpha is not None else self.alpha
        
        # Default persona if not specified
        if persona is None:
            persona = 'salaried_professional'
        
        # Step 1: Compute persona subscore (on raw features)
        persona_subscore, category_contributions = compute_persona_subscore(
            features, persona
        )
        
        # Step 2: Get GBM prediction
        if self.model is not None:
            # Preprocess features
            feature_df = pd.DataFrame([features])
            
            if self.preprocessor is not None:
                try:
                    processed_df = self.preprocessor.transform(feature_df)
                except Exception as e:
                    # If preprocessing fails, try direct prediction
                    processed_df = feature_df
            else:
                processed_df = feature_df
            
            # Ensure all expected columns exist
            expected_cols = self.model.feature_names
            for col in expected_cols:
                if col not in processed_df.columns:
                    processed_df[col] = 0  # Default fallback
            
            processed_df = processed_df[expected_cols]
            
            # Get model prediction
            gbm_prob = float(self.model.predict_proba(processed_df)[0])
            
            # Get SHAP explanation
            if include_explanation:
                explanation = self.model.explain_prediction(processed_df)
            else:
                explanation = None
        else:
            # If no model, use persona subscore only
            gbm_prob = 1 - persona_subscore
            explanation = None
        
        # Step 3: Blend scores
        final_prob = blend_scores(gbm_prob, persona_subscore, alpha)
        
        # Step 4: Map to credit score
        credit_score = prob_to_score(final_prob)
        
        # Step 5: Determine risk category
        if credit_score >= 800:
            risk_category = "Very Low Risk"
        elif credit_score >= 700:
            risk_category = "Low Risk"
        elif credit_score >= 600:
            risk_category = "Medium Risk"
        elif credit_score >= 500:
            risk_category = "High Risk"
        else:
            risk_category = "Very High Risk"
        
        # Compile result
        result = {
            'score': credit_score,
            'prob_default_90dpd': round(final_prob, 4),
            'risk_category': risk_category,
            'model_version': self.model_version,
            'persona': PERSONA_WEIGHTS.get(persona, {}).get('name', persona),
            'component_scores': {
                'gbm_prediction': round(gbm_prob, 4),
                'persona_subscore': round(persona_subscore, 4),
                'alpha': alpha,
                'blended_probability': round(final_prob, 4)
            },
            'category_contributions': {
                k: round(v, 4) for k, v in category_contributions.items()
            }
        }
        
        if explanation:
            result['explanation'] = explanation
        
        return result
    
    def score_batch(self, features_list: List[Dict], 
                    personas: List[str] = None,
                    alpha: float = None) -> List[Dict]:
        """
        Score multiple users.
        
        Args:
            features_list: List of feature dicts
            personas: List of persona identifiers (or single persona for all)
            alpha: Blending weight
            
        Returns:
            List of score dicts
        """
        if personas is None:
            personas = ['salaried_professional'] * len(features_list)
        elif isinstance(personas, str):
            personas = [personas] * len(features_list)
        
        results = []
        for features, persona in zip(features_list, personas):
            result = self.score_user(
                features, persona, alpha, 
                include_explanation=False
            )
            results.append(result)
        
        return results


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def score_user(features: Dict, persona: str = None, 
               model_path: str = None, alpha: float = 0.7) -> Dict:
    """
    Convenience function to score a single user.
    
    Args:
        features: Dict of feature values
        persona: Persona identifier
        model_path: Path to trained model (optional)
        alpha: GBM weight in blending
        
    Returns:
        Dict with score and probabilities
    """
    scorer = CreditScorer(model_path=model_path, alpha=alpha)
    return scorer.score_user(features, persona)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Example usage
    print("=" * 60)
    print("CREDIT SCORING DEMO")
    print("=" * 60)
    
    # Sample features for a user
    sample_features = {
        # Identity
        'name_dob_verified': 1,
        'phone_verified': 1,
        'phone_age_months': 48,
        'email_verified': 1,
        'email_age_months': 60,
        'location_stability_score': 0.8,
        'education_level': 3,
        'employment_tenure_months': 36,
        
        # Income
        'monthly_income': 75000,
        'income_growth_rate': 0.1,
        'avg_account_balance': 150000,
        'income_stability_score': 0.85,
        'itr_filed': 1,
        'itr_income_declared': 900000,
        'employability_score': 0.75,
        
        # Assets/Liabilities
        'current_loan_count': 1,
        'current_loan_amount': 500000,
        'credit_card_count': 2,
        'credit_card_utilization': 0.35,
        'total_assets_value': 2000000,
        'debt_to_income_ratio': 0.6,
        
        # Behavioral
        'spending_to_income_ratio': 0.6,
        'budgeting_score': 0.7,
        'financial_literacy_score': 0.65,
        'impatience_score': 0.3,
        'recurring_payment_habit_score': 0.8,
        
        # Repayments
        'utility_payment_ontime_ratio': 0.95,
        'repayment_ontime_ratio': 0.92,
        'max_dpd_ever': 15,
        'avg_dpd': 3,
        
        # Fraud
        'face_recognition_match_score': 0.98,
        'fraud_history_flag': 0,
        
        # Family
        'spouse_credit_available': 0,
        'dependents_count': 2
    }
    
    # Score with different personas
    personas = ['new_to_credit', 'gig_worker', 'salaried_professional', 
                'credit_experienced', 'mass_affluent']
    
    print("\nScoring sample user with different personas:")
    print("-" * 60)
    
    for persona in personas:
        subscore, contributions = compute_persona_subscore(sample_features, persona)
        score = prob_to_score(1 - subscore)  # Convert subscore to score
        
        print(f"\n{PERSONA_WEIGHTS[persona]['name']}:")
        print(f"  Persona Subscore: {subscore:.3f}")
        print(f"  Estimated Score: {score}")
        print(f"  Category Contributions:")
        for cat, contrib in sorted(contributions.items()):
            print(f"    {cat}: {contrib:.4f}")
    
    # Demo with scorer class (without model)
    print("\n" + "=" * 60)
    print("FULL SCORING (without model)")
    print("=" * 60)
    
    scorer = CreditScorer(alpha=0.7)
    result = scorer.score_user(sample_features, 'salaried_professional')
    
    print(f"\nCredit Score: {result['score']}")
    print(f"Default Probability: {result['prob_default_90dpd']:.4f}")
    print(f"Risk Category: {result['risk_category']}")
    print(f"\nComponent Scores:")
    for k, v in result['component_scores'].items():
        print(f"  {k}: {v}")


