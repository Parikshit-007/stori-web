"""LightGBM model wrapper for MSME credit scoring"""

import lightgbm as lgb
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
import joblib


class MSMECreditScoringModel:
    """
    LightGBM-based credit scoring model for MSME
    
    Performs BINARY CLASSIFICATION to predict default probability:
    - Target: default_90dpd (0 or 1)
    - Output: Probability of default (0-1)
    - Score: Derived from probability using rule-based mapping
    """
    
    def __init__(self, params: Optional[Dict] = None):
        """
        Initialize model with hyperparameters
        
        Args:
            params: LightGBM parameters (if None, uses defaults)
        """
        if params is None:
            params = {
                'objective': 'binary',
                'metric': ['auc', 'binary_logloss'],
                'boosting_type': 'gbdt',
                'num_leaves': 31,
                'max_depth': 6,
                'learning_rate': 0.01,
                'n_estimators': 2000,
                'random_state': 42
            }
        
        self.params = params
        self.model = None
        self.calibrator = None
        self.feature_names = None
        self.is_fitted = False
    
    def fit(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
        early_stopping_rounds: int = 200,
        verbose: int = 100
    ) -> 'MSMECreditScoringModel':
        """
        Train the LightGBM model
        
        The model learns to predict default_90dpd (0 or 1) from features.
        It outputs probabilities that represent the likelihood of default.
        
        Args:
            X_train: Training features
            y_train: Training target (0 or 1)
            X_val: Validation features
            y_val: Validation target
            early_stopping_rounds: Early stopping patience
            verbose: Logging frequency
            
        Returns:
            self
        """
        print("\n" + "="*60)
        print("TRAINING LIGHTGBM MODEL")
        print("="*60)
        print(f"Training samples: {len(X_train):,}")
        print(f"Features: {X_train.shape[1]}")
        print(f"Default rate: {y_train.mean():.2%}")
        print(f"Model type: Binary Classification")
        print(f"Objective: {self.params.get('objective', 'binary')}")
        
        # Store feature names
        self.feature_names = list(X_train.columns)
        
        # Create LightGBM datasets
        train_data = lgb.Dataset(X_train, label=y_train)
        
        valid_sets = [train_data]
        valid_names = ['train']
        
        if X_val is not None and y_val is not None:
            val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
            valid_sets.append(val_data)
            valid_names.append('valid')
            print(f"Validation samples: {len(X_val):,}")
            print(f"Validation default rate: {y_val.mean():.2%}")
        
        # Train model
        print("\nTraining in progress...")
        self.model = lgb.train(
            self.params,
            train_data,
            valid_sets=valid_sets,
            valid_names=valid_names,
            callbacks=[
                lgb.early_stopping(stopping_rounds=early_stopping_rounds, verbose=False),
                lgb.log_evaluation(period=verbose)
            ]
        )
        
        self.is_fitted = True
        print("\n✓ Model training completed")
        print(f"Best iteration: {self.model.best_iteration}")
        print(f"Best AUC: {self.model.best_score.get('valid', {}).get('auc', 'N/A')}")
        print("="*60 + "\n")
        
        return self
    
    def predict_proba(
        self,
        X: pd.DataFrame,
        calibrated: bool = False
    ) -> np.ndarray:
        """
        Predict default probability
        
        The LightGBM model uses GRADIENT BOOSTING to predict probabilities:
        1. Builds multiple decision trees (n_estimators)
        2. Each tree corrects errors of previous trees
        3. Final prediction = weighted sum of all trees
        4. Sigmoid function converts to probability (0-1)
        
        This is NOT rule-based - the model learns patterns from data!
        
        Args:
            X: Features
            calibrated: Whether to use calibrated probabilities
            
        Returns:
            Array of default probabilities (0-1)
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        # Get raw predictions from LightGBM
        raw_probs = self.model.predict(X, num_iteration=self.model.best_iteration)
        
        # Apply calibration if requested and available
        if calibrated and self.calibrator is not None:
            return self.calibrator.transform(raw_probs)
        
        return raw_probs
    
    def predict(self, X: pd.DataFrame, threshold: float = 0.5) -> np.ndarray:
        """
        Predict binary class (0 or 1)
        
        Args:
            X: Features
            threshold: Classification threshold
            
        Returns:
            Binary predictions (0 or 1)
        """
        probs = self.predict_proba(X)
        return (probs >= threshold).astype(int)
    
    def get_feature_importance(
        self,
        importance_type: str = 'gain'
    ) -> pd.DataFrame:
        """
        Get feature importance
        
        Args:
            importance_type: 'gain', 'split', or 'weight'
            
        Returns:
            DataFrame with feature importance
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        importance = self.model.feature_importance(importance_type=importance_type)
        
        return pd.DataFrame({
            'feature': self.feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)
    
    def save(self, filepath: str):
        """Save model to disk"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before saving")
        
        model_data = {
            'model': self.model,
            'params': self.params,
            'feature_names': self.feature_names,
            'calibrator': self.calibrator
        }
        
        joblib.dump(model_data, filepath)
        print(f"✓ Model saved to {filepath}")
    
    @classmethod
    def load(cls, filepath: str) -> 'MSMECreditScoringModel':
        """Load model from disk"""
        model_data = joblib.load(filepath)
        
        instance = cls(params=model_data['params'])
        instance.model = model_data['model']
        instance.feature_names = model_data['feature_names']
        instance.calibrator = model_data.get('calibrator')
        instance.is_fitted = True
        
        print(f"✓ Model loaded from {filepath}")
        return instance

