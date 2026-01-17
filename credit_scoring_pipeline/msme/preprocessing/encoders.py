"""Categorical encoding utilities"""

import pandas as pd
from typing import Dict, List
from sklearn.preprocessing import LabelEncoder


def encode_categorical_features(
    df: pd.DataFrame,
    categorical_cols: List[str],
    encoders: Dict[str, LabelEncoder] = None
) -> tuple[pd.DataFrame, Dict[str, LabelEncoder]]:
    """
    Encode categorical features using label encoding
    
    Args:
        df: Input dataframe
        categorical_cols: List of categorical column names
        encoders: Pre-fitted encoders (if None, will fit new ones)
        
    Returns:
        Tuple of (encoded_df, encoders_dict)
    """
    df_encoded = df.copy()
    
    if encoders is None:
        encoders = {}
        fit_mode = True
    else:
        fit_mode = False
    
    for col in categorical_cols:
        if col not in df.columns:
            continue
            
        if fit_mode:
            le = LabelEncoder()
            df_encoded[col] = le.fit_transform(df[col].astype(str))
            encoders[col] = le
        else:
            le = encoders[col]
            # Handle unknown categories
            df_encoded[col] = df[col].astype(str).apply(
                lambda x: x if x in le.classes_ else le.classes_[0]
            )
            df_encoded[col] = le.transform(df_encoded[col])
    
    return df_encoded, encoders

