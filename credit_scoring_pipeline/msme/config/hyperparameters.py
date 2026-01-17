"""
Hyperparameter Configuration for MSME LightGBM Model
====================================================

Centralized configuration for model hyperparameters and tuning.

Author: ML Engineering Team
Version: 2.0.0
"""

# Default LightGBM parameters for MSME scoring
DEFAULT_MSME_LGB_PARAMS = {
    'objective': 'binary',
    'metric': ['auc', 'binary_logloss'],
    'boosting_type': 'gbdt',
    'num_leaves': 31,
    'max_depth': 6,
    'learning_rate': 0.01,
    'feature_fraction': 0.8,
    'bagging_fraction': 0.8,
    'bagging_freq': 3,
    'min_child_samples': 50,
    'min_data_in_leaf': 50,
    'reg_alpha': 1.0,
    'reg_lambda': 1.0,
    'n_estimators': 2000,
    'early_stopping_rounds': 200,
    'verbose': -1,
    'random_state': 42,
    'n_jobs': -1,
    'is_unbalance': False,
    'scale_pos_weight': 1.0
}

# Optuna hyperparameter tuning configuration
OPTUNA_CONFIG = {
    'n_trials': 100,
    'timeout': 3600,  # 1 hour
    'direction': 'maximize',
    'metric': 'auc',
    'cv_folds': 5,
    'early_stopping_rounds': 50,
    'verbose': True,
    'n_jobs': -1
}

# Search space for hyperparameter tuning
OPTUNA_SEARCH_SPACE = {
    'num_leaves': {'type': 'int', 'low': 20, 'high': 150},
    'max_depth': {'type': 'int', 'low': 3, 'high': 12},
    'learning_rate': {'type': 'loguniform', 'low': 0.001, 'high': 0.1},
    'feature_fraction': {'type': 'uniform', 'low': 0.6, 'high': 1.0},
    'bagging_fraction': {'type': 'uniform', 'low': 0.6, 'high': 1.0},
    'bagging_freq': {'type': 'int', 'low': 1, 'high': 7},
    'min_child_samples': {'type': 'int', 'low': 20, 'high': 100},
    'min_data_in_leaf': {'type': 'int', 'low': 20, 'high': 100},
    'reg_alpha': {'type': 'loguniform', 'low': 0.001, 'high': 10.0},
    'reg_lambda': {'type': 'loguniform', 'low': 0.001, 'high': 10.0}
}

# Early stopping configuration
EARLY_STOPPING_CONFIG = {
    'rounds': 200,
    'min_delta': 0.0001,
    'verbose': True
}

# Class imbalance handling
CLASS_WEIGHT_CONFIG = {
    'auto_scale': True,
    'default_scale_pos_weight': 1.0,
    'use_is_unbalance': False
}
