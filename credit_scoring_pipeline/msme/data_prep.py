"""
MSME Credit Scoring Pipeline - Data Preparation Module
=======================================================

This module provides:
1. Feature schema definition for MSME-specific parameters
2. Synthetic data generator for testing MSME credit scoring
3. End-to-end preprocessing: imputation, outlier handling, feature engineering
4. Train/validation/test split with time-awareness support
5. Business segment classification

Author: ML Engineering Team
Version: 1.0.0
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from sklearn.preprocessing import StandardScaler, RobustScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
import json
import warnings
from datetime import datetime, timedelta
import random

warnings.filterwarnings('ignore')


# ============================================================================
# FEATURE SCHEMA DEFINITION
# ============================================================================

@dataclass
class MSMEFeatureSpec:
    """Specification for a single MSME feature"""
    name: str
    dtype: str  # 'numeric', 'binary', 'categorical', 'ordinal'
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    higher_is_better: Optional[bool] = None
    categories: Optional[List[str]] = None
    weight: float = 1.0
    description: str = ""


# Complete MSME feature schema
MSME_FEATURE_SCHEMA = {
    # ========== CATEGORY A: BUSINESS IDENTITY & REGISTRATION (10%) ==========
    'legal_entity_type': MSMEFeatureSpec('legal_entity_type', 'categorical', 
                                         categories=['proprietorship', 'partnership', 'llp', 'private_limited', 'public_limited', 'trust', 'society'],
                                         weight=0.5),
    'business_age_years': MSMEFeatureSpec('business_age_years', 'numeric', 0, 50, True, weight=2),
    'business_address_verified': MSMEFeatureSpec('business_address_verified', 'binary', 0, 1, True, weight=1),
    'geolocation_verified': MSMEFeatureSpec('geolocation_verified', 'binary', 0, 1, True, weight=0.5),
    'industry_code': MSMEFeatureSpec('industry_code', 'categorical',
                                     categories=['manufacturing', 'trading', 'services', 'agriculture', 'construction', 'retail', 'hospitality', 'logistics', 'technology', 'healthcare'],
                                     weight=2),
    'industry_risk_score': MSMEFeatureSpec('industry_risk_score', 'numeric', 0, 1, False, weight=1),
    'num_business_locations': MSMEFeatureSpec('num_business_locations', 'numeric', 1, 100, True, weight=0.5),
    'employees_count': MSMEFeatureSpec('employees_count', 'numeric', 0, 500, True, weight=0.5),
    'gstin_verified': MSMEFeatureSpec('gstin_verified', 'binary', 0, 1, True, weight=0.5),
    'pan_verified': MSMEFeatureSpec('pan_verified', 'binary', 0, 1, True, weight=0.5),
    'msme_registered': MSMEFeatureSpec('msme_registered', 'binary', 0, 1, True, weight=0.5),
    'msme_category': MSMEFeatureSpec('msme_category', 'categorical',
                                     categories=['micro', 'small', 'medium', 'not_registered'],
                                     weight=0.5),
    'business_structure': MSMEFeatureSpec('business_structure', 'categorical',
                                          categories=['home_based', 'shop', 'warehouse', 'office', 'factory', 'multiple'],
                                          weight=0.5),
    'licenses_certificates_score': MSMEFeatureSpec('licenses_certificates_score', 'numeric', 0, 1, True, weight=1),

    # ========== CATEGORY B: REVENUE & BUSINESS PERFORMANCE (20%) ==========
    'weekly_gtv': MSMEFeatureSpec('weekly_gtv', 'numeric', 0, 100000000, True, weight=7),
    'monthly_gtv': MSMEFeatureSpec('monthly_gtv', 'numeric', 0, 500000000, True, weight=3),
    'transaction_count_daily': MSMEFeatureSpec('transaction_count_daily', 'numeric', 0, 10000, True, weight=1.5),
    'avg_transaction_value': MSMEFeatureSpec('avg_transaction_value', 'numeric', 0, 1000000, None, weight=1.5),
    'revenue_concentration_score': MSMEFeatureSpec('revenue_concentration_score', 'numeric', 0, 1, False, weight=1),
    'peak_day_dependency': MSMEFeatureSpec('peak_day_dependency', 'numeric', 0, 1, False, weight=0.5),
    'revenue_growth_rate_mom': MSMEFeatureSpec('revenue_growth_rate_mom', 'numeric', -1, 2, True, weight=1),
    'revenue_growth_rate_qoq': MSMEFeatureSpec('revenue_growth_rate_qoq', 'numeric', -1, 3, True, weight=1),
    'profit_margin': MSMEFeatureSpec('profit_margin', 'numeric', -0.5, 0.8, True, weight=0.5),
    'profit_margin_trend': MSMEFeatureSpec('profit_margin_trend', 'numeric', -1, 1, True, weight=0.5),
    'inventory_turnover_ratio': MSMEFeatureSpec('inventory_turnover_ratio', 'numeric', 0, 50, True, weight=1),
    'total_assets_value': MSMEFeatureSpec('total_assets_value', 'numeric', 0, 500000000, True, weight=3),
    'operational_leverage_ratio': MSMEFeatureSpec('operational_leverage_ratio', 'numeric', 0, 5, False, weight=2),

    # ========== CATEGORY C: CASH FLOW & BANKING (25%) ==========
    'avg_bank_balance': MSMEFeatureSpec('avg_bank_balance', 'numeric', 0, 100000000, True, weight=1.5),
    'bank_balance_trend': MSMEFeatureSpec('bank_balance_trend', 'numeric', -1, 1, True, weight=1.5),
    'weekly_inflow_outflow_ratio': MSMEFeatureSpec('weekly_inflow_outflow_ratio', 'numeric', 0, 5, True, weight=4),
    'overdraft_days_count': MSMEFeatureSpec('overdraft_days_count', 'numeric', 0, 90, False, weight=1.5),
    'overdraft_amount_avg': MSMEFeatureSpec('overdraft_amount_avg', 'numeric', 0, 10000000, False, weight=1.5),
    'cash_buffer_days': MSMEFeatureSpec('cash_buffer_days', 'numeric', 0, 180, True, weight=3),
    'avg_daily_closing_balance': MSMEFeatureSpec('avg_daily_closing_balance', 'numeric', 0, 50000000, True, weight=2),
    'cash_balance_std_dev': MSMEFeatureSpec('cash_balance_std_dev', 'numeric', 0, 10000000, False, weight=1),
    'negative_balance_days': MSMEFeatureSpec('negative_balance_days', 'numeric', 0, 90, False, weight=2),
    'daily_min_balance_pattern': MSMEFeatureSpec('daily_min_balance_pattern', 'numeric', 0, 10000000, True, weight=2),
    'consistent_deposits_score': MSMEFeatureSpec('consistent_deposits_score', 'numeric', 0, 1, True, weight=1),
    'cashflow_regularity_score': MSMEFeatureSpec('cashflow_regularity_score', 'numeric', 0, 1, True, weight=2),
    'receivables_aging_days': MSMEFeatureSpec('receivables_aging_days', 'numeric', 0, 180, False, weight=0.5),
    'payables_aging_days': MSMEFeatureSpec('payables_aging_days', 'numeric', 0, 180, False, weight=0.5),

    # ========== CATEGORY D: CREDIT & REPAYMENT BEHAVIOR (22%) ==========
    'bounced_cheques_count': MSMEFeatureSpec('bounced_cheques_count', 'numeric', 0, 50, False, weight=3),
    'bounced_cheques_rate': MSMEFeatureSpec('bounced_cheques_rate', 'numeric', 0, 1, False, weight=1),
    'historical_loan_utilization': MSMEFeatureSpec('historical_loan_utilization', 'numeric', 0, 1, None, weight=1.5),
    'overdraft_repayment_ontime_ratio': MSMEFeatureSpec('overdraft_repayment_ontime_ratio', 'numeric', 0, 1, True, weight=4),
    'previous_defaults_count': MSMEFeatureSpec('previous_defaults_count', 'numeric', 0, 10, False, weight=1),
    'previous_writeoffs_count': MSMEFeatureSpec('previous_writeoffs_count', 'numeric', 0, 10, False, weight=1),
    'current_loans_outstanding': MSMEFeatureSpec('current_loans_outstanding', 'numeric', 0, 20, False, weight=2),
    'total_debt_amount': MSMEFeatureSpec('total_debt_amount', 'numeric', 0, 100000000, False, weight=1),
    'utility_payment_ontime_ratio': MSMEFeatureSpec('utility_payment_ontime_ratio', 'numeric', 0, 1, True, weight=3),
    'utility_payment_days_before_due': MSMEFeatureSpec('utility_payment_days_before_due', 'numeric', -30, 30, True, weight=1),
    'mobile_recharge_regularity': MSMEFeatureSpec('mobile_recharge_regularity', 'numeric', 0, 1, True, weight=1),
    'mobile_recharge_ontime_ratio': MSMEFeatureSpec('mobile_recharge_ontime_ratio', 'numeric', 0, 1, True, weight=1),
    'rent_payment_regularity': MSMEFeatureSpec('rent_payment_regularity', 'numeric', 0, 1, True, weight=1),
    'rent_payment_ontime_ratio': MSMEFeatureSpec('rent_payment_ontime_ratio', 'numeric', 0, 1, True, weight=1),
    'supplier_payment_regularity': MSMEFeatureSpec('supplier_payment_regularity', 'numeric', 0, 1, True, weight=1.5),
    'supplier_payment_ontime_ratio': MSMEFeatureSpec('supplier_payment_ontime_ratio', 'numeric', 0, 1, True, weight=1.5),

    # ========== CATEGORY E: COMPLIANCE & TAXATION (12%) ==========
    'gst_filing_regularity': MSMEFeatureSpec('gst_filing_regularity', 'numeric', 0, 1, True, weight=1.5),
    'gst_filing_ontime_ratio': MSMEFeatureSpec('gst_filing_ontime_ratio', 'numeric', 0, 1, True, weight=0.5),
    'gst_vs_platform_sales_mismatch': MSMEFeatureSpec('gst_vs_platform_sales_mismatch', 'numeric', 0, 1, False, weight=1.5),
    'outstanding_taxes_amount': MSMEFeatureSpec('outstanding_taxes_amount', 'numeric', 0, 10000000, False, weight=1),
    'outstanding_dues_flag': MSMEFeatureSpec('outstanding_dues_flag', 'binary', 0, 1, False, weight=1),
    'itr_filed': MSMEFeatureSpec('itr_filed', 'binary', 0, 1, True, weight=1),
    'itr_income_declared': MSMEFeatureSpec('itr_income_declared', 'numeric', 0, 100000000, True, weight=1),
    'gst_r1_vs_itr_mismatch': MSMEFeatureSpec('gst_r1_vs_itr_mismatch', 'numeric', 0, 1, False, weight=1),
    'tax_payment_regularity': MSMEFeatureSpec('tax_payment_regularity', 'numeric', 0, 1, True, weight=1),
    'tax_payment_ontime_ratio': MSMEFeatureSpec('tax_payment_ontime_ratio', 'numeric', 0, 1, True, weight=1),
    'refund_chargeback_rate': MSMEFeatureSpec('refund_chargeback_rate', 'numeric', 0, 1, False, weight=2),

    # ========== CATEGORY F: FRAUD & VERIFICATION (7%) ==========
    'kyc_completion_score': MSMEFeatureSpec('kyc_completion_score', 'numeric', 0, 1, True, weight=0.5),
    'kyc_attempts_count': MSMEFeatureSpec('kyc_attempts_count', 'numeric', 1, 10, False, weight=0.5),
    'device_consistency_score': MSMEFeatureSpec('device_consistency_score', 'numeric', 0, 1, True, weight=0.5),
    'ip_stability_score': MSMEFeatureSpec('ip_stability_score', 'numeric', 0, 1, True, weight=0.5),
    'pan_address_bank_mismatch': MSMEFeatureSpec('pan_address_bank_mismatch', 'binary', 0, 1, False, weight=1),
    'image_ocr_verified': MSMEFeatureSpec('image_ocr_verified', 'binary', 0, 1, True, weight=0.5),
    'shop_image_verified': MSMEFeatureSpec('shop_image_verified', 'binary', 0, 1, True, weight=0.5),
    'reporting_error_rate': MSMEFeatureSpec('reporting_error_rate', 'numeric', 0, 1, False, weight=0.5),
    'incoming_funds_verified': MSMEFeatureSpec('incoming_funds_verified', 'numeric', 0, 1, True, weight=2),
    'insurance_coverage_score': MSMEFeatureSpec('insurance_coverage_score', 'numeric', 0, 1, True, weight=1),
    'insurance_premium_paid_ratio': MSMEFeatureSpec('insurance_premium_paid_ratio', 'numeric', 0, 1, True, weight=1),

    # ========== CATEGORY G: EXTERNAL SIGNALS (4%) ==========
    'local_economic_health_score': MSMEFeatureSpec('local_economic_health_score', 'numeric', 0, 1, True, weight=1),
    'customer_concentration_risk': MSMEFeatureSpec('customer_concentration_risk', 'numeric', 0, 1, False, weight=1),
    'legal_proceedings_flag': MSMEFeatureSpec('legal_proceedings_flag', 'binary', 0, 1, False, weight=0.5),
    'legal_disputes_count': MSMEFeatureSpec('legal_disputes_count', 'numeric', 0, 10, False, weight=0.5),
    'social_media_presence_score': MSMEFeatureSpec('social_media_presence_score', 'numeric', 0, 1, True, weight=0.5),
    'social_media_sentiment_score': MSMEFeatureSpec('social_media_sentiment_score', 'numeric', 0, 1, True, weight=0.5),
    'online_reviews_score': MSMEFeatureSpec('online_reviews_score', 'numeric', 0, 5, True, weight=0.5),
}

# Feature to category mapping
MSME_FEATURE_CATEGORY_MAPPING = {
    'A_business_identity': [
        'legal_entity_type', 'business_age_years', 'business_address_verified', 'geolocation_verified',
        'industry_code', 'industry_risk_score', 'num_business_locations', 'employees_count',
        'gstin_verified', 'pan_verified', 'msme_registered', 'msme_category', 'business_structure',
        'licenses_certificates_score'
    ],
    'B_revenue_performance': [
        'weekly_gtv', 'monthly_gtv', 'transaction_count_daily', 'avg_transaction_value',
        'revenue_concentration_score', 'peak_day_dependency', 'revenue_growth_rate_mom',
        'revenue_growth_rate_qoq', 'profit_margin', 'profit_margin_trend', 'inventory_turnover_ratio',
        'total_assets_value', 'operational_leverage_ratio'
    ],
    'C_cashflow_banking': [
        'avg_bank_balance', 'bank_balance_trend', 'weekly_inflow_outflow_ratio', 'overdraft_days_count',
        'overdraft_amount_avg', 'cash_buffer_days', 'avg_daily_closing_balance', 'cash_balance_std_dev',
        'negative_balance_days', 'daily_min_balance_pattern', 'consistent_deposits_score',
        'cashflow_regularity_score', 'receivables_aging_days', 'payables_aging_days'
    ],
    'D_credit_repayment': [
        'bounced_cheques_count', 'bounced_cheques_rate', 'historical_loan_utilization',
        'overdraft_repayment_ontime_ratio', 'previous_defaults_count', 'previous_writeoffs_count',
        'current_loans_outstanding', 'total_debt_amount', 'utility_payment_ontime_ratio',
        'utility_payment_days_before_due', 'mobile_recharge_regularity', 'mobile_recharge_ontime_ratio',
        'rent_payment_regularity', 'rent_payment_ontime_ratio', 'supplier_payment_regularity',
        'supplier_payment_ontime_ratio'
    ],
    'E_compliance_taxation': [
        'gst_filing_regularity', 'gst_filing_ontime_ratio', 'gst_vs_platform_sales_mismatch',
        'outstanding_taxes_amount', 'outstanding_dues_flag', 'itr_filed', 'itr_income_declared',
        'gst_r1_vs_itr_mismatch', 'tax_payment_regularity', 'tax_payment_ontime_ratio',
        'refund_chargeback_rate'
    ],
    'F_fraud_verification': [
        'kyc_completion_score', 'kyc_attempts_count', 'device_consistency_score', 'ip_stability_score',
        'pan_address_bank_mismatch', 'image_ocr_verified', 'shop_image_verified', 'reporting_error_rate',
        'incoming_funds_verified', 'insurance_coverage_score', 'insurance_premium_paid_ratio'
    ],
    'G_external_signals': [
        'local_economic_health_score', 'customer_concentration_risk', 'legal_proceedings_flag',
        'legal_disputes_count', 'social_media_presence_score', 'social_media_sentiment_score',
        'online_reviews_score'
    ]
}


# ============================================================================
# SYNTHETIC DATA GENERATOR FOR MSME
# ============================================================================

class MSMESyntheticDataGenerator:
    """
    Generates realistic synthetic MSME credit scoring data for testing.
    
    The generator creates correlated features that mimic real-world business patterns:
    - Revenue correlates with business size and age
    - Cash flow health correlates with profitability
    - Compliance scores correlate with business formality
    - Default probability is influenced by multiple risk factors
    """
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        np.random.seed(seed)
        random.seed(seed)
        
        # Business segment distribution
        self.segment_distribution = {
            'micro_new': 0.20,
            'micro_established': 0.25,
            'small_trading': 0.20,
            'small_manufacturing': 0.10,
            'small_services': 0.15,
            'medium_enterprise': 0.10
        }
        
        # Industry distribution
        self.industry_distribution = {
            'retail': 0.25,
            'trading': 0.20,
            'services': 0.18,
            'manufacturing': 0.12,
            'hospitality': 0.08,
            'logistics': 0.06,
            'agriculture': 0.05,
            'construction': 0.03,
            'technology': 0.02,
            'healthcare': 0.01
        }
        
        # Industry risk factors
        self.industry_risk = {
            'technology': 0.15,
            'healthcare': 0.18,
            'services': 0.22,
            'retail': 0.25,
            'manufacturing': 0.28,
            'logistics': 0.30,
            'trading': 0.32,
            'hospitality': 0.35,
            'construction': 0.38,
            'agriculture': 0.40
        }
    
    def _generate_segment_features(self, segment: str, n: int) -> Dict[str, np.ndarray]:
        """
        Generate base features based on business segment.
        
        UPDATED: Realistic default rates (industry standard 5-12%)
        - micro_new: 12% (highest risk - new businesses)
        - micro_established: 6% (established but small)
        - small_trading: 5% (trading is stable)
        - small_manufacturing: 4% (manufacturing has assets)
        - small_services: 5% (services are stable)
        - medium_enterprise: 2% (lowest risk - established, assets)
        """
        features = {}
        
        if segment == 'micro_new':
            features['gtv_base'] = np.random.lognormal(12, 1.0, n)  # Lower GTV
            features['age_factor'] = np.random.uniform(0.1, 0.4, n)  # Young businesses
            features['formality_factor'] = np.random.uniform(0.2, 0.5, n)
            features['cashflow_health'] = np.random.uniform(0.3, 0.6, n)
            features['default_base_prob'] = 0.12  # REDUCED from 0.25
            
        elif segment == 'micro_established':
            features['gtv_base'] = np.random.lognormal(13, 0.9, n)
            features['age_factor'] = np.random.uniform(0.4, 0.7, n)
            features['formality_factor'] = np.random.uniform(0.4, 0.7, n)
            features['cashflow_health'] = np.random.uniform(0.4, 0.7, n)
            features['default_base_prob'] = 0.06  # REDUCED from 0.15
            
        elif segment == 'small_trading':
            features['gtv_base'] = np.random.lognormal(14, 0.8, n)
            features['age_factor'] = np.random.uniform(0.5, 0.8, n)
            features['formality_factor'] = np.random.uniform(0.5, 0.8, n)
            features['cashflow_health'] = np.random.uniform(0.5, 0.75, n)
            features['default_base_prob'] = 0.05  # REDUCED from 0.12
            
        elif segment == 'small_manufacturing':
            features['gtv_base'] = np.random.lognormal(14.5, 0.7, n)
            features['age_factor'] = np.random.uniform(0.5, 0.85, n)
            features['formality_factor'] = np.random.uniform(0.6, 0.85, n)
            features['cashflow_health'] = np.random.uniform(0.45, 0.7, n)
            features['default_base_prob'] = 0.04  # REDUCED from 0.10
            
        elif segment == 'small_services':
            features['gtv_base'] = np.random.lognormal(13.5, 0.9, n)
            features['age_factor'] = np.random.uniform(0.4, 0.75, n)
            features['formality_factor'] = np.random.uniform(0.5, 0.8, n)
            features['cashflow_health'] = np.random.uniform(0.5, 0.8, n)
            features['default_base_prob'] = 0.05  # REDUCED from 0.11
            
        else:  # medium_enterprise
            features['gtv_base'] = np.random.lognormal(15.5, 0.6, n)
            features['age_factor'] = np.random.uniform(0.6, 0.95, n)
            features['formality_factor'] = np.random.uniform(0.7, 0.95, n)
            features['cashflow_health'] = np.random.uniform(0.6, 0.85, n)
            features['default_base_prob'] = 0.02  # REDUCED from 0.06
            
        return features
    
    def _generate_edge_cases(self, n_each: int = 50) -> pd.DataFrame:
        """
        Generate edge case scenarios for comprehensive model coverage.
        
        Edge cases:
        1. Perfect business - should have ~0-1% default risk, score 800+
        2. Terrible business - should have ~30-40% default risk, score 300-350
        3. New business with no history - uncertain, score 450-550
        4. High growth startup - volatile, score 500-600
        5. Declining business - increasing risk, score 400-500
        6. Seasonal business - variable cash flow, score 450-550
        """
        edge_cases = []
        
        # 1. PERFECT BUSINESS (n_each samples)
        for _ in range(n_each):
            perfect = {
                'business_segment': 'medium_enterprise',
                'industry_code': 'technology',
                'legal_entity_type': 'private_limited',
                'business_age_years': np.random.uniform(10, 20),
                'business_address_verified': 1,
                'geolocation_verified': 1,
                'industry_risk_score': 0.15,
                'num_business_locations': np.random.randint(3, 10),
                'employees_count': np.random.randint(30, 100),
                'gstin_verified': 1,
                'pan_verified': 1,
                'msme_registered': 1,
                'msme_category': 'medium',
                'business_structure': 'office',
                'licenses_certificates_score': np.random.uniform(0.9, 1.0),
                'weekly_gtv': np.random.uniform(3000000, 10000000),
                'monthly_gtv': np.random.uniform(12000000, 40000000),
                'transaction_count_daily': np.random.randint(200, 500),
                'avg_transaction_value': np.random.uniform(500, 1500),
                'revenue_concentration_score': np.random.uniform(0.2, 0.4),
                'peak_day_dependency': np.random.uniform(0.05, 0.15),
                'revenue_growth_rate_mom': np.random.uniform(0.05, 0.15),
                'revenue_growth_rate_qoq': np.random.uniform(0.15, 0.30),
                'profit_margin': np.random.uniform(0.15, 0.25),
                'profit_margin_trend': np.random.uniform(0.02, 0.08),
                'inventory_turnover_ratio': np.random.uniform(4, 8),
                'total_assets_value': np.random.uniform(20000000, 100000000),
                'operational_leverage_ratio': np.random.uniform(1.2, 1.8),
                'avg_bank_balance': np.random.uniform(3000000, 10000000),
                'bank_balance_trend': np.random.uniform(0.05, 0.15),
                'weekly_inflow_outflow_ratio': np.random.uniform(1.3, 1.8),
                'overdraft_days_count': 0,
                'overdraft_amount_avg': 0,
                'cash_buffer_days': np.random.uniform(60, 120),
                'avg_daily_closing_balance': np.random.uniform(2500000, 8000000),
                'cash_balance_std_dev': np.random.uniform(100000, 500000),
                'negative_balance_days': 0,
                'daily_min_balance_pattern': np.random.uniform(1500000, 5000000),
                'consistent_deposits_score': np.random.uniform(0.9, 1.0),
                'cashflow_regularity_score': np.random.uniform(0.9, 1.0),
                'receivables_aging_days': np.random.uniform(10, 25),
                'payables_aging_days': np.random.uniform(15, 30),
                'bounced_cheques_count': 0,
                'bounced_cheques_rate': 0.0,
                'historical_loan_utilization': np.random.uniform(0.3, 0.5),
                'overdraft_repayment_ontime_ratio': np.random.uniform(0.95, 1.0),
                'previous_defaults_count': 0,
                'previous_writeoffs_count': 0,
                'current_loans_outstanding': np.random.randint(0, 2),
                'total_debt_amount': np.random.uniform(500000, 2000000),
                'utility_payment_ontime_ratio': np.random.uniform(0.95, 1.0),
                'utility_payment_days_before_due': np.random.uniform(3, 10),
                'mobile_recharge_regularity': np.random.uniform(0.9, 1.0),
                'mobile_recharge_ontime_ratio': np.random.uniform(0.95, 1.0),
                'rent_payment_regularity': np.random.uniform(0.95, 1.0),
                'rent_payment_ontime_ratio': np.random.uniform(0.95, 1.0),
                'supplier_payment_regularity': np.random.uniform(0.9, 1.0),
                'supplier_payment_ontime_ratio': np.random.uniform(0.95, 1.0),
                'gst_filing_regularity': np.random.uniform(0.95, 1.0),
                'gst_filing_ontime_ratio': np.random.uniform(0.95, 1.0),
                'gst_vs_platform_sales_mismatch': np.random.uniform(0.0, 0.05),
                'outstanding_taxes_amount': np.random.uniform(0, 50000),
                'outstanding_dues_flag': 0,
                'itr_filed': 1,
                'itr_income_declared': np.random.uniform(3000000, 10000000),
                'gst_r1_vs_itr_mismatch': 0.0,
                'tax_payment_regularity': np.random.uniform(0.95, 1.0),
                'tax_payment_ontime_ratio': np.random.uniform(0.95, 1.0),
                'refund_chargeback_rate': np.random.uniform(0.0, 0.02),
                'kyc_completion_score': np.random.uniform(0.95, 1.0),
                'kyc_attempts_count': 1,
                'device_consistency_score': np.random.uniform(0.95, 1.0),
                'ip_stability_score': np.random.uniform(0.9, 1.0),
                'pan_address_bank_mismatch': 0,
                'image_ocr_verified': 1,
                'shop_image_verified': 1,
                'reporting_error_rate': np.random.uniform(0.0, 0.01),
                'incoming_funds_verified': np.random.uniform(0.95, 1.0),
                'insurance_coverage_score': np.random.uniform(0.8, 1.0),
                'insurance_premium_paid_ratio': np.random.uniform(0.95, 1.0),
                'local_economic_health_score': np.random.uniform(0.7, 0.9),
                'customer_concentration_risk': np.random.uniform(0.1, 0.3),
                'legal_proceedings_flag': 0,
                'legal_disputes_count': 0,
                'social_media_presence_score': np.random.uniform(0.7, 0.9),
                'social_media_sentiment_score': np.random.uniform(0.8, 0.95),
                'online_reviews_score': np.random.uniform(4.2, 5.0),
                'default_90dpd': 0,  # Perfect business should NOT default
                'default_probability_true': np.random.uniform(0.005, 0.02),
            }
            edge_cases.append(perfect)
        
        # 2. TERRIBLE BUSINESS (n_each samples)
        for _ in range(n_each):
            terrible = {
                'business_segment': 'micro_new',
                'industry_code': 'construction',
                'legal_entity_type': 'proprietorship',
                'business_age_years': np.random.uniform(0.5, 2),
                'business_address_verified': 0,
                'geolocation_verified': 0,
                'industry_risk_score': np.random.uniform(0.35, 0.45),
                'num_business_locations': 1,
                'employees_count': np.random.randint(1, 3),
                'gstin_verified': 0,
                'pan_verified': 0,
                'msme_registered': 0,
                'msme_category': 'not_registered',
                'business_structure': 'home_based',
                'licenses_certificates_score': np.random.uniform(0.1, 0.3),
                'weekly_gtv': np.random.uniform(10000, 50000),
                'monthly_gtv': np.random.uniform(40000, 200000),
                'transaction_count_daily': np.random.randint(2, 10),
                'avg_transaction_value': np.random.uniform(50, 200),
                'revenue_concentration_score': np.random.uniform(0.7, 0.95),
                'peak_day_dependency': np.random.uniform(0.4, 0.6),
                'revenue_growth_rate_mom': np.random.uniform(-0.3, -0.1),
                'revenue_growth_rate_qoq': np.random.uniform(-0.4, -0.1),
                'profit_margin': np.random.uniform(-0.1, 0.05),
                'profit_margin_trend': np.random.uniform(-0.2, -0.05),
                'inventory_turnover_ratio': np.random.uniform(0.5, 1.5),
                'total_assets_value': np.random.uniform(50000, 200000),
                'operational_leverage_ratio': np.random.uniform(2.5, 4.0),
                'avg_bank_balance': np.random.uniform(5000, 30000),
                'bank_balance_trend': np.random.uniform(-0.3, -0.1),
                'weekly_inflow_outflow_ratio': np.random.uniform(0.5, 0.8),
                'overdraft_days_count': np.random.randint(30, 60),
                'overdraft_amount_avg': np.random.uniform(20000, 100000),
                'cash_buffer_days': np.random.uniform(0, 10),
                'avg_daily_closing_balance': np.random.uniform(2000, 20000),
                'cash_balance_std_dev': np.random.uniform(50000, 200000),
                'negative_balance_days': np.random.randint(15, 30),
                'daily_min_balance_pattern': np.random.uniform(0, 5000),
                'consistent_deposits_score': np.random.uniform(0.1, 0.3),
                'cashflow_regularity_score': np.random.uniform(0.1, 0.3),
                'receivables_aging_days': np.random.uniform(60, 120),
                'payables_aging_days': np.random.uniform(90, 150),
                'bounced_cheques_count': np.random.randint(5, 15),
                'bounced_cheques_rate': np.random.uniform(0.15, 0.30),
                'historical_loan_utilization': np.random.uniform(0.8, 1.0),
                'overdraft_repayment_ontime_ratio': np.random.uniform(0.2, 0.4),
                'previous_defaults_count': np.random.randint(1, 4),
                'previous_writeoffs_count': np.random.randint(0, 2),
                'current_loans_outstanding': np.random.randint(3, 8),
                'total_debt_amount': np.random.uniform(500000, 2000000),
                'utility_payment_ontime_ratio': np.random.uniform(0.3, 0.5),
                'utility_payment_days_before_due': np.random.uniform(-20, -10),
                'mobile_recharge_regularity': np.random.uniform(0.3, 0.5),
                'mobile_recharge_ontime_ratio': np.random.uniform(0.3, 0.5),
                'rent_payment_regularity': np.random.uniform(0.3, 0.5),
                'rent_payment_ontime_ratio': np.random.uniform(0.3, 0.5),
                'supplier_payment_regularity': np.random.uniform(0.3, 0.5),
                'supplier_payment_ontime_ratio': np.random.uniform(0.3, 0.5),
                'gst_filing_regularity': np.random.uniform(0.2, 0.4),
                'gst_filing_ontime_ratio': np.random.uniform(0.2, 0.4),
                'gst_vs_platform_sales_mismatch': np.random.uniform(0.3, 0.5),
                'outstanding_taxes_amount': np.random.uniform(100000, 500000),
                'outstanding_dues_flag': 1,
                'itr_filed': 0,
                'itr_income_declared': 0,
                'gst_r1_vs_itr_mismatch': np.random.uniform(0.3, 0.5),
                'tax_payment_regularity': np.random.uniform(0.2, 0.4),
                'tax_payment_ontime_ratio': np.random.uniform(0.2, 0.4),
                'refund_chargeback_rate': np.random.uniform(0.15, 0.25),
                'kyc_completion_score': np.random.uniform(0.3, 0.5),
                'kyc_attempts_count': np.random.randint(3, 6),
                'device_consistency_score': np.random.uniform(0.3, 0.5),
                'ip_stability_score': np.random.uniform(0.3, 0.5),
                'pan_address_bank_mismatch': 1,
                'image_ocr_verified': 0,
                'shop_image_verified': 0,
                'reporting_error_rate': np.random.uniform(0.1, 0.2),
                'incoming_funds_verified': np.random.uniform(0.3, 0.5),
                'insurance_coverage_score': np.random.uniform(0.0, 0.2),
                'insurance_premium_paid_ratio': np.random.uniform(0.0, 0.3),
                'local_economic_health_score': np.random.uniform(0.3, 0.5),
                'customer_concentration_risk': np.random.uniform(0.7, 0.95),
                'legal_proceedings_flag': 1,
                'legal_disputes_count': np.random.randint(1, 4),
                'social_media_presence_score': np.random.uniform(0.1, 0.3),
                'social_media_sentiment_score': np.random.uniform(0.2, 0.4),
                'online_reviews_score': np.random.uniform(1.0, 2.5),
                'default_90dpd': np.random.choice([0, 1], p=[0.6, 0.4]),  # 40% default
                'default_probability_true': np.random.uniform(0.30, 0.40),
            }
            edge_cases.append(terrible)
        
        # 3. NEW BUSINESS WITH NO HISTORY (n_each samples)
        for _ in range(n_each):
            new_biz = {
                'business_segment': 'micro_new',
                'industry_code': np.random.choice(['retail', 'services', 'trading']),
                'legal_entity_type': 'proprietorship',
                'business_age_years': np.random.uniform(0.1, 0.5),
                'business_address_verified': 1,
                'geolocation_verified': 1,
                'industry_risk_score': np.random.uniform(0.2, 0.35),
                'num_business_locations': 1,
                'employees_count': np.random.randint(1, 5),
                'gstin_verified': np.random.choice([0, 1]),
                'pan_verified': 1,
                'msme_registered': 0,
                'msme_category': 'not_registered',
                'business_structure': np.random.choice(['home_based', 'shop']),
                'licenses_certificates_score': np.random.uniform(0.3, 0.6),
                'weekly_gtv': np.random.uniform(30000, 150000),
                'monthly_gtv': np.random.uniform(120000, 600000),
                'transaction_count_daily': np.random.randint(5, 30),
                'avg_transaction_value': np.random.uniform(100, 400),
                'revenue_concentration_score': np.random.uniform(0.5, 0.7),
                'peak_day_dependency': np.random.uniform(0.2, 0.4),
                'revenue_growth_rate_mom': np.random.uniform(0.1, 0.5),  # High growth (new)
                'revenue_growth_rate_qoq': np.random.uniform(0.2, 0.8),
                'profit_margin': np.random.uniform(0.05, 0.15),
                'profit_margin_trend': np.random.uniform(0.0, 0.1),
                'inventory_turnover_ratio': np.random.uniform(1.5, 4),
                'total_assets_value': np.random.uniform(100000, 500000),
                'operational_leverage_ratio': np.random.uniform(1.0, 2.0),
                'avg_bank_balance': np.random.uniform(30000, 150000),
                'bank_balance_trend': np.random.uniform(0.0, 0.2),
                'weekly_inflow_outflow_ratio': np.random.uniform(0.9, 1.2),
                'overdraft_days_count': np.random.randint(0, 10),
                'overdraft_amount_avg': np.random.uniform(0, 30000),
                'cash_buffer_days': np.random.uniform(10, 40),
                'avg_daily_closing_balance': np.random.uniform(20000, 100000),
                'cash_balance_std_dev': np.random.uniform(20000, 80000),
                'negative_balance_days': np.random.randint(0, 5),
                'daily_min_balance_pattern': np.random.uniform(10000, 50000),
                'consistent_deposits_score': np.random.uniform(0.5, 0.7),
                'cashflow_regularity_score': np.random.uniform(0.4, 0.7),
                'receivables_aging_days': np.random.uniform(20, 45),
                'payables_aging_days': np.random.uniform(25, 50),
                'bounced_cheques_count': np.random.randint(0, 2),
                'bounced_cheques_rate': np.random.uniform(0.0, 0.05),
                'historical_loan_utilization': 0.0,  # No history
                'overdraft_repayment_ontime_ratio': np.random.uniform(0.7, 0.9),
                'previous_defaults_count': 0,  # No history
                'previous_writeoffs_count': 0,
                'current_loans_outstanding': 0,
                'total_debt_amount': np.random.uniform(0, 100000),
                'utility_payment_ontime_ratio': np.random.uniform(0.7, 0.9),
                'utility_payment_days_before_due': np.random.uniform(-5, 5),
                'mobile_recharge_regularity': np.random.uniform(0.7, 0.9),
                'mobile_recharge_ontime_ratio': np.random.uniform(0.7, 0.9),
                'rent_payment_regularity': np.random.uniform(0.7, 0.9),
                'rent_payment_ontime_ratio': np.random.uniform(0.7, 0.9),
                'supplier_payment_regularity': np.random.uniform(0.6, 0.8),
                'supplier_payment_ontime_ratio': np.random.uniform(0.6, 0.8),
                'gst_filing_regularity': np.random.uniform(0.5, 0.8),
                'gst_filing_ontime_ratio': np.random.uniform(0.5, 0.8),
                'gst_vs_platform_sales_mismatch': np.random.uniform(0.05, 0.15),
                'outstanding_taxes_amount': np.random.uniform(0, 30000),
                'outstanding_dues_flag': 0,
                'itr_filed': 0,  # New business
                'itr_income_declared': 0,
                'gst_r1_vs_itr_mismatch': 0.0,
                'tax_payment_regularity': np.random.uniform(0.6, 0.8),
                'tax_payment_ontime_ratio': np.random.uniform(0.6, 0.8),
                'refund_chargeback_rate': np.random.uniform(0.02, 0.08),
                'kyc_completion_score': np.random.uniform(0.7, 0.9),
                'kyc_attempts_count': np.random.randint(1, 3),
                'device_consistency_score': np.random.uniform(0.8, 0.95),
                'ip_stability_score': np.random.uniform(0.7, 0.9),
                'pan_address_bank_mismatch': 0,
                'image_ocr_verified': 1,
                'shop_image_verified': np.random.choice([0, 1]),
                'reporting_error_rate': np.random.uniform(0.02, 0.06),
                'incoming_funds_verified': np.random.uniform(0.6, 0.8),
                'insurance_coverage_score': np.random.uniform(0.2, 0.5),
                'insurance_premium_paid_ratio': np.random.uniform(0.5, 0.8),
                'local_economic_health_score': np.random.uniform(0.5, 0.7),
                'customer_concentration_risk': np.random.uniform(0.4, 0.6),
                'legal_proceedings_flag': 0,
                'legal_disputes_count': 0,
                'social_media_presence_score': np.random.uniform(0.4, 0.7),
                'social_media_sentiment_score': np.random.uniform(0.6, 0.8),
                'online_reviews_score': np.random.uniform(3.0, 4.5),
                'default_90dpd': np.random.choice([0, 1], p=[0.88, 0.12]),  # 12% default
                'default_probability_true': np.random.uniform(0.08, 0.15),
            }
            edge_cases.append(new_biz)
        
        # 4. HIGH GROWTH STARTUP (n_each samples)
        for _ in range(n_each):
            startup = {
                'business_segment': 'small_services',
                'industry_code': 'technology',
                'legal_entity_type': np.random.choice(['private_limited', 'llp']),
                'business_age_years': np.random.uniform(1, 3),
                'business_address_verified': 1,
                'geolocation_verified': 1,
                'industry_risk_score': np.random.uniform(0.15, 0.25),
                'num_business_locations': np.random.randint(1, 3),
                'employees_count': np.random.randint(5, 20),
                'gstin_verified': 1,
                'pan_verified': 1,
                'msme_registered': 1,
                'msme_category': 'small',
                'business_structure': 'office',
                'licenses_certificates_score': np.random.uniform(0.7, 0.9),
                'weekly_gtv': np.random.uniform(200000, 800000),
                'monthly_gtv': np.random.uniform(800000, 3200000),
                'transaction_count_daily': np.random.randint(30, 100),
                'avg_transaction_value': np.random.uniform(200, 600),
                'revenue_concentration_score': np.random.uniform(0.4, 0.6),
                'peak_day_dependency': np.random.uniform(0.1, 0.25),
                'revenue_growth_rate_mom': np.random.uniform(0.15, 0.40),  # HIGH growth
                'revenue_growth_rate_qoq': np.random.uniform(0.40, 0.80),
                'profit_margin': np.random.uniform(0.10, 0.20),
                'profit_margin_trend': np.random.uniform(0.03, 0.10),
                'inventory_turnover_ratio': np.random.uniform(3, 6),
                'total_assets_value': np.random.uniform(1000000, 5000000),
                'operational_leverage_ratio': np.random.uniform(1.2, 1.8),
                'avg_bank_balance': np.random.uniform(300000, 1000000),
                'bank_balance_trend': np.random.uniform(0.05, 0.20),
                'weekly_inflow_outflow_ratio': np.random.uniform(1.1, 1.4),
                'overdraft_days_count': np.random.randint(0, 8),
                'overdraft_amount_avg': np.random.uniform(0, 50000),
                'cash_buffer_days': np.random.uniform(25, 50),
                'avg_daily_closing_balance': np.random.uniform(200000, 800000),
                'cash_balance_std_dev': np.random.uniform(50000, 200000),
                'negative_balance_days': np.random.randint(0, 3),
                'daily_min_balance_pattern': np.random.uniform(100000, 400000),
                'consistent_deposits_score': np.random.uniform(0.7, 0.9),
                'cashflow_regularity_score': np.random.uniform(0.6, 0.85),
                'receivables_aging_days': np.random.uniform(20, 40),
                'payables_aging_days': np.random.uniform(25, 45),
                'bounced_cheques_count': np.random.randint(0, 2),
                'bounced_cheques_rate': np.random.uniform(0.0, 0.03),
                'historical_loan_utilization': np.random.uniform(0.3, 0.6),
                'overdraft_repayment_ontime_ratio': np.random.uniform(0.85, 0.98),
                'previous_defaults_count': 0,
                'previous_writeoffs_count': 0,
                'current_loans_outstanding': np.random.randint(0, 2),
                'total_debt_amount': np.random.uniform(200000, 1000000),
                'utility_payment_ontime_ratio': np.random.uniform(0.85, 0.98),
                'utility_payment_days_before_due': np.random.uniform(0, 8),
                'mobile_recharge_regularity': np.random.uniform(0.85, 0.98),
                'mobile_recharge_ontime_ratio': np.random.uniform(0.85, 0.98),
                'rent_payment_regularity': np.random.uniform(0.85, 0.98),
                'rent_payment_ontime_ratio': np.random.uniform(0.85, 0.98),
                'supplier_payment_regularity': np.random.uniform(0.8, 0.95),
                'supplier_payment_ontime_ratio': np.random.uniform(0.8, 0.95),
                'gst_filing_regularity': np.random.uniform(0.85, 0.98),
                'gst_filing_ontime_ratio': np.random.uniform(0.85, 0.98),
                'gst_vs_platform_sales_mismatch': np.random.uniform(0.02, 0.08),
                'outstanding_taxes_amount': np.random.uniform(0, 50000),
                'outstanding_dues_flag': 0,
                'itr_filed': 1,
                'itr_income_declared': np.random.uniform(500000, 2000000),
                'gst_r1_vs_itr_mismatch': np.random.uniform(0.0, 0.05),
                'tax_payment_regularity': np.random.uniform(0.85, 0.98),
                'tax_payment_ontime_ratio': np.random.uniform(0.85, 0.98),
                'refund_chargeback_rate': np.random.uniform(0.01, 0.04),
                'kyc_completion_score': np.random.uniform(0.85, 0.98),
                'kyc_attempts_count': 1,
                'device_consistency_score': np.random.uniform(0.9, 0.98),
                'ip_stability_score': np.random.uniform(0.85, 0.95),
                'pan_address_bank_mismatch': 0,
                'image_ocr_verified': 1,
                'shop_image_verified': 1,
                'reporting_error_rate': np.random.uniform(0.01, 0.03),
                'incoming_funds_verified': np.random.uniform(0.85, 0.95),
                'insurance_coverage_score': np.random.uniform(0.5, 0.8),
                'insurance_premium_paid_ratio': np.random.uniform(0.8, 0.95),
                'local_economic_health_score': np.random.uniform(0.6, 0.8),
                'customer_concentration_risk': np.random.uniform(0.3, 0.5),
                'legal_proceedings_flag': 0,
                'legal_disputes_count': 0,
                'social_media_presence_score': np.random.uniform(0.7, 0.9),
                'social_media_sentiment_score': np.random.uniform(0.75, 0.9),
                'online_reviews_score': np.random.uniform(4.0, 4.8),
                'default_90dpd': np.random.choice([0, 1], p=[0.94, 0.06]),  # 6% default
                'default_probability_true': np.random.uniform(0.04, 0.08),
            }
            edge_cases.append(startup)
        
        # 5. DECLINING BUSINESS (n_each samples)
        for _ in range(n_each):
            declining = {
                'business_segment': 'small_trading',
                'industry_code': 'retail',
                'legal_entity_type': 'proprietorship',
                'business_age_years': np.random.uniform(5, 12),
                'business_address_verified': 1,
                'geolocation_verified': 1,
                'industry_risk_score': np.random.uniform(0.25, 0.35),
                'num_business_locations': np.random.randint(1, 3),
                'employees_count': np.random.randint(2, 8),
                'gstin_verified': 1,
                'pan_verified': 1,
                'msme_registered': 1,
                'msme_category': 'small',
                'business_structure': 'shop',
                'licenses_certificates_score': np.random.uniform(0.5, 0.7),
                'weekly_gtv': np.random.uniform(100000, 300000),
                'monthly_gtv': np.random.uniform(400000, 1200000),
                'transaction_count_daily': np.random.randint(15, 50),
                'avg_transaction_value': np.random.uniform(150, 400),
                'revenue_concentration_score': np.random.uniform(0.5, 0.7),
                'peak_day_dependency': np.random.uniform(0.2, 0.35),
                'revenue_growth_rate_mom': np.random.uniform(-0.15, -0.03),  # DECLINING
                'revenue_growth_rate_qoq': np.random.uniform(-0.25, -0.05),
                'profit_margin': np.random.uniform(0.02, 0.08),
                'profit_margin_trend': np.random.uniform(-0.08, -0.02),
                'inventory_turnover_ratio': np.random.uniform(1.5, 3),
                'total_assets_value': np.random.uniform(500000, 2000000),
                'operational_leverage_ratio': np.random.uniform(1.5, 2.5),
                'avg_bank_balance': np.random.uniform(50000, 200000),
                'bank_balance_trend': np.random.uniform(-0.15, -0.03),
                'weekly_inflow_outflow_ratio': np.random.uniform(0.85, 1.0),
                'overdraft_days_count': np.random.randint(10, 25),
                'overdraft_amount_avg': np.random.uniform(30000, 100000),
                'cash_buffer_days': np.random.uniform(15, 35),
                'avg_daily_closing_balance': np.random.uniform(40000, 150000),
                'cash_balance_std_dev': np.random.uniform(30000, 100000),
                'negative_balance_days': np.random.randint(3, 10),
                'daily_min_balance_pattern': np.random.uniform(20000, 80000),
                'consistent_deposits_score': np.random.uniform(0.5, 0.7),
                'cashflow_regularity_score': np.random.uniform(0.4, 0.65),
                'receivables_aging_days': np.random.uniform(35, 60),
                'payables_aging_days': np.random.uniform(45, 75),
                'bounced_cheques_count': np.random.randint(1, 5),
                'bounced_cheques_rate': np.random.uniform(0.04, 0.10),
                'historical_loan_utilization': np.random.uniform(0.6, 0.85),
                'overdraft_repayment_ontime_ratio': np.random.uniform(0.6, 0.8),
                'previous_defaults_count': np.random.randint(0, 2),
                'previous_writeoffs_count': 0,
                'current_loans_outstanding': np.random.randint(1, 4),
                'total_debt_amount': np.random.uniform(300000, 1000000),
                'utility_payment_ontime_ratio': np.random.uniform(0.6, 0.8),
                'utility_payment_days_before_due': np.random.uniform(-8, 2),
                'mobile_recharge_regularity': np.random.uniform(0.6, 0.8),
                'mobile_recharge_ontime_ratio': np.random.uniform(0.6, 0.8),
                'rent_payment_regularity': np.random.uniform(0.6, 0.8),
                'rent_payment_ontime_ratio': np.random.uniform(0.55, 0.75),
                'supplier_payment_regularity': np.random.uniform(0.55, 0.75),
                'supplier_payment_ontime_ratio': np.random.uniform(0.5, 0.7),
                'gst_filing_regularity': np.random.uniform(0.6, 0.8),
                'gst_filing_ontime_ratio': np.random.uniform(0.55, 0.75),
                'gst_vs_platform_sales_mismatch': np.random.uniform(0.08, 0.18),
                'outstanding_taxes_amount': np.random.uniform(30000, 150000),
                'outstanding_dues_flag': np.random.choice([0, 1]),
                'itr_filed': 1,
                'itr_income_declared': np.random.uniform(200000, 600000),
                'gst_r1_vs_itr_mismatch': np.random.uniform(0.05, 0.15),
                'tax_payment_regularity': np.random.uniform(0.55, 0.75),
                'tax_payment_ontime_ratio': np.random.uniform(0.5, 0.7),
                'refund_chargeback_rate': np.random.uniform(0.05, 0.12),
                'kyc_completion_score': np.random.uniform(0.65, 0.85),
                'kyc_attempts_count': np.random.randint(1, 3),
                'device_consistency_score': np.random.uniform(0.7, 0.85),
                'ip_stability_score': np.random.uniform(0.65, 0.8),
                'pan_address_bank_mismatch': 0,
                'image_ocr_verified': 1,
                'shop_image_verified': 1,
                'reporting_error_rate': np.random.uniform(0.03, 0.08),
                'incoming_funds_verified': np.random.uniform(0.6, 0.8),
                'insurance_coverage_score': np.random.uniform(0.4, 0.6),
                'insurance_premium_paid_ratio': np.random.uniform(0.5, 0.7),
                'local_economic_health_score': np.random.uniform(0.4, 0.6),
                'customer_concentration_risk': np.random.uniform(0.5, 0.7),
                'legal_proceedings_flag': 0,
                'legal_disputes_count': 0,
                'social_media_presence_score': np.random.uniform(0.4, 0.6),
                'social_media_sentiment_score': np.random.uniform(0.5, 0.7),
                'online_reviews_score': np.random.uniform(3.0, 3.8),
                'default_90dpd': np.random.choice([0, 1], p=[0.85, 0.15]),  # 15% default
                'default_probability_true': np.random.uniform(0.12, 0.20),
            }
            edge_cases.append(declining)
        
        # 6. SEASONAL BUSINESS (n_each samples)
        for _ in range(n_each):
            seasonal = {
                'business_segment': 'small_trading',
                'industry_code': np.random.choice(['retail', 'hospitality', 'agriculture']),
                'legal_entity_type': np.random.choice(['proprietorship', 'partnership']),
                'business_age_years': np.random.uniform(3, 10),
                'business_address_verified': 1,
                'geolocation_verified': 1,
                'industry_risk_score': np.random.uniform(0.25, 0.35),
                'num_business_locations': np.random.randint(1, 3),
                'employees_count': np.random.randint(3, 12),
                'gstin_verified': 1,
                'pan_verified': 1,
                'msme_registered': 1,
                'msme_category': 'small',
                'business_structure': np.random.choice(['shop', 'warehouse']),
                'licenses_certificates_score': np.random.uniform(0.6, 0.8),
                'weekly_gtv': np.random.uniform(150000, 500000),
                'monthly_gtv': np.random.uniform(600000, 2000000),
                'transaction_count_daily': np.random.randint(20, 80),
                'avg_transaction_value': np.random.uniform(150, 450),
                'revenue_concentration_score': np.random.uniform(0.4, 0.6),
                'peak_day_dependency': np.random.uniform(0.35, 0.55),  # HIGH peak dependency
                'revenue_growth_rate_mom': np.random.uniform(-0.3, 0.4),  # VARIABLE
                'revenue_growth_rate_qoq': np.random.uniform(-0.2, 0.5),
                'profit_margin': np.random.uniform(0.08, 0.18),
                'profit_margin_trend': np.random.uniform(-0.05, 0.05),
                'inventory_turnover_ratio': np.random.uniform(2, 5),
                'total_assets_value': np.random.uniform(800000, 3000000),
                'operational_leverage_ratio': np.random.uniform(1.3, 2.2),
                'avg_bank_balance': np.random.uniform(80000, 350000),
                'bank_balance_trend': np.random.uniform(-0.1, 0.1),  # Variable
                'weekly_inflow_outflow_ratio': np.random.uniform(0.8, 1.3),
                'overdraft_days_count': np.random.randint(5, 20),
                'overdraft_amount_avg': np.random.uniform(20000, 80000),
                'cash_buffer_days': np.random.uniform(20, 45),
                'avg_daily_closing_balance': np.random.uniform(60000, 280000),
                'cash_balance_std_dev': np.random.uniform(80000, 250000),  # HIGH variance
                'negative_balance_days': np.random.randint(2, 8),
                'daily_min_balance_pattern': np.random.uniform(30000, 120000),
                'consistent_deposits_score': np.random.uniform(0.5, 0.7),  # Lower due to seasonality
                'cashflow_regularity_score': np.random.uniform(0.45, 0.65),
                'receivables_aging_days': np.random.uniform(25, 50),
                'payables_aging_days': np.random.uniform(30, 55),
                'bounced_cheques_count': np.random.randint(0, 3),
                'bounced_cheques_rate': np.random.uniform(0.02, 0.07),
                'historical_loan_utilization': np.random.uniform(0.4, 0.7),
                'overdraft_repayment_ontime_ratio': np.random.uniform(0.7, 0.88),
                'previous_defaults_count': np.random.randint(0, 1),
                'previous_writeoffs_count': 0,
                'current_loans_outstanding': np.random.randint(0, 3),
                'total_debt_amount': np.random.uniform(200000, 800000),
                'utility_payment_ontime_ratio': np.random.uniform(0.7, 0.88),
                'utility_payment_days_before_due': np.random.uniform(-5, 5),
                'mobile_recharge_regularity': np.random.uniform(0.7, 0.88),
                'mobile_recharge_ontime_ratio': np.random.uniform(0.7, 0.88),
                'rent_payment_regularity': np.random.uniform(0.75, 0.9),
                'rent_payment_ontime_ratio': np.random.uniform(0.7, 0.85),
                'supplier_payment_regularity': np.random.uniform(0.65, 0.82),
                'supplier_payment_ontime_ratio': np.random.uniform(0.65, 0.8),
                'gst_filing_regularity': np.random.uniform(0.7, 0.88),
                'gst_filing_ontime_ratio': np.random.uniform(0.7, 0.85),
                'gst_vs_platform_sales_mismatch': np.random.uniform(0.05, 0.12),
                'outstanding_taxes_amount': np.random.uniform(10000, 80000),
                'outstanding_dues_flag': 0,
                'itr_filed': 1,
                'itr_income_declared': np.random.uniform(400000, 1500000),
                'gst_r1_vs_itr_mismatch': np.random.uniform(0.03, 0.10),
                'tax_payment_regularity': np.random.uniform(0.7, 0.85),
                'tax_payment_ontime_ratio': np.random.uniform(0.65, 0.82),
                'refund_chargeback_rate': np.random.uniform(0.03, 0.08),
                'kyc_completion_score': np.random.uniform(0.75, 0.9),
                'kyc_attempts_count': np.random.randint(1, 2),
                'device_consistency_score': np.random.uniform(0.8, 0.92),
                'ip_stability_score': np.random.uniform(0.7, 0.85),
                'pan_address_bank_mismatch': 0,
                'image_ocr_verified': 1,
                'shop_image_verified': 1,
                'reporting_error_rate': np.random.uniform(0.02, 0.05),
                'incoming_funds_verified': np.random.uniform(0.7, 0.85),
                'insurance_coverage_score': np.random.uniform(0.5, 0.7),
                'insurance_premium_paid_ratio': np.random.uniform(0.65, 0.85),
                'local_economic_health_score': np.random.uniform(0.5, 0.7),
                'customer_concentration_risk': np.random.uniform(0.35, 0.55),
                'legal_proceedings_flag': 0,
                'legal_disputes_count': 0,
                'social_media_presence_score': np.random.uniform(0.5, 0.7),
                'social_media_sentiment_score': np.random.uniform(0.6, 0.8),
                'online_reviews_score': np.random.uniform(3.5, 4.3),
                'default_90dpd': np.random.choice([0, 1], p=[0.92, 0.08]),  # 8% default
                'default_probability_true': np.random.uniform(0.06, 0.10),
            }
            edge_cases.append(seasonal)
        
        # Create DataFrame and add timestamps
        edge_df = pd.DataFrame(edge_cases)
        edge_df['application_date'] = [
            datetime(2023, 1, 1) + timedelta(days=int(d))
            for d in np.random.uniform(0, 730, len(edge_df))
        ]
        
        return edge_df
    
    def generate(self, n_samples: int = 10000,
                 missing_rate: float = 0.05,
                 include_timestamp: bool = True) -> pd.DataFrame:
        """
        Generate synthetic MSME credit scoring dataset.
        
        Args:
            n_samples: Number of samples to generate
            missing_rate: Fraction of values to set as missing
            include_timestamp: Whether to include application timestamp
            
        Returns:
            DataFrame with all features and target variable
        """
        print(f"Generating {n_samples} synthetic MSME samples...")
        
        # Assign segments
        segments = np.random.choice(
            list(self.segment_distribution.keys()),
            size=n_samples,
            p=list(self.segment_distribution.values())
        )
        
        # Initialize data dict
        data = {'business_segment': segments}
        
        # Generate base factors per segment
        all_factors = {k: np.zeros(n_samples) for k in 
                      ['gtv_base', 'age_factor', 'formality_factor', 'cashflow_health', 'default_base_prob']}
        
        for segment in self.segment_distribution.keys():
            mask = segments == segment
            n_seg = mask.sum()
            seg_factors = self._generate_segment_features(segment, n_seg)
            for k, v in seg_factors.items():
                all_factors[k][mask] = v
        
        # Assign industries
        industries = np.random.choice(
            list(self.industry_distribution.keys()),
            size=n_samples,
            p=list(self.industry_distribution.values())
        )
        data['industry_code'] = industries
        
        # ========== CATEGORY A: BUSINESS IDENTITY ==========
        data['legal_entity_type'] = np.where(
            all_factors['formality_factor'] > 0.7,
            np.random.choice(['private_limited', 'llp'], n_samples, p=[0.7, 0.3]),
            np.where(
                all_factors['formality_factor'] > 0.4,
                np.random.choice(['partnership', 'proprietorship'], n_samples, p=[0.4, 0.6]),
                'proprietorship'
            )
        )
        
        data['business_age_years'] = np.clip(all_factors['age_factor'] * 15 + np.random.normal(0, 2, n_samples), 0.5, 50)
        data['business_address_verified'] = np.random.binomial(1, all_factors['formality_factor'] * 0.95, n_samples)
        data['geolocation_verified'] = np.random.binomial(1, all_factors['formality_factor'] * 0.9, n_samples)
        data['industry_risk_score'] = np.array([self.industry_risk[ind] for ind in industries]) + np.random.normal(0, 0.05, n_samples)
        data['industry_risk_score'] = np.clip(data['industry_risk_score'], 0, 1)
        data['num_business_locations'] = np.clip(1 + np.random.poisson(all_factors['gtv_base'] / 1e6, n_samples), 1, 100).astype(int)
        data['employees_count'] = np.clip(np.round(all_factors['gtv_base'] / 500000 + np.random.normal(0, 5, n_samples)), 1, 500).astype(int)
        data['gstin_verified'] = np.random.binomial(1, all_factors['formality_factor'], n_samples)
        data['pan_verified'] = np.random.binomial(1, np.minimum(all_factors['formality_factor'] + 0.2, 1), n_samples)
        data['msme_registered'] = np.random.binomial(1, all_factors['formality_factor'] * 0.8, n_samples)
        data['msme_category'] = np.where(
            data['msme_registered'] == 0, 'not_registered',
            np.where(all_factors['gtv_base'] < 1e6, 'micro',
                    np.where(all_factors['gtv_base'] < 1e7, 'small', 'medium'))
        )
        data['business_structure'] = np.random.choice(
            ['home_based', 'shop', 'warehouse', 'office', 'factory', 'multiple'],
            n_samples,
            p=[0.15, 0.35, 0.15, 0.20, 0.10, 0.05]
        )
        data['licenses_certificates_score'] = np.clip(all_factors['formality_factor'] + np.random.normal(0, 0.1, n_samples), 0, 1)
        
        # ========== CATEGORY B: REVENUE & PERFORMANCE ==========
        data['weekly_gtv'] = np.clip(all_factors['gtv_base'] / 4, 0, 100000000)
        data['monthly_gtv'] = np.clip(all_factors['gtv_base'], 0, 500000000)
        data['transaction_count_daily'] = np.clip(np.round(data['weekly_gtv'] / (7 * 500) + np.random.normal(0, 20, n_samples)), 1, 10000).astype(int)
        data['avg_transaction_value'] = data['weekly_gtv'] / (data['transaction_count_daily'] * 7 + 1)
        data['revenue_concentration_score'] = np.clip(1 - all_factors['cashflow_health'] * 0.5 + np.random.normal(0, 0.1, n_samples), 0, 1)
        data['peak_day_dependency'] = np.clip(np.random.beta(2, 5, n_samples), 0, 1)
        data['revenue_growth_rate_mom'] = np.clip(np.random.normal(0.05, 0.15, n_samples), -0.5, 1)
        data['revenue_growth_rate_qoq'] = np.clip(np.random.normal(0.15, 0.25, n_samples), -0.5, 2)
        data['profit_margin'] = np.clip(np.random.normal(0.15, 0.12, n_samples), -0.3, 0.6)
        data['profit_margin_trend'] = np.clip(np.random.normal(0.02, 0.1, n_samples), -0.5, 0.5)
        data['inventory_turnover_ratio'] = np.clip(np.random.lognormal(1.5, 0.8, n_samples), 0.5, 50)
        data['total_assets_value'] = np.clip(all_factors['gtv_base'] * np.random.uniform(2, 10, n_samples), 0, 500000000)
        data['operational_leverage_ratio'] = np.clip(np.random.lognormal(0.3, 0.5, n_samples), 0.5, 5)
        
        # ========== CATEGORY C: CASH FLOW & BANKING ==========
        data['avg_bank_balance'] = np.clip(data['monthly_gtv'] * np.random.uniform(0.1, 0.4, n_samples), 0, 100000000)
        data['bank_balance_trend'] = np.clip(np.random.normal(0.05, 0.2, n_samples), -0.5, 0.5)
        data['weekly_inflow_outflow_ratio'] = np.clip(1 + all_factors['cashflow_health'] * 0.3 + np.random.normal(0, 0.2, n_samples), 0.5, 3)
        data['overdraft_days_count'] = np.clip(np.round((1 - all_factors['cashflow_health']) * 30 + np.random.exponential(5, n_samples)), 0, 90).astype(int)
        data['overdraft_amount_avg'] = np.where(data['overdraft_days_count'] > 0, 
                                                np.clip(data['monthly_gtv'] * 0.1 * np.random.uniform(0.1, 0.5, n_samples), 0, 10000000), 0)
        data['cash_buffer_days'] = np.clip(all_factors['cashflow_health'] * 60 + np.random.normal(0, 15, n_samples), 0, 180)
        data['avg_daily_closing_balance'] = data['avg_bank_balance'] * np.random.uniform(0.8, 1.2, n_samples)
        data['cash_balance_std_dev'] = np.clip(data['avg_bank_balance'] * np.random.uniform(0.1, 0.5, n_samples), 0, 10000000)
        data['negative_balance_days'] = np.clip(data['overdraft_days_count'] * np.random.uniform(0, 0.5, n_samples), 0, 90).astype(int)
        data['daily_min_balance_pattern'] = np.clip(data['avg_bank_balance'] * np.random.uniform(0.1, 0.5, n_samples), 0, 10000000)
        data['consistent_deposits_score'] = np.clip(all_factors['cashflow_health'] + np.random.normal(0, 0.1, n_samples), 0, 1)
        data['cashflow_regularity_score'] = np.clip(all_factors['cashflow_health'] + np.random.normal(0, 0.1, n_samples), 0, 1)
        data['receivables_aging_days'] = np.clip(np.random.exponential(30, n_samples), 0, 180)
        data['payables_aging_days'] = np.clip(np.random.exponential(25, n_samples), 0, 180)
        
        # ========== CATEGORY D: CREDIT & REPAYMENT ==========
        repayment_discipline = all_factors['cashflow_health'] * 0.6 + all_factors['formality_factor'] * 0.4
        
        data['bounced_cheques_count'] = np.clip(np.round((1 - repayment_discipline) * 5 + np.random.poisson(1, n_samples)), 0, 50).astype(int)
        data['bounced_cheques_rate'] = np.clip((1 - repayment_discipline) * 0.1 + np.random.normal(0, 0.03, n_samples), 0, 1)
        data['historical_loan_utilization'] = np.clip(np.random.beta(3, 4, n_samples), 0, 1)
        data['overdraft_repayment_ontime_ratio'] = np.clip(repayment_discipline + np.random.normal(0, 0.1, n_samples), 0, 1)
        data['previous_defaults_count'] = np.clip(np.round((1 - repayment_discipline) * 2 + np.random.poisson(0.3, n_samples)), 0, 10).astype(int)
        data['previous_writeoffs_count'] = np.clip(np.round((1 - repayment_discipline) * 1 + np.random.poisson(0.1, n_samples)), 0, 10).astype(int)
        data['current_loans_outstanding'] = np.clip(np.round(np.random.poisson(1.5, n_samples)), 0, 20).astype(int)
        data['total_debt_amount'] = np.clip(data['monthly_gtv'] * np.random.uniform(0, 0.5, n_samples), 0, 100000000)
        data['utility_payment_ontime_ratio'] = np.clip(repayment_discipline + np.random.normal(0, 0.08, n_samples), 0, 1)
        data['utility_payment_days_before_due'] = np.clip(repayment_discipline * 10 + np.random.normal(-5, 8, n_samples), -30, 30)
        data['mobile_recharge_regularity'] = np.clip(repayment_discipline + np.random.normal(0, 0.1, n_samples), 0, 1)
        data['mobile_recharge_ontime_ratio'] = np.clip(repayment_discipline + np.random.normal(0, 0.1, n_samples), 0, 1)
        data['rent_payment_regularity'] = np.clip(repayment_discipline + np.random.normal(0, 0.1, n_samples), 0, 1)
        data['rent_payment_ontime_ratio'] = np.clip(repayment_discipline + np.random.normal(0, 0.1, n_samples), 0, 1)
        data['supplier_payment_regularity'] = np.clip(repayment_discipline + np.random.normal(0, 0.1, n_samples), 0, 1)
        data['supplier_payment_ontime_ratio'] = np.clip(repayment_discipline + np.random.normal(0, 0.1, n_samples), 0, 1)
        
        # ========== CATEGORY E: COMPLIANCE & TAXATION ==========
        data['gst_filing_regularity'] = np.clip(all_factors['formality_factor'] + np.random.normal(0, 0.1, n_samples), 0, 1)
        data['gst_filing_ontime_ratio'] = np.clip(data['gst_filing_regularity'] * 0.9 + np.random.normal(0, 0.1, n_samples), 0, 1)
        data['gst_vs_platform_sales_mismatch'] = np.clip((1 - all_factors['formality_factor']) * 0.3 + np.random.normal(0, 0.1, n_samples), 0, 1)
        data['outstanding_taxes_amount'] = np.clip((1 - all_factors['formality_factor']) * data['monthly_gtv'] * 0.05 + np.random.exponential(10000, n_samples), 0, 10000000)
        data['outstanding_dues_flag'] = np.random.binomial(1, (1 - all_factors['formality_factor']) * 0.3, n_samples)
        data['itr_filed'] = np.random.binomial(1, all_factors['formality_factor'] * 0.9, n_samples)
        data['itr_income_declared'] = data['monthly_gtv'] * 12 * data['profit_margin'] * data['itr_filed'] * np.random.uniform(0.7, 1.0, n_samples)
        data['gst_r1_vs_itr_mismatch'] = np.clip((1 - all_factors['formality_factor']) * 0.2 + np.random.normal(0, 0.1, n_samples), 0, 1)
        data['tax_payment_regularity'] = np.clip(all_factors['formality_factor'] + np.random.normal(0, 0.1, n_samples), 0, 1)
        data['tax_payment_ontime_ratio'] = np.clip(data['tax_payment_regularity'] * 0.9 + np.random.normal(0, 0.1, n_samples), 0, 1)
        data['refund_chargeback_rate'] = np.clip(np.random.beta(1, 15, n_samples), 0, 0.3)
        
        # ========== CATEGORY F: FRAUD & VERIFICATION ==========
        data['kyc_completion_score'] = np.clip(all_factors['formality_factor'] * 0.9 + np.random.normal(0.1, 0.1, n_samples), 0, 1)
        data['kyc_attempts_count'] = np.clip(1 + np.round((1 - all_factors['formality_factor']) * 3 + np.random.poisson(0.5, n_samples)), 1, 10).astype(int)
        data['device_consistency_score'] = np.clip(np.random.beta(8, 2, n_samples), 0, 1)
        data['ip_stability_score'] = np.clip(np.random.beta(7, 2, n_samples), 0, 1)
        data['pan_address_bank_mismatch'] = np.random.binomial(1, 0.05 + (1 - all_factors['formality_factor']) * 0.1, n_samples)
        data['image_ocr_verified'] = np.random.binomial(1, all_factors['formality_factor'] * 0.95, n_samples)
        data['shop_image_verified'] = np.random.binomial(1, all_factors['formality_factor'] * 0.9, n_samples)
        data['reporting_error_rate'] = np.clip((1 - all_factors['formality_factor']) * 0.1 + np.random.normal(0, 0.03, n_samples), 0, 0.5)
        data['incoming_funds_verified'] = np.clip(all_factors['formality_factor'] + np.random.normal(0, 0.1, n_samples), 0, 1)
        data['insurance_coverage_score'] = np.clip(all_factors['formality_factor'] * 0.7 + np.random.normal(0, 0.15, n_samples), 0, 1)
        data['insurance_premium_paid_ratio'] = np.clip(data['insurance_coverage_score'] * 0.9 + np.random.normal(0, 0.1, n_samples), 0, 1)
        
        # ========== CATEGORY G: EXTERNAL SIGNALS ==========
        data['local_economic_health_score'] = np.clip(np.random.beta(5, 3, n_samples), 0, 1)
        data['customer_concentration_risk'] = np.clip(np.random.beta(2, 5, n_samples), 0, 1)
        data['legal_proceedings_flag'] = np.random.binomial(1, 0.03 + (1 - all_factors['formality_factor']) * 0.05, n_samples)
        data['legal_disputes_count'] = data['legal_proceedings_flag'] * np.clip(np.random.poisson(1, n_samples), 0, 10)
        data['social_media_presence_score'] = np.clip(np.random.beta(3, 4, n_samples), 0, 1)
        data['social_media_sentiment_score'] = np.clip(np.random.beta(5, 2, n_samples), 0, 1)
        data['online_reviews_score'] = np.clip(np.random.normal(3.5, 1, n_samples), 0, 5)
        
        # ========== TARGET VARIABLE: 90 DPD DEFAULT ==========
        # IMPROVED: Proper correlations - good features CLEARLY reduce default probability
        
        # 1. Base risk from segment (now realistic: 2-12%)
        base_risk = all_factors['default_base_prob'].copy()
        
        # 2. RISK INCREASING factors (poor behavior increases default probability)
        risk_increase = np.zeros(n_samples)
        
        # Poor repayment behavior (MAJOR risk factor - weight 20%)
        risk_increase += 0.20 * (1 - data['overdraft_repayment_ontime_ratio'])
        
        # Bounced cheques (STRONG indicator - weight 15%)
        risk_increase += 0.15 * np.clip(data['bounced_cheques_count'] / 5, 0, 1)
        
        # Previous defaults (historical risk - weight 12%)
        risk_increase += 0.12 * np.clip(data['previous_defaults_count'] / 2, 0, 1)
        
        # Cash flow issues (weight 8%)
        risk_increase += 0.08 * np.clip(data['overdraft_days_count'] / 60, 0, 1)
        risk_increase += 0.06 * np.clip(1 - data['weekly_inflow_outflow_ratio'], 0, 1)
        
        # Compliance issues (weight 5%)
        risk_increase += 0.05 * (1 - data['gst_filing_regularity'])
        risk_increase += 0.04 * data['gst_vs_platform_sales_mismatch']
        
        # Payment discipline issues (weight 5%)
        risk_increase += 0.05 * (1 - data['utility_payment_ontime_ratio'])
        risk_increase += 0.04 * (1 - data['supplier_payment_ontime_ratio'])
        
        # Fraud indicators (weight 6%)
        risk_increase += 0.05 * data['pan_address_bank_mismatch']
        risk_increase += 0.04 * data['legal_proceedings_flag']
        
        # 3. RISK REDUCING factors (good behavior CLEARLY reduces default probability)
        risk_reduction = np.zeros(n_samples)
        
        # Strong cash position (MAJOR protector - weight 15%)
        risk_reduction += 0.15 * all_factors['cashflow_health']
        
        # Business formality/compliance (MAJOR protector - weight 12%)
        risk_reduction += 0.12 * all_factors['formality_factor']
        
        # Excellent repayment ratio (STRONG protector - weight 18%)
        risk_reduction += 0.18 * data['overdraft_repayment_ontime_ratio']
        
        # Good GST compliance (weight 8%)
        risk_reduction += 0.08 * data['gst_filing_regularity']
        
        # ITR filed (formal business - weight 5%)
        risk_reduction += 0.05 * data['itr_filed']
        
        # Business age/maturity (weight 6%)
        risk_reduction += 0.06 * np.clip(data['business_age_years'] / 10, 0, 1)
        
        # Strong revenue growth (weight 4%)
        risk_reduction += 0.04 * np.clip(data['revenue_growth_rate_mom'] + 0.2, 0, 0.5)
        
        # Good KYC score (weight 5%)
        risk_reduction += 0.05 * data['kyc_completion_score']
        
        # Cash buffer/liquidity (weight 5%)
        risk_reduction += 0.05 * np.clip(data['cash_buffer_days'] / 60, 0, 1)
        
        # Good utility payment (weight 4%)
        risk_reduction += 0.04 * data['utility_payment_ontime_ratio']
        
        # 4. Calculate final risk score
        risk_score = base_risk + risk_increase - risk_reduction
        
        # Add small noise for realism
        risk_score += np.random.normal(0, 0.015, n_samples)
        
        # Clip to realistic range (0.5% to 35%)
        default_prob = np.clip(risk_score, 0.005, 0.35)
        
        # Generate default labels
        data['default_90dpd'] = np.random.binomial(1, default_prob, n_samples)
        data['default_probability_true'] = default_prob
        
        # Add timestamp
        if include_timestamp:
            base_date = datetime(2023, 1, 1)
            data['application_date'] = [
                base_date + timedelta(days=int(d))
                for d in np.random.uniform(0, 730, n_samples)
            ]
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Introduce missing values
        missing_features = [
            'itr_income_declared', 'total_assets_value', 'insurance_coverage_score',
            'inventory_turnover_ratio', 'profit_margin', 'social_media_presence_score'
        ]
        
        for feat in missing_features:
            if feat in df.columns:
                mask = np.random.random(n_samples) < missing_rate * 2
                df.loc[mask, feat] = np.nan
        
        # Regular missing rate
        for col in df.select_dtypes(include=[np.number]).columns:
            if col not in missing_features and col not in ['default_90dpd', 'default_probability_true']:
                mask = np.random.random(n_samples) < missing_rate
                df.loc[mask, col] = np.nan
        
        # ========== ADD EDGE CASES ==========
        # Add edge case scenarios for comprehensive model coverage
        n_edge_each = max(50, n_samples // 100)  # ~1% of total samples per edge case type
        edge_df = self._generate_edge_cases(n_each=n_edge_each)
        
        # Combine main data with edge cases
        df = pd.concat([df, edge_df], ignore_index=True)
        
        # Shuffle the combined dataset
        df = df.sample(frac=1, random_state=self.seed).reset_index(drop=True)
        
        print(f"Generated {len(df)} MSME samples with {df['default_90dpd'].sum()} defaults ({df['default_90dpd'].mean()*100:.1f}%)")
        print(f"  - Main samples: {n_samples}")
        print(f"  - Edge cases: {len(edge_df)} ({n_edge_each} each × 6 types)")
        
        return df


# ============================================================================
# PREPROCESSING PIPELINE
# ============================================================================

class MSMEPreprocessor:
    """
    End-to-end preprocessing for MSME credit scoring pipeline.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.feature_schema = MSME_FEATURE_SCHEMA
        self.feature_bounds = {}
        self.scalers = {}
        self.encoders = {}
        self.imputers = {}
        self.fitted = False
        
        if config_path:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
    
    def _get_numeric_features(self) -> List[str]:
        """Get list of numeric features"""
        return [f for f, spec in self.feature_schema.items() 
                if spec.dtype in ['numeric', 'binary']]
    
    def _get_categorical_features(self) -> List[str]:
        """Get list of categorical features"""
        return [f for f, spec in self.feature_schema.items() if spec.dtype == 'categorical']
    
    def _clip_outliers(self, df: pd.DataFrame, lower_pct: float = 1, upper_pct: float = 99) -> pd.DataFrame:
        """Clip outliers using percentile bounds"""
        df = df.copy()
        
        for col in self._get_numeric_features():
            if col in df.columns and df[col].notna().sum() > 0:
                spec = self.feature_schema.get(col)
                
                if not self.fitted:
                    lower = max(df[col].quantile(lower_pct/100), spec.min_val if spec else -np.inf)
                    upper = min(df[col].quantile(upper_pct/100), spec.max_val if spec else np.inf)
                    self.feature_bounds[col] = {'lower': lower, 'upper': upper}
                else:
                    lower = self.feature_bounds.get(col, {}).get('lower', -np.inf)
                    upper = self.feature_bounds.get(col, {}).get('upper', np.inf)
                
                df[col] = df[col].clip(lower=lower, upper=upper)
        
        return df
    
    def _impute_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        """Impute missing values"""
        df = df.copy()
        
        numeric_cols = [c for c in self._get_numeric_features() if c in df.columns]
        
        if not self.fitted:
            self.imputers['numeric'] = SimpleImputer(strategy='median')
            if numeric_cols:
                df[numeric_cols] = self.imputers['numeric'].fit_transform(df[numeric_cols])
        else:
            if numeric_cols and 'numeric' in self.imputers:
                df[numeric_cols] = self.imputers['numeric'].transform(df[numeric_cols])
        
        for col in self._get_categorical_features():
            if col in df.columns:
                if not self.fitted:
                    mode_val = df[col].mode()[0] if not df[col].mode().empty else 'unknown'
                    self.imputers[col] = mode_val
                df[col] = df[col].fillna(self.imputers.get(col, 'unknown'))
        
        return df
    
    def _encode_categoricals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical features"""
        df = df.copy()
        
        for col in self._get_categorical_features():
            if col in df.columns:
                if not self.fitted:
                    self.encoders[col] = LabelEncoder()
                    spec = self.feature_schema.get(col)
                    all_categories = list(spec.categories or []) + ['unknown']
                    self.encoders[col].fit(all_categories)
                
                df[col] = df[col].apply(
                    lambda x: x if x in self.encoders[col].classes_ else 'unknown'
                )
                df[col] = self.encoders[col].transform(df[col])
        
        return df
    
    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create derived features"""
        df = df.copy()
        
        # Cash coverage ratio
        if 'avg_bank_balance' in df.columns and 'monthly_gtv' in df.columns:
            df['cash_coverage_ratio'] = df['avg_bank_balance'] / (df['monthly_gtv'] / 30 + 1)
        
        # Debt service coverage
        if 'monthly_gtv' in df.columns and 'total_debt_amount' in df.columns:
            df['debt_to_revenue_ratio'] = df['total_debt_amount'] / (df['monthly_gtv'] * 12 + 1)
        
        # Working capital days
        if 'receivables_aging_days' in df.columns and 'payables_aging_days' in df.columns:
            df['working_capital_days'] = df['receivables_aging_days'] - df['payables_aging_days']
        
        # Overall payment discipline
        payment_cols = ['utility_payment_ontime_ratio', 'rent_payment_ontime_ratio', 
                       'supplier_payment_ontime_ratio', 'overdraft_repayment_ontime_ratio']
        available = [c for c in payment_cols if c in df.columns]
        if available:
            df['overall_payment_discipline'] = df[available].mean(axis=1)
        
        # Compliance score
        compliance_cols = ['gst_filing_regularity', 'tax_payment_regularity', 'itr_filed']
        available = [c for c in compliance_cols if c in df.columns]
        if available:
            df['overall_compliance_score'] = df[available].mean(axis=1)
        
        # Fraud risk score
        if 'pan_address_bank_mismatch' in df.columns and 'kyc_attempts_count' in df.columns:
            df['fraud_risk_indicator'] = (df['pan_address_bank_mismatch'] + 
                                         (df['kyc_attempts_count'] > 3).astype(int))
        
        return df
    
    def fit_transform(self, df: pd.DataFrame, normalize: bool = False) -> pd.DataFrame:
        """Fit preprocessor and transform data"""
        self.fitted = False
        
        df = self._clip_outliers(df)
        df = self._impute_missing(df)
        df = self._encode_categoricals(df)
        df = self._engineer_features(df)
        
        self.fitted = True
        return df
    
    def transform(self, df: pd.DataFrame, normalize: bool = False) -> pd.DataFrame:
        """Transform new data"""
        if not self.fitted:
            raise ValueError("Preprocessor must be fitted first")
        
        df = self._clip_outliers(df)
        df = self._impute_missing(df)
        df = self._encode_categoricals(df)
        df = self._engineer_features(df)
        
        return df
    
    def get_feature_bounds(self) -> Dict:
        return self.feature_bounds
    
    def save(self, path: str):
        """Save preprocessor state"""
        import joblib
        state = {
            'feature_bounds': self.feature_bounds,
            'imputers': self.imputers,
            'encoders': self.encoders,
            'scalers': self.scalers,
            'fitted': self.fitted
        }
        joblib.dump(state, path)
        print(f"Preprocessor saved to {path}")
    
    def load(self, path: str):
        """Load preprocessor state"""
        import joblib
        state = joblib.load(path)
        self.feature_bounds = state['feature_bounds']
        self.imputers = state['imputers']
        self.encoders = state['encoders']
        self.scalers = state['scalers']
        self.fitted = state['fitted']
        print(f"Preprocessor loaded from {path}")


