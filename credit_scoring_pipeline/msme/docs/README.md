"""
MSME Credit Scoring Pipeline - Refactored Architecture
======================================================

This is a completely refactored, modular version of the MSME credit scoring pipeline.

## Directory Structure

```
credit_scoring_pipeline/msme/
│
├── config/                          # Configuration files
│   ├── __init__.py
│   ├── constants.py                 # Constants and feature schemas
│   ├── hyperparameters.py           # Model hyperparameters
│   └── feature_config.py            # Feature definitions
│
├── data/                            # Data generation and processing
│   ├── __init__.py
│   ├── synthetic_data_generator.py  # Synthetic data generation
│   ├── data_splitter.py             # Train/val/test splitting
│   └── samplers.py                  # Sampling strategies
│
├── preprocessing/                   # Feature preprocessing
│   ├── __init__.py
│   ├── preprocessor.py              # Main preprocessor
│   ├── feature_engineering.py       # Feature engineering
│   ├── scalers.py                   # Scaling transformations
│   └── encoders.py                  # Categorical encoding
│
├── models/                          # Model implementations
│   ├── __init__.py
│   ├── lightgbm_model.py           # LightGBM wrapper
│   ├── calibration.py              # Probability calibration
│   └── explainer.py                # SHAP explainability
│
├── training/                        # Training pipeline
│   ├── __init__.py
│   ├── trainer.py                  # Main training orchestrator
│   ├── hyperparameter_tuner.py     # Optuna tuning
│   └── metrics.py                  # Evaluation metrics
│
├── evaluation/                      # Model evaluation
│   ├── __init__.py
│   ├── evaluator.py                # Model evaluation
│   └── visualization.py            # Plots and charts
│
├── scoring/                         # Scoring logic
│   ├── __init__.py
│   ├── probability_to_score.py     # Prob to score conversion
│   ├── risk_tier.py                # Risk tier classification
│   └── loan_calculator.py          # Loan limit calculation
│
├── rules/                           # Rule-based logic
│   ├── __init__.py
│   ├── eligibility_checker.py      # Eligibility rules
│   ├── overdraft_calculator.py     # Overdraft calculations
│   └── pricing_calculator.py       # Interest rate pricing
│
├── utils/                           # Utility functions
│   ├── __init__.py
│   └── helpers.py                  # Common utilities
│
├── docs/                            # Documentation
│   ├── README.md                   # This file
│   ├── TRAINING_FLOW.md            # Training workflow
│   ├── LIGHTGBM_DEEP_DIVE.md       # LightGBM details
│   └── HYPERPARAMETERS_GUIDE.md    # Hyperparameter guide
│
├── main.py                          # Main orchestrator
├── train.py                         # Training script
├── score.py                         # Scoring script
└── app.py                           # API application

```

## Key Features

### 1. Modular Design
- Each component has a single, well-defined responsibility
- Easy to test, maintain, and extend
- Clear separation of concerns

### 2. Configuration Management
- Centralized configuration in `config/`
- Easy to modify hyperparameters
- Feature schemas and constants in one place

### 3. Data Pipeline
- Synthetic data generation with realistic patterns
- Time-based and stratified splitting
- Flexible sampling strategies

### 4. Preprocessing Pipeline
- Automated feature engineering
- Robust handling of missing values
- Categorical encoding and scaling

### 5. Training Pipeline
- LightGBM with binary classification
- Automated hyperparameter tuning with Optuna
- Isotonic calibration for probabilities
- SHAP explainability

### 6. Scoring Pipeline
- Probability to score conversion (300-900 scale)
- Risk tier classification
- Loan limit calculation using multiple methods

### 7. Rule-Based Systems
- Eligibility checking
- Overdraft calculations (Turnover, MPBF, Cash Flow)
- Dynamic interest rate pricing

## Usage Examples

### 1. Generate Synthetic Data

```python
from credit_scoring_pipeline.msme.data.synthetic_data_generator import MSMESyntheticDataGenerator

generator = MSMESyntheticDataGenerator(seed=42)
df = generator.generate(n_samples=10000, missing_rate=0.05)
```

### 2. Split Data

```python
from credit_scoring_pipeline.msme.data.data_splitter import create_msme_splits

train_df, val_df, test_df = create_msme_splits(
    df, 
    target_col='default_90dpd',
    timestamp_col='application_date',
    test_size=0.15,
    val_size=0.15
)
```

### 3. Train Model

```python
from credit_scoring_pipeline.msme.training.trainer import MSMETrainer

trainer = MSMETrainer()
model = trainer.train(
    train_df, val_df,
    tune_hyperparams=True,
    n_tuning_trials=50
)
```

### 4. Score New Applications

```python
from credit_scoring_pipeline.msme.scoring.probability_to_score import msme_prob_to_score
from credit_scoring_pipeline.msme.scoring.risk_tier import get_risk_tier

# Get default probability
prob = model.predict_proba(X_new)[0]

# Convert to score
score = msme_prob_to_score(prob)

# Get risk tier
tier = get_risk_tier(score)

print(f"Probability: {prob:.2%}, Score: {score}, Tier: {tier.name}")
```

### 5. Calculate Loan Limit

```python
from credit_scoring_pipeline.msme.scoring.loan_calculator import calculate_max_loan_limit
from credit_scoring_pipeline.msme.scoring.risk_tier import get_risk_tier

tier = get_risk_tier(score)

limits = calculate_max_loan_limit(
    annual_turnover=12_000_000,
    monthly_surplus=150_000,
    risk_tier_multiplier=tier.turnover_multiplier,
    dscr_required=tier.dscr_required
)

print(f"Recommended Limit: ₹{limits['recommended_limit']:,.0f}")
```

## Model Architecture

### LightGBM Configuration
- **Objective**: Binary classification (`default_90dpd`)
- **Number of Trees**: Up to 2000 (with early stopping)
- **Learning Rate**: 0.01 (slow, stable learning)
- **Max Depth**: 6 (prevents overfitting)
- **Regularization**: L1=1.0, L2=1.0

### Prediction Flow
1. **Raw Features** → Preprocessing (imputation, encoding, scaling)
2. **Processed Features** → LightGBM Model
3. **Raw Probability** → Isotonic Calibration
4. **Calibrated Probability** → Score Conversion (300-900)
5. **Score** → Risk Tier + Loan Limit

## Training Process

1. **Data Generation**: Synthetic data with realistic patterns
2. **Data Splitting**: Time-based or stratified split
3. **Preprocessing**: Imputation, encoding, feature engineering
4. **Hyperparameter Tuning** (optional): Optuna with 50-100 trials
5. **Model Training**: LightGBM with early stopping
6. **Calibration**: Isotonic regression on validation set
7. **Evaluation**: AUC, Gini, KS, Brier score, bucket analysis
8. **SHAP Analysis**: Feature importance and explainability
9. **Model Saving**: Serialized artifacts for deployment

## Key Formulas

### Default Probability → Credit Score
Uses piecewise linear interpolation:
- 0% default → 900 score
- 2% default → 750 score
- 5% default → 650 score
- 12% default → 550 score
- 25% default → 450 score
- 40% default → 400 score
- 60% default → 350 score
- 100% default → 300 score

### Overdraft Limit (Turnover Method)
```
OD_Limit = Annual_Turnover × Risk_Tier_Multiplier
```

### DSCR (Debt Service Coverage Ratio)
```
DSCR = Net_Operating_Income / Total_Debt_Service
```

## Best Practices

1. **Always use time-based splits** for production models
2. **Calibrate probabilities** before score conversion
3. **Monitor class imbalance** and adjust `scale_pos_weight`
4. **Use early stopping** to prevent overfitting
5. **Generate SHAP values** for explainability
6. **Validate on holdout test set** before deployment
7. **Document hyperparameter choices** and rationale

## Maintenance

### Adding New Features
1. Add feature schema to `config/feature_config.py`
2. Update synthetic data generator if needed
3. Add feature engineering logic to `preprocessing/feature_engineering.py`
4. Retrain model with new features

### Updating Model
1. Modify hyperparameters in `config/hyperparameters.py`
2. Run hyperparameter tuning
3. Compare metrics with previous version
4. Deploy if improved

### Debugging
1. Check data quality in synthetic generator
2. Verify preprocessing outputs
3. Examine feature importance from SHAP
4. Review calibration plots
5. Analyze bucket-wise default rates

## Support

For questions or issues:
- Check documentation in `docs/`
- Review code comments
- Contact ML Engineering Team

---

**Version**: 2.0.0  
**Last Updated**: 2026-01-10  
**Author**: ML Engineering Team
