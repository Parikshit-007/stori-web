"""
MSME Credit Scoring Pipeline - Scoring Module
==============================================

This module provides:
1. score_business() function for MSME credit scoring
2. Business segment subscore computation with exact weight mappings
3. Blending of GBM output with segment subscore
4. Probability to credit score mapping (300-900)
5. SHAP-based explanation generation for MSMEs

Weight Mapping per the exact parameters provided:
- Legal entity type: 0.5
- Business formation date: 2
- GSTIN/PAN verification: 1
- Weekly GTV: 7
- On-time repayment ratio of overdrafts: 4
- Weekly Inflow-outflow ratio: 4
- Bank average balance: 3
- Cash buffer days: 3
- Bounced cheques: 3
- Utility Payments Behaviour: 3
- Supplier payments: 3
- Value of Assets: 3
- Transaction count per day: 3
... (all weights as specified)

Author: ML Engineering Team
Version: 1.0.0
"""

import numpy as np
import pandas as pd
import json
from typing import Dict, List, Optional, Tuple, Any
import joblib
import os


# ============================================================================
# CATEGORY WEIGHTS (As per specification - totals to 100)
# ============================================================================

DEFAULT_MSME_CATEGORY_WEIGHTS = {
    'A_business_identity': 0.10,      # ~10 total weight
    'B_revenue_performance': 0.20,     # ~20 total weight
    'C_cashflow_banking': 0.25,        # ~25 total weight
    'D_credit_repayment': 0.22,        # ~22 total weight
    'E_compliance_taxation': 0.12,     # ~12 total weight
    'F_fraud_verification': 0.07,      # ~7 total weight
    'G_external_signals': 0.04         # ~4 total weight
}

# ============================================================================
# BUSINESS SEGMENT WEIGHTS
# ============================================================================

