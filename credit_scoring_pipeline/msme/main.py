"""
Main Orchestrator for MSME Credit Scoring Pipeline
==================================================

Simplified entry point for the entire pipeline.

Author: ML Engineering Team
Version: 2.0.0
"""

import os
import pandas as pd
from typing import Optional, Dict

from .data.synthetic_data_generator import MSMESyntheticDataGenerator
from .data.data_splitter import create_msme_splits
from .preprocessing.preprocessor import MSMEPreprocessor
from .models.lightgbm_model import MSMECreditScoringModel
from .training.hyperparameter_tuner import run_msme_hyperparameter_tuning
from .evaluation.evaluator import evaluate_msme_model
from .scoring.probability_to_score import msme_prob_to_score
from .scoring.risk_tier import get_risk_tier
from .scoring.loan_calculator import calculate_max_loan_limit


class MSMEPipeline:
    """
    End-to-end MSME credit scoring pipeline.
    
    Usage:
        pipeline = MSMEPipeline()
        pipeline.run_training(n_samples=25000, tune_hyperparams=True)
        results = pipeline.score_application(application_data)
    """
    
    def __init__(self, model_dir: str = "msme_model_artifacts"):
        """
        Initialize pipeline.
        
        Args:
            model_dir: Directory for model artifacts
        """
        self.model_dir = model_dir
        self.model = None
        self.preprocessor = None
        os.makedirs(model_dir, exist_ok=True)
    
    def run_training(
        self,
        data_path: Optional[str] = None,
        n_samples: int = 25000,
        tune_hyperparams: bool = True,
        n_tuning_trials: int = 50
    ) -> Dict:
        """
        Run complete training pipeline.
        
        Args:
            data_path: Path to existing data (if None, generates synthetic)
            n_samples: Number of samples to generate
            tune_hyperparams: Whether to run hyperparameter tuning
            n_tuning_trials: Number of Optuna trials
            
        Returns:
            Dictionary with training results
        """
        print("=" * 60)
        print("MSME CREDIT SCORING PIPELINE - TRAINING")
        print("=" * 60)
        
        # Step 1: Generate or load data
        if data_path and os.path.exists(data_path):
            print(f"\nLoading data from {data_path}...")
            df = pd.read_csv(data_path)
        else:
            print(f"\nGenerating {n_samples} synthetic MSME samples...")
            generator = MSMESyntheticDataGenerator(seed=42)
            df = generator.generate(n_samples=n_samples, missing_rate=0.05)
        
        print(f"Dataset shape: {df.shape}")
        print(f"Default rate: {df['default_90dpd'].mean()*100:.2f}%")
        
        # Step 2: Split data
        train_df, val_df, test_df = create_msme_splits(
            df, target_col='default_90dpd', timestamp_col='application_date'
        )
        
        # Step 3: Preprocess
        print("\nPreprocessing data...")
        self.preprocessor = MSMEPreprocessor()
        
        exclude_cols = ['default_90dpd', 'default_probability_true', 'application_date', 'business_segment']
        feature_cols = [c for c in train_df.columns if c not in exclude_cols]
        
        train_processed = self.preprocessor.fit_transform(train_df[feature_cols])
        val_processed = self.preprocessor.transform(val_df[feature_cols])
        test_processed = self.preprocessor.transform(test_df[feature_cols])
        
        y_train = train_df['default_90dpd'].reset_index(drop=True)
        y_val = val_df['default_90dpd'].reset_index(drop=True)
        y_test = test_df['default_90dpd'].reset_index(drop=True)
        
        print(f"Features: {len(train_processed.columns)}")
        
        # Step 4: Train model
        print("\nTraining LightGBM model...")
        self.model = MSMECreditScoringModel()
        self.model.train(
            train_processed, y_train,
            val_processed, y_val,
            categorical_features=[],
            tune_hyperparams=tune_hyperparams,
            n_tuning_trials=n_tuning_trials
        )
        
        # Step 5: Evaluate
        print("\nEvaluating model...")
        eval_results = evaluate_msme_model(
            self.model, test_processed, y_test,
            output_dir=os.path.join(self.model_dir, 'evaluation')
        )
        
        # Step 6: Save artifacts
        print("\nSaving model artifacts...")
        self.model.save(os.path.join(self.model_dir, 'msme_credit_scoring_model.joblib'))
        self.preprocessor.save(os.path.join(self.model_dir, 'msme_preprocessor.joblib'))
        
        print("\n" + "=" * 60)
        print("TRAINING COMPLETE")
        print("=" * 60)
        
        return eval_results
    
    def load_model(self):
        """Load trained model and preprocessor"""
        print("Loading model artifacts...")
        self.model = MSMECreditScoringModel.load(
            os.path.join(self.model_dir, 'msme_credit_scoring_model.joblib')
        )
        self.preprocessor = MSMEPreprocessor()
        self.preprocessor.load(
            os.path.join(self.model_dir, 'msme_preprocessor.joblib')
        )
        print("Model loaded successfully")
    
    def score_application(
        self,
        application_data: pd.DataFrame,
        calculate_limit: bool = True
    ) -> Dict:
        """
        Score a new MSME application.
        
        Args:
            application_data: DataFrame with application features
            calculate_limit: Whether to calculate loan limit
            
        Returns:
            Dictionary with scoring results
        """
        if self.model is None or self.preprocessor is None:
            self.load_model()
        
        # Preprocess
        processed_data = self.preprocessor.transform(application_data)
        
        # Predict
        prob = self.model.predict_proba(processed_data, calibrated=True)[0]
        score = msme_prob_to_score(prob)
        tier = get_risk_tier(score)
        
        # Get explanation
        explanation = self.model.explain_prediction(processed_data, top_n=5)
        
        result = {
            'default_probability': float(prob),
            'credit_score': int(score),
            'risk_tier': tier.name,
            'eligible': tier.eligible,
            'explanation': explanation
        }
        
        # Calculate loan limit if requested
        if calculate_limit and tier.eligible:
            # Extract required fields
            annual_turnover = application_data.get('monthly_gtv', [0])[0] * 12
            monthly_surplus = application_data.get('weekly_inflow_outflow_ratio', [1])[0] * \
                             application_data.get('monthly_gtv', [0])[0] * 0.1
            
            limits = calculate_max_loan_limit(
                annual_turnover=annual_turnover,
                monthly_surplus=monthly_surplus,
                risk_tier_multiplier=tier.turnover_multiplier,
                dscr_required=tier.dscr_required
            )
            
            result['loan_limits'] = limits
            result['recommended_limit'] = limits['recommended_limit']
            result['interest_rate_range'] = {
                'min': tier.interest_rate_min,
                'max': tier.interest_rate_max
            }
        
        return result


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MSME Credit Scoring Pipeline')
    parser.add_argument('--train', action='store_true', help='Run training')
    parser.add_argument('--data', type=str, default=None, help='Path to data file')
    parser.add_argument('--samples', type=int, default=25000, help='Number of samples')
    parser.add_argument('--tune', action='store_true', help='Run hyperparameter tuning')
    parser.add_argument('--trials', type=int, default=50, help='Number of tuning trials')
    parser.add_argument('--output', type=str, default='msme_model_artifacts', help='Output directory')
    
    args = parser.parse_args()
    
    pipeline = MSMEPipeline(model_dir=args.output)
    
    if args.train:
        pipeline.run_training(
            data_path=args.data,
            n_samples=args.samples,
            tune_hyperparams=args.tune,
            n_tuning_trials=args.trials
        )
    else:
        print("Specify --train to run training pipeline")
        print("Example: python main.py --train --samples 25000 --tune --trials 50")


if __name__ == "__main__":
    main()


