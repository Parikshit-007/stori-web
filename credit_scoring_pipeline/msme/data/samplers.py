"""Sampling utilities for handling class imbalance"""

import pandas as pd
import numpy as np
from typing import Tuple
from sklearn.utils import resample


def balance_classes(
    X: pd.DataFrame,
    y: pd.Series,
    method: str = 'oversample',
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Balance classes using oversampling or undersampling
    
    Args:
        X: Feature dataframe
        y: Target series
        method: 'oversample' or 'undersample'
        random_state: Random seed
        
    Returns:
        Balanced X, y
    """
    print(f"\nBalancing classes using {method}...")
    print(f"Original class distribution:")
    print(y.value_counts())
    print(f"Original default rate: {y.mean():.2%}")
    
    if method == 'oversample':
        X_balanced, y_balanced = oversample_minority(X, y, random_state)
    elif method == 'undersample':
        X_balanced, y_balanced = undersample_majority(X, y, random_state)
    else:
        raise ValueError(f"Unknown method: {method}")
    
    print(f"\nBalanced class distribution:")
    print(y_balanced.value_counts())
    print(f"Balanced default rate: {y_balanced.mean():.2%}")
    
    return X_balanced, y_balanced


def oversample_minority(
    X: pd.DataFrame,
    y: pd.Series,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Oversample minority class to match majority class size
    
    This creates duplicate samples of the minority class.
    Use with caution as it may lead to overfitting.
    """
    # Combine X and y
    df = X.copy()
    df['target'] = y
    
    # Separate majority and minority classes
    df_majority = df[df['target'] == 0]
    df_minority = df[df['target'] == 1]
    
    # Oversample minority class
    df_minority_upsampled = resample(
        df_minority,
        replace=True,  # Sample with replacement
        n_samples=len(df_majority),
        random_state=random_state
    )
    
    # Combine
    df_balanced = pd.concat([df_majority, df_minority_upsampled])
    df_balanced = df_balanced.sample(frac=1, random_state=random_state).reset_index(drop=True)
    
    # Separate X and y
    y_balanced = df_balanced['target']
    X_balanced = df_balanced.drop('target', axis=1)
    
    return X_balanced, y_balanced


def undersample_majority(
    X: pd.DataFrame,
    y: pd.Series,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Undersample majority class to match minority class size
    
    This removes samples from the majority class.
    May lose information but prevents overfitting.
    """
    # Combine X and y
    df = X.copy()
    df['target'] = y
    
    # Separate majority and minority classes
    df_majority = df[df['target'] == 0]
    df_minority = df[df['target'] == 1]
    
    # Undersample majority class
    df_majority_downsampled = resample(
        df_majority,
        replace=False,  # Sample without replacement
        n_samples=len(df_minority),
        random_state=random_state
    )
    
    # Combine
    df_balanced = pd.concat([df_majority_downsampled, df_minority])
    df_balanced = df_balanced.sample(frac=1, random_state=random_state).reset_index(drop=True)
    
    # Separate X and y
    y_balanced = df_balanced['target']
    X_balanced = df_balanced.drop('target', axis=1)
    
    return X_balanced, y_balanced


def calculate_scale_pos_weight(y: pd.Series) -> float:
    """
    Calculate scale_pos_weight for LightGBM to handle class imbalance
    
    Formula: (number of negative samples) / (number of positive samples)
    """
    n_neg = (y == 0).sum()
    n_pos = (y == 1).sum()
    
    if n_pos == 0:
        return 1.0
    
    scale_pos_weight = n_neg / n_pos
    
    print(f"\nClass imbalance info:")
    print(f"  Negative samples (0): {n_neg:,}")
    print(f"  Positive samples (1): {n_pos:,}")
    print(f"  Ratio: {n_neg/n_pos:.2f}:1")
    print(f"  Calculated scale_pos_weight: {scale_pos_weight:.2f}")
    
    return scale_pos_weight