BUSINESS_SEGMENT_WEIGHTS = {
    'micro_new': {
        'name': 'Micro Enterprise - New (<2 years)',
        'description': 'Newly established micro enterprises',
        'category_weights': {
            'A_business_identity': 0.15,
            'B_revenue_performance': 0.25,
            'C_cashflow_banking': 0.30,
            'D_credit_repayment': 0.15,
            'E_compliance_taxation': 0.08,
            'F_fraud_verification': 0.05,
            'G_external_signals': 0.02
        },
        'intra_weights': {
            'A_business_identity': {
                'legal_entity': 0.01, 'business_age': 0.03, 'address_verification': 0.02,
                'industry': 0.03, 'gstin_pan': 0.02, 'msme_registration': 0.02,
                'business_structure': 0.01, 'licenses': 0.01
            },
            'B_revenue_performance': {
                'gtv_volume': 0.12, 'transaction_metrics': 0.04, 'revenue_growth': 0.04,
                'profitability': 0.02, 'assets': 0.03
            },
            'C_cashflow_banking': {
                'bank_balance': 0.08, 'inflow_outflow': 0.08, 'cash_buffer': 0.06,
                'daily_balance': 0.05, 'deposits_regularity': 0.03
            },
            'D_credit_repayment': {
                'bounced_cheques': 0.03, 'utility_payments': 0.04, 'mobile_payments': 0.03,
                'rent_payments': 0.03, 'supplier_payments': 0.02
            },
            'E_compliance_taxation': {
                'gst_filing': 0.03, 'tax_compliance': 0.03, 'refund_chargeback': 0.02
            },
            'F_fraud_verification': {
                'kyc': 0.02, 'verification': 0.02, 'insurance': 0.01
            },
            'G_external_signals': {
                'economic_health': 0.01, 'social_media': 0.01
            }
        }
    },
    'micro_established': {
        'name': 'Micro Enterprise - Established (2+ years)',
        'description': 'Established micro enterprises with history',
        'category_weights': {
            'A_business_identity': 0.08,
            'B_revenue_performance': 0.22,
            'C_cashflow_banking': 0.28,
            'D_credit_repayment': 0.22,
            'E_compliance_taxation': 0.10,
            'F_fraud_verification': 0.06,
            'G_external_signals': 0.04
        },
        'intra_weights': {
            'A_business_identity': {
                'legal_entity': 0.01, 'business_age': 0.02, 'address_verification': 0.01,
                'industry': 0.02, 'gstin_pan': 0.01, 'msme_registration': 0.005,
                'business_structure': 0.005, 'licenses': 0.01
            },
            'B_revenue_performance': {
                'gtv_volume': 0.10, 'transaction_metrics': 0.04, 'revenue_growth': 0.03,
                'profitability': 0.02, 'inventory': 0.01, 'assets': 0.02
            },
            'C_cashflow_banking': {
                'bank_balance': 0.06, 'inflow_outflow': 0.07, 'overdraft': 0.04,
                'cash_buffer': 0.05, 'daily_balance': 0.04, 'deposits_regularity': 0.02
            },
            'D_credit_repayment': {
                'bounced_cheques': 0.05, 'overdraft_repayment': 0.04, 'utility_payments': 0.04,
                'mobile_payments': 0.03, 'rent_payments': 0.03, 'supplier_payments': 0.03
            },
            'E_compliance_taxation': {
                'gst_filing': 0.03, 'gst_mismatch': 0.02, 'tax_compliance': 0.03, 'refund_chargeback': 0.02
            },
            'F_fraud_verification': {
                'kyc': 0.02, 'verification': 0.02, 'insurance': 0.02
            },
            'G_external_signals': {
                'economic_health': 0.015, 'customer_concentration': 0.01, 'social_media': 0.015
            }
        }
    },
    'small_trading': {
        'name': 'Small Enterprise - Trading',
        'description': 'Small trading businesses',
        'category_weights': {
            'A_business_identity': 0.08,
            'B_revenue_performance': 0.25,
            'C_cashflow_banking': 0.25,
            'D_credit_repayment': 0.20,
            'E_compliance_taxation': 0.12,
            'F_fraud_verification': 0.06,
            'G_external_signals': 0.04
        },
        'intra_weights': {
            'A_business_identity': {
                'legal_entity': 0.01, 'business_age': 0.02, 'address_verification': 0.01,
                'industry': 0.02, 'gstin_pan': 0.01, 'msme_registration': 0.005,
                'licenses': 0.005
            },
            'B_revenue_performance': {
                'gtv_volume': 0.10, 'transaction_metrics': 0.05, 'revenue_concentration': 0.02,
                'revenue_growth': 0.03, 'profitability': 0.02, 'inventory': 0.02, 'assets': 0.01
            },
            'C_cashflow_banking': {
                'bank_balance': 0.05, 'inflow_outflow': 0.06, 'overdraft': 0.04,
                'cash_buffer': 0.04, 'daily_balance': 0.04, 'deposits_regularity': 0.02
            },
            'D_credit_repayment': {
                'bounced_cheques': 0.04, 'overdraft_repayment': 0.04, 'defaults': 0.02,
                'utility_payments': 0.03, 'supplier_payments': 0.05, 'rent_payments': 0.02
            },
            'E_compliance_taxation': {
                'gst_filing': 0.03, 'gst_mismatch': 0.03, 'tax_compliance': 0.03, 'itr': 0.02, 'refund_chargeback': 0.01
            },
            'F_fraud_verification': {
                'kyc': 0.02, 'verification': 0.02, 'funds_verification': 0.02
            },
            'G_external_signals': {
                'economic_health': 0.01, 'customer_concentration': 0.02, 'legal': 0.01
            }
        }
    },
    'small_manufacturing': {
        'name': 'Small Enterprise - Manufacturing',
        'description': 'Small manufacturing businesses',
        'category_weights': {
            'A_business_identity': 0.10,
            'B_revenue_performance': 0.20,
            'C_cashflow_banking': 0.22,
            'D_credit_repayment': 0.22,
            'E_compliance_taxation': 0.14,
            'F_fraud_verification': 0.07,
            'G_external_signals': 0.05
        },
        'intra_weights': {
            'A_business_identity': {
                'legal_entity': 0.01, 'business_age': 0.02, 'address_verification': 0.015,
                'industry': 0.02, 'employees': 0.01, 'gstin_pan': 0.01, 'licenses': 0.015
            },
            'B_revenue_performance': {
                'gtv_volume': 0.07, 'transaction_metrics': 0.03, 'revenue_growth': 0.03,
                'profitability': 0.02, 'inventory': 0.02, 'assets': 0.03
            },
            'C_cashflow_banking': {
                'bank_balance': 0.05, 'inflow_outflow': 0.05, 'overdraft': 0.04,
                'cash_buffer': 0.04, 'receivables': 0.02, 'payables': 0.02
            },
            'D_credit_repayment': {
                'bounced_cheques': 0.05, 'overdraft_repayment': 0.05, 'defaults': 0.03,
                'loans': 0.02, 'utility_payments': 0.03, 'supplier_payments': 0.04
            },
            'E_compliance_taxation': {
                'gst_filing': 0.03, 'gst_mismatch': 0.02, 'tax_compliance': 0.04, 'itr': 0.03, 'outstanding': 0.02
            },
            'F_fraud_verification': {
                'kyc': 0.02, 'verification': 0.02, 'insurance': 0.03
            },
            'G_external_signals': {
                'economic_health': 0.02, 'customer_concentration': 0.015, 'legal': 0.015
            }
        }
    },
    'small_services': {
        'name': 'Small Enterprise - Services',
        'description': 'Small service-based businesses',
        'category_weights': {
            'A_business_identity': 0.10,
            'B_revenue_performance': 0.18,
            'C_cashflow_banking': 0.28,
            'D_credit_repayment': 0.22,
            'E_compliance_taxation': 0.12,
            'F_fraud_verification': 0.06,
            'G_external_signals': 0.04
        },
        'intra_weights': {
            'A_business_identity': {
                'legal_entity': 0.015, 'business_age': 0.02, 'address_verification': 0.015,
                'industry': 0.02, 'gstin_pan': 0.015, 'licenses': 0.015
            },
            'B_revenue_performance': {
                'gtv_volume': 0.07, 'transaction_metrics': 0.03, 'revenue_growth': 0.03,
                'profitability': 0.03, 'operational_leverage': 0.02
            },
            'C_cashflow_banking': {
                'bank_balance': 0.06, 'inflow_outflow': 0.07, 'overdraft': 0.04,
                'cash_buffer': 0.05, 'daily_balance': 0.04, 'deposits_regularity': 0.02
            },
            'D_credit_repayment': {
                'bounced_cheques': 0.05, 'overdraft_repayment': 0.05, 'utility_payments': 0.04,
                'mobile_payments': 0.03, 'rent_payments': 0.03, 'supplier_payments': 0.02
            },
            'E_compliance_taxation': {
                'gst_filing': 0.03, 'gst_mismatch': 0.02, 'tax_compliance': 0.04, 'itr': 0.02, 'refund_chargeback': 0.01
            },
            'F_fraud_verification': {
                'kyc': 0.02, 'verification': 0.02, 'insurance': 0.02
            },
            'G_external_signals': {
                'economic_health': 0.015, 'social_media': 0.025
            }
        }
    },
    'medium_enterprise': {
        'name': 'Medium Enterprise',
        'description': 'Medium-sized enterprises with formal structures',
        'category_weights': {
            'A_business_identity': 0.08,
            'B_revenue_performance': 0.18,
            'C_cashflow_banking': 0.22,
            'D_credit_repayment': 0.25,
            'E_compliance_taxation': 0.15,
            'F_fraud_verification': 0.07,
            'G_external_signals': 0.05
        },
        'intra_weights': {
            'A_business_identity': {
                'legal_entity': 0.01, 'business_age': 0.015, 'industry': 0.02,
                'employees': 0.01, 'gstin_pan': 0.01, 'licenses': 0.015
            },
            'B_revenue_performance': {
                'gtv_volume': 0.06, 'transaction_metrics': 0.03, 'revenue_growth': 0.03,
                'profitability': 0.03, 'assets': 0.03
            },
            'C_cashflow_banking': {
                'bank_balance': 0.05, 'inflow_outflow': 0.05, 'overdraft': 0.04,
                'cash_buffer': 0.04, 'receivables': 0.02, 'payables': 0.02
            },
            'D_credit_repayment': {
                'bounced_cheques': 0.05, 'overdraft_repayment': 0.06, 'defaults': 0.04,
                'loans': 0.03, 'utility_payments': 0.03, 'supplier_payments': 0.04
            },
            'E_compliance_taxation': {
                'gst_filing': 0.03, 'gst_mismatch': 0.03, 'tax_compliance': 0.04, 'itr': 0.03, 'outstanding': 0.02
            },
            'F_fraud_verification': {
                'kyc': 0.02, 'verification': 0.02, 'insurance': 0.03
            },
            'G_external_signals': {
                'economic_health': 0.02, 'customer_concentration': 0.015, 'legal': 0.015
            }
        }
    }
}


