"""
MSME Credit Scoring Pipeline - Training Module
===============================================

This module provides:
1. LightGBM training pipeline optimized for MSME credit scoring
2. Hyperparameter tuning with Optuna
3. SHAP explainability integration
4. Comprehensive model evaluation
5. Model serialization

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
from sklearn.calibration import calibration_curve
from sklearn.isotonic import IsotonicRegression
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
import os

from data_prep import (
    MSMESyntheticDataGenerator, MSMEPreprocessor,
    create_msme_splits, MSME_FEATURE_SCHEMA, MSME_FEATURE_CATEGORY_MAPPING
)

warnings.filterwarnings('ignore')


# ============================================================================
# MODEL CONFIGURATION
# ============================================================================

DEFAULT_MSME_LGB_PARAMS = {
    'objective': 'binary',
    'metric': ['auc', 'binary_logloss'],
    'boosting_type': 'gbdt',
    'num_leaves': 31,          # REDUCED for better generalization (was 63)
    'max_depth': 6,            # REDUCED to prevent overfitting (was 8)
    'learning_rate': 0.01,     # SLOWER learning for better convergence (was 0.03)
    'feature_fraction': 0.8,   # Slightly reduced for regularization
    'bagging_fraction': 0.8,   # Slightly reduced for regularization
    'bagging_freq': 3,         # More frequent bagging
    'min_child_samples': 50,   # INCREASED to prevent overfitting (was 30)
    'min_data_in_leaf': 50,    # NEW: Minimum data in leaf
    'reg_alpha': 1.0,          # INCREASED L1 regularization (was 0.5)
    'reg_lambda': 1.0,         # INCREASED L2 regularization (was 0.5)
    'n_estimators': 2000,      # INCREASED for slower learning rate (was 1000)
    'early_stopping_rounds': 200,  # MORE PATIENCE - wait longer (was 100)
    'verbose': -1,
    'random_state': 42,
    'n_jobs': -1,
    'is_unbalance': False,     # CHANGED: Use class_weight instead
    'scale_pos_weight': 1.0    # Will be set dynamically based on class imbalance
}


# ============================================================================
# METRICS
# ============================================================================

def compute_ks_statistic(y_true: np.ndarray, y_pred: np.ndarray) -> Tuple[float, float]:
    """Compute KS statistic"""
    sorted_indices = np.argsort(y_pred)
    y_true_sorted = y_true[sorted_indices]
    
    n_pos = y_true.sum()
    n_neg = len(y_true) - n_pos
    
    tpr = np.cumsum(y_true_sorted) / n_pos
    fpr = np.cumsum(1 - y_true_sorted) / n_neg
    
    ks_stat = np.max(np.abs(tpr - fpr))
    ks_threshold = y_pred[sorted_indices][np.argmax(np.abs(tpr - fpr))]
    
    return ks_stat, ks_threshold


def compute_gini(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute Gini coefficient"""
    return 2 * roc_auc_score(y_true, y_pred) - 1


def compute_risk_bucket_metrics(y_true: np.ndarray, scores: np.ndarray) -> Dict:
    """Compute metrics by risk bucket for MSME"""
    buckets = [(300, 449), (450, 549), (550, 649), (650, 749), (750, 900)]
    
    results = {}
    for min_score, max_score in buckets:
        mask = (scores >= min_score) & (scores <= max_score)
        if mask.sum() > 0:
            results[f"{min_score}-{max_score}"] = {
                'count': int(mask.sum()),
                'pct': float(mask.sum() / len(y_true) * 100),
                'default_rate': float(y_true[mask].mean() * 100),
                'expected_defaults': int(y_true[mask].sum())
            }
    
    return results


