"""Feature engineering utilities"""

import pandas as pd
import numpy as np
from typing import List


def create_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create derived features from existing ones
    
    Common MSME-specific derived features:
    - Ratios and percentages
    - Growth rates
    - Volatility measures
    """
    df_new = df.copy()
    
    # Revenue efficiency
    if 'monthly_gtv' in df.columns and 'employees_count' in df.columns:
        df_new['revenue_per_employee'] = df['monthly_gtv'] / (df['employees_count'] + 1)
    
    # Cash flow efficiency
    if 'avg_bank_balance' in df.columns and 'monthly_gtv' in df.columns:
        df_new['cash_to_revenue_ratio'] = df['avg_bank_balance'] / (df['monthly_gtv'] + 1)
    
    # Debt burden
    if 'total_debt_amount' in df.columns and 'monthly_gtv' in df.columns:
        df_new['debt_to_revenue_ratio'] = df['total_debt_amount'] / (df['monthly_gtv'] * 12 + 1)
    
    # Business maturity
    if 'business_age_years' in df.columns:
        df_new['is_mature_business'] = (df['business_age_years'] >= 5).astype(int)
        df_new['is_new_business'] = (df['business_age_years'] < 2).astype(int)
    
    # Compliance health
    compliance_cols = ['gst_filing_regularity', 'tax_payment_regularity']
    available_cols = [c for c in compliance_cols if c in df.columns]
    if available_cols:
        df_new['compliance_score'] = df[available_cols].mean(axis=1)
    
    # Payment behavior
    payment_cols = ['utility_payment_ontime_ratio', 'overdraft_repayment_ontime_ratio']
    available_cols = [c for c in payment_cols if c in df.columns]
    if available_cols:
        df_new['payment_behavior_score'] = df[available_cols].mean(axis=1)
    
    return df_new


def create_interaction_features(
    df: pd.DataFrame,
    feature_pairs: List[tuple] = None
) -> pd.DataFrame:
    """
    Create interaction features (multiplicative combinations)
    
    Args:
        df: Input dataframe
        feature_pairs: List of (feature1, feature2) tuples to interact
        
    Returns:
        DataFrame with interaction features added
    """
    df_new = df.copy()
    
    if feature_pairs is None:
        # Default important interactions for MSME
        feature_pairs = [
            ('business_age_years', 'monthly_gtv'),
            ('cash_buffer_days', 'profit_margin'),
            ('gst_filing_regularity', 'tax_payment_regularity'),
            ('bounced_cheques_count', 'negative_balance_days')
        ]
    
    for feat1, feat2 in feature_pairs:
        if feat1 in df.columns and feat2 in df.columns:
            interaction_name = f'{feat1}_x_{feat2}'
            df_new[interaction_name] = df[feat1] * df[feat2]
    
    return df_new


def create_binned_features(
    df: pd.DataFrame,
    feature: str,
    bins: List[float],
    labels: List[str]
) -> pd.DataFrame:
    """
    Create binned categorical features from continuous ones
    
    Args:
        df: Input dataframe
        feature: Feature to bin
        bins: Bin edges
        labels: Bin labels
        
    Returns:
        DataFrame with binned feature
    """
    df_new = df.copy()
    
    if feature in df.columns:
        df_new[f'{feature}_binned'] = pd.cut(
            df[feature],
            bins=bins,
            labels=labels,
            include_lowest=True
        )
    
    return df_new