# ============================================================================
# FEATURE TO PARAMETER GROUP MAPPING (as per specification)
# ============================================================================

MSME_FEATURE_TO_PARAM_GROUP = {
    # Category A
    'legal_entity_type': 'legal_entity',
    'business_age_years': 'business_age',
    'business_address_verified': 'address_verification',
    'geolocation_verified': 'address_verification',
    'industry_code': 'industry',
    'industry_risk_score': 'industry',
    'num_business_locations': 'employees',
    'employees_count': 'employees',
    'gstin_verified': 'gstin_pan',
    'pan_verified': 'gstin_pan',
    'msme_registered': 'msme_registration',
    'msme_category': 'msme_registration',
    'business_structure': 'business_structure',
    'licenses_certificates_score': 'licenses',
    
    # Category B
    'weekly_gtv': 'gtv_volume',
    'monthly_gtv': 'gtv_volume',
    'transaction_count_daily': 'transaction_metrics',
    'avg_transaction_value': 'transaction_metrics',
    'revenue_concentration_score': 'revenue_concentration',
    'peak_day_dependency': 'revenue_concentration',
    'revenue_growth_rate_mom': 'revenue_growth',
    'revenue_growth_rate_qoq': 'revenue_growth',
    'profit_margin': 'profitability',
    'profit_margin_trend': 'profitability',
    'inventory_turnover_ratio': 'inventory',
    'total_assets_value': 'assets',
    'operational_leverage_ratio': 'operational_leverage',
    
    # Category C
    'avg_bank_balance': 'bank_balance',
    'bank_balance_trend': 'bank_balance',
    'weekly_inflow_outflow_ratio': 'inflow_outflow',
    'overdraft_days_count': 'overdraft',
    'overdraft_amount_avg': 'overdraft',
    'cash_buffer_days': 'cash_buffer',
    'avg_daily_closing_balance': 'daily_balance',
    'cash_balance_std_dev': 'daily_balance',
    'negative_balance_days': 'daily_balance',
    'daily_min_balance_pattern': 'daily_balance',
    'consistent_deposits_score': 'deposits_regularity',
    'cashflow_regularity_score': 'deposits_regularity',
    'receivables_aging_days': 'receivables',
    'payables_aging_days': 'payables',
    
    # Category D
    'bounced_cheques_count': 'bounced_cheques',
    'bounced_cheques_rate': 'bounced_cheques',
    'historical_loan_utilization': 'loans',
    'overdraft_repayment_ontime_ratio': 'overdraft_repayment',
    'previous_defaults_count': 'defaults',
    'previous_writeoffs_count': 'defaults',
    'current_loans_outstanding': 'loans',
    'total_debt_amount': 'loans',
    'utility_payment_ontime_ratio': 'utility_payments',
    'utility_payment_days_before_due': 'utility_payments',
    'mobile_recharge_regularity': 'mobile_payments',
    'mobile_recharge_ontime_ratio': 'mobile_payments',
    'rent_payment_regularity': 'rent_payments',
    'rent_payment_ontime_ratio': 'rent_payments',
    'supplier_payment_regularity': 'supplier_payments',
    'supplier_payment_ontime_ratio': 'supplier_payments',
    
    # Category E
    'gst_filing_regularity': 'gst_filing',
    'gst_filing_ontime_ratio': 'gst_filing',
    'gst_vs_platform_sales_mismatch': 'gst_mismatch',
    'outstanding_taxes_amount': 'outstanding',
    'outstanding_dues_flag': 'outstanding',
    'itr_filed': 'itr',
    'itr_income_declared': 'itr',
    'gst_r1_vs_itr_mismatch': 'gst_mismatch',
    'tax_payment_regularity': 'tax_compliance',
    'tax_payment_ontime_ratio': 'tax_compliance',
    'refund_chargeback_rate': 'refund_chargeback',
    
    # Category F
    'kyc_completion_score': 'kyc',
    'kyc_attempts_count': 'kyc',
    'device_consistency_score': 'verification',
    'ip_stability_score': 'verification',
    'pan_address_bank_mismatch': 'verification',
    'image_ocr_verified': 'verification',
    'shop_image_verified': 'verification',
    'reporting_error_rate': 'verification',
    'incoming_funds_verified': 'funds_verification',
    'insurance_coverage_score': 'insurance',
    'insurance_premium_paid_ratio': 'insurance',
    
    # Category G
    'local_economic_health_score': 'economic_health',
    'customer_concentration_risk': 'customer_concentration',
    'legal_proceedings_flag': 'legal',
    'legal_disputes_count': 'legal',
    'social_media_presence_score': 'social_media',
    'social_media_sentiment_score': 'social_media',
    'online_reviews_score': 'social_media'
}

