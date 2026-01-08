"""
Credit Scoring Pipeline - Data Preparation Module
==================================================

This module provides:
1. Feature schema definition matching the exact parameters specified
2. Synthetic data generator for testing
3. End-to-end preprocessing: imputation, outlier handling, feature engineering
4. Train/validation/test split with time-awareness support
5. Normalization and categorical encoding utilities

Author: ML Engineering Team
Version: 1.0.0
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from sklearn.preprocessing import StandardScaler, RobustScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split, TimeSeriesSplit
import json
import warnings
from datetime import datetime, timedelta
import random

warnings.filterwarnings('ignore')

# ============================================================================
# FEATURE SCHEMA DEFINITION
# ============================================================================

@dataclass
class FeatureSpec:
    """Specification for a single feature"""
    name: str
    dtype: str  # 'numeric', 'binary', 'categorical', 'ordinal'
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    higher_is_better: Optional[bool] = None
    categories: Optional[List[str]] = None
    ordinal_mapping: Optional[Dict[str, int]] = None
    impute_strategy: str = 'median'  # 'median', 'mean', 'mode', 'constant'
    impute_value: Optional[Any] = None


# Complete feature schema matching the exact parameters specified
FEATURE_SCHEMA = {
    # ========== CATEGORY A: IDENTITY, STABILITY & DEMOGRAPHICS (10%) ==========
    'name_dob_verified': FeatureSpec('name_dob_verified', 'binary', 0, 1, True),
    'phone_verified': FeatureSpec('phone_verified', 'binary', 0, 1, True),
    'phone_age_months': FeatureSpec('phone_age_months', 'numeric', 0, 240, True),
    'email_verified': FeatureSpec('email_verified', 'binary', 0, 1, True),
    'email_age_months': FeatureSpec('email_age_months', 'numeric', 0, 240, True),
    'location_stability_score': FeatureSpec('location_stability_score', 'numeric', 0, 1, True),
    'location_tier': FeatureSpec('location_tier', 'categorical', categories=['tier1', 'tier2', 'tier3', 'rural']),
    'education_level': FeatureSpec('education_level', 'ordinal', 0, 5, True, 
                                   ordinal_mapping={'none': 0, 'high_school': 1, 'diploma': 2, 'bachelors': 3, 'masters': 4, 'doctorate': 5}),
    'employment_tenure_months': FeatureSpec('employment_tenure_months', 'numeric', 0, 480, True),
    'employment_type': FeatureSpec('employment_type', 'categorical', 
                                   categories=['unemployed', 'self_employed', 'contract', 'part_time', 'full_time', 'government']),
    
    # ========== CATEGORY B: INCOME & CASH FLOW STRENGTH (25%) ==========
    'monthly_income': FeatureSpec('monthly_income', 'numeric', 0, 5000000, True),
    'income_growth_rate': FeatureSpec('income_growth_rate', 'numeric', -0.5, 1.0, True),
    'avg_account_balance': FeatureSpec('avg_account_balance', 'numeric', 0, 10000000, True),
    'min_account_balance': FeatureSpec('min_account_balance', 'numeric', 0, 10000000, True),
    'income_stability_score': FeatureSpec('income_stability_score', 'numeric', 0, 1, True),
    'income_variance_coefficient': FeatureSpec('income_variance_coefficient', 'numeric', 0, 2, False),
    'itr_filed': FeatureSpec('itr_filed', 'binary', 0, 1, True),
    'itr_income_declared': FeatureSpec('itr_income_declared', 'numeric', 0, 50000000, True),
    'employability_score': FeatureSpec('employability_score', 'numeric', 0, 1, True),
    'ppf_balance': FeatureSpec('ppf_balance', 'numeric', 0, 5000000, True),
    'gov_schemes_enrolled': FeatureSpec('gov_schemes_enrolled', 'numeric', 0, 10, True),
    'bank_statement_months_available': FeatureSpec('bank_statement_months_available', 'numeric', 0, 36, True),
    
    # ========== CATEGORY C: ASSETS, LIABILITIES & OBLIGATIONS (20%) ==========
    'current_loan_count': FeatureSpec('current_loan_count', 'numeric', 0, 20, False),
    'current_loan_amount': FeatureSpec('current_loan_amount', 'numeric', 0, 50000000, False),
    'credit_card_count': FeatureSpec('credit_card_count', 'numeric', 0, 10),
    'credit_card_utilization': FeatureSpec('credit_card_utilization', 'numeric', 0, 1, False),
    'credit_card_limit': FeatureSpec('credit_card_limit', 'numeric', 0, 10000000, True),
    'lic_policy_count': FeatureSpec('lic_policy_count', 'numeric', 0, 10, True),
    'lic_premium_annual': FeatureSpec('lic_premium_annual', 'numeric', 0, 1000000, True),
    'fd_total_amount': FeatureSpec('fd_total_amount', 'numeric', 0, 50000000, True),
    'total_assets_value': FeatureSpec('total_assets_value', 'numeric', 0, 100000000, True),
    'insurance_premium_paid_ratio': FeatureSpec('insurance_premium_paid_ratio', 'numeric', 0, 1, True),
    'insurance_renewal_ontime_ratio': FeatureSpec('insurance_renewal_ontime_ratio', 'numeric', 0, 1, True),
    'debt_to_income_ratio': FeatureSpec('debt_to_income_ratio', 'numeric', 0, 5, False),
    
    # ========== CATEGORY D: SPENDING, BEHAVIOURAL & PSYCHOLOGICAL (25%) ==========
    'monthly_spending': FeatureSpec('monthly_spending', 'numeric', 0, 5000000),
    'spending_to_income_ratio': FeatureSpec('spending_to_income_ratio', 'numeric', 0, 2, False),
    'essential_spending_ratio': FeatureSpec('essential_spending_ratio', 'numeric', 0, 1, True),
    'discretionary_spending_ratio': FeatureSpec('discretionary_spending_ratio', 'numeric', 0, 1, False),
    'purchase_frequency': FeatureSpec('purchase_frequency', 'numeric', 0, 500),
    'avg_purchase_value': FeatureSpec('avg_purchase_value', 'numeric', 0, 100000),
    'subscription_cancellation_count': FeatureSpec('subscription_cancellation_count', 'numeric', 0, 20, False),
    'subscription_downgrade_count': FeatureSpec('subscription_downgrade_count', 'numeric', 0, 20, False),
    'impatience_score': FeatureSpec('impatience_score', 'numeric', 0, 1, False),
    'impulse_buying_score': FeatureSpec('impulse_buying_score', 'numeric', 0, 1, False),
    'budgeting_score': FeatureSpec('budgeting_score', 'numeric', 0, 1, True),
    'financial_literacy_score': FeatureSpec('financial_literacy_score', 'numeric', 0, 1, True),
    'recurring_payment_habit_score': FeatureSpec('recurring_payment_habit_score', 'numeric', 0, 1, True),
    'loan_application_count_6m': FeatureSpec('loan_application_count_6m', 'numeric', 0, 20, False),
    'application_rejection_rate': FeatureSpec('application_rejection_rate', 'numeric', 0, 1, False),
    'social_media_score': FeatureSpec('social_media_score', 'numeric', 0, 1, True),
    'email_response_time_score': FeatureSpec('email_response_time_score', 'numeric', 0, 1, True),
    
    # ========== CATEGORY E: TRANSACTIONS, REPAYMENTS & UTILITY (15%) ==========
    'upi_transaction_count_monthly': FeatureSpec('upi_transaction_count_monthly', 'numeric', 0, 500),
    'upi_transaction_amount_monthly': FeatureSpec('upi_transaction_amount_monthly', 'numeric', 0, 5000000),
    'p2m_transaction_ratio': FeatureSpec('p2m_transaction_ratio', 'numeric', 0, 1),
    'utility_payment_ontime_ratio': FeatureSpec('utility_payment_ontime_ratio', 'numeric', 0, 1, True),
    'rent_payment_ontime_ratio': FeatureSpec('rent_payment_ontime_ratio', 'numeric', 0, 1, True),
    'phone_bill_ontime_ratio': FeatureSpec('phone_bill_ontime_ratio', 'numeric', 0, 1, True),
    'internet_bill_ontime_ratio': FeatureSpec('internet_bill_ontime_ratio', 'numeric', 0, 1, True),
    'repayment_ontime_ratio': FeatureSpec('repayment_ontime_ratio', 'numeric', 0, 1, True),
    'max_dpd_ever': FeatureSpec('max_dpd_ever', 'numeric', 0, 180, False),
    'avg_dpd': FeatureSpec('avg_dpd', 'numeric', 0, 90, False),
    'ecommerce_transaction_count': FeatureSpec('ecommerce_transaction_count', 'numeric', 0, 200),
    'ecommerce_return_rate': FeatureSpec('ecommerce_return_rate', 'numeric', 0, 1, False),
    'paid_subscription_count': FeatureSpec('paid_subscription_count', 'numeric', 0, 20, True),
    'sip_active_count': FeatureSpec('sip_active_count', 'numeric', 0, 10, True),
    'sip_monthly_amount': FeatureSpec('sip_monthly_amount', 'numeric', 0, 500000, True),
    'investment_portfolio_value': FeatureSpec('investment_portfolio_value', 'numeric', 0, 50000000, True),
    'savings_rate': FeatureSpec('savings_rate', 'numeric', 0, 1, True),
    
    # ========== CATEGORY F: FRAUD & IDENTITY STRENGTH (5%) ==========
    'face_recognition_match_score': FeatureSpec('face_recognition_match_score', 'numeric', 0, 1, True),
    'name_match_score': FeatureSpec('name_match_score', 'numeric', 0, 1, True),
    'location_mismatch_flag': FeatureSpec('location_mismatch_flag', 'binary', 0, 1, False),
    'device_anomaly_score': FeatureSpec('device_anomaly_score', 'numeric', 0, 1, False),
    'fraud_history_flag': FeatureSpec('fraud_history_flag', 'binary', 0, 1, False),
    'fraud_attempt_count': FeatureSpec('fraud_attempt_count', 'numeric', 0, 10, False),
    'income_source_verified': FeatureSpec('income_source_verified', 'binary', 0, 1, True),
    
    # ========== CATEGORY G: FAMILY & NETWORK SIGNALS (5%) ==========
    'spouse_credit_score': FeatureSpec('spouse_credit_score', 'numeric', 300, 900, True),
    'spouse_credit_available': FeatureSpec('spouse_credit_available', 'binary', 0, 1, True),
    'family_credit_score_avg': FeatureSpec('family_credit_score_avg', 'numeric', 300, 900, True),
    'family_credit_available': FeatureSpec('family_credit_available', 'binary', 0, 1, True),
    'family_financial_responsibility_score': FeatureSpec('family_financial_responsibility_score', 'numeric', 0, 1, True),
    'dependents_count': FeatureSpec('dependents_count', 'numeric', 0, 10, False),
}

# Feature to category mapping
FEATURE_CATEGORY_MAPPING = {
    'A_identity_stability_demographics': [
        'name_dob_verified', 'phone_verified', 'phone_age_months', 'email_verified', 
        'email_age_months', 'location_stability_score', 'location_tier', 
        'education_level', 'employment_tenure_months', 'employment_type'
    ],
    'B_income_cashflow': [
        'monthly_income', 'income_growth_rate', 'avg_account_balance', 'min_account_balance',
        'income_stability_score', 'income_variance_coefficient', 'itr_filed', 'itr_income_declared',
        'employability_score', 'ppf_balance', 'gov_schemes_enrolled', 'bank_statement_months_available'
    ],
    'C_assets_liabilities': [
        'current_loan_count', 'current_loan_amount', 'credit_card_count', 'credit_card_utilization',
        'credit_card_limit', 'lic_policy_count', 'lic_premium_annual', 'fd_total_amount',
        'total_assets_value', 'insurance_premium_paid_ratio', 'insurance_renewal_ontime_ratio',
        'debt_to_income_ratio'
    ],
    'D_spending_behavioral': [
        'monthly_spending', 'spending_to_income_ratio', 'essential_spending_ratio',
        'discretionary_spending_ratio', 'purchase_frequency', 'avg_purchase_value',
        'subscription_cancellation_count', 'subscription_downgrade_count', 'impatience_score',
        'impulse_buying_score', 'budgeting_score', 'financial_literacy_score',
        'recurring_payment_habit_score', 'loan_application_count_6m', 'application_rejection_rate',
        'social_media_score', 'email_response_time_score'
    ],
    'E_transactions_repayments': [
        'upi_transaction_count_monthly', 'upi_transaction_amount_monthly', 'p2m_transaction_ratio',
        'utility_payment_ontime_ratio', 'rent_payment_ontime_ratio', 'phone_bill_ontime_ratio',
        'internet_bill_ontime_ratio', 'repayment_ontime_ratio', 'max_dpd_ever', 'avg_dpd',
        'ecommerce_transaction_count', 'ecommerce_return_rate', 'paid_subscription_count',
        'sip_active_count', 'sip_monthly_amount', 'investment_portfolio_value', 'savings_rate'
    ],
    'F_fraud_identity': [
        'face_recognition_match_score', 'name_match_score', 'location_mismatch_flag',
        'device_anomaly_score', 'fraud_history_flag', 'fraud_attempt_count', 'income_source_verified'
    ],
    'G_family_network': [
        'spouse_credit_score', 'spouse_credit_available', 'family_credit_score_avg',
        'family_credit_available', 'family_financial_responsibility_score', 'dependents_count'
    ]
}


# ============================================================================
# SYNTHETIC DATA GENERATOR
# ============================================================================

class SyntheticDataGenerator:
    """
    Generates realistic synthetic credit scoring data for testing.
    
    The generator creates correlated features that mimic real-world patterns:
    - Higher income correlates with better financial metrics
    - Default probability is influenced by multiple risk factors
    - Realistic missing data patterns
    """
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        np.random.seed(seed)
        random.seed(seed)
        
        # Persona distribution in synthetic data
        self.persona_distribution = {
            'new_to_credit': 0.25,
            'gig_worker': 0.15,
            'salaried_professional': 0.35,
            'credit_experienced': 0.15,
            'mass_affluent': 0.10
        }
    
    def _generate_persona_features(self, persona: str, n: int) -> Dict[str, np.ndarray]:
        """Generate features based on persona characteristics"""
        features = {}
        
        if persona == 'new_to_credit':
            # NTC: Lower credit history, younger, less assets
            features['income_base'] = np.random.lognormal(10.5, 0.6, n)  # Lower income
            features['credit_history_months'] = np.random.uniform(0, 12, n)
            features['age_factor'] = np.random.uniform(0.3, 0.6, n)
            features['asset_factor'] = np.random.uniform(0.1, 0.4, n)
            features['default_base_prob'] = 0.15
            
        elif persona == 'gig_worker':
            # Gig: Variable income, moderate history
            features['income_base'] = np.random.lognormal(10.8, 0.8, n)  # Variable
            features['credit_history_months'] = np.random.uniform(6, 48, n)
            features['age_factor'] = np.random.uniform(0.4, 0.7, n)
            features['asset_factor'] = np.random.uniform(0.2, 0.5, n)
            features['default_base_prob'] = 0.12
            
        elif persona == 'salaried_professional':
            # Salaried: Stable income, good history
            features['income_base'] = np.random.lognormal(11.2, 0.5, n)
            features['credit_history_months'] = np.random.uniform(24, 120, n)
            features['age_factor'] = np.random.uniform(0.5, 0.8, n)
            features['asset_factor'] = np.random.uniform(0.4, 0.7, n)
            features['default_base_prob'] = 0.06
            
        elif persona == 'credit_experienced':
            # Experienced: Long history, multiple products
            features['income_base'] = np.random.lognormal(11.5, 0.5, n)
            features['credit_history_months'] = np.random.uniform(60, 240, n)
            features['age_factor'] = np.random.uniform(0.6, 0.9, n)
            features['asset_factor'] = np.random.uniform(0.5, 0.8, n)
            features['default_base_prob'] = 0.04
            
        else:  # mass_affluent
            # Affluent: High income, significant assets
            features['income_base'] = np.random.lognormal(12.5, 0.6, n)
            features['credit_history_months'] = np.random.uniform(48, 180, n)
            features['age_factor'] = np.random.uniform(0.7, 1.0, n)
            features['asset_factor'] = np.random.uniform(0.7, 1.0, n)
            features['default_base_prob'] = 0.02
            
        return features
    
    def generate(self, n_samples: int = 10000, 
                 missing_rate: float = 0.05,
                 include_timestamp: bool = True) -> pd.DataFrame:
        """
        Generate synthetic credit scoring dataset.
        
        Args:
            n_samples: Number of samples to generate
            missing_rate: Fraction of values to set as missing
            include_timestamp: Whether to include application timestamp
            
        Returns:
            DataFrame with all features and target variable
        """
        print(f"Generating {n_samples} synthetic samples...")
        
        # Assign personas based on distribution
        personas = np.random.choice(
            list(self.persona_distribution.keys()),
            size=n_samples,
            p=list(self.persona_distribution.values())
        )
        
        # Initialize data dict
        data = {'persona': personas}
        
        # Generate base factors per persona
        all_factors = {k: np.zeros(n_samples) for k in 
                      ['income_base', 'credit_history_months', 'age_factor', 'asset_factor', 'default_base_prob']}
        
        for persona in self.persona_distribution.keys():
            mask = personas == persona
            n_persona = mask.sum()
            persona_factors = self._generate_persona_features(persona, n_persona)
            for k, v in persona_factors.items():
                all_factors[k][mask] = v
        
        # ========== CATEGORY A: IDENTITY & DEMOGRAPHICS ==========
        data['name_dob_verified'] = np.random.binomial(1, 0.95, n_samples)
        data['phone_verified'] = np.random.binomial(1, 0.90, n_samples)
        data['phone_age_months'] = np.clip(all_factors['age_factor'] * 120 + np.random.normal(0, 20, n_samples), 0, 240)
        data['email_verified'] = np.random.binomial(1, 0.85, n_samples)
        data['email_age_months'] = np.clip(all_factors['age_factor'] * 100 + np.random.normal(0, 25, n_samples), 0, 240)
        data['location_stability_score'] = np.clip(all_factors['age_factor'] * 0.7 + np.random.normal(0.2, 0.15, n_samples), 0, 1)
        data['location_tier'] = np.random.choice(['tier1', 'tier2', 'tier3', 'rural'], n_samples, p=[0.3, 0.35, 0.25, 0.1])
        data['education_level'] = np.clip(np.round(all_factors['age_factor'] * 3 + np.random.normal(0.5, 1, n_samples)), 0, 5).astype(int)
        data['employment_tenure_months'] = np.clip(all_factors['credit_history_months'] * 1.5 + np.random.normal(0, 24, n_samples), 0, 480)
        data['employment_type'] = np.where(
            personas == 'gig_worker', 
            np.random.choice(['self_employed', 'contract', 'part_time'], n_samples),
            np.where(
                personas == 'salaried_professional',
                np.random.choice(['full_time', 'government'], n_samples, p=[0.85, 0.15]),
                np.random.choice(['unemployed', 'self_employed', 'contract', 'part_time', 'full_time', 'government'], 
                               n_samples, p=[0.05, 0.2, 0.15, 0.1, 0.4, 0.1])
            )
        )
        
        # ========== CATEGORY B: INCOME & CASH FLOW ==========
        data['monthly_income'] = np.clip(all_factors['income_base'], 0, 5000000)
        data['income_growth_rate'] = np.clip(np.random.normal(0.08, 0.15, n_samples), -0.5, 1.0)
        data['avg_account_balance'] = np.clip(data['monthly_income'] * np.random.uniform(1, 6, n_samples), 0, 10000000)
        data['min_account_balance'] = np.clip(data['avg_account_balance'] * np.random.uniform(0.1, 0.5, n_samples), 0, 10000000)
        
        # Income stability varies by persona
        income_stability_base = np.where(personas == 'gig_worker', 0.4, 
                                         np.where(personas == 'salaried_professional', 0.85, 0.65))
        data['income_stability_score'] = np.clip(income_stability_base + np.random.normal(0, 0.15, n_samples), 0, 1)
        data['income_variance_coefficient'] = np.clip(1 - data['income_stability_score'] + np.random.normal(0, 0.1, n_samples), 0, 2)
        
        data['itr_filed'] = np.random.binomial(1, np.where(personas == 'salaried_professional', 0.9, 0.6), n_samples)
        data['itr_income_declared'] = data['monthly_income'] * 12 * data['itr_filed'] * np.random.uniform(0.8, 1.0, n_samples)
        data['employability_score'] = np.clip(all_factors['age_factor'] * 0.6 + np.random.normal(0.3, 0.15, n_samples), 0, 1)
        data['ppf_balance'] = np.clip(all_factors['asset_factor'] * 500000 + np.random.normal(0, 100000, n_samples), 0, 5000000)
        data['gov_schemes_enrolled'] = np.clip(np.round(all_factors['asset_factor'] * 3 + np.random.normal(0, 1, n_samples)), 0, 10).astype(int)
        data['bank_statement_months_available'] = np.clip(np.random.choice([3, 6, 12, 24, 36], n_samples, p=[0.1, 0.3, 0.35, 0.15, 0.1]), 0, 36)
        
        # ========== CATEGORY C: ASSETS & LIABILITIES ==========
        data['current_loan_count'] = np.clip(np.round(np.random.poisson(2, n_samples) * (1 - all_factors['asset_factor'] + 0.5)), 0, 20).astype(int)
        data['current_loan_amount'] = np.clip(data['current_loan_count'] * data['monthly_income'] * np.random.uniform(6, 24, n_samples), 0, 50000000)
        data['credit_card_count'] = np.clip(np.round(all_factors['age_factor'] * 3 + np.random.normal(0, 1, n_samples)), 0, 10).astype(int)
        data['credit_card_utilization'] = np.clip(np.random.beta(2, 5, n_samples), 0, 1)
        data['credit_card_limit'] = np.clip(data['monthly_income'] * np.random.uniform(2, 8, n_samples), 0, 10000000)
        data['lic_policy_count'] = np.clip(np.round(all_factors['asset_factor'] * 3 + np.random.normal(0, 1, n_samples)), 0, 10).astype(int)
        data['lic_premium_annual'] = np.clip(data['lic_policy_count'] * np.random.uniform(10000, 100000, n_samples), 0, 1000000)
        data['fd_total_amount'] = np.clip(all_factors['asset_factor'] * 1000000 + np.random.normal(0, 200000, n_samples), 0, 50000000)
        data['total_assets_value'] = np.clip(
            data['fd_total_amount'] + data['ppf_balance'] + 
            all_factors['asset_factor'] * 5000000 + np.random.normal(0, 500000, n_samples), 
            0, 100000000
        )
        data['insurance_premium_paid_ratio'] = np.clip(all_factors['age_factor'] * 0.7 + np.random.normal(0.2, 0.15, n_samples), 0, 1)
        data['insurance_renewal_ontime_ratio'] = np.clip(all_factors['age_factor'] * 0.6 + np.random.normal(0.3, 0.15, n_samples), 0, 1)
        data['debt_to_income_ratio'] = np.clip(
            data['current_loan_amount'] / (data['monthly_income'] * 12 + 1) + np.random.normal(0, 0.2, n_samples), 
            0, 5
        )
        
        # ========== CATEGORY D: SPENDING & BEHAVIORAL ==========
        data['monthly_spending'] = np.clip(data['monthly_income'] * np.random.uniform(0.4, 0.9, n_samples), 0, 5000000)
        data['spending_to_income_ratio'] = data['monthly_spending'] / (data['monthly_income'] + 1)
        data['essential_spending_ratio'] = np.clip(np.random.beta(5, 3, n_samples), 0, 1)
        data['discretionary_spending_ratio'] = 1 - data['essential_spending_ratio']
        data['purchase_frequency'] = np.clip(np.random.poisson(50, n_samples), 0, 500)
        data['avg_purchase_value'] = np.clip(data['monthly_spending'] / (data['purchase_frequency'] + 1), 0, 100000)
        data['subscription_cancellation_count'] = np.clip(np.random.poisson(1, n_samples), 0, 20)
        data['subscription_downgrade_count'] = np.clip(np.random.poisson(0.5, n_samples), 0, 20)
        
        # Behavioral scores - inversely related to default risk
        data['impatience_score'] = np.clip(1 - all_factors['age_factor'] * 0.5 + np.random.normal(0, 0.2, n_samples), 0, 1)
        data['impulse_buying_score'] = np.clip(1 - all_factors['age_factor'] * 0.4 + np.random.normal(0, 0.2, n_samples), 0, 1)
        data['budgeting_score'] = np.clip(all_factors['age_factor'] * 0.6 + np.random.normal(0.2, 0.15, n_samples), 0, 1)
        data['financial_literacy_score'] = np.clip(all_factors['age_factor'] * 0.5 + np.random.normal(0.3, 0.15, n_samples), 0, 1)
        data['recurring_payment_habit_score'] = np.clip(all_factors['age_factor'] * 0.6 + np.random.normal(0.25, 0.15, n_samples), 0, 1)
        data['loan_application_count_6m'] = np.clip(np.random.poisson(1.5, n_samples), 0, 20)
        data['application_rejection_rate'] = np.clip(1 - all_factors['age_factor'] * 0.5 + np.random.normal(0, 0.2, n_samples), 0, 1)
        data['social_media_score'] = np.clip(np.random.uniform(0.3, 0.9, n_samples), 0, 1)
        data['email_response_time_score'] = np.clip(all_factors['age_factor'] * 0.5 + np.random.normal(0.3, 0.15, n_samples), 0, 1)
        
        # ========== CATEGORY E: TRANSACTIONS & REPAYMENTS ==========
        data['upi_transaction_count_monthly'] = np.clip(np.random.poisson(40, n_samples), 0, 500)
        data['upi_transaction_amount_monthly'] = np.clip(
            data['monthly_spending'] * np.random.uniform(0.3, 0.7, n_samples), 0, 5000000
        )
        data['p2m_transaction_ratio'] = np.clip(np.random.uniform(0.3, 0.8, n_samples), 0, 1)
        
        # Payment behavior - key for default prediction
        payment_discipline = all_factors['age_factor'] * 0.6 + np.random.normal(0.25, 0.15, n_samples)
        data['utility_payment_ontime_ratio'] = np.clip(payment_discipline, 0, 1)
        data['rent_payment_ontime_ratio'] = np.clip(payment_discipline + np.random.normal(0, 0.1, n_samples), 0, 1)
        data['phone_bill_ontime_ratio'] = np.clip(payment_discipline + np.random.normal(0.05, 0.1, n_samples), 0, 1)
        data['internet_bill_ontime_ratio'] = np.clip(payment_discipline + np.random.normal(0.05, 0.1, n_samples), 0, 1)
        data['repayment_ontime_ratio'] = np.clip(payment_discipline + np.random.normal(0, 0.12, n_samples), 0, 1)
        
        # DPD - inversely related to payment discipline
        data['max_dpd_ever'] = np.clip((1 - payment_discipline) * 60 + np.random.exponential(15, n_samples), 0, 180).astype(int)
        data['avg_dpd'] = np.clip(data['max_dpd_ever'] * 0.3 + np.random.normal(0, 10, n_samples), 0, 90)
        
        data['ecommerce_transaction_count'] = np.clip(np.random.poisson(15, n_samples), 0, 200)
        data['ecommerce_return_rate'] = np.clip(np.random.beta(1, 10, n_samples), 0, 1)
        data['paid_subscription_count'] = np.clip(np.round(all_factors['asset_factor'] * 5 + np.random.normal(0, 2, n_samples)), 0, 20).astype(int)
        data['sip_active_count'] = np.clip(np.round(all_factors['asset_factor'] * 3 + np.random.normal(0, 1, n_samples)), 0, 10).astype(int)
        data['sip_monthly_amount'] = np.clip(data['sip_active_count'] * data['monthly_income'] * 0.05 + np.random.normal(0, 5000, n_samples), 0, 500000)
        data['investment_portfolio_value'] = np.clip(
            data['sip_monthly_amount'] * 24 + all_factors['asset_factor'] * 500000 + np.random.normal(0, 100000, n_samples), 
            0, 50000000
        )
        data['savings_rate'] = np.clip(1 - data['spending_to_income_ratio'] + np.random.normal(0, 0.05, n_samples), 0, 1)
        
        # ========== CATEGORY F: FRAUD & IDENTITY ==========
        data['face_recognition_match_score'] = np.clip(np.random.beta(20, 2, n_samples), 0, 1)
        data['name_match_score'] = np.clip(np.random.beta(15, 2, n_samples), 0, 1)
        data['location_mismatch_flag'] = np.random.binomial(1, 0.05, n_samples)
        data['device_anomaly_score'] = np.clip(np.random.beta(1, 15, n_samples), 0, 1)
        data['fraud_history_flag'] = np.random.binomial(1, 0.02, n_samples)
        data['fraud_attempt_count'] = data['fraud_history_flag'] * np.random.poisson(1, n_samples)
        data['income_source_verified'] = np.random.binomial(1, 0.75, n_samples)
        
        # ========== CATEGORY G: FAMILY & NETWORK ==========
        data['spouse_credit_available'] = np.random.binomial(1, 0.4, n_samples)
        data['spouse_credit_score'] = np.where(
            data['spouse_credit_available'] == 1,
            np.clip(np.random.normal(680, 80, n_samples), 300, 900),
            np.nan
        )
        data['family_credit_available'] = np.random.binomial(1, 0.3, n_samples)
        data['family_credit_score_avg'] = np.where(
            data['family_credit_available'] == 1,
            np.clip(np.random.normal(650, 100, n_samples), 300, 900),
            np.nan
        )
        data['family_financial_responsibility_score'] = np.clip(np.random.beta(5, 3, n_samples), 0, 1)
        data['dependents_count'] = np.clip(np.random.poisson(1.5, n_samples), 0, 10)
        
        # ========== TARGET VARIABLE: 90 DPD DEFAULT ==========
        # Calculate default probability based on risk factors
        risk_score = (
            all_factors['default_base_prob'] +
            0.15 * (1 - data['repayment_ontime_ratio']) +
            0.10 * data['debt_to_income_ratio'] / 2 +
            0.08 * data['credit_card_utilization'] +
            0.05 * (1 - data['income_stability_score']) +
            0.05 * data['impatience_score'] +
            0.03 * data['max_dpd_ever'] / 180 +
            0.02 * data['fraud_history_flag'] +
            0.02 * data['application_rejection_rate'] +
            -0.08 * all_factors['asset_factor'] +
            -0.05 * data['budgeting_score'] +
            np.random.normal(0, 0.05, n_samples)
        )
        
        default_prob = np.clip(risk_score, 0.01, 0.50)
        data['default_90dpd'] = np.random.binomial(1, default_prob, n_samples)
        data['default_probability_true'] = default_prob  # For analysis
        
        # Add timestamp if requested
        if include_timestamp:
            base_date = datetime(2023, 1, 1)
            data['application_date'] = [
                base_date + timedelta(days=int(d)) 
                for d in np.random.uniform(0, 730, n_samples)  # 2 years of data
            ]
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Introduce missing values (more realistic)
        missing_features = [
            'ppf_balance', 'spouse_credit_score', 'family_credit_score_avg',
            'itr_income_declared', 'investment_portfolio_value', 'sip_monthly_amount',
            'lic_premium_annual', 'fd_total_amount'
        ]
        
        for feat in missing_features:
            if feat in df.columns:
                mask = np.random.random(n_samples) < missing_rate * 2  # Higher missing rate for these
                df.loc[mask, feat] = np.nan
        
        # Regular missing rate for other numeric features
        for col in df.select_dtypes(include=[np.number]).columns:
            if col not in missing_features and col not in ['default_90dpd', 'default_probability_true']:
                mask = np.random.random(n_samples) < missing_rate
                df.loc[mask, col] = np.nan
        
        print(f"Generated {len(df)} samples with {df['default_90dpd'].sum()} defaults ({df['default_90dpd'].mean()*100:.1f}%)")
        
        return df


# ============================================================================
# PREPROCESSING PIPELINE
# ============================================================================

class CreditScoringPreprocessor:
    """
    End-to-end preprocessing for credit scoring pipeline.
    
    Handles:
    - Imputation with configurable strategies
    - Outlier handling (clipping to percentiles)
    - Feature engineering (derived features)
    - Normalization using RobustScaler
    - Categorical encoding (LabelEncoder for LightGBM)
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.feature_schema = FEATURE_SCHEMA
        self.feature_bounds = {}
        self.scalers = {}
        self.encoders = {}
        self.imputers = {}
        self.fitted = False
        
        # Load config if provided
        if config_path:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = None
    
    def _get_feature_list(self) -> List[str]:
        """Get list of all feature names"""
        return list(self.feature_schema.keys())
    
    def _get_numeric_features(self) -> List[str]:
        """Get list of numeric feature names"""
        return [f for f, spec in self.feature_schema.items() 
                if spec.dtype in ['numeric', 'binary', 'ordinal']]
    
    def _get_categorical_features(self) -> List[str]:
        """Get list of categorical feature names"""
        return [f for f, spec in self.feature_schema.items() if spec.dtype == 'categorical']
    
    def _clip_outliers(self, df: pd.DataFrame, lower_pct: float = 1, upper_pct: float = 99) -> pd.DataFrame:
        """Clip outliers using percentile bounds"""
        df = df.copy()
        
        for col in self._get_numeric_features():
            if col in df.columns and df[col].notna().sum() > 0:
                spec = self.feature_schema[col]
                
                if not self.fitted:
                    # Compute bounds from data during fitting
                    lower = max(df[col].quantile(lower_pct/100), spec.min_val or -np.inf)
                    upper = min(df[col].quantile(upper_pct/100), spec.max_val or np.inf)
                    self.feature_bounds[col] = {'lower': lower, 'upper': upper}
                else:
                    lower = self.feature_bounds.get(col, {}).get('lower', spec.min_val or -np.inf)
                    upper = self.feature_bounds.get(col, {}).get('upper', spec.max_val or np.inf)
                
                df[col] = df[col].clip(lower=lower, upper=upper)
        
        return df
    
    def _impute_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        """Impute missing values with appropriate strategies"""
        df = df.copy()
        
        # Numeric features: median imputation
        numeric_cols = [c for c in self._get_numeric_features() if c in df.columns]
        
        if not self.fitted:
            self.imputers['numeric'] = SimpleImputer(strategy='median')
            if numeric_cols:
                df[numeric_cols] = self.imputers['numeric'].fit_transform(df[numeric_cols])
        else:
            if numeric_cols and 'numeric' in self.imputers:
                df[numeric_cols] = self.imputers['numeric'].transform(df[numeric_cols])
        
        # Categorical features: mode imputation
        for col in self._get_categorical_features():
            if col in df.columns:
                if not self.fitted:
                    mode_val = df[col].mode()[0] if not df[col].mode().empty else df[col].dropna().iloc[0] if len(df[col].dropna()) > 0 else 'unknown'
                    self.imputers[col] = mode_val
                    df[col] = df[col].fillna(mode_val)
                else:
                    df[col] = df[col].fillna(self.imputers.get(col, 'unknown'))
        
        return df
    
    def _encode_categoricals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical features for LightGBM"""
        df = df.copy()
        
        for col in self._get_categorical_features():
            if col in df.columns:
                if not self.fitted:
                    self.encoders[col] = LabelEncoder()
                    # Fit with all known categories plus 'unknown'
                    spec = self.feature_schema[col]
                    all_categories = list(spec.categories or []) + ['unknown']
                    self.encoders[col].fit(all_categories)
                
                # Transform, handling unseen categories
                df[col] = df[col].apply(
                    lambda x: x if x in self.encoders[col].classes_ else 'unknown'
                )
                df[col] = self.encoders[col].transform(df[col])
        
        return df
    
    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create derived features"""
        df = df.copy()
        
        # Ratio features
        if 'monthly_income' in df.columns and 'monthly_spending' in df.columns:
            df['savings_amount'] = df['monthly_income'] - df['monthly_spending']
        
        if 'avg_account_balance' in df.columns and 'monthly_income' in df.columns:
            df['balance_income_ratio'] = df['avg_account_balance'] / (df['monthly_income'] + 1)
        
        if 'total_assets_value' in df.columns and 'current_loan_amount' in df.columns:
            df['net_worth'] = df['total_assets_value'] - df['current_loan_amount']
            df['leverage_ratio'] = df['current_loan_amount'] / (df['total_assets_value'] + 1)
        
        # Payment behavior composite
        payment_cols = ['utility_payment_ontime_ratio', 'rent_payment_ontime_ratio', 
                        'phone_bill_ontime_ratio', 'internet_bill_ontime_ratio', 
                        'repayment_ontime_ratio']
        available_payment_cols = [c for c in payment_cols if c in df.columns]
        if available_payment_cols:
            df['payment_discipline_score'] = df[available_payment_cols].mean(axis=1)
        
        # Risk flags composite
        risk_cols = ['fraud_history_flag', 'location_mismatch_flag']
        available_risk_cols = [c for c in risk_cols if c in df.columns]
        if available_risk_cols:
            df['fraud_risk_composite'] = df[available_risk_cols].sum(axis=1)
        
        # Credit utilization stress
        if 'credit_card_utilization' in df.columns and 'debt_to_income_ratio' in df.columns:
            df['credit_stress_score'] = (df['credit_card_utilization'] + df['debt_to_income_ratio'] / 5) / 2
        
        return df
    
    def _normalize_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize numeric features using RobustScaler"""
        df = df.copy()
        
        # Use RobustScaler for better handling of outliers
        numeric_cols = [c for c in self._get_numeric_features() if c in df.columns]
        
        # Exclude binary and ordinal features from scaling
        scale_cols = [c for c in numeric_cols 
                     if self.feature_schema.get(c, FeatureSpec(c, 'numeric')).dtype == 'numeric']
        
        if not self.fitted:
            self.scalers['robust'] = RobustScaler()
            if scale_cols:
                df[scale_cols] = self.scalers['robust'].fit_transform(df[scale_cols])
        else:
            if scale_cols and 'robust' in self.scalers:
                df[scale_cols] = self.scalers['robust'].transform(df[scale_cols])
        
        return df
    
    def fit_transform(self, df: pd.DataFrame, normalize: bool = False) -> pd.DataFrame:
        """
        Fit preprocessor on training data and transform.
        
        Args:
            df: Training DataFrame
            normalize: Whether to apply normalization (skip for tree models)
            
        Returns:
            Preprocessed DataFrame
        """
        self.fitted = False
        
        # Step 1: Clip outliers
        df = self._clip_outliers(df)
        
        # Step 2: Impute missing values
        df = self._impute_missing(df)
        
        # Step 3: Encode categoricals
        df = self._encode_categoricals(df)
        
        # Step 4: Engineer derived features
        df = self._engineer_features(df)
        
        # Step 5: Normalize (optional, usually skip for tree models)
        if normalize:
            df = self._normalize_features(df)
        
        self.fitted = True
        return df
    
    def transform(self, df: pd.DataFrame, normalize: bool = False) -> pd.DataFrame:
        """
        Transform new data using fitted preprocessor.
        
        Args:
            df: New DataFrame to transform
            normalize: Whether to apply normalization
            
        Returns:
            Preprocessed DataFrame
        """
        if not self.fitted:
            raise ValueError("Preprocessor must be fitted before transform. Call fit_transform first.")
        
        df = self._clip_outliers(df)
        df = self._impute_missing(df)
        df = self._encode_categoricals(df)
        df = self._engineer_features(df)
        
        if normalize:
            df = self._normalize_features(df)
        
        return df
    
    def get_feature_bounds(self) -> Dict[str, Dict[str, float]]:
        """Get fitted feature bounds for normalization"""
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
# TRAIN/VALIDATION/TEST SPLIT
# ============================================================================

def create_splits(df: pd.DataFrame, 
                  target_col: str = 'default_90dpd',
                  timestamp_col: Optional[str] = 'application_date',
                  test_size: float = 0.15,
                  val_size: float = 0.15,
                  random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Create train/validation/test splits with time-awareness.
    
    If timestamp column exists, uses time-based split.
    Otherwise, uses stratified random split.
    
    Args:
        df: Full dataset
        target_col: Name of target column
        timestamp_col: Name of timestamp column (optional)
        test_size: Fraction for test set
        val_size: Fraction for validation set
        random_state: Random seed
        
    Returns:
        Tuple of (train_df, val_df, test_df)
    """
    print(f"Creating data splits (test={test_size}, val={val_size})...")
    
    if timestamp_col and timestamp_col in df.columns:
        # Time-based split
        df_sorted = df.sort_values(timestamp_col).reset_index(drop=True)
        n = len(df_sorted)
        
        test_idx = int(n * (1 - test_size))
        val_idx = int(test_idx * (1 - val_size / (1 - test_size)))
        
        train_df = df_sorted.iloc[:val_idx].copy()
        val_df = df_sorted.iloc[val_idx:test_idx].copy()
        test_df = df_sorted.iloc[test_idx:].copy()
        
        print(f"Time-based split:")
        print(f"  Train: {len(train_df)} samples ({train_df[target_col].mean()*100:.1f}% default rate)")
        print(f"  Val: {len(val_df)} samples ({val_df[target_col].mean()*100:.1f}% default rate)")
        print(f"  Test: {len(test_df)} samples ({test_df[target_col].mean()*100:.1f}% default rate)")
        
    else:
        # Stratified random split
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
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Example usage
    print("=" * 60)
    print("CREDIT SCORING DATA PREPARATION")
    print("=" * 60)
    
    # Generate synthetic data
    generator = SyntheticDataGenerator(seed=42)
    df = generator.generate(n_samples=10000, missing_rate=0.05)
    
    print(f"\nDataset shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()[:10]}... ({len(df.columns)} total)")
    
    # Create splits
    train_df, val_df, test_df = create_splits(df, timestamp_col='application_date')
    
    # Preprocess
    preprocessor = CreditScoringPreprocessor()
    train_processed = preprocessor.fit_transform(train_df)
    val_processed = preprocessor.transform(val_df)
    test_processed = preprocessor.transform(test_df)
    
    print(f"\nProcessed dataset shapes:")
    print(f"  Train: {train_processed.shape}")
    print(f"  Val: {val_processed.shape}")
    print(f"  Test: {test_processed.shape}")
    
    # Save preprocessor
    preprocessor.save("preprocessor.joblib")
    
    print("\nData preparation complete!")


