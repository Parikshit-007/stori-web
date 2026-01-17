"""Numerical scaling utilities"""

import pandas as pd
import numpy as np
from typing import List, Optional
from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler


def scale_numerical_features(
    df: pd.DataFrame,
    numerical_cols: List[str],
    scaler: Optional[StandardScaler] = None,
    method: str = 'standard'
) -> tuple[pd.DataFrame, StandardScaler]:
    """
    Scale numerical features
    
    Args:
        df: Input dataframe
        numerical_cols: List of numerical column names
        scaler: Pre-fitted scaler (if None, will fit new one)
        method: Scaling method ('standard', 'robust', 'minmax')
        
    Returns:
        Tuple of (scaled_df, scaler)
    """
    df_scaled = df.copy()
    
    if scaler is None:
        if method == 'standard':
            scaler = StandardScaler()
        elif method == 'robust':
            scaler = RobustScaler()
        elif method == 'minmax':
            scaler = MinMaxScaler()
        else:
            raise ValueError(f"Unknown scaling method: {method}")
        
        df_scaled[numerical_cols] = scaler.fit_transform(df[numerical_cols])
    else:
        df_scaled[numerical_cols] = scaler.transform(df[numerical_cols])
    
    return df_scaled, scaler