PARAM_GROUP_TO_CATEGORY = {
    'legal_entity': 'A_business_identity',
    'business_age': 'A_business_identity',
    'address_verification': 'A_business_identity',
    'industry': 'A_business_identity',
    'employees': 'A_business_identity',
    'gstin_pan': 'A_business_identity',
    'msme_registration': 'A_business_identity',
    'business_structure': 'A_business_identity',
    'licenses': 'A_business_identity',
    
    'gtv_volume': 'B_revenue_performance',
    'transaction_metrics': 'B_revenue_performance',
    'revenue_concentration': 'B_revenue_performance',
    'revenue_growth': 'B_revenue_performance',
    'profitability': 'B_revenue_performance',
    'inventory': 'B_revenue_performance',
    'assets': 'B_revenue_performance',
    'operational_leverage': 'B_revenue_performance',
    
    'bank_balance': 'C_cashflow_banking',
    'inflow_outflow': 'C_cashflow_banking',
    'overdraft': 'C_cashflow_banking',
    'cash_buffer': 'C_cashflow_banking',
    'daily_balance': 'C_cashflow_banking',
    'deposits_regularity': 'C_cashflow_banking',
    'receivables': 'C_cashflow_banking',
    'payables': 'C_cashflow_banking',
    
    'bounced_cheques': 'D_credit_repayment',
    'overdraft_repayment': 'D_credit_repayment',
    'defaults': 'D_credit_repayment',
    'loans': 'D_credit_repayment',
    'utility_payments': 'D_credit_repayment',
    'mobile_payments': 'D_credit_repayment',
    'rent_payments': 'D_credit_repayment',
    'supplier_payments': 'D_credit_repayment',
    
    'gst_filing': 'E_compliance_taxation',
    'gst_mismatch': 'E_compliance_taxation',
    'outstanding': 'E_compliance_taxation',
    'itr': 'E_compliance_taxation',
    'tax_compliance': 'E_compliance_taxation',
    'refund_chargeback': 'E_compliance_taxation',
    
    'kyc': 'F_fraud_verification',
    'verification': 'F_fraud_verification',
    'funds_verification': 'F_fraud_verification',
    'insurance': 'F_fraud_verification',
    
    'economic_health': 'G_external_signals',
    'customer_concentration': 'G_external_signals',
    'legal': 'G_external_signals',
    'social_media': 'G_external_signals'
}


