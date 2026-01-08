"""
Credit Scoring Pipeline - Training Module
==========================================

This module provides:
1. LightGBM training pipeline with categorical handling
2. Hyperparameter tuning with Optuna
3. SHAP explainability integration
4. Comprehensive model evaluation metrics
5. Model serialization and reproducible training

Author: ML Engineering Team
Version: 1.0.0
"""

import numpy as np
import pandas as pd
import lightgbm as lgb
import optuna
from optuna.samplers import TPESampler
import shap
import joblib
import json
from typing import Dict, List, Optional, Tuple, Any
from sklearn.metrics import (
    roc_auc_score, precision_recall_curve, average_precision_score,
    confusion_matrix, classification_report, brier_score_loss
)
from sklearn.calibration import calibration_curve, CalibratedClassifierCV
from sklearn.isotonic import IsotonicRegression
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
import os

from data_prep import (
    SyntheticDataGenerator, CreditScoringPreprocessor, 
    create_splits, FEATURE_SCHEMA, FEATURE_CATEGORY_MAPPING
)

warnings.filterwarnings('ignore')

# ============================================================================
# MODEL CONFIGURATION
# ============================================================================

DEFAULT_LGB_PARAMS = {
    'objective': 'binary',
    'metric': ['auc', 'binary_logloss'],
    'boosting_type': 'gbdt',
    'num_leaves': 31,
    'max_depth': 6,
    'learning_rate': 0.05,
    'feature_fraction': 0.8,
    'bagging_fraction': 0.8,
    'bagging_freq': 5,
    'min_child_samples': 20,
    'reg_alpha': 0.1,
    'reg_lambda': 0.1,
    'n_estimators': 500,
    'early_stopping_rounds': 50,
    'verbose': -1,
    'random_state': 42,
    'n_jobs': -1
}


# ============================================================================
# METRICS COMPUTATION
# ============================================================================

def compute_ks_statistic(y_true: np.ndarray, y_pred: np.ndarray) -> Tuple[float, float]:
    """
    Compute Kolmogorov-Smirnov statistic for binary classification.
    
    Returns:
        Tuple of (KS statistic, optimal threshold)
    """
    from scipy import stats
    
    # Sort by predicted probability
    sorted_indices = np.argsort(y_pred)
    y_true_sorted = y_true[sorted_indices]
    y_pred_sorted = y_pred[sorted_indices]
    
    # Cumulative distributions
    n_pos = y_true.sum()
    n_neg = len(y_true) - n_pos
    
    tpr = np.cumsum(y_true_sorted) / n_pos
    fpr = np.cumsum(1 - y_true_sorted) / n_neg
    
    ks_stat = np.max(np.abs(tpr - fpr))
    ks_threshold = y_pred_sorted[np.argmax(np.abs(tpr - fpr))]
    
    return ks_stat, ks_threshold


