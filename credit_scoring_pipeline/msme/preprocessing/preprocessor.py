"""Main preprocessing pipeline for MSME data"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
import warnings

warnings.filterwarnings('ignore')


class MSMEPreprocessor:
    """
    Complete preprocessing pipeline for MSME credit scoring data
    
    Handles:
    - Missing value imputation
    - Categorical encoding
    - Numerical scaling
    - Outlier handling
    - Feature engineering
    """
    
    def __init__(
        self,
        categorical_features: Optional[List[str]] = None,
        numerical_features: Optional[List[str]] = None,
        handle_outliers: bool = True,
        outlier_method: str = 'clip',
        outlier_threshold: float = 3.0
    ):
        self.categorical_features = categorical_features or []
        self.numerical_features = numerical_features or []
        self.handle_outliers = handle_outliers
        self.outlier_method = outlier_method
        self.outlier_threshold = outlier_threshold
        
        # Imputers
        self.num_imputer = SimpleImputer(strategy='median')
        self.cat_imputer = SimpleImputer(strategy='most_frequent')
        
        # Encoders
        self.label_encoders = {}
        
        # Scaler
        self.scaler = StandardScaler()
        
        # Fitted flag
        self.is_fitted = False
        
        # Stats
        self.feature_stats = {}
    
    def fit(self, df: pd.DataFrame, target_col: Optional[str] = None) -> 'MSMEPreprocessor':
        """
        Fit the preprocessor on training data
        
        Args:
            df: Training dataframe
            target_col: Target column name (excluded from preprocessing)
            
        Returns:
            self
        """
        print("\n" + "="*60)
        print("FITTING PREPROCESSOR")
        print("="*60)
        
        df_work = df.copy()
        
        # Remove target if present
        if target_col and target_col in df_work.columns:
            df_work = df_work.drop(target_col, axis=1)
        
        # Auto-detect feature types if not provided
        if not self.categorical_features and not self.numerical_features:
            self._auto_detect_features(df_work)
        
        print(f"Categorical features: {len(self.categorical_features)}")
        print(f"Numerical features: {len(self.numerical_features)}")
        
        # Fit numerical imputer and scaler
        if self.numerical_features:
            num_data = df_work[self.numerical_features]
            self.num_imputer.fit(num_data)
            
            # Impute before scaling
            num_data_imputed = self.num_imputer.transform(num_data)
            self.scaler.fit(num_data_imputed)
            
            # Calculate outlier bounds
            if self.handle_outliers:
                self._calculate_outlier_bounds(num_data_imputed)
        
        # Fit categorical encoders
        if self.categorical_features:
            cat_data = df_work[self.categorical_features]
            self.cat_imputer.fit(cat_data)
            
            # Fit label encoders
            cat_data_imputed = pd.DataFrame(
                self.cat_imputer.transform(cat_data),
                columns=self.categorical_features
            )
            
            for col in self.categorical_features:
                le = LabelEncoder()
                le.fit(cat_data_imputed[col].astype(str))
                self.label_encoders[col] = le
        
        self.is_fitted = True
        print("✓ Preprocessor fitted successfully")
        print("="*60 + "\n")
        
        return self
    
    def transform(self, df: pd.DataFrame, target_col: Optional[str] = None) -> pd.DataFrame:
        """
        Transform data using fitted preprocessor
        
        Args:
            df: Input dataframe
            target_col: Target column name (excluded from preprocessing)
            
        Returns:
            Transformed dataframe
        """
        if not self.is_fitted:
            raise ValueError("Preprocessor must be fitted before transform")
        
        df_work = df.copy()
        
        # Store target if present
        target = None
        if target_col and target_col in df_work.columns:
            target = df_work[target_col].copy()
            df_work = df_work.drop(target_col, axis=1)
        
        # Transform numerical features
        if self.numerical_features:
            num_data = df_work[self.numerical_features]
            num_data_imputed = self.num_imputer.transform(num_data)
            
            # Handle outliers
            if self.handle_outliers:
                num_data_imputed = self._handle_outliers(num_data_imputed)
            
            # Scale
            num_data_scaled = self.scaler.transform(num_data_imputed)
            
            # Update dataframe
            df_work[self.numerical_features] = num_data_scaled
        
        # Transform categorical features
        if self.categorical_features:
            cat_data = df_work[self.categorical_features]
            cat_data_imputed = pd.DataFrame(
                self.cat_imputer.transform(cat_data),
                columns=self.categorical_features,
                index=cat_data.index
            )
            
            # Encode
            for col in self.categorical_features:
                le = self.label_encoders[col]
                # Handle unknown categories
                cat_data_imputed[col] = cat_data_imputed[col].astype(str).apply(
                    lambda x: x if x in le.classes_ else le.classes_[0]
                )
                df_work[col] = le.transform(cat_data_imputed[col])
        
        # Add target back if it was present
        if target is not None:
            df_work[target_col] = target
        
        return df_work
    
    def fit_transform(self, df: pd.DataFrame, target_col: Optional[str] = None) -> pd.DataFrame:
        """Fit and transform in one step"""
        self.fit(df, target_col)
        return self.transform(df, target_col)
    
    def _auto_detect_features(self, df: pd.DataFrame):
        """Auto-detect categorical and numerical features"""
        for col in df.columns:
            if df[col].dtype in ['object', 'category']:
                self.categorical_features.append(col)
            elif df[col].dtype in ['int64', 'float64', 'int32', 'float32']:
                self.numerical_features.append(col)
    
    def _calculate_outlier_bounds(self, data: np.ndarray):
        """Calculate outlier bounds using z-score method"""
        self.feature_stats['mean'] = np.mean(data, axis=0)
        self.feature_stats['std'] = np.std(data, axis=0)
        self.feature_stats['lower_bound'] = (
            self.feature_stats['mean'] - self.outlier_threshold * self.feature_stats['std']
        )
        self.feature_stats['upper_bound'] = (
            self.feature_stats['mean'] + self.outlier_threshold * self.feature_stats['std']
        )
    
    def _handle_outliers(self, data: np.ndarray) -> np.ndarray:
        """Handle outliers using configured method"""
        if self.outlier_method == 'clip':
            return np.clip(
                data,
                self.feature_stats['lower_bound'],
                self.feature_stats['upper_bound']
            )
        elif self.outlier_method == 'remove':
            # For transform, we clip instead of remove to maintain shape
            return np.clip(
                data,
                self.feature_stats['lower_bound'],
                self.feature_stats['upper_bound']
            )
        else:
            return data