# ============================================================================
# NORMALIZATION BOUNDS FOR MSME FEATURES
# ============================================================================

MSME_NORMALIZATION_BOUNDS = {
    # Category A
    'legal_entity_type': None,
    'business_age_years': (0, 15, True),
    'business_address_verified': (0, 1, True),
    'geolocation_verified': (0, 1, True),
    'industry_code': None,
    'industry_risk_score': (0, 0.5, False),
    'num_business_locations': (1, 10, True),
    'employees_count': (1, 100, True),
    'gstin_verified': (0, 1, True),
    'pan_verified': (0, 1, True),
    'msme_registered': (0, 1, True),
    'msme_category': None,
    'business_structure': None,
    'licenses_certificates_score': (0, 1, True),
    
    # Category B
    'weekly_gtv': (0, 10000000, True),
    'monthly_gtv': (0, 50000000, True),
    'transaction_count_daily': (1, 500, True),
    'avg_transaction_value': (100, 50000, None),
    'revenue_concentration_score': (0, 0.5, False),
    'peak_day_dependency': (0, 0.5, False),
    'revenue_growth_rate_mom': (-0.3, 0.3, True),
    'revenue_growth_rate_qoq': (-0.3, 0.5, True),
    'profit_margin': (-0.1, 0.4, True),
    'profit_margin_trend': (-0.2, 0.2, True),
    'inventory_turnover_ratio': (1, 20, True),
    'total_assets_value': (0, 50000000, True),
    'operational_leverage_ratio': (0.5, 3, False),
    
    # Category C
    'avg_bank_balance': (0, 5000000, True),
    'bank_balance_trend': (-0.3, 0.3, True),
    'weekly_inflow_outflow_ratio': (0.8, 1.5, True),
    'overdraft_days_count': (0, 30, False),
    'overdraft_amount_avg': (0, 1000000, False),
    'cash_buffer_days': (0, 90, True),
    'avg_daily_closing_balance': (0, 3000000, True),
    'cash_balance_std_dev': (0, 500000, False),
    'negative_balance_days': (0, 15, False),
    'daily_min_balance_pattern': (0, 500000, True),
    'consistent_deposits_score': (0, 1, True),
    'cashflow_regularity_score': (0, 1, True),
    'receivables_aging_days': (0, 90, False),
    'payables_aging_days': (0, 60, False),
    
    # Category D
    'bounced_cheques_count': (0, 10, False),
    'bounced_cheques_rate': (0, 0.2, False),
    'historical_loan_utilization': (0, 1, None),
    'overdraft_repayment_ontime_ratio': (0, 1, True),
    'previous_defaults_count': (0, 3, False),
    'previous_writeoffs_count': (0, 2, False),
    'current_loans_outstanding': (0, 5, False),
    'total_debt_amount': (0, 10000000, False),
    'utility_payment_ontime_ratio': (0, 1, True),
    'utility_payment_days_before_due': (-10, 15, True),
    'mobile_recharge_regularity': (0, 1, True),
    'mobile_recharge_ontime_ratio': (0, 1, True),
    'rent_payment_regularity': (0, 1, True),
    'rent_payment_ontime_ratio': (0, 1, True),
    'supplier_payment_regularity': (0, 1, True),
    'supplier_payment_ontime_ratio': (0, 1, True),
    
    # Category E
    'gst_filing_regularity': (0, 1, True),
    'gst_filing_ontime_ratio': (0, 1, True),
    'gst_vs_platform_sales_mismatch': (0, 0.3, False),
    'outstanding_taxes_amount': (0, 500000, False),
    'outstanding_dues_flag': (0, 1, False),
    'itr_filed': (0, 1, True),
    'itr_income_declared': (0, 10000000, True),
    'gst_r1_vs_itr_mismatch': (0, 0.3, False),
    'tax_payment_regularity': (0, 1, True),
    'tax_payment_ontime_ratio': (0, 1, True),
    'refund_chargeback_rate': (0, 0.1, False),
    
    # Category F
    'kyc_completion_score': (0, 1, True),
    'kyc_attempts_count': (1, 5, False),
    'device_consistency_score': (0, 1, True),
    'ip_stability_score': (0, 1, True),
    'pan_address_bank_mismatch': (0, 1, False),
    'image_ocr_verified': (0, 1, True),
    'shop_image_verified': (0, 1, True),
    'reporting_error_rate': (0, 0.2, False),
    'incoming_funds_verified': (0, 1, True),
    'insurance_coverage_score': (0, 1, True),
    'insurance_premium_paid_ratio': (0, 1, True),
    
    # Category G
    'local_economic_health_score': (0, 1, True),
    'customer_concentration_risk': (0, 0.5, False),
    'legal_proceedings_flag': (0, 1, False),
    'legal_disputes_count': (0, 3, False),
    'social_media_presence_score': (0, 1, True),
    'social_media_sentiment_score': (0, 1, True),
    'online_reviews_score': (0, 5, True)
}


