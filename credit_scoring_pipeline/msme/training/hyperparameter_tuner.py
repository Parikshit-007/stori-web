"""
Hyperparameter Tuning with Optuna for MSME Credit Scoring
==========================================================

Automated hyperparameter optimization using Optuna.

Author: ML Engineering Team
Version: 2.0.0
"""

import numpy as np
import pandas as pd
import lightgbm as lgb
import optuna
from optuna.samplers import TPESampler
from sklearn.metrics import roc_auc_score
from typing import Dict, List

from ..config.hyperparameters import OPTUNA_CONFIG, OPTUNA_SEARCH_SPACE


class MSMEOptunaObjective:
    """Optuna objective function for MSME model tuning"""
    
    def __init__(self, X_train: pd.DataFrame, y_train: pd.Series,
                 X_val: pd.DataFrame, y_val: pd.Series,
                 categorical_features: List[str]):
        """
        Initialize objective function.
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features
            y_val: Validation labels
            categorical_features: List of categorical feature names
        """
        self.X_train = X_train
        self.y_train = y_train
        self.X_val = X_val
        self.y_val = y_val
        self.categorical_features = categorical_features
    
    def __call__(self, trial: optuna.Trial) -> float:
        """
        Evaluate a set of hyperparameters.
        
        Args:
            trial: Optuna trial object
            
        Returns:
            Validation AUC score
        """
        # Sample hyperparameters
        params = {
            'objective': 'binary',
            'metric': 'auc',
            'boosting_type': 'gbdt',
            'num_leaves': trial.suggest_int('num_leaves', 
                                           OPTUNA_SEARCH_SPACE['num_leaves']['low'],
                                           OPTUNA_SEARCH_SPACE['num_leaves']['high']),
            'max_depth': trial.suggest_int('max_depth',
                                          OPTUNA_SEARCH_SPACE['max_depth']['low'],
                                          OPTUNA_SEARCH_SPACE['max_depth']['high']),
            'learning_rate': trial.suggest_loguniform('learning_rate',
                                                      OPTUNA_SEARCH_SPACE['learning_rate']['low'],
                                                      OPTUNA_SEARCH_SPACE['learning_rate']['high']),
            'feature_fraction': trial.suggest_uniform('feature_fraction',
                                                      OPTUNA_SEARCH_SPACE['feature_fraction']['low'],
                                                      OPTUNA_SEARCH_SPACE['feature_fraction']['high']),
            'bagging_fraction': trial.suggest_uniform('bagging_fraction',
                                                      OPTUNA_SEARCH_SPACE['bagging_fraction']['low'],
                                                      OPTUNA_SEARCH_SPACE['bagging_fraction']['high']),
            'bagging_freq': trial.suggest_int('bagging_freq',
                                             OPTUNA_SEARCH_SPACE['bagging_freq']['low'],
                                             OPTUNA_SEARCH_SPACE['bagging_freq']['high']),
            'min_child_samples': trial.suggest_int('min_child_samples',
                                                   OPTUNA_SEARCH_SPACE['min_child_samples']['low'],
                                                   OPTUNA_SEARCH_SPACE['min_child_samples']['high']),
            'reg_alpha': trial.suggest_loguniform('reg_alpha',
                                                  OPTUNA_SEARCH_SPACE['reg_alpha']['low'],
                                                  OPTUNA_SEARCH_SPACE['reg_alpha']['high']),
            'reg_lambda': trial.suggest_loguniform('reg_lambda',
                                                   OPTUNA_SEARCH_SPACE['reg_lambda']['low'],
                                                   OPTUNA_SEARCH_SPACE['reg_lambda']['high']),
            'verbose': -1,
            'random_state': 42,
            'n_jobs': -1,
            'is_unbalance': True
        }
        
        # Create datasets
        train_data = lgb.Dataset(
            self.X_train, label=self.y_train,
            categorical_feature=self.categorical_features
        )
        val_data = lgb.Dataset(
            self.X_val, label=self.y_val,
            categorical_feature=self.categorical_features,
            reference=train_data
        )
        
        # Train model
        model = lgb.train(
            params, train_data,
            num_boost_round=1000,
            valid_sets=[val_data],
            callbacks=[lgb.early_stopping(100, verbose=False)]
        )
        
        # Evaluate
        y_pred = model.predict(self.X_val)
        auc = roc_auc_score(self.y_val, y_pred)
        
        return auc


def run_msme_hyperparameter_tuning(
    X_train: pd.DataFrame, y_train: pd.Series,
    X_val: pd.DataFrame, y_val: pd.Series,
    categorical_features: List[str],
    n_trials: int = 50
) -> Dict:
    """
    Run hyperparameter tuning for MSME model.
    
    Args:
        X_train: Training features
        y_train: Training labels
        X_val: Validation features
        y_val: Validation labels
        categorical_features: List of categorical feature names
        n_trials: Number of Optuna trials
        
    Returns:
        Dictionary with best params and AUC
    """
    print(f"Starting MSME hyperparameter tuning with {n_trials} trials...")
    
    objective = MSMEOptunaObjective(
        X_train, y_train, X_val, y_val, categorical_features
    )
    
    sampler = TPESampler(seed=42)
    study = optuna.create_study(direction='maximize', sampler=sampler)
    study.optimize(objective, n_trials=n_trials, show_progress_bar=True)
    
    print(f"\nBest trial: AUC={study.best_trial.value:.4f}")
    print(f"Best params: {study.best_trial.params}")
    
    return {
        'best_params': study.best_trial.params,
        'best_auc': study.best_trial.value,
        'n_trials': n_trials
    }


