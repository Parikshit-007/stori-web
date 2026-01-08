"""
Comprehensive MSME Synthetic Data Generator
============================================

Generates realistic synthetic data covering ALL risk scenarios:
1. VERY LOW RISK - Perfect businesses (Score 750-900, Default 0-2%)
2. LOW RISK - Good businesses (Score 650-749, Default 2-5%)
3. MEDIUM RISK - Average businesses (Score 550-649, Default 5-12%)
4. HIGH RISK - Struggling businesses (Score 450-549, Default 12-20%)
5. VERY HIGH RISK - Distressed businesses (Score 300-449, Default 20-40%)

Edge Cases:
- Brand new businesses with no history
- High growth startups
- Declining businesses
- Seasonal businesses
- Fraud-suspicious profiles
- Recovering businesses (improving after issues)
- Asset-rich but cash-poor businesses
- Cash-rich but unregistered businesses

Author: ML Engineering Team
Version: 2.0 - Comprehensive Coverage
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import os

# Seed for reproducibility
np.random.seed(42)
random.seed(42)

# ============================================================================
# CONFIGURATION
# ============================================================================

BUSINESS_SEGMENTS = [
    'micro_new', 'micro_established', 'small_trading', 
    'small_manufacturing', 'small_services', 'medium_enterprise'
]

INDUSTRIES = [
    'manufacturing', 'trading', 'services', 'agriculture', 
    'construction', 'retail', 'hospitality', 'logistics', 
    'technology', 'healthcare'
]

LEGAL_ENTITY_TYPES = [
    'proprietorship', 'partnership', 'llp', 'private_limited', 
    'public_limited', 'trust', 'society'
]

MSME_CATEGORIES = ['micro', 'small', 'medium', 'not_registered']
BUSINESS_STRUCTURES = ['home_based', 'shop', 'warehouse', 'office', 'factory', 'multiple']

INDUSTRY_BASE_RISK = {
    'technology': 0.03,
    'healthcare': 0.04,
    'services': 0.05,
    'retail': 0.06,
    'manufacturing': 0.05,
    'logistics': 0.07,
    'trading': 0.06,
    'hospitality': 0.10,
    'construction': 0.12,
    'agriculture': 0.09
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def clip(value, min_val, max_val):
    """Clip value to range"""
    return max(min_val, min(max_val, value))

def add_noise(value, std_pct=0.1):
    """Add gaussian noise"""
    return value * (1 + np.random.normal(0, std_pct))

def generate_date():
    """Generate random application date in last 2 years"""
    base = datetime(2023, 1, 1)
    return base + timedelta(days=random.randint(0, 730))

# ============================================================================
# RISK PROFILE GENERATORS
# ============================================================================

def generate_very_low_risk_profile(n):
    """
    VERY LOW RISK - Score 750-900, Default 0-2%
    Perfect, established businesses with excellent track record
    """
    profiles = []
    
    for _ in range(n):
        profile = {
            'risk_category': 'very_low',
            'expected_score_range': '750-900',
            'expected_default_prob': '0-2%',
            
            # Business Identity
            'business_segment': np.random.choice(['medium_enterprise', 'small_manufacturing', 'small_services'], p=[0.5, 0.3, 0.2]),
            'industry_code': np.random.choice(['technology', 'healthcare', 'manufacturing', 'services'], p=[0.3, 0.2, 0.3, 0.2]),
            'legal_entity_type': np.random.choice(['private_limited', 'llp', 'public_limited'], p=[0.6, 0.3, 0.1]),
            'business_age_years': clip(np.random.normal(12, 4), 5, 30),
            'business_address_verified': 1,
            'geolocation_verified': 1,
            'industry_risk_score': clip(np.random.uniform(0.10, 0.20), 0, 1),
            'num_business_locations': int(clip(np.random.normal(4, 2), 1, 15)),
            'employees_count': int(clip(np.random.normal(50, 25), 10, 200)),
            'gstin_verified': 1,
            'pan_verified': 1,
            'msme_registered': 1,
            'msme_category': np.random.choice(['medium', 'small'], p=[0.6, 0.4]),
            'business_structure': np.random.choice(['office', 'factory', 'multiple'], p=[0.5, 0.3, 0.2]),
            'licenses_certificates_score': clip(np.random.normal(0.92, 0.05), 0.8, 1),
            
            # Revenue & Performance - STRONG
            'weekly_gtv': clip(np.random.lognormal(15, 0.5), 2000000, 50000000),
            'transaction_count_daily': int(clip(np.random.normal(200, 80), 50, 500)),
            'revenue_concentration_score': clip(np.random.uniform(0.15, 0.35), 0, 1),
            'peak_day_dependency': clip(np.random.uniform(0.05, 0.15), 0, 1),
            'revenue_growth_rate_mom': clip(np.random.normal(0.08, 0.04), -0.05, 0.20),
            'revenue_growth_rate_qoq': clip(np.random.normal(0.18, 0.08), 0.05, 0.40),
            'profit_margin': clip(np.random.normal(0.18, 0.05), 0.10, 0.30),
            'profit_margin_trend': clip(np.random.normal(0.03, 0.02), -0.02, 0.08),
            'inventory_turnover_ratio': clip(np.random.normal(5, 1.5), 3, 10),
            'operational_leverage_ratio': clip(np.random.normal(1.4, 0.3), 0.8, 2.2),
            
            # Cash Flow & Banking - EXCELLENT
            'bank_balance_trend': clip(np.random.normal(0.08, 0.04), 0, 0.20),
            'weekly_inflow_outflow_ratio': clip(np.random.normal(1.45, 0.15), 1.2, 2.0),
            'overdraft_days_count': int(clip(np.random.exponential(1), 0, 5)),
            'overdraft_amount_avg': clip(np.random.exponential(5000), 0, 30000),
            'cash_buffer_days': clip(np.random.normal(75, 20), 45, 150),
            'cash_balance_std_dev': clip(np.random.exponential(200000), 50000, 500000),
            'negative_balance_days': 0,
            'consistent_deposits_score': clip(np.random.normal(0.93, 0.04), 0.85, 1),
            'cashflow_regularity_score': clip(np.random.normal(0.92, 0.04), 0.85, 1),
            'receivables_aging_days': clip(np.random.normal(18, 6), 5, 35),
            'payables_aging_days': clip(np.random.normal(22, 8), 10, 40),
            
            # Credit & Repayment - EXCELLENT
            'bounced_cheques_count': 0,
            'bounced_cheques_rate': 0,
            'historical_loan_utilization': clip(np.random.uniform(0.25, 0.50), 0, 1),
            'overdraft_repayment_ontime_ratio': clip(np.random.normal(0.97, 0.02), 0.92, 1),
            'previous_defaults_count': 0,
            'previous_writeoffs_count': 0,
            'current_loans_outstanding': int(clip(np.random.poisson(1), 0, 3)),
            'utility_payment_ontime_ratio': clip(np.random.normal(0.97, 0.02), 0.92, 1),
            'utility_payment_days_before_due': clip(np.random.normal(6, 2), 2, 12),
            'mobile_recharge_regularity': clip(np.random.normal(0.95, 0.03), 0.88, 1),
            'mobile_recharge_ontime_ratio': clip(np.random.normal(0.96, 0.03), 0.90, 1),
            'rent_payment_regularity': clip(np.random.normal(0.97, 0.02), 0.92, 1),
            'rent_payment_ontime_ratio': clip(np.random.normal(0.97, 0.02), 0.92, 1),
            'supplier_payment_regularity': clip(np.random.normal(0.95, 0.03), 0.88, 1),
            'supplier_payment_ontime_ratio': clip(np.random.normal(0.95, 0.03), 0.88, 1),
            
            # Compliance & Taxation - EXCELLENT
            'gst_filing_regularity': clip(np.random.normal(0.97, 0.02), 0.92, 1),
            'gst_filing_ontime_ratio': clip(np.random.normal(0.96, 0.03), 0.90, 1),
            'gst_vs_platform_sales_mismatch': clip(np.random.uniform(0, 0.03), 0, 0.1),
            'outstanding_taxes_amount': clip(np.random.exponential(10000), 0, 50000),
            'outstanding_dues_flag': 0,
            'itr_filed': 1,
            'gst_r1_vs_itr_mismatch': clip(np.random.uniform(0, 0.02), 0, 0.05),
            'tax_payment_regularity': clip(np.random.normal(0.96, 0.03), 0.90, 1),
            'tax_payment_ontime_ratio': clip(np.random.normal(0.96, 0.03), 0.90, 1),
            'refund_chargeback_rate': clip(np.random.exponential(0.01), 0, 0.03),
            
            # Fraud & Verification - CLEAN
            'kyc_completion_score': clip(np.random.normal(0.97, 0.02), 0.92, 1),
            'kyc_attempts_count': 1,
            'device_consistency_score': clip(np.random.normal(0.95, 0.03), 0.88, 1),
            'ip_stability_score': clip(np.random.normal(0.93, 0.04), 0.85, 1),
            'pan_address_bank_mismatch': 0,
            'image_ocr_verified': 1,
            'shop_image_verified': 1,
            'reporting_error_rate': clip(np.random.exponential(0.005), 0, 0.02),
            'incoming_funds_verified': clip(np.random.normal(0.95, 0.03), 0.88, 1),
            'insurance_coverage_score': clip(np.random.normal(0.85, 0.10), 0.65, 1),
            'insurance_premium_paid_ratio': clip(np.random.normal(0.95, 0.04), 0.85, 1),
            
            # External Signals - POSITIVE
            'local_economic_health_score': clip(np.random.normal(0.75, 0.10), 0.55, 0.95),
            'customer_concentration_risk': clip(np.random.uniform(0.10, 0.30), 0, 0.5),
            'legal_proceedings_flag': 0,
            'legal_disputes_count': 0,
            'social_media_presence_score': clip(np.random.normal(0.75, 0.12), 0.50, 0.95),
            'social_media_sentiment_score': clip(np.random.normal(0.85, 0.08), 0.70, 0.98),
            'online_reviews_score': clip(np.random.normal(4.4, 0.3), 3.8, 5.0),
            
            # Target - VERY LOW DEFAULT
            'default_90dpd': 0,
            'default_probability_true': clip(np.random.uniform(0.005, 0.02), 0, 0.025),
        }
        
        # Calculate derived fields
        profile['monthly_gtv'] = profile['weekly_gtv'] * 4
        profile['avg_transaction_value'] = profile['weekly_gtv'] / (profile['transaction_count_daily'] * 7 + 1)
        profile['total_assets_value'] = profile['monthly_gtv'] * np.random.uniform(3, 8)
        profile['avg_bank_balance'] = profile['monthly_gtv'] * np.random.uniform(0.20, 0.40)
        profile['avg_daily_closing_balance'] = profile['avg_bank_balance'] * np.random.uniform(0.85, 1.15)
        profile['daily_min_balance_pattern'] = profile['avg_bank_balance'] * np.random.uniform(0.40, 0.60)
        profile['total_debt_amount'] = profile['monthly_gtv'] * np.random.uniform(0.1, 0.4)
        profile['itr_income_declared'] = profile['monthly_gtv'] * 12 * profile['profit_margin'] * np.random.uniform(0.85, 1.0)
        profile['application_date'] = generate_date()
        
        profiles.append(profile)
    
    return profiles


def generate_low_risk_profile(n):
    """
    LOW RISK - Score 650-749, Default 2-5%
    Good businesses with solid track record
    """
    profiles = []
    
    for _ in range(n):
        profile = {
            'risk_category': 'low',
            'expected_score_range': '650-749',
            'expected_default_prob': '2-5%',
            
            # Business Identity
            'business_segment': np.random.choice(['small_trading', 'small_services', 'micro_established', 'small_manufacturing'], 
                                                 p=[0.3, 0.3, 0.25, 0.15]),
            'industry_code': np.random.choice(INDUSTRIES, p=[0.12, 0.20, 0.18, 0.05, 0.05, 0.20, 0.08, 0.05, 0.05, 0.02]),
            'legal_entity_type': np.random.choice(['private_limited', 'partnership', 'proprietorship', 'llp'], p=[0.3, 0.25, 0.30, 0.15]),
            'business_age_years': clip(np.random.normal(7, 3), 3, 18),
            'business_address_verified': np.random.choice([0, 1], p=[0.05, 0.95]),
            'geolocation_verified': np.random.choice([0, 1], p=[0.08, 0.92]),
            'industry_risk_score': clip(np.random.uniform(0.18, 0.30), 0, 1),
            'num_business_locations': int(clip(np.random.normal(2, 1), 1, 6)),
            'employees_count': int(clip(np.random.normal(15, 10), 3, 50)),
            'gstin_verified': np.random.choice([0, 1], p=[0.05, 0.95]),
            'pan_verified': 1,
            'msme_registered': np.random.choice([0, 1], p=[0.10, 0.90]),
            'msme_category': np.random.choice(['small', 'micro', 'medium'], p=[0.5, 0.35, 0.15]),
            'business_structure': np.random.choice(BUSINESS_STRUCTURES, p=[0.08, 0.40, 0.15, 0.25, 0.08, 0.04]),
            'licenses_certificates_score': clip(np.random.normal(0.78, 0.10), 0.55, 0.95),
            
            # Revenue & Performance - GOOD
            'weekly_gtv': clip(np.random.lognormal(13.5, 0.7), 300000, 8000000),
            'transaction_count_daily': int(clip(np.random.normal(60, 30), 15, 200)),
            'revenue_concentration_score': clip(np.random.uniform(0.28, 0.50), 0, 1),
            'peak_day_dependency': clip(np.random.uniform(0.12, 0.28), 0, 1),
            'revenue_growth_rate_mom': clip(np.random.normal(0.04, 0.06), -0.10, 0.15),
            'revenue_growth_rate_qoq': clip(np.random.normal(0.10, 0.10), -0.08, 0.30),
            'profit_margin': clip(np.random.normal(0.12, 0.05), 0.04, 0.22),
            'profit_margin_trend': clip(np.random.normal(0.01, 0.03), -0.04, 0.06),
            'inventory_turnover_ratio': clip(np.random.normal(3.5, 1.2), 1.5, 7),
            'operational_leverage_ratio': clip(np.random.normal(1.6, 0.4), 0.9, 2.5),
            
            # Cash Flow & Banking - GOOD
            'bank_balance_trend': clip(np.random.normal(0.04, 0.06), -0.05, 0.15),
            'weekly_inflow_outflow_ratio': clip(np.random.normal(1.20, 0.12), 1.02, 1.5),
            'overdraft_days_count': int(clip(np.random.exponential(4), 0, 18)),
            'overdraft_amount_avg': clip(np.random.exponential(25000), 0, 100000),
            'cash_buffer_days': clip(np.random.normal(42, 15), 20, 80),
            'cash_balance_std_dev': clip(np.random.exponential(120000), 30000, 400000),
            'negative_balance_days': int(clip(np.random.exponential(1), 0, 5)),
            'consistent_deposits_score': clip(np.random.normal(0.80, 0.08), 0.60, 0.95),
            'cashflow_regularity_score': clip(np.random.normal(0.78, 0.10), 0.55, 0.92),
            'receivables_aging_days': clip(np.random.normal(28, 10), 12, 55),
            'payables_aging_days': clip(np.random.normal(32, 12), 15, 60),
            
            # Credit & Repayment - GOOD
            'bounced_cheques_count': int(clip(np.random.poisson(0.5), 0, 3)),
            'bounced_cheques_rate': clip(np.random.exponential(0.015), 0, 0.05),
            'historical_loan_utilization': clip(np.random.uniform(0.35, 0.65), 0, 1),
            'overdraft_repayment_ontime_ratio': clip(np.random.normal(0.88, 0.06), 0.75, 0.98),
            'previous_defaults_count': 0,
            'previous_writeoffs_count': 0,
            'current_loans_outstanding': int(clip(np.random.poisson(1.5), 0, 4)),
            'utility_payment_ontime_ratio': clip(np.random.normal(0.88, 0.06), 0.75, 0.98),
            'utility_payment_days_before_due': clip(np.random.normal(3, 3), -3, 10),
            'mobile_recharge_regularity': clip(np.random.normal(0.85, 0.08), 0.65, 0.98),
            'mobile_recharge_ontime_ratio': clip(np.random.normal(0.86, 0.07), 0.70, 0.98),
            'rent_payment_regularity': clip(np.random.normal(0.88, 0.06), 0.72, 0.98),
            'rent_payment_ontime_ratio': clip(np.random.normal(0.87, 0.07), 0.70, 0.98),
            'supplier_payment_regularity': clip(np.random.normal(0.84, 0.08), 0.65, 0.96),
            'supplier_payment_ontime_ratio': clip(np.random.normal(0.83, 0.08), 0.64, 0.96),
            
            # Compliance & Taxation - GOOD
            'gst_filing_regularity': clip(np.random.normal(0.88, 0.07), 0.70, 0.98),
            'gst_filing_ontime_ratio': clip(np.random.normal(0.85, 0.08), 0.68, 0.98),
            'gst_vs_platform_sales_mismatch': clip(np.random.uniform(0.02, 0.10), 0, 0.18),
            'outstanding_taxes_amount': clip(np.random.exponential(40000), 0, 150000),
            'outstanding_dues_flag': np.random.choice([0, 1], p=[0.92, 0.08]),
            'itr_filed': np.random.choice([0, 1], p=[0.08, 0.92]),
            'gst_r1_vs_itr_mismatch': clip(np.random.uniform(0.02, 0.08), 0, 0.12),
            'tax_payment_regularity': clip(np.random.normal(0.85, 0.08), 0.65, 0.98),
            'tax_payment_ontime_ratio': clip(np.random.normal(0.84, 0.08), 0.64, 0.97),
            'refund_chargeback_rate': clip(np.random.exponential(0.025), 0, 0.07),
            
            # Fraud & Verification - MOSTLY CLEAN
            'kyc_completion_score': clip(np.random.normal(0.88, 0.07), 0.72, 0.98),
            'kyc_attempts_count': np.random.choice([1, 2], p=[0.85, 0.15]),
            'device_consistency_score': clip(np.random.normal(0.88, 0.07), 0.70, 0.98),
            'ip_stability_score': clip(np.random.normal(0.85, 0.08), 0.68, 0.98),
            'pan_address_bank_mismatch': 0,
            'image_ocr_verified': np.random.choice([0, 1], p=[0.05, 0.95]),
            'shop_image_verified': np.random.choice([0, 1], p=[0.08, 0.92]),
            'reporting_error_rate': clip(np.random.exponential(0.018), 0, 0.05),
            'incoming_funds_verified': clip(np.random.normal(0.85, 0.08), 0.68, 0.98),
            'insurance_coverage_score': clip(np.random.normal(0.65, 0.15), 0.35, 0.90),
            'insurance_premium_paid_ratio': clip(np.random.normal(0.80, 0.12), 0.55, 0.98),
            
            # External Signals - NEUTRAL TO POSITIVE
            'local_economic_health_score': clip(np.random.normal(0.65, 0.12), 0.40, 0.85),
            'customer_concentration_risk': clip(np.random.uniform(0.22, 0.45), 0, 0.65),
            'legal_proceedings_flag': 0,
            'legal_disputes_count': 0,
            'social_media_presence_score': clip(np.random.normal(0.60, 0.15), 0.30, 0.85),
            'social_media_sentiment_score': clip(np.random.normal(0.75, 0.10), 0.55, 0.92),
            'online_reviews_score': clip(np.random.normal(4.0, 0.4), 3.3, 4.8),
            
            # Target - LOW DEFAULT
            'default_90dpd': np.random.choice([0, 1], p=[0.97, 0.03]),
            'default_probability_true': clip(np.random.uniform(0.02, 0.05), 0.015, 0.06),
        }
        
        # Calculate derived fields
        profile['monthly_gtv'] = profile['weekly_gtv'] * 4
        profile['avg_transaction_value'] = profile['weekly_gtv'] / (profile['transaction_count_daily'] * 7 + 1)
        profile['total_assets_value'] = profile['monthly_gtv'] * np.random.uniform(2, 5)
        profile['avg_bank_balance'] = profile['monthly_gtv'] * np.random.uniform(0.12, 0.28)
        profile['avg_daily_closing_balance'] = profile['avg_bank_balance'] * np.random.uniform(0.80, 1.20)
        profile['daily_min_balance_pattern'] = profile['avg_bank_balance'] * np.random.uniform(0.30, 0.55)
        profile['total_debt_amount'] = profile['monthly_gtv'] * np.random.uniform(0.15, 0.50)
        profile['itr_income_declared'] = profile['monthly_gtv'] * 12 * profile['profit_margin'] * profile['itr_filed'] * np.random.uniform(0.75, 0.95)
        profile['application_date'] = generate_date()
        
        profiles.append(profile)
    
    return profiles


def generate_medium_risk_profile(n):
    """
    MEDIUM RISK - Score 550-649, Default 5-12%
    Average businesses with some concerns
    """
    profiles = []
    
    for _ in range(n):
        profile = {
            'risk_category': 'medium',
            'expected_score_range': '550-649',
            'expected_default_prob': '5-12%',
            
            # Business Identity - MIXED
            'business_segment': np.random.choice(BUSINESS_SEGMENTS, p=[0.20, 0.30, 0.20, 0.10, 0.15, 0.05]),
            'industry_code': np.random.choice(INDUSTRIES, p=[0.10, 0.20, 0.15, 0.08, 0.08, 0.18, 0.10, 0.05, 0.03, 0.03]),
            'legal_entity_type': np.random.choice(LEGAL_ENTITY_TYPES[:4], p=[0.50, 0.25, 0.10, 0.15]),
            'business_age_years': clip(np.random.normal(4, 2.5), 1, 12),
            'business_address_verified': np.random.choice([0, 1], p=[0.15, 0.85]),
            'geolocation_verified': np.random.choice([0, 1], p=[0.20, 0.80]),
            'industry_risk_score': clip(np.random.uniform(0.25, 0.38), 0, 1),
            'num_business_locations': int(clip(np.random.poisson(1.5), 1, 4)),
            'employees_count': int(clip(np.random.normal(8, 6), 1, 25)),
            'gstin_verified': np.random.choice([0, 1], p=[0.20, 0.80]),
            'pan_verified': np.random.choice([0, 1], p=[0.08, 0.92]),
            'msme_registered': np.random.choice([0, 1], p=[0.35, 0.65]),
            'msme_category': np.random.choice(MSME_CATEGORIES, p=[0.40, 0.30, 0.05, 0.25]),
            'business_structure': np.random.choice(BUSINESS_STRUCTURES, p=[0.18, 0.45, 0.12, 0.15, 0.05, 0.05]),
            'licenses_certificates_score': clip(np.random.normal(0.55, 0.15), 0.25, 0.80),
            
            # Revenue & Performance - MODERATE
            'weekly_gtv': clip(np.random.lognormal(12.5, 0.9), 80000, 2000000),
            'transaction_count_daily': int(clip(np.random.normal(30, 18), 5, 80)),
            'revenue_concentration_score': clip(np.random.uniform(0.40, 0.65), 0, 1),
            'peak_day_dependency': clip(np.random.uniform(0.22, 0.40), 0, 1),
            'revenue_growth_rate_mom': clip(np.random.normal(0.01, 0.10), -0.18, 0.12),
            'revenue_growth_rate_qoq': clip(np.random.normal(0.03, 0.15), -0.20, 0.20),
            'profit_margin': clip(np.random.normal(0.08, 0.06), -0.02, 0.18),
            'profit_margin_trend': clip(np.random.normal(-0.01, 0.04), -0.08, 0.04),
            'inventory_turnover_ratio': clip(np.random.normal(2.5, 1.0), 1.0, 5),
            'operational_leverage_ratio': clip(np.random.normal(1.9, 0.5), 1.1, 3.0),
            
            # Cash Flow & Banking - CONCERNING
            'bank_balance_trend': clip(np.random.normal(-0.02, 0.08), -0.15, 0.08),
            'weekly_inflow_outflow_ratio': clip(np.random.normal(1.02, 0.12), 0.82, 1.25),
            'overdraft_days_count': int(clip(np.random.exponential(12), 2, 35)),
            'overdraft_amount_avg': clip(np.random.exponential(60000), 10000, 250000),
            'cash_buffer_days': clip(np.random.normal(25, 12), 8, 50),
            'cash_balance_std_dev': clip(np.random.exponential(90000), 20000, 350000),
            'negative_balance_days': int(clip(np.random.exponential(4), 0, 15)),
            'consistent_deposits_score': clip(np.random.normal(0.58, 0.12), 0.35, 0.78),
            'cashflow_regularity_score': clip(np.random.normal(0.55, 0.14), 0.30, 0.78),
            'receivables_aging_days': clip(np.random.normal(42, 15), 20, 80),
            'payables_aging_days': clip(np.random.normal(50, 18), 25, 95),
            
            # Credit & Repayment - ISSUES
            'bounced_cheques_count': int(clip(np.random.poisson(2), 0, 8)),
            'bounced_cheques_rate': clip(np.random.exponential(0.05), 0.01, 0.15),
            'historical_loan_utilization': clip(np.random.uniform(0.55, 0.80), 0, 1),
            'overdraft_repayment_ontime_ratio': clip(np.random.normal(0.70, 0.10), 0.50, 0.88),
            'previous_defaults_count': np.random.choice([0, 1], p=[0.75, 0.25]),
            'previous_writeoffs_count': 0,
            'current_loans_outstanding': int(clip(np.random.poisson(2.5), 0, 6)),
            'utility_payment_ontime_ratio': clip(np.random.normal(0.70, 0.12), 0.48, 0.88),
            'utility_payment_days_before_due': clip(np.random.normal(-2, 5), -12, 5),
            'mobile_recharge_regularity': clip(np.random.normal(0.68, 0.12), 0.42, 0.88),
            'mobile_recharge_ontime_ratio': clip(np.random.normal(0.68, 0.12), 0.45, 0.88),
            'rent_payment_regularity': clip(np.random.normal(0.70, 0.12), 0.45, 0.88),
            'rent_payment_ontime_ratio': clip(np.random.normal(0.68, 0.12), 0.42, 0.88),
            'supplier_payment_regularity': clip(np.random.normal(0.65, 0.12), 0.40, 0.85),
            'supplier_payment_ontime_ratio': clip(np.random.normal(0.62, 0.14), 0.38, 0.85),
            
            # Compliance & Taxation - MODERATE ISSUES
            'gst_filing_regularity': clip(np.random.normal(0.68, 0.12), 0.42, 0.88),
            'gst_filing_ontime_ratio': clip(np.random.normal(0.62, 0.14), 0.38, 0.85),
            'gst_vs_platform_sales_mismatch': clip(np.random.uniform(0.08, 0.22), 0, 0.35),
            'outstanding_taxes_amount': clip(np.random.exponential(100000), 15000, 400000),
            'outstanding_dues_flag': np.random.choice([0, 1], p=[0.70, 0.30]),
            'itr_filed': np.random.choice([0, 1], p=[0.30, 0.70]),
            'gst_r1_vs_itr_mismatch': clip(np.random.uniform(0.08, 0.20), 0, 0.28),
            'tax_payment_regularity': clip(np.random.normal(0.62, 0.14), 0.35, 0.85),
            'tax_payment_ontime_ratio': clip(np.random.normal(0.58, 0.15), 0.32, 0.82),
            'refund_chargeback_rate': clip(np.random.exponential(0.06), 0.02, 0.15),
            
            # Fraud & Verification - SOME FLAGS
            'kyc_completion_score': clip(np.random.normal(0.70, 0.12), 0.48, 0.88),
            'kyc_attempts_count': np.random.choice([1, 2, 3], p=[0.60, 0.30, 0.10]),
            'device_consistency_score': clip(np.random.normal(0.72, 0.12), 0.48, 0.90),
            'ip_stability_score': clip(np.random.normal(0.68, 0.14), 0.42, 0.88),
            'pan_address_bank_mismatch': np.random.choice([0, 1], p=[0.88, 0.12]),
            'image_ocr_verified': np.random.choice([0, 1], p=[0.18, 0.82]),
            'shop_image_verified': np.random.choice([0, 1], p=[0.22, 0.78]),
            'reporting_error_rate': clip(np.random.exponential(0.045), 0.01, 0.12),
            'incoming_funds_verified': clip(np.random.normal(0.68, 0.12), 0.45, 0.88),
            'insurance_coverage_score': clip(np.random.normal(0.42, 0.18), 0.15, 0.70),
            'insurance_premium_paid_ratio': clip(np.random.normal(0.58, 0.18), 0.28, 0.85),
            
            # External Signals - MIXED
            'local_economic_health_score': clip(np.random.normal(0.52, 0.14), 0.28, 0.75),
            'customer_concentration_risk': clip(np.random.uniform(0.40, 0.65), 0.20, 0.80),
            'legal_proceedings_flag': np.random.choice([0, 1], p=[0.92, 0.08]),
            'legal_disputes_count': int(np.random.choice([0, 1], p=[0.92, 0.08])),
            'social_media_presence_score': clip(np.random.normal(0.45, 0.18), 0.15, 0.75),
            'social_media_sentiment_score': clip(np.random.normal(0.62, 0.14), 0.35, 0.85),
            'online_reviews_score': clip(np.random.normal(3.4, 0.5), 2.5, 4.3),
            
            # Target - MEDIUM DEFAULT
            'default_90dpd': np.random.choice([0, 1], p=[0.92, 0.08]),
            'default_probability_true': clip(np.random.uniform(0.05, 0.12), 0.04, 0.14),
        }
        
        # Calculate derived fields
        profile['monthly_gtv'] = profile['weekly_gtv'] * 4
        profile['avg_transaction_value'] = profile['weekly_gtv'] / (profile['transaction_count_daily'] * 7 + 1)
        profile['total_assets_value'] = profile['monthly_gtv'] * np.random.uniform(1.2, 3.5)
        profile['avg_bank_balance'] = profile['monthly_gtv'] * np.random.uniform(0.08, 0.18)
        profile['avg_daily_closing_balance'] = profile['avg_bank_balance'] * np.random.uniform(0.70, 1.30)
        profile['daily_min_balance_pattern'] = profile['avg_bank_balance'] * np.random.uniform(0.15, 0.40)
        profile['total_debt_amount'] = profile['monthly_gtv'] * np.random.uniform(0.30, 0.70)
        profile['itr_income_declared'] = profile['monthly_gtv'] * 12 * max(0.02, profile['profit_margin']) * profile['itr_filed'] * np.random.uniform(0.60, 0.85)
        profile['application_date'] = generate_date()
        
        profiles.append(profile)
    
    return profiles


def generate_high_risk_profile(n):
    """
    HIGH RISK - Score 450-549, Default 12-20%
    Struggling businesses with significant issues
    """
    profiles = []
    
    for _ in range(n):
        profile = {
            'risk_category': 'high',
            'expected_score_range': '450-549',
            'expected_default_prob': '12-20%',
            
            # Business Identity - WEAK
            'business_segment': np.random.choice(['micro_new', 'micro_established', 'small_trading'], p=[0.45, 0.35, 0.20]),
            'industry_code': np.random.choice(['construction', 'agriculture', 'hospitality', 'trading', 'retail'], p=[0.25, 0.20, 0.20, 0.20, 0.15]),
            'legal_entity_type': 'proprietorship',
            'business_age_years': clip(np.random.normal(2, 1.5), 0.5, 6),
            'business_address_verified': np.random.choice([0, 1], p=[0.35, 0.65]),
            'geolocation_verified': np.random.choice([0, 1], p=[0.40, 0.60]),
            'industry_risk_score': clip(np.random.uniform(0.32, 0.42), 0, 1),
            'num_business_locations': 1,
            'employees_count': int(clip(np.random.normal(3, 2), 1, 10)),
            'gstin_verified': np.random.choice([0, 1], p=[0.45, 0.55]),
            'pan_verified': np.random.choice([0, 1], p=[0.20, 0.80]),
            'msme_registered': np.random.choice([0, 1], p=[0.60, 0.40]),
            'msme_category': np.random.choice(['micro', 'not_registered'], p=[0.45, 0.55]),
            'business_structure': np.random.choice(['home_based', 'shop'], p=[0.45, 0.55]),
            'licenses_certificates_score': clip(np.random.normal(0.35, 0.12), 0.15, 0.55),
            
            # Revenue & Performance - WEAK/DECLINING
            'weekly_gtv': clip(np.random.lognormal(11.5, 1.0), 25000, 500000),
            'transaction_count_daily': int(clip(np.random.normal(12, 8), 2, 35)),
            'revenue_concentration_score': clip(np.random.uniform(0.58, 0.82), 0.40, 1),
            'peak_day_dependency': clip(np.random.uniform(0.35, 0.55), 0.20, 0.70),
            'revenue_growth_rate_mom': clip(np.random.normal(-0.08, 0.12), -0.30, 0.05),
            'revenue_growth_rate_qoq': clip(np.random.normal(-0.12, 0.15), -0.35, 0.05),
            'profit_margin': clip(np.random.normal(0.02, 0.06), -0.10, 0.12),
            'profit_margin_trend': clip(np.random.normal(-0.05, 0.04), -0.15, 0.02),
            'inventory_turnover_ratio': clip(np.random.normal(1.5, 0.7), 0.5, 3),
            'operational_leverage_ratio': clip(np.random.normal(2.5, 0.6), 1.5, 3.8),
            
            # Cash Flow & Banking - DISTRESSED
            'bank_balance_trend': clip(np.random.normal(-0.12, 0.10), -0.30, 0.02),
            'weekly_inflow_outflow_ratio': clip(np.random.normal(0.85, 0.12), 0.60, 1.05),
            'overdraft_days_count': int(clip(np.random.exponential(25), 10, 55)),
            'overdraft_amount_avg': clip(np.random.exponential(100000), 30000, 400000),
            'cash_buffer_days': clip(np.random.normal(12, 8), 2, 28),
            'cash_balance_std_dev': clip(np.random.exponential(150000), 40000, 500000),
            'negative_balance_days': int(clip(np.random.exponential(10), 3, 28)),
            'consistent_deposits_score': clip(np.random.normal(0.38, 0.12), 0.18, 0.58),
            'cashflow_regularity_score': clip(np.random.normal(0.35, 0.14), 0.15, 0.55),
            'receivables_aging_days': clip(np.random.normal(65, 20), 35, 120),
            'payables_aging_days': clip(np.random.normal(85, 25), 50, 140),
            
            # Credit & Repayment - POOR
            'bounced_cheques_count': int(clip(np.random.poisson(5), 2, 15)),
            'bounced_cheques_rate': clip(np.random.exponential(0.12), 0.05, 0.28),
            'historical_loan_utilization': clip(np.random.uniform(0.75, 0.95), 0.60, 1),
            'overdraft_repayment_ontime_ratio': clip(np.random.normal(0.50, 0.12), 0.28, 0.70),
            'previous_defaults_count': int(np.random.choice([0, 1, 2], p=[0.40, 0.40, 0.20])),
            'previous_writeoffs_count': np.random.choice([0, 1], p=[0.85, 0.15]),
            'current_loans_outstanding': int(clip(np.random.poisson(4), 2, 8)),
            'utility_payment_ontime_ratio': clip(np.random.normal(0.48, 0.14), 0.25, 0.68),
            'utility_payment_days_before_due': clip(np.random.normal(-10, 6), -22, 2),
            'mobile_recharge_regularity': clip(np.random.normal(0.48, 0.15), 0.22, 0.70),
            'mobile_recharge_ontime_ratio': clip(np.random.normal(0.45, 0.15), 0.22, 0.68),
            'rent_payment_regularity': clip(np.random.normal(0.48, 0.15), 0.22, 0.70),
            'rent_payment_ontime_ratio': clip(np.random.normal(0.45, 0.15), 0.22, 0.68),
            'supplier_payment_regularity': clip(np.random.normal(0.42, 0.15), 0.18, 0.65),
            'supplier_payment_ontime_ratio': clip(np.random.normal(0.40, 0.15), 0.18, 0.62),
            
            # Compliance & Taxation - POOR
            'gst_filing_regularity': clip(np.random.normal(0.42, 0.15), 0.18, 0.65),
            'gst_filing_ontime_ratio': clip(np.random.normal(0.38, 0.15), 0.15, 0.60),
            'gst_vs_platform_sales_mismatch': clip(np.random.uniform(0.20, 0.40), 0.10, 0.55),
            'outstanding_taxes_amount': clip(np.random.exponential(200000), 50000, 700000),
            'outstanding_dues_flag': np.random.choice([0, 1], p=[0.40, 0.60]),
            'itr_filed': np.random.choice([0, 1], p=[0.55, 0.45]),
            'gst_r1_vs_itr_mismatch': clip(np.random.uniform(0.18, 0.38), 0.10, 0.50),
            'tax_payment_regularity': clip(np.random.normal(0.38, 0.15), 0.15, 0.60),
            'tax_payment_ontime_ratio': clip(np.random.normal(0.35, 0.15), 0.12, 0.58),
            'refund_chargeback_rate': clip(np.random.exponential(0.12), 0.05, 0.25),
            
            # Fraud & Verification - FLAGS
            'kyc_completion_score': clip(np.random.normal(0.52, 0.15), 0.28, 0.72),
            'kyc_attempts_count': np.random.choice([1, 2, 3, 4], p=[0.30, 0.35, 0.25, 0.10]),
            'device_consistency_score': clip(np.random.normal(0.55, 0.15), 0.30, 0.78),
            'ip_stability_score': clip(np.random.normal(0.50, 0.15), 0.28, 0.72),
            'pan_address_bank_mismatch': np.random.choice([0, 1], p=[0.70, 0.30]),
            'image_ocr_verified': np.random.choice([0, 1], p=[0.40, 0.60]),
            'shop_image_verified': np.random.choice([0, 1], p=[0.45, 0.55]),
            'reporting_error_rate': clip(np.random.exponential(0.08), 0.03, 0.18),
            'incoming_funds_verified': clip(np.random.normal(0.50, 0.15), 0.25, 0.72),
            'insurance_coverage_score': clip(np.random.normal(0.25, 0.15), 0.05, 0.48),
            'insurance_premium_paid_ratio': clip(np.random.normal(0.35, 0.18), 0.08, 0.62),
            
            # External Signals - NEGATIVE
            'local_economic_health_score': clip(np.random.normal(0.40, 0.12), 0.20, 0.60),
            'customer_concentration_risk': clip(np.random.uniform(0.60, 0.85), 0.45, 0.95),
            'legal_proceedings_flag': np.random.choice([0, 1], p=[0.75, 0.25]),
            'legal_disputes_count': int(np.random.choice([0, 1, 2], p=[0.75, 0.18, 0.07])),
            'social_media_presence_score': clip(np.random.normal(0.28, 0.15), 0.08, 0.52),
            'social_media_sentiment_score': clip(np.random.normal(0.45, 0.15), 0.22, 0.68),
            'online_reviews_score': clip(np.random.normal(2.8, 0.6), 1.8, 3.8),
            
            # Target - HIGH DEFAULT
            'default_90dpd': np.random.choice([0, 1], p=[0.84, 0.16]),
            'default_probability_true': clip(np.random.uniform(0.12, 0.20), 0.10, 0.22),
        }
        
        # Calculate derived fields
        profile['monthly_gtv'] = profile['weekly_gtv'] * 4
        profile['avg_transaction_value'] = profile['weekly_gtv'] / (profile['transaction_count_daily'] * 7 + 1)
        profile['total_assets_value'] = profile['monthly_gtv'] * np.random.uniform(0.8, 2.2)
        profile['avg_bank_balance'] = profile['monthly_gtv'] * np.random.uniform(0.04, 0.12)
        profile['avg_daily_closing_balance'] = profile['avg_bank_balance'] * np.random.uniform(0.50, 1.50)
        profile['daily_min_balance_pattern'] = profile['avg_bank_balance'] * np.random.uniform(0.05, 0.25)
        profile['total_debt_amount'] = profile['monthly_gtv'] * np.random.uniform(0.50, 1.20)
        profile['itr_income_declared'] = profile['monthly_gtv'] * 12 * max(0.01, profile['profit_margin']) * profile['itr_filed'] * np.random.uniform(0.40, 0.70)
        profile['application_date'] = generate_date()
        
        profiles.append(profile)
    
    return profiles


def generate_very_high_risk_profile(n):
    """
    VERY HIGH RISK - Score 300-449, Default 20-40%
    Severely distressed businesses likely to default
    """
    profiles = []
    
    for _ in range(n):
        profile = {
            'risk_category': 'very_high',
            'expected_score_range': '300-449',
            'expected_default_prob': '20-40%',
            
            # Business Identity - VERY WEAK
            'business_segment': 'micro_new',
            'industry_code': np.random.choice(['construction', 'agriculture', 'hospitality'], p=[0.40, 0.35, 0.25]),
            'legal_entity_type': 'proprietorship',
            'business_age_years': clip(np.random.exponential(1), 0.3, 3),
            'business_address_verified': np.random.choice([0, 1], p=[0.55, 0.45]),
            'geolocation_verified': np.random.choice([0, 1], p=[0.60, 0.40]),
            'industry_risk_score': clip(np.random.uniform(0.38, 0.50), 0.30, 0.55),
            'num_business_locations': 1,
            'employees_count': int(clip(np.random.exponential(2), 1, 5)),
            'gstin_verified': np.random.choice([0, 1], p=[0.65, 0.35]),
            'pan_verified': np.random.choice([0, 1], p=[0.40, 0.60]),
            'msme_registered': np.random.choice([0, 1], p=[0.80, 0.20]),
            'msme_category': 'not_registered',
            'business_structure': 'home_based',
            'licenses_certificates_score': clip(np.random.normal(0.20, 0.10), 0.05, 0.38),
            
            # Revenue & Performance - VERY WEAK
            'weekly_gtv': clip(np.random.lognormal(10.5, 1.2), 8000, 150000),
            'transaction_count_daily': int(clip(np.random.exponential(5), 1, 15)),
            'revenue_concentration_score': clip(np.random.uniform(0.75, 0.98), 0.60, 1),
            'peak_day_dependency': clip(np.random.uniform(0.45, 0.70), 0.30, 0.85),
            'revenue_growth_rate_mom': clip(np.random.normal(-0.18, 0.12), -0.40, -0.02),
            'revenue_growth_rate_qoq': clip(np.random.normal(-0.28, 0.15), -0.55, -0.05),
            'profit_margin': clip(np.random.normal(-0.05, 0.08), -0.20, 0.05),
            'profit_margin_trend': clip(np.random.normal(-0.10, 0.05), -0.25, -0.02),
            'inventory_turnover_ratio': clip(np.random.normal(0.8, 0.4), 0.3, 1.8),
            'operational_leverage_ratio': clip(np.random.normal(3.2, 0.7), 2.2, 4.5),
            
            # Cash Flow & Banking - SEVERELY DISTRESSED
            'bank_balance_trend': clip(np.random.normal(-0.22, 0.10), -0.45, -0.08),
            'weekly_inflow_outflow_ratio': clip(np.random.normal(0.65, 0.12), 0.40, 0.85),
            'overdraft_days_count': int(clip(np.random.exponential(40), 25, 75)),
            'overdraft_amount_avg': clip(np.random.exponential(150000), 50000, 600000),
            'cash_buffer_days': clip(np.random.normal(5, 4), 0, 15),
            'cash_balance_std_dev': clip(np.random.exponential(200000), 60000, 700000),
            'negative_balance_days': int(clip(np.random.exponential(18), 8, 45)),
            'consistent_deposits_score': clip(np.random.normal(0.22, 0.10), 0.08, 0.38),
            'cashflow_regularity_score': clip(np.random.normal(0.20, 0.10), 0.05, 0.35),
            'receivables_aging_days': clip(np.random.normal(95, 25), 55, 160),
            'payables_aging_days': clip(np.random.normal(130, 30), 80, 200),
            
            # Credit & Repayment - VERY POOR
            'bounced_cheques_count': int(clip(np.random.poisson(10), 5, 25)),
            'bounced_cheques_rate': clip(np.random.exponential(0.22), 0.12, 0.45),
            'historical_loan_utilization': clip(np.random.uniform(0.88, 1.0), 0.80, 1),
            'overdraft_repayment_ontime_ratio': clip(np.random.normal(0.32, 0.12), 0.12, 0.52),
            'previous_defaults_count': int(np.random.choice([1, 2, 3, 4], p=[0.30, 0.35, 0.25, 0.10])),
            'previous_writeoffs_count': np.random.choice([0, 1, 2], p=[0.50, 0.35, 0.15]),
            'current_loans_outstanding': int(clip(np.random.poisson(6), 3, 12)),
            'utility_payment_ontime_ratio': clip(np.random.normal(0.32, 0.12), 0.12, 0.52),
            'utility_payment_days_before_due': clip(np.random.normal(-18, 6), -30, -5),
            'mobile_recharge_regularity': clip(np.random.normal(0.32, 0.12), 0.12, 0.52),
            'mobile_recharge_ontime_ratio': clip(np.random.normal(0.30, 0.12), 0.10, 0.50),
            'rent_payment_regularity': clip(np.random.normal(0.35, 0.12), 0.12, 0.55),
            'rent_payment_ontime_ratio': clip(np.random.normal(0.30, 0.12), 0.10, 0.50),
            'supplier_payment_regularity': clip(np.random.normal(0.28, 0.12), 0.08, 0.48),
            'supplier_payment_ontime_ratio': clip(np.random.normal(0.25, 0.12), 0.08, 0.45),
            
            # Compliance & Taxation - VERY POOR
            'gst_filing_regularity': clip(np.random.normal(0.28, 0.12), 0.08, 0.48),
            'gst_filing_ontime_ratio': clip(np.random.normal(0.25, 0.12), 0.05, 0.45),
            'gst_vs_platform_sales_mismatch': clip(np.random.uniform(0.35, 0.58), 0.25, 0.70),
            'outstanding_taxes_amount': clip(np.random.exponential(400000), 100000, 1200000),
            'outstanding_dues_flag': 1,
            'itr_filed': np.random.choice([0, 1], p=[0.75, 0.25]),
            'gst_r1_vs_itr_mismatch': clip(np.random.uniform(0.35, 0.55), 0.25, 0.70),
            'tax_payment_regularity': clip(np.random.normal(0.25, 0.12), 0.05, 0.45),
            'tax_payment_ontime_ratio': clip(np.random.normal(0.22, 0.12), 0.05, 0.42),
            'refund_chargeback_rate': clip(np.random.exponential(0.20), 0.10, 0.40),
            
            # Fraud & Verification - MANY FLAGS
            'kyc_completion_score': clip(np.random.normal(0.38, 0.15), 0.15, 0.58),
            'kyc_attempts_count': np.random.choice([2, 3, 4, 5], p=[0.20, 0.35, 0.30, 0.15]),
            'device_consistency_score': clip(np.random.normal(0.40, 0.15), 0.18, 0.62),
            'ip_stability_score': clip(np.random.normal(0.38, 0.15), 0.15, 0.58),
            'pan_address_bank_mismatch': np.random.choice([0, 1], p=[0.45, 0.55]),
            'image_ocr_verified': np.random.choice([0, 1], p=[0.60, 0.40]),
            'shop_image_verified': np.random.choice([0, 1], p=[0.65, 0.35]),
            'reporting_error_rate': clip(np.random.exponential(0.12), 0.06, 0.28),
            'incoming_funds_verified': clip(np.random.normal(0.35, 0.15), 0.12, 0.58),
            'insurance_coverage_score': clip(np.random.normal(0.12, 0.10), 0, 0.32),
            'insurance_premium_paid_ratio': clip(np.random.normal(0.18, 0.15), 0, 0.42),
            
            # External Signals - VERY NEGATIVE
            'local_economic_health_score': clip(np.random.normal(0.32, 0.12), 0.12, 0.52),
            'customer_concentration_risk': clip(np.random.uniform(0.78, 0.98), 0.65, 1),
            'legal_proceedings_flag': np.random.choice([0, 1], p=[0.55, 0.45]),
            'legal_disputes_count': int(np.random.choice([0, 1, 2, 3], p=[0.55, 0.25, 0.15, 0.05])),
            'social_media_presence_score': clip(np.random.normal(0.15, 0.10), 0.02, 0.35),
            'social_media_sentiment_score': clip(np.random.normal(0.30, 0.15), 0.10, 0.52),
            'online_reviews_score': clip(np.random.normal(2.0, 0.6), 1.0, 3.0),
            
            # Target - VERY HIGH DEFAULT
            'default_90dpd': np.random.choice([0, 1], p=[0.70, 0.30]),
            'default_probability_true': clip(np.random.uniform(0.20, 0.40), 0.18, 0.45),
        }
        
        # Calculate derived fields
        profile['monthly_gtv'] = profile['weekly_gtv'] * 4
        profile['avg_transaction_value'] = profile['weekly_gtv'] / (profile['transaction_count_daily'] * 7 + 1)
        profile['total_assets_value'] = profile['monthly_gtv'] * np.random.uniform(0.5, 1.5)
        profile['avg_bank_balance'] = profile['monthly_gtv'] * np.random.uniform(0.02, 0.08)
        profile['avg_daily_closing_balance'] = profile['avg_bank_balance'] * np.random.uniform(0.30, 1.80)
        profile['daily_min_balance_pattern'] = max(0, profile['avg_bank_balance'] * np.random.uniform(-0.10, 0.15))
        profile['total_debt_amount'] = profile['monthly_gtv'] * np.random.uniform(0.80, 2.00)
        profile['itr_income_declared'] = profile['monthly_gtv'] * 12 * max(0, profile['profit_margin']) * profile['itr_filed'] * np.random.uniform(0.20, 0.50)
        profile['application_date'] = generate_date()
        
        profiles.append(profile)
    
    return profiles


# ============================================================================
# EDGE CASE GENERATORS
# ============================================================================

def generate_edge_cases(n_each=100):
    """Generate special edge cases for comprehensive coverage"""
    edge_cases = []
    
    # 1. BRAND NEW BUSINESS - No history at all
    for _ in range(n_each):
        profile = generate_medium_risk_profile(1)[0]
        profile['risk_category'] = 'edge_new_business'
        profile['business_age_years'] = np.random.uniform(0.1, 0.5)
        profile['historical_loan_utilization'] = 0
        profile['previous_defaults_count'] = 0
        profile['previous_writeoffs_count'] = 0
        profile['itr_filed'] = 0
        profile['itr_income_declared'] = 0
        profile['gst_r1_vs_itr_mismatch'] = 0
        profile['default_probability_true'] = clip(np.random.uniform(0.08, 0.15), 0.06, 0.18)
        profile['default_90dpd'] = np.random.choice([0, 1], p=[0.88, 0.12])
        edge_cases.append(profile)
    
    # 2. HIGH GROWTH STARTUP - Volatile but promising
    for _ in range(n_each):
        profile = generate_low_risk_profile(1)[0]
        profile['risk_category'] = 'edge_high_growth'
        profile['business_age_years'] = np.random.uniform(1, 3)
        profile['revenue_growth_rate_mom'] = np.random.uniform(0.20, 0.50)
        profile['revenue_growth_rate_qoq'] = np.random.uniform(0.50, 1.20)
        profile['cash_balance_std_dev'] = profile['avg_bank_balance'] * np.random.uniform(0.40, 0.80)
        profile['default_probability_true'] = clip(np.random.uniform(0.04, 0.08), 0.03, 0.10)
        profile['default_90dpd'] = np.random.choice([0, 1], p=[0.94, 0.06])
        edge_cases.append(profile)
    
    # 3. SEASONAL BUSINESS - High variability
    for _ in range(n_each):
        profile = generate_medium_risk_profile(1)[0]
        profile['risk_category'] = 'edge_seasonal'
        profile['peak_day_dependency'] = np.random.uniform(0.45, 0.70)
        profile['revenue_growth_rate_mom'] = np.random.uniform(-0.30, 0.40)
        profile['cash_balance_std_dev'] = profile['avg_bank_balance'] * np.random.uniform(0.60, 1.20)
        profile['consistent_deposits_score'] = np.random.uniform(0.35, 0.55)
        profile['cashflow_regularity_score'] = np.random.uniform(0.30, 0.50)
        profile['default_probability_true'] = clip(np.random.uniform(0.06, 0.12), 0.05, 0.14)
        profile['default_90dpd'] = np.random.choice([0, 1], p=[0.91, 0.09])
        edge_cases.append(profile)
    
    # 4. RECOVERING BUSINESS - Was bad, now improving
    for _ in range(n_each):
        profile = generate_high_risk_profile(1)[0]
        profile['risk_category'] = 'edge_recovering'
        profile['revenue_growth_rate_mom'] = np.random.uniform(0.05, 0.20)
        profile['revenue_growth_rate_qoq'] = np.random.uniform(0.10, 0.35)
        profile['profit_margin_trend'] = np.random.uniform(0.02, 0.08)
        profile['bank_balance_trend'] = np.random.uniform(0.05, 0.15)
        profile['overdraft_repayment_ontime_ratio'] = clip(profile['overdraft_repayment_ontime_ratio'] + 0.15, 0, 1)
        profile['default_probability_true'] = clip(np.random.uniform(0.10, 0.18), 0.08, 0.20)
        profile['default_90dpd'] = np.random.choice([0, 1], p=[0.86, 0.14])
        edge_cases.append(profile)
    
    # 5. ASSET RICH BUT CASH POOR
    for _ in range(n_each):
        profile = generate_medium_risk_profile(1)[0]
        profile['risk_category'] = 'edge_asset_rich_cash_poor'
        profile['total_assets_value'] = profile['monthly_gtv'] * np.random.uniform(8, 15)
        profile['avg_bank_balance'] = profile['monthly_gtv'] * np.random.uniform(0.02, 0.06)
        profile['cash_buffer_days'] = np.random.uniform(5, 15)
        profile['weekly_inflow_outflow_ratio'] = np.random.uniform(0.80, 1.0)
        profile['overdraft_days_count'] = int(np.random.uniform(15, 35))
        profile['default_probability_true'] = clip(np.random.uniform(0.08, 0.15), 0.06, 0.18)
        profile['default_90dpd'] = np.random.choice([0, 1], p=[0.88, 0.12])
        edge_cases.append(profile)
    
    # 6. CASH RICH BUT INFORMAL
    for _ in range(n_each):
        profile = generate_low_risk_profile(1)[0]
        profile['risk_category'] = 'edge_cash_rich_informal'
        profile['weekly_gtv'] = clip(np.random.lognormal(14, 0.6), 500000, 5000000)
        profile['monthly_gtv'] = profile['weekly_gtv'] * 4
        profile['avg_bank_balance'] = profile['monthly_gtv'] * np.random.uniform(0.25, 0.45)
        profile['cash_buffer_days'] = np.random.uniform(50, 90)
        profile['gstin_verified'] = 0
        profile['msme_registered'] = 0
        profile['msme_category'] = 'not_registered'
        profile['itr_filed'] = 0
        profile['gst_filing_regularity'] = np.random.uniform(0.20, 0.40)
        profile['default_probability_true'] = clip(np.random.uniform(0.04, 0.08), 0.03, 0.10)
        profile['default_90dpd'] = np.random.choice([0, 1], p=[0.94, 0.06])
        edge_cases.append(profile)
    
    # 7. FRAUD SUSPICIOUS - Good numbers but fraud flags
    for _ in range(n_each):
        profile = generate_low_risk_profile(1)[0]
        profile['risk_category'] = 'edge_fraud_suspicious'
        profile['pan_address_bank_mismatch'] = 1
        profile['kyc_attempts_count'] = np.random.choice([3, 4, 5])
        profile['device_consistency_score'] = np.random.uniform(0.35, 0.55)
        profile['ip_stability_score'] = np.random.uniform(0.30, 0.50)
        profile['reporting_error_rate'] = np.random.uniform(0.08, 0.15)
        profile['gst_vs_platform_sales_mismatch'] = np.random.uniform(0.25, 0.45)
        profile['default_probability_true'] = clip(np.random.uniform(0.12, 0.22), 0.10, 0.25)
        profile['default_90dpd'] = np.random.choice([0, 1], p=[0.82, 0.18])
        edge_cases.append(profile)
    
    return edge_cases


# ============================================================================
# MAIN GENERATOR
# ============================================================================

def generate_comprehensive_dataset(
    n_very_low=2000,
    n_low=2500,
    n_medium=2500,
    n_high=1500,
    n_very_high=1000,
    n_edge_each=100,
    output_path='msme_comprehensive_training_data.csv'
):
    """
    Generate comprehensive MSME dataset with all risk levels and edge cases
    """
    print("=" * 70)
    print("COMPREHENSIVE MSME SYNTHETIC DATA GENERATOR")
    print("=" * 70)
    print()
    
    all_profiles = []
    
    # Generate each risk category
    print(f"Generating {n_very_low} VERY LOW RISK profiles (Score 750-900, Default 0-2%)...")
    all_profiles.extend(generate_very_low_risk_profile(n_very_low))
    
    print(f"Generating {n_low} LOW RISK profiles (Score 650-749, Default 2-5%)...")
    all_profiles.extend(generate_low_risk_profile(n_low))
    
    print(f"Generating {n_medium} MEDIUM RISK profiles (Score 550-649, Default 5-12%)...")
    all_profiles.extend(generate_medium_risk_profile(n_medium))
    
    print(f"Generating {n_high} HIGH RISK profiles (Score 450-549, Default 12-20%)...")
    all_profiles.extend(generate_high_risk_profile(n_high))
    
    print(f"Generating {n_very_high} VERY HIGH RISK profiles (Score 300-449, Default 20-40%)...")
    all_profiles.extend(generate_very_high_risk_profile(n_very_high))
    
    print(f"\nGenerating edge cases ({n_edge_each} each)...")
    edge_cases = generate_edge_cases(n_edge_each)
    all_profiles.extend(edge_cases)
    
    # Create DataFrame
    df = pd.DataFrame(all_profiles)
    
    # Remove metadata columns
    meta_cols = ['risk_category', 'expected_score_range', 'expected_default_prob']
    df_export = df.drop(columns=[c for c in meta_cols if c in df.columns])
    
    # Shuffle
    df_export = df_export.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Save to CSV
    df_export.to_csv(output_path, index=False)
    
    # Print summary
    print()
    print("=" * 70)
    print("GENERATION COMPLETE")
    print("=" * 70)
    print(f"\nTotal samples: {len(df_export)}")
    print(f"Default rate: {df_export['default_90dpd'].mean()*100:.2f}%")
    print(f"Avg default probability: {df_export['default_probability_true'].mean()*100:.2f}%")
    print(f"\nOutput saved to: {output_path}")
    
    # Print distribution
    print("\n" + "-" * 50)
    print("RISK DISTRIBUTION:")
    print("-" * 50)
    
    risk_counts = df['risk_category'].value_counts()
    for risk, count in risk_counts.items():
        subset = df[df['risk_category'] == risk]
        avg_prob = subset['default_probability_true'].mean() * 100
        default_rate = subset['default_90dpd'].mean() * 100
        print(f"  {risk}: {count} samples, Avg Default Prob: {avg_prob:.1f}%, Actual Default Rate: {default_rate:.1f}%")
    
    # Feature statistics
    print("\n" + "-" * 50)
    print("KEY FEATURE STATISTICS:")
    print("-" * 50)
    key_features = ['business_age_years', 'weekly_gtv', 'overdraft_repayment_ontime_ratio', 
                   'bounced_cheques_count', 'cash_buffer_days', 'gst_filing_regularity']
    
    for feat in key_features:
        if feat in df_export.columns:
            print(f"  {feat}: min={df_export[feat].min():.2f}, max={df_export[feat].max():.2f}, mean={df_export[feat].mean():.2f}")
    
    print("\n" + "=" * 70)
    
    return df_export


# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    # Generate comprehensive dataset
    output_file = os.path.join(os.path.dirname(__file__), 'msme_comprehensive_training_data.csv')
    
    df = generate_comprehensive_dataset(
        n_very_low=2000,    # ~16%
        n_low=2500,         # ~20%
        n_medium=2500,      # ~20%
        n_high=1500,        # ~12%
        n_very_high=1000,   # ~8%
        n_edge_each=100,    # 7 types × 100 = 700 (~6%)
        output_path=output_file
    )
    
    print(f"\n[SUCCESS] Data saved to: {output_file}")
    print(f"   Total rows: {len(df)}")
    print(f"   Total columns: {len(df.columns)}")