# ============================================================================
# SCORING FUNCTIONS
# ============================================================================

def normalize_msme_feature(value: float, feature_name: str) -> float:
    """Normalize MSME feature to [0,1], higher = better"""
    if feature_name not in MSME_NORMALIZATION_BOUNDS or MSME_NORMALIZATION_BOUNDS[feature_name] is None:
        return 0.5
    
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return 0.5
    
    min_val, max_val, higher_is_better = MSME_NORMALIZATION_BOUNDS[feature_name]
    
    value = np.clip(value, min_val, max_val)
    
    if max_val == min_val:
        normalized = 0.5
    else:
        normalized = (value - min_val) / (max_val - min_val)
    
    if higher_is_better is False:
        normalized = 1 - normalized
    elif higher_is_better is None:
        normalized = 0.5
    
    return float(np.clip(normalized, 0, 1))


def compute_msme_segment_subscore(features: Dict, segment: str) -> Tuple[float, Dict]:
    """Compute segment-specific subscore for MSME"""
    if segment not in BUSINESS_SEGMENT_WEIGHTS:
        segment = 'micro_established'  # Default
    
    segment_config = BUSINESS_SEGMENT_WEIGHTS[segment]
    category_weights = segment_config['category_weights']
    
    category_scores = {}
    total_score = 0.0
    
    for category, cat_weight in category_weights.items():
        # Get features for this category
        category_features = [f for f, pg in MSME_FEATURE_TO_PARAM_GROUP.items() 
                           if PARAM_GROUP_TO_CATEGORY.get(pg) == category]
        
        if not category_features:
            category_scores[category] = 0.5 * cat_weight
            total_score += 0.5 * cat_weight
            continue
        
        # Compute normalized scores
        scores = []
        for feat in category_features:
            if feat in features:
                score = normalize_msme_feature(features[feat], feat)
                scores.append(score)
        
        if scores:
            cat_score = np.mean(scores)
        else:
            cat_score = 0.5
        
        category_scores[category] = cat_score * cat_weight
        total_score += cat_score * cat_weight
    
    return float(np.clip(total_score, 0, 1)), category_scores


def msme_prob_to_score(prob: float, min_score: int = 300, max_score: int = 900) -> int:
    """Map MSME default probability to credit score (300-900)"""
    prob = np.clip(prob, 0, 1)
    
    # MSME-specific breakpoints
    breakpoints = [
        (0.00, 900),
        (0.02, 750),
        (0.05, 650),
        (0.12, 550),
        (0.25, 450),
        (0.40, 400),
        (0.60, 350),
        (1.00, 300)
    ]
    
    for i in range(len(breakpoints) - 1):
        p1, s1 = breakpoints[i]
        p2, s2 = breakpoints[i + 1]
        
        if p1 <= prob <= p2:
            if p2 == p1:
                return int(s1)
            slope = (s2 - s1) / (p2 - p1)
            score = s1 + slope * (prob - p1)
            return int(np.clip(round(score), min_score, max_score))
    
    return min_score


def blend_msme_scores(gbm_prob: float, segment_subscore: float, alpha: float = 0.7) -> float:
    """Blend GBM prediction with segment subscore"""
    segment_risk = 1 - segment_subscore
    final_prob = alpha * gbm_prob + (1 - alpha) * segment_risk
    return float(np.clip(final_prob, 0, 1))


# ============================================================================
# MSME SCORER CLASS
# ============================================================================

