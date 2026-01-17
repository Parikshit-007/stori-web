"""
Consumer Credit Scoring - Model Training Script
===============================================

Train LightGBM model on consumer credit data.

Author: ML Engineering Team
Version: 1.0.0
"""

import os
import sys
import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report
from sklearn.calibration import calibration_curve
from sklearn.isotonic import IsotonicRegression
import matplotlib.pyplot as plt
import joblib
import argparse
from datetime import datetime

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.hyperparameters import DEFAULT_CONSUMER_LGB_PARAMS
from data.synthetic_data_generator import ConsumerSyntheticDataGenerator


def prepare_data(df):
    """Prepare data for training"""
    
    # Exclude non-feature columns
    exclude_cols = [
        'default_90dpd', 'default_probability_true', 'application_date',
        'consumer_segment', 'age_group', 'risk_bucket'
    ]
    
    feature_cols = [c for c in df.columns if c not in exclude_cols]
    
    # Handle categorical features
    categorical_features = [
        'education_level', 'employment_type', 'income_source_type',
        'spending_personality', 'risk_appetite', 'location_type'
    ]
    
    # Encode categorical features
    from sklearn.preprocessing import LabelEncoder
    encoders = {}
    
    for col in categorical_features:
        if col in df.columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            encoders[col] = le
    
    X = df[feature_cols]
    y = df['default_90dpd']
    
    return X, y, feature_cols, encoders