def compute_precision_at_k(y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
    """Compute precision at top k%"""
    results = {}
    sorted_indices = np.argsort(y_pred)[::-1]
    
    for k_pct in [5, 10, 20, 30]:
        k = int(len(y_true) * k_pct / 100)
        top_k = sorted_indices[:k]
        results[f"precision@{k_pct}%"] = float(y_true[top_k].mean())
    
    return results


# ============================================================================
# HYPERPARAMETER TUNING
# ============================================================================

class MSMEOptunaObjective:
    """Optuna objective for MSME model tuning"""
    
    def __init__(self, X_train, y_train, X_val, y_val, categorical_features):
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
            'num_leaves': trial.suggest_int('num_leaves', 31, 127),
            'max_depth': trial.suggest_int('max_depth', 5, 12),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.1, log=True),
            'feature_fraction': trial.suggest_float('feature_fraction', 0.6, 1.0),
            'bagging_fraction': trial.suggest_float('bagging_fraction', 0.6, 1.0),
            'bagging_freq': trial.suggest_int('bagging_freq', 1, 10),
            'min_child_samples': trial.suggest_int('min_child_samples', 20, 100),
            'reg_alpha': trial.suggest_float('reg_alpha', 1e-4, 10.0, log=True),
            'reg_lambda': trial.suggest_float('reg_lambda', 1e-4, 10.0, log=True),
            'verbose': -1,
            'random_state': 42,
            'n_jobs': -1,
            'is_unbalance': True
        }
        
        train_data = lgb.Dataset(self.X_train, label=self.y_train, 
                                categorical_feature=self.categorical_features)
        val_data = lgb.Dataset(self.X_val, label=self.y_val,
                              categorical_feature=self.categorical_features, reference=train_data)
        
        model = lgb.train(
            params, train_data,
            num_boost_round=1000,
            valid_sets=[val_data],
            callbacks=[lgb.early_stopping(100, verbose=False)]
        )
        
        y_pred = model.predict(self.X_val)
        return roc_auc_score(self.y_val, y_pred)


def run_msme_hyperparameter_tuning(X_train, y_train, X_val, y_val, 
                                    categorical_features, n_trials=50):
    """Run hyperparameter tuning for MSME model"""
    print(f"Starting MSME hyperparameter tuning with {n_trials} trials...")
    
    objective = MSMEOptunaObjective(X_train, y_train, X_val, y_val, categorical_features)
    
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


# ============================================================================
# MODEL CLASS
# ============================================================================

