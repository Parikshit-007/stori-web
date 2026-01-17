"""
Consumer Credit Scoring - Comprehensive Synthetic Data Generator
=================================================================

Generates realistic synthetic consumer credit data with:
- All 30+ parameters with proper correlations
- Edge cases and boundary scenarios
- Realistic behavioral patterns
- 360-degree coverage

Author: ML Engineering Team
Version: 1.0.0
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random


class ConsumerSyntheticDataGenerator:
    """
    Generates comprehensive synthetic consumer credit data.
    
    Scenarios covered:
    1. Perfect consumer - Excellent score (80-100)
    2. Good consumer - Good score (65-79)
    3. Average consumer - Fair score (50-64)
    4. Struggling consumer - Poor score (35-49)
    5. High-risk consumer - Very Poor score (0-34)
    6. Young professional - Just started career
    7. Established professional - Stable income
    8. Freelancer - Variable income
    9. Business owner - High income, high risk
    10. Student - Low income, high potential
    11. Fraudster - Synthetic ID, manipulation
    12. Defaulter - History of defaults
    """
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        np.random.seed(seed)
        random.seed(seed)
        
        # Consumer segment distribution
        self.segment_distribution = {
            'perfect_consumer': 0.10,          # 10% - Score 80-100
            'good_consumer': 0.25,             # 25% - Score 65-79
            'average_consumer': 0.35,          # 35% - Score 50-64
            'struggling_consumer': 0.20,       # 20% - Score 35-49
            'high_risk_consumer': 0.10         # 10% - Score 0-34
        }
        
        # Age distribution
        self.age_distribution = {
            'gen_z': 0.15,                     # 18-25
            'young_millennial': 0.25,          # 26-32
            'millennial': 0.30,                # 33-40
            'gen_x': 0.20,                     # 41-55
            'boomer': 0.10                     # 56+
        }
        
        # Employment type distribution
        self.employment_distribution = {
            'salaried_private': 0.40,
            'salaried_government': 0.15,
            'self_employed': 0.20,
            'business_owner': 0.10,
            'freelancer': 0.10,
            'student': 0.05
        }
    
    def _generate_segment_base_features(self, segment: str, n: int) -> Dict:
        """Generate base features for a consumer segment"""
        
        segment_params = {
            'perfect_consumer': {
                'income_base': (50000, 150000),
                'stability_factor': (0.85, 0.95),
                'discipline_factor': (0.90, 0.98),
                'fraud_risk': (0.0, 0.05),
                'default_base_prob': 0.01
            },
            'good_consumer': {
                'income_base': (30000, 80000),
                'stability_factor': (0.70, 0.85),
                'discipline_factor': (0.75, 0.90),
                'fraud_risk': (0.0, 0.10),
                'default_base_prob': 0.03
            },
            'average_consumer': {
                'income_base': (20000, 50000),
                'stability_factor': (0.50, 0.70),
                'discipline_factor': (0.60, 0.75),
                'fraud_risk': (0.05, 0.15),
                'default_base_prob': 0.07
            },
            'struggling_consumer': {
                'income_base': (15000, 35000),
                'stability_factor': (0.30, 0.50),
                'discipline_factor': (0.40, 0.60),
                'fraud_risk': (0.10, 0.25),
                'default_base_prob': 0.15
            },
            'high_risk_consumer': {
                'income_base': (10000, 25000),
                'stability_factor': (0.10, 0.30),
                'discipline_factor': (0.20, 0.40),
                'fraud_risk': (0.20, 0.50),
                'default_base_prob': 0.30
            }
        }
        
        params = segment_params.get(segment, segment_params['average_consumer'])
        
        return {
            'income_monthly': np.random.uniform(params['income_base'][0], params['income_base'][1], n),
            'stability_factor': np.random.uniform(params['stability_factor'][0], params['stability_factor'][1], n),
            'discipline_factor': np.random.uniform(params['discipline_factor'][0], params['discipline_factor'][1], n),
            'fraud_risk': np.random.uniform(params['fraud_risk'][0], params['fraud_risk'][1], n),
            'default_base_prob': params['default_base_prob']
        }
    
    def generate(self, n_samples: int = 10000, include_edge_cases: bool = True) -> pd.DataFrame:
        """
        Generate comprehensive synthetic consumer dataset.
        
        Args:
            n_samples: Number of samples to generate
            include_edge_cases: Whether to include edge case scenarios
            
        Returns:
            DataFrame with all consumer features
        """
        print(f"Generating {n_samples} synthetic consumer credit profiles...")
        
        # Assign segments
        segments = np.random.choice(
            list(self.segment_distribution.keys()),
            size=n_samples,
            p=list(self.segment_distribution.values())
        )
        
        data = {'consumer_segment': segments}
        
        # Generate base factors
        all_factors = {
            k: np.zeros(n_samples)
            for k in ['income_monthly', 'stability_factor', 'discipline_factor', 'fraud_risk', 'default_base_prob']
        }
        
        for segment in self.segment_distribution.keys():
            mask = segments == segment
            n_seg = mask.sum()
            if n_seg > 0:
                seg_factors = self._generate_segment_base_features(segment, n_seg)
                for k, v in seg_factors.items():
                    all_factors[k][mask] = v
        
        # ========== CATEGORY A: IDENTITY & VERIFICATION (7%) ==========
        
        # Name & DOB verification (1%)
        data['name_dob_verified'] = np.random.binomial(1, 1 - all_factors['fraud_risk'], n_samples)
        data['age'] = np.clip(np.random.normal(35, 12, n_samples), 18, 75).astype(int)
        
        # Phone number verification (1.5%)
        data['phone_number_verified'] = np.random.binomial(1, 1 - all_factors['fraud_risk'] * 0.8, n_samples)
        data['phone_number_tenure_months'] = np.clip(
            all_factors['discipline_factor'] * 60 + np.random.normal(0, 12, n_samples), 1, 120
        )
        
        # Email verification (1%)
        data['email_verified'] = np.random.binomial(1, 1 - all_factors['fraud_risk'] * 0.7, n_samples)
        data['email_tenure_months'] = np.clip(
            all_factors['discipline_factor'] * 80 + np.random.normal(0, 15, n_samples), 1, 150
        )
        
        # Education level (1.5%)
        education_scores = {
            'no_formal_education': 0.2,
            'primary_school': 0.3,
            'high_school': 0.5,
            'diploma': 0.6,
            'undergraduate': 0.8,
            'postgraduate': 0.9,
            'phd': 1.0
        }
        education_levels = list(education_scores.keys())
        education_probs = [0.02, 0.05, 0.15, 0.20, 0.40, 0.15, 0.03]
        data['education_level'] = np.random.choice(education_levels, n_samples, p=education_probs)
        data['education_score'] = np.array([education_scores[e] for e in data['education_level']])
        
        # Identity matching (2%)
        data['identity_matching'] = np.clip(
            (1 - all_factors['fraud_risk']) * all_factors['discipline_factor'] + np.random.normal(0, 0.1, n_samples),
            0, 1
        )
        
        # ========== CATEGORY B: EMPLOYMENT & INCOME (14%) ==========
        
        # Employment history (3%)
        employment_types = list(self.employment_distribution.keys())
        employment_probs = list(self.employment_distribution.values())
        data['employment_type'] = np.random.choice(employment_types, n_samples, p=employment_probs)
        data['employment_tenure_months'] = np.clip(
            all_factors['stability_factor'] * 60 + np.random.exponential(24, n_samples), 1, 360
        )
        data['employment_changes_last_5yr'] = np.clip(
            np.round((1 - all_factors['stability_factor']) * 5 + np.random.poisson(1, n_samples)), 0, 10
        ).astype(int)
        data['employment_history_score'] = np.clip(
            all_factors['stability_factor'] * (data['employment_tenure_months'] / 60) + np.random.normal(0, 0.1, n_samples),
            0, 1
        )
        
        # Monthly income stability (5%)
        data['monthly_income'] = all_factors['income_monthly']
        data['income_cv'] = np.clip(
            (1 - all_factors['stability_factor']) * 0.5 + np.random.exponential(0.1, n_samples), 0.05, 1.0
        )
        data['income_trend'] = np.clip(
            all_factors['stability_factor'] * 0.1 + np.random.normal(0, 0.05, n_samples), -0.2, 0.3
        )
        data['monthly_income_stability'] = np.clip(
            all_factors['stability_factor'] + np.random.normal(0, 0.1, n_samples), 0, 1
        )
        
        # Income source verification (3%)
        data['income_source_verified'] = np.random.binomial(1, all_factors['discipline_factor'], n_samples)
        data['income_source_type'] = np.random.choice(
            ['salary', 'business', 'freelance', 'investments', 'other'],
            n_samples,
            p=[0.50, 0.20, 0.15, 0.10, 0.05]
        )
        data['income_source_verification'] = np.clip(
            data['income_source_verified'] * all_factors['discipline_factor'] + np.random.normal(0, 0.1, n_samples),
            0, 1
        )
        
        # Regular P2P UPI transactions (3%)
        data['p2p_upi_transaction_count'] = np.clip(
            np.round(all_factors['discipline_factor'] * 30 + np.random.poisson(10, n_samples)), 0, 100
        ).astype(int)
        data['p2p_upi_regularity_score'] = np.clip(
            (data['p2p_upi_transaction_count'] / 30) + np.random.normal(0, 0.1, n_samples), 0, 1
        )
        data['regular_p2p_upi_transactions'] = data['p2p_upi_regularity_score']
        
        # ========== CATEGORY C: CASH FLOW & BANKING (24%) ==========
        
        # Average account balance (4%)
        data['avg_account_balance'] = np.clip(
            data['monthly_income'] * np.random.uniform(0.5, 3.0, n_samples) * all_factors['discipline_factor'],
            5000, 5000000
        )
        data['account_balance_trend'] = np.clip(
            all_factors['stability_factor'] * 0.1 + np.random.normal(0, 0.05, n_samples), -0.3, 0.3
        )
        
        # Monthly outflow burden (4%)
        data['total_monthly_outflow'] = np.clip(
            data['monthly_income'] * np.random.uniform(0.6, 1.2, n_samples) * (1 - all_factors['discipline_factor'] * 0.3),
            10000, data['monthly_income'] * 1.5
        )
        data['monthly_outflow_burden'] = data['total_monthly_outflow'] / (data['monthly_income'] + 1)
        
        # Survivability months (4%)
        monthly_expenses = data['total_monthly_outflow']
        data['survivability_months'] = np.clip(
            data['avg_account_balance'] / (monthly_expenses + 1), 0, 24
        )
        
        # Income retention ratio (4%)
        data['income_retention_ratio'] = np.clip(
            1 - (data['total_monthly_outflow'] / (data['monthly_income'] + 1)),
            -0.2, 0.5
        )
        
        # Expense rigidity (3%)
        fixed_expenses = data['total_monthly_outflow'] * np.random.uniform(0.4, 0.8, n_samples)
        data['expense_rigidity'] = fixed_expenses / (data['total_monthly_outflow'] + 1)
        
        # Inflow time consistency (2%)
        data['inflow_consistency_cv'] = np.clip(
            (1 - all_factors['stability_factor']) * 0.5 + np.random.exponential(0.15, n_samples), 0, 1
        )
        data['inflow_time_consistency'] = np.clip(
            1 - data['inflow_consistency_cv'] + np.random.normal(0, 0.1, n_samples), 0, 1
        )
        
        # EMI to monthly UPI amount (4%)
        data['monthly_upi_amount'] = data['monthly_income'] * np.random.uniform(0.5, 1.5, n_samples)
        data['total_emi'] = data['monthly_income'] * np.random.uniform(0, 0.5, n_samples) * (1 - all_factors['discipline_factor'] * 0.3)
        data['emi_to_monthly_upi_amount'] = data['total_emi'] / (data['monthly_upi_amount'] + 1)
        
        # ========== CATEGORY D: FINANCIAL ASSETS & INSURANCE (9%) ==========
        
        # Total financial assets (6%)
        data['total_financial_assets'] = np.clip(
            data['monthly_income'] * np.random.uniform(5, 50, n_samples) * all_factors['discipline_factor'],
            0, 10000000
        )
        data['liquid_assets'] = data['total_financial_assets'] * np.random.uniform(0.2, 0.6, n_samples)
        data['investments'] = data['total_financial_assets'] * np.random.uniform(0.3, 0.7, n_samples)
        
        # Insurance coverage (3%)
        data['has_insurance'] = np.random.binomial(1, all_factors['discipline_factor'] * 0.7, n_samples)
        data['insurance_count'] = np.where(
            data['has_insurance'],
            np.random.randint(1, 4, n_samples),
            0
        )
        data['insurance_coverage'] = np.clip(
            data['has_insurance'] * (data['insurance_count'] / 3) + np.random.normal(0, 0.1, n_samples),
            0, 1
        )
        
        # ========== CATEGORY E: DEBT BURDEN (11%) ==========
        
        # EMI to income ratio (4%)
        data['emi_to_income_ratio'] = data['total_emi'] / (data['monthly_income'] + 1)
        
        # Rent to income ratio (2%)
        data['monthly_rent'] = np.where(
            np.random.random(n_samples) < 0.6,  # 60% pay rent
            data['monthly_income'] * np.random.uniform(0.15, 0.35, n_samples),
            0
        )
        data['rent_to_income_ratio'] = data['monthly_rent'] / (data['monthly_income'] + 1)
        
        # Utility to income ratio (2%)
        data['monthly_utility'] = data['monthly_income'] * np.random.uniform(0.05, 0.15, n_samples)
        data['utility_to_income_ratio'] = data['monthly_utility'] / (data['monthly_income'] + 1)
        
        # Insurance payment discipline (3%)
        data['insurance_payment_ontime_ratio'] = np.where(
            data['has_insurance'],
            np.clip(all_factors['discipline_factor'] + np.random.normal(0, 0.15, n_samples), 0, 1),
            0.5
        )
        data['insurance_payment_discipline'] = data['insurance_payment_ontime_ratio']
        
        # ========== CATEGORY F: BEHAVIORAL PATTERNS (17%) ==========
        
        # Spending personality (3%)
        spending_personalities = ['conservative_spender', 'planned_spender', 'impulsive_spender',
                                 'luxury_seeker', 'value_hunter', 'balanced_spender']
        spending_scores = {
            'conservative_spender': 0.9,
            'planned_spender': 0.85,
            'balanced_spender': 0.75,
            'value_hunter': 0.70,
            'impulsive_spender': 0.4,
            'luxury_seeker': 0.3
        }
        # Assign based on discipline factor
        personality_probs = np.zeros((n_samples, len(spending_personalities)))
        for i, personality in enumerate(spending_personalities):
            if personality in ['conservative_spender', 'planned_spender', 'balanced_spender']:
                personality_probs[:, i] = all_factors['discipline_factor']
            else:
                personality_probs[:, i] = 1 - all_factors['discipline_factor']
        personality_probs /= personality_probs.sum(axis=1, keepdims=True)
        
        data['spending_personality'] = np.array([
            np.random.choice(spending_personalities, p=personality_probs[i])
            for i in range(n_samples)
        ])
        data['spending_personality_score'] = np.array([
            spending_scores[p] for p in data['spending_personality']
        ])
        
        # Spending discipline index (4%)
        data['impulse_purchase_ratio'] = np.clip(
            (1 - all_factors['discipline_factor']) * 0.5 + np.random.exponential(0.1, n_samples), 0, 1
        )
        data['budget_adherence'] = np.clip(
            all_factors['discipline_factor'] + np.random.normal(0, 0.15, n_samples), 0, 1
        )
        data['spending_discipline_index'] = np.clip(
            0.6 * data['budget_adherence'] + 0.4 * (1 - data['impulse_purchase_ratio']),
            0, 1
        )
        
        # Bill payment discipline (5%)
        data['bill_payment_ontime_ratio'] = np.clip(
            all_factors['discipline_factor'] + np.random.normal(0, 0.15, n_samples), 0, 1
        )
        data['bill_payment_delays_count'] = np.clip(
            np.round((1 - all_factors['discipline_factor']) * 6 + np.random.poisson(1, n_samples)), 0, 12
        ).astype(int)
        data['bill_payment_discipline'] = data['bill_payment_ontime_ratio']
        
        # Late-night payment behaviour (3%)
        data['late_night_transaction_ratio'] = np.clip(
            (1 - all_factors['discipline_factor']) * 0.3 + np.random.exponential(0.1, n_samples), 0, 0.5
        )
        data['late_night_payment_behaviour'] = np.clip(
            1 - data['late_night_transaction_ratio'] * 2 + np.random.normal(0, 0.1, n_samples), 0, 1
        )
        
        # Utility payment consistency (2%)
        data['utility_payment_ontime_ratio'] = np.clip(
            all_factors['discipline_factor'] + np.random.normal(0, 0.15, n_samples), 0, 1
        )
        data['utility_payment_consistency'] = data['utility_payment_ontime_ratio']
        
        # ========== CATEGORY G: RISK & FRAUD (18%) ==========
        
        # Risk appetite (3%)
        risk_appetite_levels = ['very_low', 'low', 'moderate', 'high', 'very_high']
        risk_scores = {'very_low': 0.9, 'low': 0.8, 'moderate': 0.6, 'high': 0.4, 'very_high': 0.2}
        risk_appetite_probs = [0.15, 0.25, 0.35, 0.20, 0.05]
        data['risk_appetite'] = np.random.choice(risk_appetite_levels, n_samples, p=risk_appetite_probs)
        data['risk_appetite_score'] = np.array([risk_scores[r] for r in data['risk_appetite']])
        
        # Pin code risk (2%)
        location_types = ['metro', 'tier_1', 'tier_2', 'tier_3', 'rural']
        location_risk_scores = {'metro': 0.9, 'tier_1': 0.8, 'tier_2': 0.6, 'tier_3': 0.4, 'rural': 0.2}
        location_probs = [0.30, 0.25, 0.20, 0.15, 0.10]
        data['location_type'] = np.random.choice(location_types, n_samples, p=location_probs)
        data['pin_code_risk_score'] = np.array([location_risk_scores[l] for l in data['location_type']])
        
        # Bank statement manipulation (4%)
        data['statement_tampering_detected'] = np.random.binomial(1, all_factors['fraud_risk'], n_samples)
        data['transaction_pattern_anomaly'] = np.clip(
            all_factors['fraud_risk'] + np.random.exponential(0.1, n_samples), 0, 1
        )
        data['bank_statement_manipulation'] = np.clip(
            0.5 * data['statement_tampering_detected'] + 0.5 * data['transaction_pattern_anomaly'],
            0, 1
        )
        
        # Synthetic ID risk (4%)
        data['digital_footprint_age_days'] = np.clip(
            (1 - all_factors['fraud_risk']) * 1000 + np.random.exponential(500, n_samples), 30, 5000
        )
        data['cross_platform_consistency'] = np.clip(
            (1 - all_factors['fraud_risk']) + np.random.normal(0, 0.15, n_samples), 0, 1
        )
        data['device_fingerprint_changes'] = np.clip(
            np.round(all_factors['fraud_risk'] * 10 + np.random.poisson(2, n_samples)), 0, 20
        ).astype(int)
        data['synthetic_id_risk'] = np.clip(
            all_factors['fraud_risk'] * 0.5 + (1 - data['cross_platform_consistency']) * 0.3 +
            (data['device_fingerprint_changes'] / 20) * 0.2,
            0, 1
        )
        
        # ========== TARGET VARIABLE: DEFAULT PROBABILITY ==========
        
        # Calculate risk score from all factors
        risk_score = all_factors['default_base_prob'].copy()
        
        # Risk increasing factors
        risk_score += 0.15 * (1 - data['bill_payment_discipline'])
        risk_score += 0.12 * data['emi_to_income_ratio'].clip(0, 0.6)
        risk_score += 0.10 * (1 - data['monthly_income_stability'])
        risk_score += 0.08 * (1 - data['employment_history_score'])
        risk_score += 0.10 * data['bank_statement_manipulation']
        risk_score += 0.10 * data['synthetic_id_risk']
        risk_score += 0.05 * data['monthly_outflow_burden'].clip(0, 1.5)
        
        # Risk reducing factors
        risk_score -= 0.12 * data['spending_discipline_index']
        risk_score -= 0.10 * (data['survivability_months'] / 12).clip(0, 1)
        risk_score -= 0.08 * data['income_retention_ratio'].clip(0, 0.4)
        risk_score -= 0.08 * data['identity_matching']
        risk_score -= 0.06 * data['education_score']
        risk_score -= 0.05 * (np.log1p(data['total_financial_assets']) / 15).clip(0, 1)
        
        # Add noise and clip
        default_prob = np.clip(risk_score + np.random.normal(0, 0.02, n_samples), 0.005, 0.50)
        
        data['default_90dpd'] = np.random.binomial(1, default_prob, n_samples)
        data['default_probability_true'] = default_prob
        
        # Add timestamp
        base_date = datetime(2023, 1, 1)
        data['application_date'] = [
            base_date + timedelta(days=int(d))
            for d in np.random.uniform(0, 730, n_samples)
        ]
        
        df = pd.DataFrame(data)
        
        # Add edge cases if requested
        if include_edge_cases:
            edge_df = self._generate_edge_cases()
            df = pd.concat([df, edge_df], ignore_index=True)
            df = df.sample(frac=1, random_state=self.seed).reset_index(drop=True)
        
        print(f"Generated {len(df)} consumer profiles with {df['default_90dpd'].sum()} defaults ({df['default_90dpd'].mean()*100:.1f}%)")
        print(f"Segments: {df['consumer_segment'].value_counts().to_dict()}")
        
        return df
    
    def _generate_edge_cases(self, n_each: int = 100) -> pd.DataFrame:
        """Generate specific edge case scenarios"""
        
        edge_cases = []
        
        # 1. Perfect Consumer - Score 90-100
        for _ in range(n_each):
            perfect = {
                'consumer_segment': 'perfect_consumer',
                'age': np.random.randint(30, 45),
                'monthly_income': np.random.uniform(80000, 200000),
                'employment_history_score': np.random.uniform(0.90, 1.0),
                'monthly_income_stability': np.random.uniform(0.90, 1.0),
                'bill_payment_discipline': np.random.uniform(0.95, 1.0),
                'spending_discipline_index': np.random.uniform(0.85, 0.95),
                'identity_matching': np.random.uniform(0.95, 1.0),
                'default_90dpd': 0,
                'default_probability_true': np.random.uniform(0.005, 0.02)
            }
            edge_cases.append(perfect)
        
        # 2. Fraudster - Score 0-20
        for _ in range(n_each):
            fraudster = {
                'consumer_segment': 'high_risk_consumer',
                'age': np.random.randint(22, 35),
                'monthly_income': np.random.uniform(15000, 40000),
                'employment_history_score': np.random.uniform(0.1, 0.3),
                'bank_statement_manipulation': np.random.uniform(0.7, 1.0),
                'synthetic_id_risk': np.random.uniform(0.7, 1.0),
                'identity_matching': np.random.uniform(0.0, 0.3),
                'bill_payment_discipline': np.random.uniform(0.1, 0.4),
                'default_90dpd': 1,
                'default_probability_true': np.random.uniform(0.30, 0.50)
            }
            edge_cases.append(fraudster)
        
        # 3. Young Professional - Score 60-70
        for _ in range(n_each):
            young_prof = {
                'consumer_segment': 'average_consumer',
                'age': np.random.randint(24, 30),
                'monthly_income': np.random.uniform(40000, 70000),
                'employment_history_score': np.random.uniform(0.5, 0.7),
                'monthly_income_stability': np.random.uniform(0.7, 0.85),
                'education_score': np.random.uniform(0.8, 1.0),
                'bill_payment_discipline': np.random.uniform(0.75, 0.90),
                'default_90dpd': np.random.choice([0, 1], p=[0.93, 0.07]),
                'default_probability_true': np.random.uniform(0.05, 0.10)
            }
            edge_cases.append(young_prof)
        
        # Fill remaining required fields with defaults
        df_edge = pd.DataFrame(edge_cases)
        
        # Fill missing columns with reasonable defaults
        all_cols = set([
            'name_dob_verified', 'phone_number_verified', 'email_verified', 'education_level',
            'employment_type', 'avg_account_balance', 'total_monthly_outflow', 'survivability_months',
            'income_retention_ratio', 'expense_rigidity', 'inflow_time_consistency',
            'emi_to_monthly_upi_amount', 'total_financial_assets', 'insurance_coverage',
            'emi_to_income_ratio', 'rent_to_income_ratio', 'utility_to_income_ratio',
            'insurance_payment_discipline', 'spending_personality_score', 'late_night_payment_behaviour',
            'utility_payment_consistency', 'risk_appetite_score', 'pin_code_risk_score',
            'application_date'
        ])
        
        for col in all_cols:
            if col not in df_edge.columns:
                if col.endswith('_score') or col.endswith('_ratio') or col.endswith('_discipline'):
                    df_edge[col] = np.random.uniform(0.3, 0.7, len(df_edge))
                elif col == 'application_date':
                    df_edge[col] = datetime(2023, 6, 1)
                elif col.endswith('_verified'):
                    df_edge[col] = np.random.choice([0, 1], len(df_edge))
                else:
                    df_edge[col] = 0
        
        return df_edge


if __name__ == "__main__":
    generator = ConsumerSyntheticDataGenerator(seed=42)
    df = generator.generate(n_samples=10000, include_edge_cases=True)
    
    print("\n=== Dataset Summary ===")
    print(df.info())
    print("\n=== Sample Data ===")
    print(df.head())
    print("\n=== Default Rate by Segment ===")
    print(df.groupby('consumer_segment')['default_90dpd'].agg(['count', 'mean']))


