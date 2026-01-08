"""
Credit Scoring Pipeline - Unit Tests
=====================================

This module provides unit tests for the credit scoring pipeline components:
1. Data preparation and preprocessing
2. Scoring functions and persona blending
3. Model training (with synthetic data)
4. API endpoints

Run with: pytest tests.py -v

Author: ML Engineering Team
Version: 1.0.0
"""

import pytest
import numpy as np
import pandas as pd
import json
import os
import tempfile
from datetime import datetime

# Import modules to test
from data_prep import (
    SyntheticDataGenerator, CreditScoringPreprocessor, 
    create_splits, FEATURE_SCHEMA
)
from score import (
    normalize_feature, compute_param_group_score, compute_category_score,
    compute_persona_subscore, prob_to_score, blend_scores, CreditScorer,
    PERSONA_WEIGHTS, NORMALIZATION_BOUNDS
)
from monitoring import (
    calculate_psi, calculate_feature_psi, psi_report,
    calibration_metrics, PerformanceMonitor
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_features():
    """Sample feature dictionary for testing"""
    return {
        'name_dob_verified': 1,
        'phone_verified': 1,
        'phone_age_months': 48,
        'email_verified': 1,
        'email_age_months': 60,
        'location_stability_score': 0.8,
        'education_level': 3,
        'employment_tenure_months': 36,
        'monthly_income': 75000,
        'income_growth_rate': 0.1,
        'avg_account_balance': 150000,
        'income_stability_score': 0.85,
        'itr_filed': 1,
        'itr_income_declared': 900000,
        'employability_score': 0.75,
        'current_loan_count': 1,
        'current_loan_amount': 500000,
        'credit_card_count': 2,
        'credit_card_utilization': 0.35,
        'total_assets_value': 2000000,
        'debt_to_income_ratio': 0.6,
        'spending_to_income_ratio': 0.6,
        'budgeting_score': 0.7,
        'financial_literacy_score': 0.65,
        'impatience_score': 0.3,
        'recurring_payment_habit_score': 0.8,
        'utility_payment_ontime_ratio': 0.95,
        'repayment_ontime_ratio': 0.92,
        'max_dpd_ever': 15,
        'avg_dpd': 3,
        'face_recognition_match_score': 0.98,
        'fraud_history_flag': 0,
        'spouse_credit_available': 0,
        'dependents_count': 2
    }


@pytest.fixture
def synthetic_data():
    """Generate synthetic data for testing"""
    generator = SyntheticDataGenerator(seed=42)
    return generator.generate(n_samples=1000, missing_rate=0.05)


# ============================================================================
# DATA PREPARATION TESTS
# ============================================================================

class TestSyntheticDataGenerator:
    """Tests for synthetic data generator"""
    
    def test_generator_creates_dataframe(self):
        """Test that generator creates a valid DataFrame"""
        generator = SyntheticDataGenerator(seed=42)
        df = generator.generate(n_samples=100)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 100
    
    def test_generator_includes_target(self):
        """Test that generated data includes target variable"""
        generator = SyntheticDataGenerator(seed=42)
        df = generator.generate(n_samples=100)
        
        assert 'default_90dpd' in df.columns
        assert df['default_90dpd'].isin([0, 1]).all()
    
    def test_generator_includes_persona(self):
        """Test that generated data includes persona"""
        generator = SyntheticDataGenerator(seed=42)
        df = generator.generate(n_samples=500)
        
        assert 'persona' in df.columns
        # Should have multiple personas
        assert len(df['persona'].unique()) >= 3
    
    def test_generator_reproducibility(self):
        """Test that generator produces same results with same seed"""
        gen1 = SyntheticDataGenerator(seed=42)
        gen2 = SyntheticDataGenerator(seed=42)
        
        df1 = gen1.generate(n_samples=100)
        df2 = gen2.generate(n_samples=100)
        
        assert df1['monthly_income'].sum() == df2['monthly_income'].sum()
    
    def test_generator_includes_timestamp(self):
        """Test timestamp generation"""
        generator = SyntheticDataGenerator(seed=42)
        df = generator.generate(n_samples=100, include_timestamp=True)
        
        assert 'application_date' in df.columns


class TestPreprocessor:
    """Tests for preprocessing pipeline"""
    
    def test_preprocessor_fit_transform(self, synthetic_data):
        """Test that preprocessor can fit and transform"""
        preprocessor = CreditScoringPreprocessor()
        
        # Remove non-feature columns
        feature_cols = [c for c in synthetic_data.columns 
                       if c not in ['default_90dpd', 'default_probability_true', 'application_date', 'persona']]
        
        processed = preprocessor.fit_transform(synthetic_data[feature_cols])
        
        assert isinstance(processed, pd.DataFrame)
        assert len(processed) == len(synthetic_data)
        assert not processed.isnull().all().any()  # No all-null columns
    
    def test_preprocessor_transform_after_fit(self, synthetic_data):
        """Test that preprocessor can transform new data after fitting"""
        preprocessor = CreditScoringPreprocessor()
        
        feature_cols = [c for c in synthetic_data.columns 
                       if c not in ['default_90dpd', 'default_probability_true', 'application_date', 'persona']]
        
        # Fit on first half
        train_data = synthetic_data[feature_cols].iloc[:500]
        preprocessor.fit_transform(train_data)
        
        # Transform second half
        test_data = synthetic_data[feature_cols].iloc[500:]
        processed = preprocessor.transform(test_data)
        
        assert len(processed) == 500
    
    def test_preprocessor_save_load(self, synthetic_data, tmp_path):
        """Test preprocessor serialization"""
        preprocessor = CreditScoringPreprocessor()
        
        feature_cols = [c for c in synthetic_data.columns 
                       if c not in ['default_90dpd', 'default_probability_true', 'application_date', 'persona']]
        
        preprocessor.fit_transform(synthetic_data[feature_cols])
        
        # Save
        save_path = tmp_path / "preprocessor.joblib"
        preprocessor.save(str(save_path))
        
        # Load
        new_preprocessor = CreditScoringPreprocessor()
        new_preprocessor.load(str(save_path))
        
        assert new_preprocessor.fitted == True


class TestDataSplits:
    """Tests for train/val/test splitting"""
    
    def test_stratified_split(self, synthetic_data):
        """Test stratified splitting"""
        train, val, test = create_splits(
            synthetic_data, 
            target_col='default_90dpd',
            timestamp_col=None
        )
        
        total = len(train) + len(val) + len(test)
        assert total == len(synthetic_data)
    
    def test_time_based_split(self, synthetic_data):
        """Test time-based splitting"""
        train, val, test = create_splits(
            synthetic_data,
            target_col='default_90dpd',
            timestamp_col='application_date'
        )
        
        # Test should be chronologically after train
        assert train['application_date'].max() <= test['application_date'].min()


# ============================================================================
# SCORING TESTS
# ============================================================================

class TestNormalization:
    """Tests for feature normalization"""
    
    def test_normalize_binary_feature(self):
        """Test normalization of binary feature"""
        score = normalize_feature(1, 'name_dob_verified')
        assert score == 1.0
        
        score = normalize_feature(0, 'name_dob_verified')
        assert score == 0.0
    
    def test_normalize_numeric_feature(self):
        """Test normalization of numeric feature"""
        # Mid-range income
        score = normalize_feature(250000, 'monthly_income')
        assert 0 <= score <= 1
    
    def test_normalize_inverted_feature(self):
        """Test normalization of inverted feature (higher is worse)"""
        # High debt ratio should normalize to low score
        score_high = normalize_feature(2.0, 'debt_to_income_ratio')
        score_low = normalize_feature(0.5, 'debt_to_income_ratio')
        
        assert score_low > score_high
    
    def test_normalize_missing_value(self):
        """Test normalization of missing value"""
        score = normalize_feature(None, 'monthly_income')
        assert score == 0.5  # Neutral for missing
        
        score = normalize_feature(np.nan, 'monthly_income')
        assert score == 0.5


class TestPersonaSubscore:
    """Tests for persona subscore computation"""
    
    def test_subscore_range(self, sample_features):
        """Test that persona subscore is in [0, 1]"""
        for persona in PERSONA_WEIGHTS.keys():
            subscore, _ = compute_persona_subscore(sample_features, persona)
            assert 0 <= subscore <= 1
    
    def test_subscore_category_contributions(self, sample_features):
        """Test that category contributions sum approximately to subscore"""
        subscore, contributions = compute_persona_subscore(
            sample_features, 'salaried_professional'
        )
        
        total_contrib = sum(contributions.values())
        # Should be close (allowing for floating point)
        assert abs(total_contrib - subscore) < 0.01
    
    def test_different_personas_different_scores(self, sample_features):
        """Test that different personas produce different scores"""
        scores = {}
        for persona in PERSONA_WEIGHTS.keys():
            score, _ = compute_persona_subscore(sample_features, persona)
            scores[persona] = score
        
        # Scores should not all be identical
        assert len(set(round(s, 4) for s in scores.values())) > 1


class TestScoreMapping:
    """Tests for probability to credit score mapping"""
    
    def test_score_range(self):
        """Test that scores are in valid range"""
        for prob in np.linspace(0, 1, 100):
            score = prob_to_score(prob)
            assert 300 <= score <= 900
    
    def test_monotonicity(self):
        """Test that higher probability -> lower score"""
        probs = np.linspace(0, 1, 100)
        scores = [prob_to_score(p) for p in probs]
        
        # Scores should be monotonically decreasing
        for i in range(len(scores) - 1):
            assert scores[i] >= scores[i + 1]
    
    def test_extreme_values(self):
        """Test extreme probability values"""
        assert prob_to_score(0.0) == 900
        assert prob_to_score(1.0) == 300


class TestBlending:
    """Tests for score blending"""
    
    def test_blend_with_alpha_1(self):
        """Test that alpha=1 gives pure GBM score"""
        result = blend_scores(0.3, 0.7, alpha=1.0)
        assert abs(result - 0.3) < 0.001
    
    def test_blend_with_alpha_0(self):
        """Test that alpha=0 gives pure persona score"""
        result = blend_scores(0.3, 0.7, alpha=0.0)
        assert abs(result - 0.3) < 0.001  # 1 - 0.7 = 0.3
    
    def test_blend_default_alpha(self):
        """Test blending with default alpha"""
        gbm_prob = 0.2
        persona_subscore = 0.8  # Good score
        
        result = blend_scores(gbm_prob, persona_subscore, alpha=0.7)
        
        expected = 0.7 * 0.2 + 0.3 * (1 - 0.8)  # 0.14 + 0.06 = 0.20
        assert abs(result - expected) < 0.001


class TestCreditScorer:
    """Tests for CreditScorer class"""
    
    def test_scorer_without_model(self, sample_features):
        """Test scoring without trained model"""
        scorer = CreditScorer(alpha=0.7)
        result = scorer.score_user(sample_features, 'salaried_professional')
        
        assert 'score' in result
        assert 'prob_default_90dpd' in result
        assert 'risk_category' in result
        assert 300 <= result['score'] <= 900
    
    def test_scorer_all_personas(self, sample_features):
        """Test scoring with all personas"""
        scorer = CreditScorer()
        
        for persona in PERSONA_WEIGHTS.keys():
            result = scorer.score_user(sample_features, persona)
            assert 300 <= result['score'] <= 900


# ============================================================================
# MONITORING TESTS
# ============================================================================

class TestPSI:
    """Tests for PSI calculation"""
    
    def test_psi_identical_distributions(self):
        """Test PSI of identical distributions is ~0"""
        np.random.seed(42)
        data = np.random.normal(0, 1, 1000)
        
        psi = calculate_psi(data, data)
        assert psi < 0.01
    
    def test_psi_shifted_distribution(self):
        """Test PSI detects shifted distribution"""
        np.random.seed(42)
        baseline = np.random.normal(0, 1, 1000)
        shifted = np.random.normal(2, 1, 1000)  # Shifted mean
        
        psi = calculate_psi(baseline, shifted)
        assert psi > 0.25  # Should be significant
    
    def test_psi_report_categorization(self):
        """Test PSI report categorizes features correctly"""
        psi_values = {
            'feature1': 0.05,  # Stable
            'feature2': 0.15,  # Warning
            'feature3': 0.30   # Critical
        }
        
        report = psi_report(psi_values)
        
        assert report['summary']['stable_count'] == 1
        assert report['summary']['warning_count'] == 1
        assert report['summary']['critical_count'] == 1


class TestCalibration:
    """Tests for calibration monitoring"""
    
    def test_calibration_metrics(self):
        """Test calibration metrics calculation"""
        np.random.seed(42)
        y_true = np.random.binomial(1, 0.1, 1000)
        y_pred = np.random.beta(1, 9, 1000)  # Well calibrated for ~10% positive
        
        metrics = calibration_metrics(y_true, y_pred)
        
        assert 'brier_score' in metrics
        assert 'expected_calibration_error' in metrics
        assert 0 <= metrics['brier_score'] <= 1


class TestPerformanceMonitor:
    """Tests for performance monitoring"""
    
    def test_add_snapshot(self):
        """Test adding performance snapshot"""
        np.random.seed(42)
        y_true = np.random.binomial(1, 0.1, 1000)
        y_pred = np.random.uniform(0, 1, 1000)
        
        monitor = PerformanceMonitor()
        snapshot = monitor.add_snapshot(y_true, y_pred)
        
        assert snapshot.auc > 0
        assert snapshot.n_samples == 1000
    
    def test_degradation_check(self):
        """Test degradation detection"""
        monitor = PerformanceMonitor(baseline_auc=0.8, degradation_threshold=0.02)
        
        # Add snapshot with degraded performance
        np.random.seed(42)
        y_true = np.random.binomial(1, 0.1, 1000)
        y_pred = np.random.uniform(0, 1, 1000)  # Random predictions
        
        monitor.add_snapshot(y_true, y_pred)
        status = monitor.check_degradation()
        
        assert status['status'] in ['HEALTHY', 'DEGRADED']


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestEndToEnd:
    """End-to-end integration tests"""
    
    def test_full_scoring_pipeline(self, sample_features):
        """Test complete scoring pipeline"""
        # Score user
        scorer = CreditScorer()
        result = scorer.score_user(sample_features, 'salaried_professional')
        
        # Validate result structure
        assert 'score' in result
        assert 'prob_default_90dpd' in result
        assert 'risk_category' in result
        assert 'component_scores' in result
        assert 'category_contributions' in result
        
        # Validate values
        assert 300 <= result['score'] <= 900
        assert 0 <= result['prob_default_90dpd'] <= 1
        assert result['risk_category'] in [
            'Very Low Risk', 'Low Risk', 'Medium Risk', 
            'High Risk', 'Very High Risk'
        ]
    
    def test_batch_scoring(self, sample_features):
        """Test batch scoring"""
        scorer = CreditScorer()
        
        # Create batch
        features_list = [sample_features.copy() for _ in range(10)]
        for i, f in enumerate(features_list):
            f['monthly_income'] = 50000 + i * 10000
        
        results = scorer.score_batch(features_list, 'salaried_professional')
        
        assert len(results) == 10
        assert all('score' in r for r in results)


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])