def train_consumer_model(
    data_path=None,
    n_samples=25000,
    test_size=0.15,
    val_size=0.15,
    output_dir='consumer_model_artifacts'
):
    """
    Train consumer credit scoring model.
    
    Args:
        data_path: Path to existing data (if None, generates synthetic)
        n_samples: Number of samples to generate
        test_size: Test set fraction
        val_size: Validation set fraction
        output_dir: Output directory
    """
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 70)
    print("CONSUMER CREDIT SCORING - MODEL TRAINING")
    print("=" * 70)
    
    # Load or generate data
    if data_path and os.path.exists(data_path):
        print(f"\nLoading data from {data_path}...")
        df = pd.read_csv(data_path)
    else:
        print(f"\nGenerating {n_samples} synthetic consumer samples...")
        generator = ConsumerSyntheticDataGenerator(seed=42)
        df = generator.generate(n_samples=n_samples, include_edge_cases=True)
    
    print(f"Dataset shape: {df.shape}")
    print(f"Default rate: {df['default_90dpd'].mean()*100:.2f}%")
    
    # Prepare data
    print("\nPreparing features...")
    X, y, feature_cols, encoders = prepare_data(df)
    
    print(f"Features: {len(feature_cols)}")
    print(f"Samples: {len(X)}")
    
    # Split data
    print("\nSplitting data...")
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=test_size, stratify=y, random_state=42
    )
    
    val_ratio = val_size / (1 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=val_ratio, stratify=y_temp, random_state=42
    )
    
    print(f"Train: {len(X_train)} ({y_train.mean()*100:.1f}% default)")
    print(f"Val: {len(X_val)} ({y_val.mean()*100:.1f}% default)")
    print(f"Test: {len(X_test)} ({y_test.mean()*100:.1f}% default)")
    
    # Calculate class weight
    n_negative = (y_train == 0).sum()
    n_positive = (y_train == 1).sum()
    scale_pos_weight = n_negative / max(n_positive, 1)
    
    print(f"\nClass balance: {n_negative} negative, {n_positive} positive")
    print(f"Scale pos weight: {scale_pos_weight:.2f}")
    
    # Prepare LightGBM datasets
    train_data = lgb.Dataset(X_train, label=y_train)
    val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
    
    # Update params
    params = DEFAULT_CONSUMER_LGB_PARAMS.copy()
    params['scale_pos_weight'] = min(scale_pos_weight, 10.0)
    
    # Remove keys not for lgb.train
    early_stopping_rounds = params.pop('early_stopping_rounds', 200)
    n_estimators = params.pop('n_estimators', 2000)
    
    # Train model
    print("\nTraining LightGBM model...")
    print(f"Max iterations: {n_estimators}")
    print(f"Early stopping: {early_stopping_rounds} rounds")
    
    model = lgb.train(
        params,
        train_data,
        num_boost_round=n_estimators,
        valid_sets=[train_data, val_data],
        valid_names=['train', 'valid'],
        callbacks=[
            lgb.early_stopping(early_stopping_rounds),
            lgb.log_evaluation(period=100)
        ]
    )
    
    print(f"\nBest iteration: {model.best_iteration}")
    
    # Calibrate probabilities
    print("\nCalibrating probabilities...")
    val_pred_raw = model.predict(X_val)
    calibrator = IsotonicRegression(out_of_bounds='clip')
    calibrator.fit(val_pred_raw, y_val)
    
    # Evaluate
    print("\n" + "=" * 70)
    print("MODEL EVALUATION")
    print("=" * 70)
    
    # Training set
    train_pred = calibrator.transform(model.predict(X_train))
    train_auc = roc_auc_score(y_train, train_pred)
    print(f"\nTrain AUC: {train_auc:.4f}")
    
    # Validation set
    val_pred = calibrator.transform(val_pred_raw)
    val_auc = roc_auc_score(y_val, val_pred)
    print(f"Validation AUC: {val_auc:.4f}")
    
    # Test set
    test_pred_raw = model.predict(X_test)
    test_pred = calibrator.transform(test_pred_raw)
    test_auc = roc_auc_score(y_test, test_pred)
    print(f"Test AUC: {test_auc:.4f}")
    
    # Classification report
    print("\nClassification Report (Test Set):")
    test_pred_binary = (test_pred >= 0.5).astype(int)
    print(classification_report(y_test, test_pred_binary))
    
    # Feature importance
    importance = model.feature_importance(importance_type='gain')
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': importance
    }).sort_values('importance', ascending=False)
    
    print("\nTop 20 Important Features:")
    print(feature_importance.head(20).to_string(index=False))
    
    # Save artifacts
    print("\n" + "=" * 70)
    print("SAVING MODEL ARTIFACTS")
    print("=" * 70)
    
    # Save model
    model_path = os.path.join(output_dir, 'consumer_credit_model.joblib')
    joblib.dump({
        'model': model,
        'calibrator': calibrator,
        'feature_cols': feature_cols,
        'encoders': encoders,
        'params': params
    }, model_path)
    print(f"\n[SUCCESS] Model saved: {model_path}")
    
    # Save feature importance
    importance_path = os.path.join(output_dir, 'feature_importance.csv')
    feature_importance.to_csv(importance_path, index=False)
    print(f"[SUCCESS] Feature importance saved: {importance_path}")
    
    # Save calibration plot
    try:
        prob_true, prob_pred = calibration_curve(y_test, test_pred, n_bins=10)
        
        plt.figure(figsize=(8, 6))
        plt.plot(prob_pred, prob_true, 's-', label='Model')
        plt.plot([0, 1], [0, 1], 'k--', label='Perfect Calibration')
        plt.xlabel('Mean Predicted Probability')
        plt.ylabel('Fraction of Positives')
        plt.title('Calibration Plot - Consumer Credit Scoring')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        calib_path = os.path.join(output_dir, 'calibration_plot.png')
        plt.savefig(calib_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"[SUCCESS] Calibration plot saved: {calib_path}")
    except Exception as e:
        print(f"Warning: Could not generate calibration plot: {e}")
    
    # Save metrics
    metrics = {
        'train_auc': float(train_auc),
        'val_auc': float(val_auc),
        'test_auc': float(test_auc),
        'n_train': len(X_train),
        'n_val': len(X_val),
        'n_test': len(X_test),
        'n_features': len(feature_cols),
        'best_iteration': int(model.best_iteration),
        'training_date': datetime.now().isoformat()
    }
    
    metrics_path = os.path.join(output_dir, 'training_metrics.json')
    import json
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"[SUCCESS] Metrics saved: {metrics_path}")
    
    print("\n" + "=" * 70)
    print("TRAINING COMPLETE!")
    print("=" * 70)
    print(f"\nTest AUC: {test_auc:.4f}")
    print(f"Model artifacts saved to: {output_dir}/")
    
    return model, calibrator, feature_cols, encoders, metrics


def main():
    parser = argparse.ArgumentParser(description='Train Consumer Credit Scoring Model')
    parser.add_argument('--data', type=str, default=None, help='Path to data CSV')
    parser.add_argument('--samples', type=int, default=25000, help='Number of samples to generate')
    parser.add_argument('--output', type=str, default='consumer_model_artifacts', help='Output directory')
    
    args = parser.parse_args()
    
    train_consumer_model(
        data_path=args.data,
        n_samples=args.samples,
        output_dir=args.output
    )


if __name__ == "__main__":
    main()