class MSMECreditScoringModel:
    """LightGBM-based MSME credit scoring model"""
    
    def __init__(self, params: Dict = None):
        self.params = params or DEFAULT_MSME_LGB_PARAMS.copy()
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
              n_tuning_trials: int = 50) -> 'MSMECreditScoringModel':
        """Train the model"""
        
        self.feature_names = list(X_train.columns)
        self.categorical_features = categorical_features or []
        
        print("=" * 60)
        print("MSME MODEL TRAINING")
        print("=" * 60)
        print(f"Training samples: {len(X_train)}")
        print(f"Validation samples: {len(X_val)}")
        print(f"Features: {len(self.feature_names)}")
        print(f"Default rate (train): {y_train.mean()*100:.2f}%")
        print(f"Default rate (val): {y_val.mean()*100:.2f}%")
        
        # Hyperparameter tuning
        if tune_hyperparams:
            tuning_results = run_msme_hyperparameter_tuning(
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
        
        # Train
        print("\nTraining LightGBM model...")
        callbacks = [
            lgb.early_stopping(self.params.get('early_stopping_rounds', 200)),
            lgb.log_evaluation(period=100)
        ]
        
        lgb_params = {k: v for k, v in self.params.items() 
                     if k not in ['early_stopping_rounds', 'n_estimators']}
        
        # Calculate scale_pos_weight dynamically for class balance
        n_negative = (y_train == 0).sum()
        n_positive = (y_train == 1).sum()
        scale_pos_weight = n_negative / max(n_positive, 1)
        lgb_params['scale_pos_weight'] = min(scale_pos_weight, 10.0)  # Cap at 10x
        print(f"Class balance: {n_negative} negative, {n_positive} positive")
        print(f"Scale pos weight: {lgb_params['scale_pos_weight']:.2f}")
        
        self.model = lgb.train(
            lgb_params,
            train_data,
            num_boost_round=self.params.get('n_estimators', 2000),
            valid_sets=[train_data, val_data],
            valid_names=['train', 'valid'],
            callbacks=callbacks
        )
        
        print(f"Best iteration: {self.model.best_iteration}")
        
        # Calibrate
        print("\nCalibrating probabilities...")
        self._calibrate(X_val, y_val)
        
        # SHAP
        print("Initializing SHAP explainer...")
        self.shap_explainer = shap.TreeExplainer(self.model)
        
        # Compute metrics
        self._compute_training_metrics(X_train, y_train, X_val, y_val)
        
        return self
    
    def _calibrate(self, X_val, y_val):
        """Calibrate predictions"""
        raw_probs = self.model.predict(X_val)
        self.calibrator = IsotonicRegression(out_of_bounds='clip')
        self.calibrator.fit(raw_probs, y_val)
    
    def _compute_training_metrics(self, X_train, y_train, X_val, y_val):
        """Compute training metrics"""
        train_pred = self.calibrator.transform(self.model.predict(X_train))
        val_pred = self.calibrator.transform(self.model.predict(X_val))
        
        self.training_metrics['train'] = {
            'auc': float(roc_auc_score(y_train, train_pred)),
            'gini': float(compute_gini(y_train.values, train_pred)),
            'brier_score': float(brier_score_loss(y_train, train_pred))
        }
        
        ks_stat, ks_thresh = compute_ks_statistic(y_val.values, val_pred)
        self.training_metrics['validation'] = {
            'auc': float(roc_auc_score(y_val, val_pred)),
            'gini': float(compute_gini(y_val.values, val_pred)),
            'ks_statistic': float(ks_stat),
            'ks_threshold': float(ks_thresh),
            'brier_score': float(brier_score_loss(y_val, val_pred))
        }
        self.training_metrics['validation'].update(compute_precision_at_k(y_val.values, val_pred))
        
        print("\n" + "=" * 60)
        print("TRAINING METRICS")
        print("=" * 60)
        print(f"Train AUC: {self.training_metrics['train']['auc']:.4f}")
        print(f"Train Gini: {self.training_metrics['train']['gini']:.4f}")
        print(f"Val AUC: {self.training_metrics['validation']['auc']:.4f}")
        print(f"Val Gini: {self.training_metrics['validation']['gini']:.4f}")
        print(f"Val KS: {self.training_metrics['validation']['ks_statistic']:.4f}")
    
    def predict_proba(self, X: pd.DataFrame, calibrated: bool = True) -> np.ndarray:
        """Predict default probability"""
        raw_probs = self.model.predict(X)
        if calibrated and self.calibrator:
            return self.calibrator.transform(raw_probs)
        return raw_probs
    
    def explain_prediction(self, X: pd.DataFrame, top_n: int = 5) -> Dict:
        """Generate SHAP explanation"""
        if self.shap_explainer is None:
            raise ValueError("SHAP explainer not initialized")
        
        shap_values = self.shap_explainer.shap_values(X)
        
        if len(X) == 1:
            shap_values = shap_values[0]
            X_values = X.values[0]
        else:
            X_values = X.values
        
        explanations = []
        for i in range(len(X)):
            sv = shap_values[i] if len(X) > 1 else shap_values
            xv = X_values[i] if len(X) > 1 else X_values
            
            feature_importance = list(zip(self.feature_names, sv, xv))
            sorted_features = sorted(feature_importance, key=lambda x: abs(x[1]), reverse=True)
            
            positive_features = [(f, v, x) for f, v, x in sorted_features if v > 0][:top_n]
            negative_features = [(f, v, x) for f, v, x in sorted_features if v < 0][:top_n]
            
            # Category contributions
            category_contributions = {}
            for cat_name, cat_features in MSME_FEATURE_CATEGORY_MAPPING.items():
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
        """Get feature importance"""
        importance = self.model.feature_importance(importance_type=importance_type)
        return pd.DataFrame({
            'feature': self.feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)
    
    def get_shap_summary(self, X: pd.DataFrame, max_samples: int = 1000) -> Dict:
        """Generate global SHAP summary"""
        X_sample = X.sample(n=min(max_samples, len(X)), random_state=42)
        shap_values = self.shap_explainer.shap_values(X_sample)
        
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
        """Save model"""
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
    def load(cls, path: str) -> 'MSMECreditScoringModel':
        """Load model"""
        artifacts = joblib.load(path)
        
        instance = cls(params=artifacts['params'])
        instance.model = artifacts['model']
        instance.calibrator = artifacts['calibrator']
        instance.feature_names = artifacts['feature_names']
        instance.categorical_features = artifacts['categorical_features']
        instance.training_metrics = artifacts['training_metrics']
        instance.model_version = artifacts['model_version']
        instance.shap_explainer = shap.TreeExplainer(instance.model)
        
        print(f"Model loaded from {path}")
        return instance


# ============================================================================
# EVALUATION
# ============================================================================

def evaluate_msme_model(model: MSMECreditScoringModel,
                        X_test: pd.DataFrame,
                        y_test: pd.Series,
                        output_dir: str = "evaluation_results") -> Dict:
    """Comprehensive evaluation"""
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("MSME MODEL EVALUATION")
    print("=" * 60)
    
    y_pred_proba = model.predict_proba(X_test)
    y_pred = (y_pred_proba >= 0.5).astype(int)
    
    auc = roc_auc_score(y_test, y_pred_proba)
    gini = compute_gini(y_test.values, y_pred_proba)
    ks_stat, ks_thresh = compute_ks_statistic(y_test.values, y_pred_proba)
    brier = brier_score_loss(y_test, y_pred_proba)
    
    print(f"\nCore Metrics:")
    print(f"  AUC-ROC: {auc:.4f}")
    print(f"  Gini: {gini:.4f}")
    print(f"  KS Statistic: {ks_stat:.4f}")
    print(f"  Brier Score: {brier:.4f}")
    
    print(f"\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    precision_k = compute_precision_at_k(y_test.values, y_pred_proba)
    print(f"\nPrecision @ K:")
    for k, v in precision_k.items():
        print(f"  {k}: {v:.4f}")
    
    # Convert to scores
    from score import msme_prob_to_score
    scores = np.array([msme_prob_to_score(p) for p in y_pred_proba])
    
    bucket_metrics = compute_risk_bucket_metrics(y_test.values, scores)
    print(f"\nRisk Bucket Analysis:")
    print(f"{'Bucket':<15} {'Count':>8} {'Pct':>8} {'Default%':>10}")
    print("-" * 45)
    for bucket, metrics in bucket_metrics.items():
        print(f"{bucket:<15} {metrics['count']:>8} {metrics['pct']:>7.1f}% {metrics['default_rate']:>9.1f}%")
    
    # Save plots
    try:
        # Feature importance
        importance_df = model.get_feature_importance()
        fig, ax = plt.subplots(figsize=(10, 8))
        top_features = importance_df.head(25)
        ax.barh(range(len(top_features)), top_features['importance'])
        ax.set_yticks(range(len(top_features)))
        ax.set_yticklabels(top_features['feature'])
        ax.set_xlabel('Feature Importance (Gain)')
        ax.set_title('Top 25 Feature Importance - MSME Model')
        ax.invert_yaxis()
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'feature_importance.png'), dpi=150)
        plt.close()
        
        # Calibration
        fig, ax = plt.subplots(figsize=(8, 6))
        prob_true, prob_pred = calibration_curve(y_test, y_pred_proba, n_bins=10)
        ax.plot(prob_pred, prob_true, 's-', label='Model')
        ax.plot([0, 1], [0, 1], 'k--', label='Perfect')
        ax.set_xlabel('Mean predicted probability')
        ax.set_ylabel('Fraction of positives')
        ax.set_title('Calibration Plot - MSME Model')
        ax.legend()
        plt.savefig(os.path.join(output_dir, 'calibration_plot.png'), dpi=150)
        plt.close()
        
        # SHAP summary
        shap_summary = model.get_shap_summary(X_test)
        fig, ax = plt.subplots(figsize=(12, 10))
        shap.summary_plot(shap_summary['shap_values'], shap_summary['X_sample'],
                         feature_names=model.feature_names, show=False, max_display=25)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'shap_summary.png'), dpi=150)
        plt.close()
    except Exception as e:
        print(f"Warning: Could not generate some plots: {e}")
    
    results = {
        'auc': float(auc),
        'gini': float(gini),
        'ks_statistic': float(ks_stat),
        'brier_score': float(brier),
        'precision_at_k': precision_k,
        'risk_buckets': bucket_metrics,
        'test_samples': len(y_test),
        'test_default_rate': float(y_test.mean())
    }
    
    with open(os.path.join(output_dir, 'evaluation_metrics.json'), 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {output_dir}/")
    
    return results


# ============================================================================
# MAIN
# ============================================================================

def main(data_path: str = None,
         output_dir: str = "msme_model_artifacts",
         n_samples: int = 25000,
         tune_hyperparams: bool = True,
         n_tuning_trials: int = 50):
    """Main training script"""
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("MSME CREDIT SCORING MODEL TRAINING PIPELINE")
    print("=" * 60)
    
    # Generate or load data
    if data_path and os.path.exists(data_path):
        print(f"\nLoading data from {data_path}...")
        df = pd.read_csv(data_path)
    else:
        print(f"\nGenerating {n_samples} synthetic MSME samples...")
        generator = MSMESyntheticDataGenerator(seed=42)
        df = generator.generate(n_samples=n_samples, missing_rate=0.05)
    
    print(f"Dataset shape: {df.shape}")
    print(f"Default rate: {df['default_90dpd'].mean()*100:.2f}%")
    
    # Split
    train_df, val_df, test_df = create_msme_splits(
        df, target_col='default_90dpd', timestamp_col='application_date'
    )
    
    # Preprocess
    print("\nPreprocessing data...")
    preprocessor = MSMEPreprocessor()
    
    exclude_cols = ['default_90dpd', 'default_probability_true', 'application_date', 'business_segment']
    feature_cols = [c for c in train_df.columns if c not in exclude_cols]
    
    train_processed = preprocessor.fit_transform(train_df[feature_cols])
    val_processed = preprocessor.transform(val_df[feature_cols])
    test_processed = preprocessor.transform(test_df[feature_cols])
    
    categorical_features = [c for c in preprocessor._get_categorical_features() 
                           if c in train_processed.columns]
    
    y_train = train_df['default_90dpd'].reset_index(drop=True)
    y_val = val_df['default_90dpd'].reset_index(drop=True)
    y_test = test_df['default_90dpd'].reset_index(drop=True)
    
    train_processed = train_processed.reset_index(drop=True)
    val_processed = val_processed.reset_index(drop=True)
    test_processed = test_processed.reset_index(drop=True)
    
    print(f"Features: {len(train_processed.columns)}")
    
    # Train
    model = MSMECreditScoringModel()
    model.train(
        train_processed, y_train,
        val_processed, y_val,
        categorical_features=categorical_features,
        tune_hyperparams=tune_hyperparams,
        n_tuning_trials=n_tuning_trials
    )
    
    # Evaluate
    eval_results = evaluate_msme_model(
        model, test_processed, y_test,
        output_dir=os.path.join(output_dir, 'evaluation')
    )
    
    # Save
    model.save(os.path.join(output_dir, 'msme_credit_scoring_model.joblib'))
    preprocessor.save(os.path.join(output_dir, 'msme_preprocessor.joblib'))
    
    # Save config
    with open(os.path.join(output_dir, 'feature_list.json'), 'w') as f:
        json.dump({
            'features': list(train_processed.columns),
            'categorical_features': categorical_features,
            'target': 'default_90dpd'
        }, f, indent=2)
    
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
    print("MSME TRAINING COMPLETE")
    print("=" * 60)
    print(f"\nArtifacts saved to {output_dir}/")
    
    return model, preprocessor, eval_results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Train MSME credit scoring model')
    parser.add_argument('--data', type=str, default=None)
    parser.add_argument('--output', type=str, default='msme_model_artifacts')
    parser.add_argument('--samples', type=int, default=25000)
    parser.add_argument('--tune', action='store_true')
    parser.add_argument('--trials', type=int, default=50)
    
    args = parser.parse_args()
    
    main(
        data_path=args.data,
        output_dir=args.output,
        n_samples=args.samples,
        tune_hyperparams=args.tune,
        n_tuning_trials=args.trials
    )


