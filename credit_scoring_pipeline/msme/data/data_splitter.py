"""
Data Splitting Module for MSME Credit Scoring
==============================================

Handles train/validation/test split with stratification and time-awareness.

Author: ML Engineering Team
Version: 2.0.0
"""

import pandas as pd
from typing import Tuple, Optional
from sklearn.model_split import train_test_split


def create_msme_splits(
    df: pd.DataFrame,
    target_col: str = 'default_90dpd',
    timestamp_col: Optional[str] = 'application_date',
    test_size: float = 0.15,
    val_size: float = 0.15,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Create train/validation/test splits for MSME data.
    
    Args:
        df: Input dataframe
        target_col: Name of target column
        timestamp_col: Name of timestamp column (if None, uses stratified split)
        test_size: Fraction of data for test set
        val_size: Fraction of remaining data for validation set
        random_state: Random seed
        
    Returns:
        Tuple of (train_df, val_df, test_df)
    """
    print(f"Creating MSME data splits (test={test_size}, val={val_size})...")
    
    if timestamp_col and timestamp_col in df.columns:
        # Time-based split
        df_sorted = df.sort_values(timestamp_col).reset_index(drop=True)
        n = len(df_sorted)
        
        test_idx = int(n * (1 - test_size))
        val_idx = int(test_idx * (1 - val_size / (1 - test_size)))
        
        train_df = df_sorted.iloc[:val_idx].copy()
        val_df = df_sorted.iloc[val_idx:test_idx].copy()
        test_df = df_sorted.iloc[test_idx:].copy()
        
        print(f"Time-based split")
    else:
        # Stratified split
        train_val_df, test_df = train_test_split(
            df, test_size=test_size, stratify=df[target_col], random_state=random_state
        )
        
        val_ratio = val_size / (1 - test_size)
        train_df, val_df = train_test_split(
            train_val_df, test_size=val_ratio, stratify=train_val_df[target_col], random_state=random_state
        )
        
        print(f"Stratified split")
    
    print(f"  Train: {len(train_df)} samples ({train_df[target_col].mean()*100:.1f}% default rate)")
    print(f"  Val: {len(val_df)} samples ({val_df[target_col].mean()*100:.1f}% default rate)")
    print(f"  Test: {len(test_df)} samples ({test_df[target_col].mean()*100:.1f}% default rate)")
    
    return train_df, val_df, test_df