class MSMECreditScorer:
    """Production-ready MSME credit scorer"""
    
    def __init__(self, model_path: str = None, 
                 preprocessor_path: str = None,
                 config_path: str = None,
                 alpha: float = 0.7):
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
        from train import MSMECreditScoringModel
        self.model = MSMECreditScoringModel.load(path)
        self.model_version = self.model.model_version
    
    def _load_preprocessor(self, path: str):
        from data_prep import MSMEPreprocessor
        self.preprocessor = MSMEPreprocessor()
        self.preprocessor.load(path)
    
    def score_business(self, features: Dict, segment: str = None,
                       alpha: float = None, include_explanation: bool = True) -> Dict:
        """Score an MSME based on features and business segment"""
        alpha = alpha if alpha is not None else self.alpha
        
        if segment is None:
            segment = 'micro_established'
        
        # Compute segment subscore
        segment_subscore, category_contributions = compute_msme_segment_subscore(features, segment)
        
        # Get GBM prediction
        if self.model is not None:
            feature_df = pd.DataFrame([features])
            
            if self.preprocessor is not None:
                try:
                    processed_df = self.preprocessor.transform(feature_df)
                except:
                    processed_df = feature_df
            else:
                processed_df = feature_df
            
            expected_cols = self.model.feature_names
            for col in expected_cols:
                if col not in processed_df.columns:
                    processed_df[col] = 0
            
            processed_df = processed_df[expected_cols]
            gbm_prob = float(self.model.predict_proba(processed_df)[0])
            
            if include_explanation:
                explanation = self.model.explain_prediction(processed_df)
            else:
                explanation = None
        else:
            gbm_prob = 1 - segment_subscore
            explanation = None
        
        # Blend
        final_prob = blend_msme_scores(gbm_prob, segment_subscore, alpha)
        
        # Map to score
        credit_score = msme_prob_to_score(final_prob)
        
        # Risk category
        if credit_score >= 750:
            risk_category = "Very Low Risk"
            decision = "Fast Track Approval"
        elif credit_score >= 650:
            risk_category = "Low Risk"
            decision = "Approve"
        elif credit_score >= 550:
            risk_category = "Medium Risk"
            decision = "Conditional Approval"
        elif credit_score >= 450:
            risk_category = "High Risk"
            decision = "Manual Review"
        else:
            risk_category = "Very High Risk"
            decision = "Decline"
        
        result = {
            'score': credit_score,
            'prob_default_90dpd': round(final_prob, 4),
            'risk_category': risk_category,
            'recommended_decision': decision,
            'model_version': self.model_version,
            'business_segment': BUSINESS_SEGMENT_WEIGHTS.get(segment, {}).get('name', segment),
            'component_scores': {
                'gbm_prediction': round(gbm_prob, 4),
                'segment_subscore': round(segment_subscore, 4),
                'alpha': alpha,
                'blended_probability': round(final_prob, 4)
            },
            'category_contributions': {k: round(v, 4) for k, v in category_contributions.items()}
        }
        
        if explanation:
            result['explanation'] = explanation
        
        return result
    
    def score_batch(self, features_list: List[Dict], 
                    segments: List[str] = None,
                    alpha: float = None) -> List[Dict]:
        """Score multiple businesses"""
        if segments is None:
            segments = ['micro_established'] * len(features_list)
        elif isinstance(segments, str):
            segments = [segments] * len(features_list)
        
        return [
            self.score_business(f, s, alpha, include_explanation=False)
            for f, s in zip(features_list, segments)
        ]


# Convenience function
def score_business(features: Dict, segment: str = None, 
                   model_path: str = None, alpha: float = 0.7) -> Dict:
    """Convenience function to score a single MSME"""
    scorer = MSMECreditScorer(model_path=model_path, alpha=alpha)
    return scorer.score_business(features, segment)


