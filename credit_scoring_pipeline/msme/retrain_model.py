"""
MSME Credit Scoring Model - Retrain with Comprehensive Data
============================================================

This script retrains the MSME credit scoring model using the 
comprehensive synthetic dataset with all risk levels and edge cases.

Usage: python retrain_model.py

Author: ML Engineering Team
"""

import pandas as pd
import numpy as np
import os
import sys
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_prep import MSMEPreprocessor, create_msme_splits
from model import MSMECreditScorerTrainer

def main():
    print("=" * 70)
    print("MSME CREDIT SCORING MODEL - RETRAINING")
    print("=" * 70)
    print()
    
    # Load the comprehensive training data
    data_path = os.path.join(os.path.dirname(__file__), 'msme_comprehensive_training_data.csv')
    
    if not os.path.exists(data_path):
        print(f"ERROR: Training data not found at {data_path}")
        print("Please run generate_comprehensive_data.py first.")
        return
    
    print(f"Loading data from: {data_path}")
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} samples with {len(df.columns)} features")
    print(f"Default rate: {df['default_90dpd'].mean()*100:.2f}%")
    
    # Split data
    print("\n" + "-" * 50)
    print("CREATING TRAIN/VAL/TEST SPLITS")
    print("-" * 50)
    
    train_df, val_df, test_df = create_msme_splits(
        df, 
        target_col='default_90dpd',
        timestamp_col='application_date',
        test_size=0.15,
        val_size=0.15
    )
    
    # Preprocess
    print("\n" + "-" * 50)
    print("PREPROCESSING DATA")
    print("-" * 50)
    
    preprocessor = MSMEPreprocessor()
    train_processed = preprocessor.fit_transform(train_df)
    val_processed = preprocessor.transform(val_df)
    test_processed = preprocessor.transform(test_df)
    
    print(f"Train shape: {train_processed.shape}")
    print(f"Val shape: {val_processed.shape}")
    print(f"Test shape: {test_processed.shape}")
    
    # Train model
    print("\n" + "-" * 50)
    print("TRAINING MODEL")
    print("-" * 50)
    
    trainer = MSMECreditScorerTrainer(
        n_trials=50,  # Number of Optuna trials for hyperparameter tuning
        early_stopping_rounds=30
    )
    
    # Prepare features
    exclude_cols = ['default_90dpd', 'default_probability_true', 'application_date']
    feature_cols = [c for c in train_processed.columns if c not in exclude_cols]
    
    # Handle categorical columns
    categorical_cols = ['business_segment', 'industry_code', 'legal_entity_type', 
                       'msme_category', 'business_structure']
    for col in categorical_cols:
        if col in train_processed.columns:
            # These should already be encoded by preprocessor
            pass
    
    X_train = train_processed[feature_cols]
    y_train = train_processed['default_90dpd']
    
    X_val = val_processed[feature_cols]
    y_val = val_processed['default_90dpd']
    
    X_test = test_processed[feature_cols]
    y_test = test_processed['default_90dpd']
    
    print(f"\nFeatures used: {len(feature_cols)}")
    print(f"Training samples: {len(X_train)}")
    print(f"Validation samples: {len(X_val)}")
    print(f"Test samples: {len(X_test)}")
    
    # Train
    trainer.train(X_train, y_train, X_val, y_val)
    
    # Evaluate
    print("\n" + "-" * 50)
    print("EVALUATING ON TEST SET")
    print("-" * 50)
    
    from sklearn.metrics import roc_auc_score, precision_recall_curve, auc
    
    test_proba = trainer.model.predict(X_test)
    test_auc = roc_auc_score(y_test, test_proba)
    
    precision, recall, _ = precision_recall_curve(y_test, test_proba)
    pr_auc = auc(recall, precision)
    
    print(f"Test ROC-AUC: {test_auc:.4f}")
    print(f"Test PR-AUC: {pr_auc:.4f}")
    
    # Score distribution analysis
    print("\n" + "-" * 50)
    print("SCORE DISTRIBUTION ANALYSIS")
    print("-" * 50)
    
    # Convert probabilities to scores (300-900 range)
    test_scores = 300 + (1 - test_proba) * 600
    
    # Define risk buckets
    def get_risk_bucket(score):
        if score >= 750:
            return 'Very Low (750-900)'
        elif score >= 650:
            return 'Low (650-749)'
        elif score >= 550:
            return 'Medium (550-649)'
        elif score >= 450:
            return 'High (450-549)'
        else:
            return 'Very High (300-449)'
    
    risk_buckets = [get_risk_bucket(s) for s in test_scores]
    
    # Analyze by bucket
    test_df_analysis = pd.DataFrame({
        'score': test_scores,
        'default': y_test.values,
        'risk_bucket': risk_buckets
    })
    
    print("\nDefault Rate by Risk Bucket:")
    bucket_order = ['Very Low (750-900)', 'Low (650-749)', 'Medium (550-649)', 
                    'High (450-549)', 'Very High (300-449)']
    
    for bucket in bucket_order:
        subset = test_df_analysis[test_df_analysis['risk_bucket'] == bucket]
        if len(subset) > 0:
            default_rate = subset['default'].mean() * 100
            print(f"  {bucket}: {len(subset)} samples, {default_rate:.1f}% default rate")
    
    # Save model
    print("\n" + "-" * 50)
    print("SAVING MODEL")
    print("-" * 50)
    
    artifacts_dir = os.path.join(os.path.dirname(__file__), 'msme_model_artifacts')
    os.makedirs(artifacts_dir, exist_ok=True)
    
    trainer.save(artifacts_dir)
    preprocessor.save(os.path.join(artifacts_dir, 'msme_preprocessor.joblib'))
    
    print(f"\nModel saved to: {artifacts_dir}")
    print("\n" + "=" * 70)
    print("RETRAINING COMPLETE!")
    print("=" * 70)

if __name__ == "__main__":
    main()



