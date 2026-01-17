"""Synthetic data generator for MSME credit scoring"""

import numpy as np
import pandas as pd
from typing import Dict, Optional
import random


class MSMESyntheticDataGenerator:
    """
    Generates realistic synthetic MSME credit scoring data for testing.
    
    Creates correlated features that mimic real-world business patterns:
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
        
        # Industry risk mapping
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
        
        # Segment-based default rates (realistic: 2-12%)
        self.segment_default_rates = {
            'micro_new': 0.12,
            'micro_established': 0.06,
            'small_trading': 0.05,
            'small_manufacturing': 0.04,
            'small_services': 0.05,
            'medium_enterprise': 0.02
        }
    
    def generate(self, n_samples: int = 10000, default_rate: Optional[float] = None) -> pd.DataFrame:
        """
        Generate synthetic MSME dataset
        
        Args:
            n_samples: Number of samples to generate
            default_rate: Overall default rate (if None, uses segment-based rates)
            
        Returns:
            DataFrame with all features and target variable
        """
        print(f"Generating {n_samples} synthetic MSME records...")
        
        # Calculate samples per segment
        samples_per_segment = {
            segment: int(n_samples * prob)
            for segment, prob in self.segment_distribution.items()
        }
        
        # Adjust for rounding
        total = sum(samples_per_segment.values())
        if total < n_samples:
            samples_per_segment['micro_new'] += (n_samples - total)
        
        # Generate data for each segment
        all_data = []
        for segment, n in samples_per_segment.items():
            segment_data = self._generate_segment_data(segment, n)
            all_data.append(segment_data)
        
        # Combine all segments
        df = pd.concat(all_data, ignore_index=True)
        
        # Shuffle
        df = df.sample(frac=1, random_state=self.seed).reset_index(drop=True)
        
        print(f"✓ Generated {len(df)} records")
        print(f"  Default rate: {df['default_90dpd'].mean():.2%}")
        
        return df
    
    def _generate_segment_data(self, segment: str, n: int) -> pd.DataFrame:
        """Generate data for a specific business segment"""
        
        # Get segment parameters
        if segment == 'micro_new':
            gtv = np.random.lognormal(12, 1.0, n)
            age = np.random.uniform(0.5, 2, n)
            formality = np.random.uniform(0.2, 0.5, n)
            cashflow = np.random.uniform(0.3, 0.6, n)
        elif segment == 'micro_established':
            gtv = np.random.lognormal(13, 0.9, n)
            age = np.random.uniform(2, 5, n)
            formality = np.random.uniform(0.4, 0.7, n)
            cashflow = np.random.uniform(0.4, 0.7, n)
        elif segment == 'small_trading':
            gtv = np.random.lognormal(14, 0.8, n)
            age = np.random.uniform(3, 8, n)
            formality = np.random.uniform(0.5, 0.8, n)
            cashflow = np.random.uniform(0.5, 0.75, n)
        elif segment == 'small_manufacturing':
            gtv = np.random.lognormal(14.5, 0.7, n)
            age = np.random.uniform(3, 10, n)
            formality = np.random.uniform(0.6, 0.85, n)
            cashflow = np.random.uniform(0.45, 0.7, n)
        elif segment == 'small_services':
            gtv = np.random.lognormal(13.5, 0.9, n)
            age = np.random.uniform(2, 7, n)
            formality = np.random.uniform(0.5, 0.8, n)
            cashflow = np.random.uniform(0.5, 0.8, n)
        else:  # medium_enterprise
            gtv = np.random.lognormal(15.5, 0.6, n)
            age = np.random.uniform(5, 15, n)
            formality = np.random.uniform(0.7, 0.95, n)
            cashflow = np.random.uniform(0.6, 0.85, n)
        
        # Generate all features
        data = {
            # Business Identity
            'business_age_years': age,
            'monthly_gtv': gtv,
            'weekly_gtv': gtv / 4.33,
            'employees_count': np.clip(age * 2 + np.random.randint(1, 10, n), 1, 500),
            
            # Banking & Cash Flow
            'avg_bank_balance': gtv * cashflow * np.random.uniform(0.1, 0.3, n),
            'weekly_inflow_outflow_ratio': np.random.normal(1.1, 0.2, n),
            'cash_buffer_days': cashflow * np.random.uniform(15, 60, n),
            'negative_balance_days': (1 - cashflow) * np.random.uniform(0, 30, n),
            
            # Revenue metrics
            'transaction_count_daily': np.random.poisson(gtv / 50000, n),
            'avg_transaction_value': gtv / (np.random.poisson(gtv / 50000, n) + 1) / 30,
            'revenue_growth_rate_mom': np.random.normal(0.05, 0.1, n),
            'profit_margin': formality * np.random.uniform(0.05, 0.25, n),
            'inventory_turnover_ratio': np.random.uniform(2, 12, n),
            
            # Credit & Repayment
            'bounced_cheques_count': np.random.poisson((1 - cashflow) * 5, n),
            'overdraft_repayment_ontime_ratio': cashflow * np.random.uniform(0.6, 1.0, n),
            'utility_payment_ontime_ratio': formality * np.random.uniform(0.7, 1.0, n),
            'current_loans_outstanding': np.random.poisson(2, n),
            'total_debt_amount': gtv * np.random.uniform(0.5, 2, n),
            
            # Compliance
            'gst_filing_regularity': formality * np.random.uniform(0.5, 1.0, n),
            'gst_filing_ontime_ratio': formality * np.random.uniform(0.6, 1.0, n),
            'tax_payment_regularity': formality * np.random.uniform(0.6, 1.0, n),
            'itr_filed': (formality > 0.5).astype(int),
            'outstanding_taxes_amount': (1 - formality) * gtv * np.random.uniform(0, 0.1, n),
            
            # Fraud & Verification
            'kyc_completion_score': formality * np.random.uniform(0.5, 1.0, n),
            'pan_address_bank_mismatch': (np.random.random(n) > formality).astype(int),
            'fraud_transaction_signals': ((1 - formality) * np.random.poisson(3, n)).astype(int),
            'incoming_funds_verified': formality * np.random.uniform(0.5, 1.0, n),
            
            # Owner verification
            'owner_cibil_score': np.clip(formality * np.random.normal(750, 80, n), 300, 900),
            'owner_pan_verified': (formality > 0.4).astype(int),
            'owner_aadhaar_verified': (formality > 0.3).astype(int),
            'owner_bank_verified': (formality > 0.5).astype(int),
            
            # External signals
            'digital_payment_adoption': formality * np.random.uniform(0.3, 1.0, n),
            'online_presence_score': formality * np.random.uniform(0.2, 0.9, n),
            'legal_proceedings_flag': (np.random.random(n) > 0.95).astype(int),
            
            # Categorical
            'industry_sector': np.random.choice(list(self.industry_risk.keys()), n),
            'business_type': np.random.choice(['Proprietorship', 'Partnership', 'Private Limited', 'LLP'], n),
            'business_segment': segment
        }
        
        # Calculate default probability
        base_prob = self.segment_default_rates[segment]
        
        # Risk factors
        risk_score = (
            (1 - cashflow) * 0.3 +
            (1 - formality) * 0.2 +
            (data['bounced_cheques_count'] > 2) * 0.2 +
            (data['negative_balance_days'] > 10) * 0.15 +
            (data['gst_filing_regularity'] < 0.5) * 0.15
        )
        
        default_prob = np.clip(base_prob * (1 + risk_score), 0.01, 0.50)
        
        # Generate default labels
        data['default_90dpd'] = np.random.binomial(1, default_prob, n)
        data['default_probability_true'] = default_prob
        
        return pd.DataFrame(data)


def generate_msme_data(n_samples: int = 10000, seed: int = 42) -> pd.DataFrame:
    """Convenience function to generate MSME data"""
    generator = MSMESyntheticDataGenerator(seed=seed)
    return generator.generate(n_samples)