# ============================================================================
# TRAIN/VAL/TEST SPLIT
# ============================================================================

def create_msme_splits(df: pd.DataFrame,
                       target_col: str = 'default_90dpd',
                       timestamp_col: Optional[str] = 'application_date',
                       test_size: float = 0.15,
                       val_size: float = 0.15,
                       random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create train/validation/test splits"""
    
    print(f"Creating MSME data splits (test={test_size}, val={val_size})...")
    
    if timestamp_col and timestamp_col in df.columns:
        df_sorted = df.sort_values(timestamp_col).reset_index(drop=True)
        n = len(df_sorted)
        
        test_idx = int(n * (1 - test_size))
        val_idx = int(test_idx * (1 - val_size / (1 - test_size)))
        
        train_df = df_sorted.iloc[:val_idx].copy()
        val_df = df_sorted.iloc[val_idx:test_idx].copy()
        test_df = df_sorted.iloc[test_idx:].copy()
        
        print(f"Time-based split:")
    else:
        train_val_df, test_df = train_test_split(
            df, test_size=test_size, stratify=df[target_col], random_state=random_state
        )
        
        val_ratio = val_size / (1 - test_size)
        train_df, val_df = train_test_split(
            train_val_df, test_size=val_ratio, stratify=train_val_df[target_col], random_state=random_state
        )
        
        print(f"Stratified split:")
    
    print(f"  Train: {len(train_df)} samples ({train_df[target_col].mean()*100:.1f}% default rate)")
    print(f"  Val: {len(val_df)} samples ({val_df[target_col].mean()*100:.1f}% default rate)")
    print(f"  Test: {len(test_df)} samples ({test_df[target_col].mean()*100:.1f}% default rate)")
    
    return train_df, val_df, test_df


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("MSME CREDIT SCORING DATA PREPARATION")
    print("=" * 60)
    
    generator = MSMESyntheticDataGenerator(seed=42)
    df = generator.generate(n_samples=10000, missing_rate=0.05)
    
    print(f"\nDataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)[:10]}... ({len(df.columns)} total)")
    
    train_df, val_df, test_df = create_msme_splits(df, timestamp_col='application_date')
    
    preprocessor = MSMEPreprocessor()
    train_processed = preprocessor.fit_transform(train_df)
    val_processed = preprocessor.transform(val_df)
    test_processed = preprocessor.transform(test_df)
    
    print(f"\nProcessed shapes: Train={train_processed.shape}, Val={val_processed.shape}, Test={test_processed.shape}")
    
    preprocessor.save("msme_preprocessor.joblib")
    print("\nData preparation complete!")