def compute_gini(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute Gini coefficient from AUC"""
    auc = roc_auc_score(y_true, y_pred)
    return 2 * auc - 1


def compute_risk_bucket_metrics(y_true: np.ndarray, 
                                  scores: np.ndarray, 
                                  buckets: List[Tuple[int, int]] = None) -> Dict:
    """
    Compute default rates by risk bucket.
    
    Args:
        y_true: True labels
        scores: Credit scores (300-900)
        buckets: List of (min, max) score ranges
        
    Returns:
        Dict with bucket-level metrics
    """
    if buckets is None:
        buckets = [(300, 499), (500, 599), (600, 699), (700, 799), (800, 900)]
    
    results = {}
    for min_score, max_score in buckets:
        mask = (scores >= min_score) & (scores <= max_score)
        if mask.sum() > 0:
            bucket_default_rate = y_true[mask].mean()
            bucket_count = mask.sum()
            results[f"{min_score}-{max_score}"] = {
                'count': int(bucket_count),
                'pct': float(bucket_count / len(y_true) * 100),
                'default_rate': float(bucket_default_rate * 100),
                'expected_defaults': int(y_true[mask].sum())
            }
    
    return results


def compute_precision_at_k(y_true: np.ndarray, y_pred: np.ndarray, k_pcts: List[float] = None) -> Dict:
    """Compute precision at top k% of predictions"""
    if k_pcts is None:
        k_pcts = [5, 10, 20, 30]
    
    results = {}
    sorted_indices = np.argsort(y_pred)[::-1]  # Descending
    
    for k_pct in k_pcts:
        k = int(len(y_true) * k_pct / 100)
        top_k_indices = sorted_indices[:k]
        precision_k = y_true[top_k_indices].mean()
        results[f"precision@{k_pct}%"] = float(precision_k)
    
    return results


# ============================================================================
# HYPERPARAMETER TUNING
# ============================================================================

class OptunaObjective:
    """Optuna objective for LightGBM hyperparameter tuning"""
    
    def __init__(self, X_train: pd.DataFrame, y_train: pd.Series,
                 X_val: pd.DataFrame, y_val: pd.Series,
                 categorical_features: List[str]):
        self.X_train = X_train
        self.y_train = y_train
        self.X_val = X_val
        self.y_val = y_val
        self.categorical_features = categorical_features
    
    def __call__(self, trial: optuna.Trial) -> float:
        params = {
            'objective': 'binary',
            'metric': 'auc',
            'boosting_type': 'gbdt',
            'num_leaves': trial.suggest_int('num_leaves', 20, 100),
            'max_depth': trial.suggest_int('max_depth', 4, 10),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.2, log=True),
            'feature_fraction': trial.suggest_float('feature_fraction', 0.5, 1.0),
            'bagging_fraction': trial.suggest_float('bagging_fraction', 0.5, 1.0),
            'bagging_freq': trial.suggest_int('bagging_freq', 1, 10),
            'min_child_samples': trial.suggest_int('min_child_samples', 10, 100),
            'reg_alpha': trial.suggest_float('reg_alpha', 1e-4, 10.0, log=True),
            'reg_lambda': trial.suggest_float('reg_lambda', 1e-4, 10.0, log=True),
            'verbose': -1,
            'random_state': 42,
            'n_jobs': -1
        }
        
        train_data = lgb.Dataset(
            self.X_train, label=self.y_train,
            categorical_feature=self.categorical_features
        )
        val_data = lgb.Dataset(
            self.X_val, label=self.y_val,
            categorical_feature=self.categorical_features,
            reference=train_data
        )
        
        model = lgb.train(
            params,
            train_data,
            num_boost_round=500,
            valid_sets=[val_data],
            callbacks=[lgb.early_stopping(50, verbose=False)]
        )
        
        y_pred = model.predict(self.X_val)
        auc = roc_auc_score(self.y_val, y_pred)
        
        return auc


def run_hyperparameter_tuning(X_train: pd.DataFrame, y_train: pd.Series,
                               X_val: pd.DataFrame, y_val: pd.Series,
                               categorical_features: List[str],
                               n_trials: int = 50) -> Dict:
    """
    Run Optuna hyperparameter search.
    
    Returns:
        Dict with best parameters and study results
    """
    print(f"Starting hyperparameter tuning with {n_trials} trials...")
    
    objective = OptunaObjective(X_train, y_train, X_val, y_val, categorical_features)
    
    sampler = TPESampler(seed=42)
    study = optuna.create_study(direction='maximize', sampler=sampler)
    
    study.optimize(objective, n_trials=n_trials, show_progress_bar=True)
    
    print(f"\nBest trial:")
    print(f"  AUC: {study.best_trial.value:.4f}")
    print(f"  Params: {study.best_trial.params}")
    
    return {
        'best_params': study.best_trial.params,
        'best_auc': study.best_trial.value,
        'n_trials': n_trials
    }


# ============================================================================
# MODEL TRAINING
# ============================================================================

class CreditScoringModel:
    """
    LightGBM-based credit scoring model with SHAP integration.
    """
    
    def __init__(self, params: Dict = None):
        self.params = params or DEFAULT_LGB_PARAMS.copy()
        self.model = None
        self.calibrator = None
        self.shap_explainer = None
        self.feature_names = None
        self.categorical_features = None
        self.training_metrics = {}
        self.model_version = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def train(self, X_train: pd.DataFrame, y_train: pd.Series,
              X_val: pd.DataFrame, y_val: pd.Series,
              categorical_features: List[str] = None,
              tune_hyperparams: bool = False,
              n_tuning_trials: int = 30) -> 'CreditScoringModel':
        """
        Train the LightGBM model.
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features
            y_val: Validation labels
            categorical_features: List of categorical column names
            tune_hyperparams: Whether to run hyperparameter tuning
            n_tuning_trials: Number of Optuna trials
            
        Returns:
            self
        """
        self.feature_names = list(X_train.columns)
        self.categorical_features = categorical_features or []
        
        print("=" * 60)
        print("MODEL TRAINING")
        print("=" * 60)
        print(f"Training samples: {len(X_train)}")
        print(f"Validation samples: {len(X_val)}")
        print(f"Features: {len(self.feature_names)}")
        print(f"Categorical features: {len(self.categorical_features)}")
        print(f"Default rate (train): {y_train.mean()*100:.2f}%")
        print(f"Default rate (val): {y_val.mean()*100:.2f}%")
        
        # Hyperparameter tuning
        if tune_hyperparams:
            tuning_results = run_hyperparameter_tuning(
                X_train, y_train, X_val, y_val,
                self.categorical_features, n_tuning_trials
            )
            self.params.update(tuning_results['best_params'])
            self.training_metrics['tuning'] = tuning_results
        
        # Prepare datasets
        train_data = lgb.Dataset(
            X_train, label=y_train,
            categorical_feature=self.categorical_features,
            feature_name=self.feature_names
        )
        val_data = lgb.Dataset(
            X_val, label=y_val,
            categorical_feature=self.categorical_features,
            reference=train_data
        )
        
        # Train model
        print("\nTraining LightGBM model...")
        callbacks = [
            lgb.early_stopping(self.params.get('early_stopping_rounds', 50)),
            lgb.log_evaluation(period=100)
        ]
        
        # Remove non-lgb params
        lgb_params = {k: v for k, v in self.params.items() 
                     if k not in ['early_stopping_rounds', 'n_estimators']}
        
        self.model = lgb.train(
            lgb_params,
            train_data,
            num_boost_round=self.params.get('n_estimators', 500),
            valid_sets=[train_data, val_data],
            valid_names=['train', 'valid'],
            callbacks=callbacks
        )
        
        print(f"Best iteration: {self.model.best_iteration}")
        
        # Calibrate probabilities
        print("\nCalibrating probabilities...")
        self._calibrate(X_val, y_val)
        
        # Initialize SHAP explainer
        print("Initializing SHAP explainer...")
        self.shap_explainer = shap.TreeExplainer(self.model)
        
        # Compute training metrics
        self._compute_training_metrics(X_train, y_train, X_val, y_val)
        
        return self
    
    def _calibrate(self, X_val: pd.DataFrame, y_val: pd.Series):
        """Calibrate model probabilities using isotonic regression"""
        raw_probs = self.model.predict(X_val)
        self.calibrator = IsotonicRegression(out_of_bounds='clip')
        self.calibrator.fit(raw_probs, y_val)
    
    def _compute_training_metrics(self, X_train, y_train, X_val, y_val):
        """Compute and store training metrics"""
        # Train predictions
        train_pred_raw = self.model.predict(X_train)
        train_pred = self.calibrator.transform(train_pred_raw)
        
        # Validation predictions
        val_pred_raw = self.model.predict(X_val)
        val_pred = self.calibrator.transform(val_pred_raw)
        
        self.training_metrics['train'] = {
            'auc': float(roc_auc_score(y_train, train_pred)),
            'gini': float(compute_gini(y_train, train_pred)),
            'brier_score': float(brier_score_loss(y_train, train_pred))
        }
        
        ks_stat, ks_thresh = compute_ks_statistic(y_val.values, val_pred)
        self.training_metrics['validation'] = {
            'auc': float(roc_auc_score(y_val, val_pred)),
            'gini': float(compute_gini(y_val, val_pred)),
            'ks_statistic': float(ks_stat),
            'ks_threshold': float(ks_thresh),
            'brier_score': float(brier_score_loss(y_val, val_pred))
        }
        
        # Precision at k
        self.training_metrics['validation'].update(
            compute_precision_at_k(y_val.values, val_pred)
        )
        
        print("\n" + "=" * 60)
        print("TRAINING METRICS")
        print("=" * 60)
        print(f"Train AUC: {self.training_metrics['train']['auc']:.4f}")
        print(f"Train Gini: {self.training_metrics['train']['gini']:.4f}")
        print(f"Val AUC: {self.training_metrics['validation']['auc']:.4f}")
        print(f"Val Gini: {self.training_metrics['validation']['gini']:.4f}")
        print(f"Val KS: {self.training_metrics['validation']['ks_statistic']:.4f}")
        print(f"Val Brier: {self.training_metrics['validation']['brier_score']:.4f}")
    
    def predict_proba(self, X: pd.DataFrame, calibrated: bool = True) -> np.ndarray:
        """
        Predict default probability.
        
        Args:
            X: Features DataFrame
            calibrated: Whether to return calibrated probabilities
            
        Returns:
            Array of default probabilities
        """
        raw_probs = self.model.predict(X)
        
        if calibrated and self.calibrator is not None:
            return self.calibrator.transform(raw_probs)
        
        return raw_probs
    
    def explain_prediction(self, X: pd.DataFrame, 
                           top_n: int = 5) -> Dict:
        """
        Generate SHAP-based explanation for predictions.
        
        Args:
            X: Features DataFrame (single row or batch)
            top_n: Number of top features to return
            
        Returns:
            Dict with SHAP values and top contributing features
        """
        if self.shap_explainer is None:
            raise ValueError("SHAP explainer not initialized. Train model first.")
        
        shap_values = self.shap_explainer.shap_values(X)
        
        # Handle single prediction vs batch
        if len(X) == 1:
            shap_values = shap_values[0]
            X_values = X.values[0]
        else:
            X_values = X.values
        
        explanations = []
        for i in range(len(X)):
            sv = shap_values[i] if len(X) > 1 else shap_values
            xv = X_values[i] if len(X) > 1 else X_values
            
            # Get feature importance
            feature_importance = list(zip(self.feature_names, sv, xv))
            sorted_features = sorted(feature_importance, key=lambda x: abs(x[1]), reverse=True)
            
            # Top positive (increasing risk) and negative (decreasing risk)
            positive_features = [(f, v, x) for f, v, x in sorted_features if v > 0][:top_n]
            negative_features = [(f, v, x) for f, v, x in sorted_features if v < 0][:top_n]
            
            # Category-level contributions
            category_contributions = {}
            for cat_name, cat_features in FEATURE_CATEGORY_MAPPING.items():
                cat_shap = sum(sv[self.feature_names.index(f)] 
                              for f in cat_features if f in self.feature_names)
                category_contributions[cat_name] = float(cat_shap)
            
            explanations.append({
                'base_value': float(self.shap_explainer.expected_value),
                'top_positive_features': [
                    {'feature': f, 'shap_value': float(v), 'feature_value': float(x)}
                    for f, v, x in positive_features
                ],
                'top_negative_features': [
                    {'feature': f, 'shap_value': float(v), 'feature_value': float(x)}
                    for f, v, x in negative_features
                ],
                'category_contributions': category_contributions
            })
        
        return explanations if len(X) > 1 else explanations[0]
    
    def get_feature_importance(self, importance_type: str = 'gain') -> pd.DataFrame:
        """Get feature importance from trained model"""
        importance = self.model.feature_importance(importance_type=importance_type)
        return pd.DataFrame({
            'feature': self.feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)
    
    def get_shap_summary(self, X: pd.DataFrame, max_samples: int = 1000) -> Dict:
        """Generate global SHAP summary"""
        if len(X) > max_samples:
            X_sample = X.sample(n=max_samples, random_state=42)
        else:
            X_sample = X
        
        shap_values = self.shap_explainer.shap_values(X_sample)
        
        # Mean absolute SHAP values
        mean_abs_shap = np.abs(shap_values).mean(axis=0)
        
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'mean_abs_shap': mean_abs_shap
        }).sort_values('mean_abs_shap', ascending=False)
        
        return {
            'feature_importance': feature_importance.to_dict('records'),
            'shap_values': shap_values,
            'X_sample': X_sample
        }
    
    def save(self, path: str):
        """Save model and related artifacts"""
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
        
        artifacts = {
            'model': self.model,
            'calibrator': self.calibrator,
            'params': self.params,
            'feature_names': self.feature_names,
            'categorical_features': self.categorical_features,
            'training_metrics': self.training_metrics,
            'model_version': self.model_version
        }
        
        joblib.dump(artifacts, path)
        print(f"Model saved to {path}")
    
    @classmethod
    def load(cls, path: str) -> 'CreditScoringModel':
        """Load model from file"""
        artifacts = joblib.load(path)
        
        instance = cls(params=artifacts['params'])
        instance.model = artifacts['model']
        instance.calibrator = artifacts['calibrator']
        instance.feature_names = artifacts['feature_names']
        instance.categorical_features = artifacts['categorical_features']
        instance.training_metrics = artifacts['training_metrics']
        instance.model_version = artifacts['model_version']
        
        # Reinitialize SHAP explainer
        instance.shap_explainer = shap.TreeExplainer(instance.model)
        
        print(f"Model loaded from {path}")
        return instance


# ============================================================================
# MODEL EVALUATION
# ============================================================================

def evaluate_model(model: CreditScoringModel,
                   X_test: pd.DataFrame,
                   y_test: pd.Series,
                   output_dir: str = "evaluation_results") -> Dict:
    """
    Comprehensive model evaluation on test set.
    
    Args:
        model: Trained CreditScoringModel
        X_test: Test features
        y_test: Test labels
        output_dir: Directory for saving plots
        
    Returns:
        Dict with all evaluation metrics
    """
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("MODEL EVALUATION ON TEST SET")
    print("=" * 60)
    
    # Get predictions
    y_pred_proba = model.predict_proba(X_test)
    y_pred = (y_pred_proba >= 0.5).astype(int)
    
    # Core metrics
    auc = roc_auc_score(y_test, y_pred_proba)
    gini = compute_gini(y_test.values, y_pred_proba)
    ks_stat, ks_thresh = compute_ks_statistic(y_test.values, y_pred_proba)
    brier = brier_score_loss(y_test, y_pred_proba)
    
    print(f"\nCore Metrics:")
    print(f"  AUC-ROC: {auc:.4f}")
    print(f"  Gini: {gini:.4f}")
    print(f"  KS Statistic: {ks_stat:.4f}")
    print(f"  Brier Score: {brier:.4f}")
    
    # Classification report
    print(f"\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Precision at k
    precision_k = compute_precision_at_k(y_test.values, y_pred_proba)
    print(f"\nPrecision @ K:")
    for k, v in precision_k.items():
        print(f"  {k}: {v:.4f}")
    
    # Convert scores to 300-900 scale for bucket analysis
    # Lower probability = higher score
    from score import prob_to_score
    scores = np.array([prob_to_score(p) for p in y_pred_proba])
    
    # Risk bucket analysis
    bucket_metrics = compute_risk_bucket_metrics(y_test.values, scores)
    print(f"\nRisk Bucket Analysis:")
    print(f"{'Bucket':<15} {'Count':>8} {'Pct':>8} {'Default%':>10}")
    print("-" * 45)
    for bucket, metrics in bucket_metrics.items():
        print(f"{bucket:<15} {metrics['count']:>8} {metrics['pct']:>7.1f}% {metrics['default_rate']:>9.1f}%")
    
    # Calibration plot
    try:
        fig, ax = plt.subplots(1, 1, figsize=(8, 6))
        prob_true, prob_pred = calibration_curve(y_test, y_pred_proba, n_bins=10)
        ax.plot(prob_pred, prob_true, 's-', label='Model')
        ax.plot([0, 1], [0, 1], 'k--', label='Perfectly calibrated')
        ax.set_xlabel('Mean predicted probability')
        ax.set_ylabel('Fraction of positives')
        ax.set_title('Calibration Plot')
        ax.legend()
        plt.savefig(os.path.join(output_dir, 'calibration_plot.png'), dpi=150, bbox_inches='tight')
        plt.close()
    except Exception as e:
        print(f"Warning: Could not generate calibration plot: {e}")
    
    # Feature importance plot
    try:
        importance_df = model.get_feature_importance()
        fig, ax = plt.subplots(1, 1, figsize=(10, 8))
        top_features = importance_df.head(20)
        ax.barh(range(len(top_features)), top_features['importance'])
        ax.set_yticks(range(len(top_features)))
        ax.set_yticklabels(top_features['feature'])
        ax.set_xlabel('Feature Importance (Gain)')
        ax.set_title('Top 20 Feature Importance')
        ax.invert_yaxis()
        plt.savefig(os.path.join(output_dir, 'feature_importance.png'), dpi=150, bbox_inches='tight')
        plt.close()
    except Exception as e:
        print(f"Warning: Could not generate feature importance plot: {e}")
    
    # SHAP summary
    try:
        shap_summary = model.get_shap_summary(X_test)
        fig, ax = plt.subplots(1, 1, figsize=(10, 8))
        shap.summary_plot(shap_summary['shap_values'], shap_summary['X_sample'],
                         feature_names=model.feature_names, show=False, max_display=20)
        plt.savefig(os.path.join(output_dir, 'shap_summary.png'), dpi=150, bbox_inches='tight')
        plt.close()
    except Exception as e:
        print(f"Warning: Could not generate SHAP summary plot: {e}")
    
    # Compile results
    results = {
        'auc': float(auc),
        'gini': float(gini),
        'ks_statistic': float(ks_stat),
        'ks_threshold': float(ks_thresh),
        'brier_score': float(brier),
        'precision_at_k': precision_k,
        'risk_buckets': bucket_metrics,
        'test_samples': len(y_test),
        'test_default_rate': float(y_test.mean())
    }
    
    # Save results
    with open(os.path.join(output_dir, 'evaluation_metrics.json'), 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nEvaluation results saved to {output_dir}/")
    
    return results


# ============================================================================
# MAIN TRAINING SCRIPT
# ============================================================================

def main(data_path: str = None,
         output_dir: str = "model_artifacts",
         n_samples: int = 20000,
         tune_hyperparams: bool = True,
         n_tuning_trials: int = 30):
    """
    Main training script.
    
    Args:
        data_path: Path to data file (optional, uses synthetic if not provided)
        output_dir: Directory for saving model artifacts
        n_samples: Number of synthetic samples if no data provided
        tune_hyperparams: Whether to run hyperparameter tuning
        n_tuning_trials: Number of Optuna trials
    """
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("CREDIT SCORING MODEL TRAINING PIPELINE")
    print("=" * 60)
    print(f"Output directory: {output_dir}")
    print(f"Hyperparameter tuning: {tune_hyperparams}")
    
    # Step 1: Load or generate data
    if data_path and os.path.exists(data_path):
        print(f"\nLoading data from {data_path}...")
        df = pd.read_csv(data_path)
    else:
        print(f"\nGenerating {n_samples} synthetic samples...")
        generator = SyntheticDataGenerator(seed=42)
        df = generator.generate(n_samples=n_samples, missing_rate=0.05)
    
    print(f"Dataset shape: {df.shape}")
    print(f"Default rate: {df['default_90dpd'].mean()*100:.2f}%")
    
    # Step 2: Create splits
    train_df, val_df, test_df = create_splits(
        df, target_col='default_90dpd', timestamp_col='application_date'
    )
    
    # Step 3: Preprocess
    print("\nPreprocessing data...")
    preprocessor = CreditScoringPreprocessor()
    
    # Columns to exclude from features
    exclude_cols = ['default_90dpd', 'default_probability_true', 'application_date', 'persona']
    feature_cols = [c for c in train_df.columns if c not in exclude_cols]
    
    train_processed = preprocessor.fit_transform(train_df[feature_cols])
    val_processed = preprocessor.transform(val_df[feature_cols])
    test_processed = preprocessor.transform(test_df[feature_cols])
    
    # Identify categorical features after encoding
    categorical_features = [c for c in preprocessor._get_categorical_features() 
                           if c in train_processed.columns]
    
    # Prepare targets
    y_train = train_df['default_90dpd'].reset_index(drop=True)
    y_val = val_df['default_90dpd'].reset_index(drop=True)
    y_test = test_df['default_90dpd'].reset_index(drop=True)
    
    # Reset indices
    train_processed = train_processed.reset_index(drop=True)
    val_processed = val_processed.reset_index(drop=True)
    test_processed = test_processed.reset_index(drop=True)
    
    print(f"Processed feature count: {len(train_processed.columns)}")
    
    # Step 4: Train model
    model = CreditScoringModel()
    model.train(
        train_processed, y_train,
        val_processed, y_val,
        categorical_features=categorical_features,
        tune_hyperparams=tune_hyperparams,
        n_tuning_trials=n_tuning_trials
    )
    
    # Step 5: Evaluate on test set
    eval_results = evaluate_model(
        model, test_processed, y_test,
        output_dir=os.path.join(output_dir, 'evaluation')
    )
    
    # Step 6: Save artifacts
    model.save(os.path.join(output_dir, 'credit_scoring_model.joblib'))
    preprocessor.save(os.path.join(output_dir, 'preprocessor.joblib'))
    
    # Save feature list
    feature_list = {
        'features': list(train_processed.columns),
        'categorical_features': categorical_features,
        'target': 'default_90dpd'
    }
    with open(os.path.join(output_dir, 'feature_list.json'), 'w') as f:
        json.dump(feature_list, f, indent=2)
    
    # Save training config
    training_config = {
        'model_version': model.model_version,
        'n_samples': len(df),
        'train_samples': len(train_df),
        'val_samples': len(val_df),
        'test_samples': len(test_df),
        'n_features': len(train_processed.columns),
        'hyperparams': model.params,
        'training_metrics': model.training_metrics,
        'evaluation_results': eval_results,
        'training_timestamp': datetime.now().isoformat()
    }
    with open(os.path.join(output_dir, 'training_config.json'), 'w') as f:
        json.dump(training_config, f, indent=2, default=str)
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    print(f"\nArtifacts saved to {output_dir}/:")
    print("  - credit_scoring_model.joblib")
    print("  - preprocessor.joblib")
    print("  - feature_list.json")
    print("  - training_config.json")
    print("  - evaluation/")
    
    return model, preprocessor, eval_results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Train credit scoring model')
    parser.add_argument('--data', type=str, default=None, help='Path to training data')
    parser.add_argument('--output', type=str, default='model_artifacts', help='Output directory')
    parser.add_argument('--samples', type=int, default=20000, help='Number of synthetic samples')
    parser.add_argument('--tune', action='store_true', help='Run hyperparameter tuning')
    parser.add_argument('--trials', type=int, default=30, help='Number of tuning trials')
    
    args = parser.parse_args()
    
    main(
        data_path=args.data,
        output_dir=args.output,
        n_samples=args.samples,
        tune_hyperparams=args.tune,
        n_tuning_trials=args.trials
    )