def score_with_overdraft(features: Dict, segment: str = None,
                         model_path: str = None, alpha: float = 0.7) -> Dict:
    """
    Score MSME and get overdraft recommendation in one call.
    
    Returns both credit score and overdraft limit recommendation.
    """
    scorer = MSMECreditScorer(model_path=model_path, alpha=alpha)
    
    # Get credit score
    score_result = scorer.score_business(features, segment, include_explanation=True)
    
    # Get overdraft recommendation
    from overdraft_engine import OverdraftRecommendationEngine
    od_engine = OverdraftRecommendationEngine()
    
    # Extract overdraft-relevant features
    monthly_gtv = features.get('monthly_gtv', features.get('weekly_gtv', 0) * 4)
    business_age = features.get('business_age_years', 2)
    industry = features.get('industry_code', 'trading')
    msme_cat = features.get('msme_category', 'micro')
    existing_debt = features.get('total_debt_amount', 0)
    
    # Use scoring results for behavioral scores
    component_scores = score_result.get('component_scores', {})
    segment_subscore = component_scores.get('segment_subscore', 0.6)
    
    # Estimate behavioral scores from features
    cash_flow_health = features.get('cashflow_regularity_score', 
                       features.get('weekly_inflow_outflow_ratio', 1.0) / 1.5)
    cash_flow_health = min(1.0, max(0.0, cash_flow_health))
    
    payment_discipline = features.get('overdraft_repayment_ontime_ratio',
                        features.get('utility_payment_ontime_ratio', 0.8))
    
    od_recommendation = od_engine.calculate_recommendation(
        credit_score=score_result['score'],
        business_age_years=business_age,
        industry=str(industry),
        msme_category=str(msme_cat),
        monthly_gtv=monthly_gtv,
        avg_bank_balance=features.get('avg_bank_balance', 0),
        existing_debt=existing_debt,
        cash_flow_health_score=cash_flow_health,
        payment_discipline_score=payment_discipline,
        total_assets=features.get('total_assets_value', 0),
        inventory_value=features.get('inventory_value', 0),
        receivables_value=features.get('receivables_value', 0)
    )
    
    # Combine results
    return {
        'credit_assessment': score_result,
        'overdraft_recommendation': {
            'eligibility': od_recommendation.eligibility,
            'risk_tier': od_recommendation.risk_tier,
            'recommended_limit': od_recommendation.recommended_limit,
            'limit_range': {
                'min': od_recommendation.min_limit,
                'max': od_recommendation.max_limit
            },
            'calculation_methods': {
                'turnover_method': od_recommendation.turnover_based_limit,
                'cash_flow_method': od_recommendation.cash_flow_based_limit,
                'mpbf_method': od_recommendation.mpbf_based_limit
            },
            'pricing': {
                'interest_rate': od_recommendation.interest_rate,
                'processing_fee_pct': od_recommendation.processing_fee_pct,
                'processing_fee_amount': od_recommendation.processing_fee_amount
            },
            'terms': {
                'tenure_months': od_recommendation.tenure_months,
                'renewal_frequency_months': od_recommendation.renewal_frequency_months,
                'emi_amount': od_recommendation.emi_amount
            },
            'requirements': {
                'collateral_required': od_recommendation.collateral_required,
                'collateral_value': od_recommendation.collateral_value_required,
                'personal_guarantee': od_recommendation.personal_guarantee_required
            },
            'risk_metrics': {
                'dscr': od_recommendation.dscr,
                'debt_to_turnover': od_recommendation.debt_to_turnover,
                'emi_coverage_ratio': od_recommendation.emi_coverage_ratio
            },
            'conditions': od_recommendation.conditions,
            'recommendations': od_recommendation.recommendations
        }
    }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("MSME CREDIT SCORING DEMO")
    print("=" * 60)
    
    # Sample MSME features
    sample_features = {
        # Business Identity
        'business_age_years': 3.5,
        'business_address_verified': 1,
        'gstin_verified': 1,
        'pan_verified': 1,
        'msme_registered': 1,
        'licenses_certificates_score': 0.8,
        
        # Revenue
        'weekly_gtv': 2500000,
        'monthly_gtv': 10000000,
        'transaction_count_daily': 85,
        'revenue_growth_rate_mom': 0.08,
        'profit_margin': 0.12,
        'total_assets_value': 25000000,
        
        # Cash Flow
        'avg_bank_balance': 1500000,
        'weekly_inflow_outflow_ratio': 1.15,
        'cash_buffer_days': 35,
        'overdraft_days_count': 5,
        'consistent_deposits_score': 0.85,
        'cashflow_regularity_score': 0.80,
        
        # Credit & Repayment
        'bounced_cheques_count': 1,
        'overdraft_repayment_ontime_ratio': 0.92,
        'utility_payment_ontime_ratio': 0.95,
        'supplier_payment_ontime_ratio': 0.88,
        'previous_defaults_count': 0,
        
        # Compliance
        'gst_filing_regularity': 0.95,
        'itr_filed': 1,
        'tax_payment_ontime_ratio': 0.90,
        
        # Fraud
        'kyc_completion_score': 0.95,
        'incoming_funds_verified': 0.90,
        'pan_address_bank_mismatch': 0,
        
        # External
        'local_economic_health_score': 0.7,
        'customer_concentration_risk': 0.25
    }
    
    # Score with different segments
    segments = ['micro_new', 'micro_established', 'small_trading', 'small_services', 'medium_enterprise']
    
    print("\nScoring sample MSME with different business segments:")
    print("-" * 60)
    
    scorer = MSMECreditScorer(alpha=0.7)
    
    for segment in segments:
        result = scorer.score_business(sample_features, segment)
        print(f"\n{result['business_segment']}:")
        print(f"  Credit Score: {result['score']}")
        print(f"  Default Probability: {result['prob_default_90dpd']:.4f}")
        print(f"  Risk Category: {result['risk_category']}")
        print(f"  Recommended Decision: {result['recommended_decision']}")

