"""
MSME Credit Scoring Pipeline - Refactoring Summary
==================================================

## What Was Done

The entire MSME credit scoring pipeline has been **completely refactored** into a clean, modular architecture that is:
- ✅ Easy to understand
- ✅ Easy to maintain
- ✅ Easy to extend
- ✅ Production-ready
- ✅ Well-documented

## New Directory Structure

```
credit_scoring_pipeline/msme/
│
├── config/                          # All configuration in one place
│   ├── hyperparameters.py           # Model hyperparameters, Optuna config
│   ├── constants.py                 # Feature schemas, category mappings
│   └── feature_config.py            # Feature definitions
│
├── data/                            # Data generation & splitting
│   ├── synthetic_data_generator.py  # Generate realistic synthetic data
│   ├── data_splitter.py             # Train/val/test splitting
│   └── samplers.py                  # Sampling strategies (SMOTE, etc.)
│
├── preprocessing/                   # Feature preprocessing
│   ├── preprocessor.py              # Main preprocessor class
│   ├── feature_engineering.py       # Derived features
│   ├── scalers.py                   # Scaling transformations
│   └── encoders.py                  # Categorical encoding
│
├── models/                          # Model implementations
│   ├── lightgbm_model.py           # LightGBM wrapper class
│   ├── calibration.py              # Isotonic calibration
│   └── explainer.py                # SHAP explainability
│
├── training/                        # Training pipeline
│   ├── trainer.py                  # Main training orchestrator
│   ├── hyperparameter_tuner.py     # Optuna hyperparameter tuning
│   └── metrics.py                  # Evaluation metrics (AUC, Gini, KS)
│
├── evaluation/                      # Model evaluation
│   ├── evaluator.py                # Comprehensive evaluation
│   └── visualization.py            # Plots (calibration, SHAP, etc.)
│
├── scoring/                         # Scoring logic
│   ├── probability_to_score.py     # Probability → Credit Score (300-900)
│   ├── risk_tier.py                # Risk tier classification
│   └── loan_calculator.py          # Overdraft/loan limit calculation
│
├── rules/                           # Rule-based systems
│   ├── eligibility_checker.py      # Eligibility rules
│   ├── overdraft_calculator.py     # Overdraft calculations (Turnover, MPBF)
│   └── pricing_calculator.py       # Interest rate pricing
│
├── utils/                           # Utility functions
│   └── helpers.py                  # Common utilities
│
├── docs/                            # Documentation
│   └── README.md                   # Comprehensive documentation
│
└── main.py                          # Main orchestrator (SIMPLE!)

```

## Key Improvements

### 1. **Separation of Concerns**
Each module has ONE clear responsibility:
- `data/` → Data generation and splitting
- `preprocessing/` → Feature transformation
- `models/` → Model training and prediction
- `scoring/` → Score conversion and loan calculation
- `rules/` → Business rules and eligibility

### 2. **Clean Interfaces**
Simple, intuitive API:

```python
# Training (3 lines)
from msme.main import MSMEPipeline
pipeline = MSMEPipeline()
results = pipeline.run_training(n_samples=25000, tune_hyperparams=True)

# Scoring (2 lines)
pipeline.load_model()
result = pipeline.score_application(application_data)
```

### 3. **Configuration Management**
All hyperparameters in `config/hyperparameters.py`:
- Easy to modify
- No magic numbers in code
- Centralized configuration

### 4. **Modular Training**
Training split into logical steps:
1. Data generation (`data/synthetic_data_generator.py`)
2. Data splitting (`data/data_splitter.py`)
3. Preprocessing (`preprocessing/preprocessor.py`)
4. Hyperparameter tuning (`training/hyperparameter_tuner.py`)
5. Model training (`models/lightgbm_model.py`)
6. Evaluation (`evaluation/evaluator.py`)

### 5. **Scoring Pipeline**
Clear flow:
```
Raw Features → Preprocessing → LightGBM → Probability → Score → Risk Tier → Loan Limit
```

Each step in a separate module:
- `preprocessing/preprocessor.py`
- `models/lightgbm_model.py`
- `scoring/probability_to_score.py`
- `scoring/risk_tier.py`
- `scoring/loan_calculator.py`

### 6. **Rule-Based Calculations**
Loan limit calculation uses industry-standard formulas:
- **Turnover Method**: `Limit = Annual Turnover × Risk Multiplier`
- **MPBF Method**: `Limit = 0.75 × (Current Assets - Current Liabilities) - Debt`
- **Cash Flow Method**: `Limit = (Monthly Surplus / DSCR) / 0.03`

All in `scoring/loan_calculator.py`

## How to Use

### 1. Training a New Model

```python
from credit_scoring_pipeline.msme.main import MSMEPipeline

# Initialize pipeline
pipeline = MSMEPipeline(model_dir="my_model")

# Train with hyperparameter tuning
results = pipeline.run_training(
    n_samples=25000,
    tune_hyperparams=True,
    n_tuning_trials=50
)

print(f"Test AUC: {results['auc']:.4f}")
```

### 2. Scoring Applications

```python
# Load trained model
pipeline.load_model()

# Score new application
application_data = pd.DataFrame({
    'business_age_years': [5.0],
    'weekly_gtv': [350000],
    'monthly_gtv': [1400000],
    # ... other features
})

result = pipeline.score_application(application_data)

print(f"Credit Score: {result['credit_score']}")
print(f"Risk Tier: {result['risk_tier']}")
print(f"Eligible: {result['eligible']}")
print(f"Recommended Limit: ₹{result['recommended_limit']:,.0f}")
```

### 3. Custom Hyperparameters

Edit `config/hyperparameters.py`:

```python
DEFAULT_MSME_LGB_PARAMS = {
    'objective': 'binary',
    'n_estimators': 3000,  # Change this
    'learning_rate': 0.005,  # Or this
    # ... other params
}
```

### 4. Adding New Features

1. Update synthetic data generator (`data/synthetic_data_generator.py`)
2. Add feature engineering logic (`preprocessing/feature_engineering.py`)
3. Retrain model

## File Responsibilities

### Data Layer
- `synthetic_data_generator.py`: Creates realistic MSME data
- `data_splitter.py`: Splits data into train/val/test
- `samplers.py`: Handles class imbalance (SMOTE, undersampling)

### Preprocessing Layer
- `preprocessor.py`: Main preprocessing class (imputation, encoding, scaling)
- `feature_engineering.py`: Creates derived features
- `scalers.py`: Scaling transformations (StandardScaler, RobustScaler)
- `encoders.py`: Categorical encoding (LabelEncoder, OneHotEncoder)

### Model Layer
- `lightgbm_model.py`: LightGBM wrapper with train/predict/explain
- `calibration.py`: Isotonic calibration for probabilities
- `explainer.py`: SHAP value calculation

### Training Layer
- `trainer.py`: Training orchestrator
- `hyperparameter_tuner.py`: Optuna tuning
- `metrics.py`: AUC, Gini, KS, Precision@K

### Scoring Layer
- `probability_to_score.py`: Maps probability [0,1] → score [300,900]
- `risk_tier.py`: Classifies score into Prime/Near Prime/Standard/Subprime/High Risk
- `loan_calculator.py`: Calculates max loan using Turnover/MPBF/Cash Flow methods

### Rules Layer
- `eligibility_checker.py`: Business rules for eligibility
- `overdraft_calculator.py`: Overdraft-specific calculations
- `pricing_calculator.py`: Interest rate pricing based on risk

## Benefits of Refactoring

### 1. **Readability**
- Each file < 300 lines
- Clear function names
- Comprehensive docstrings

### 2. **Maintainability**
- Change hyperparameters in ONE place
- Modify scoring logic in ONE file
- Update rules without touching ML code

### 3. **Testability**
- Each module can be tested independently
- Clear inputs and outputs
- Easy to mock dependencies

### 4. **Extensibility**
- Add new features without breaking existing code
- Swap out LightGBM for another model easily
- Add new scoring rules without changing ML pipeline

### 5. **Production-Ready**
- Clean API for deployment
- Serializable artifacts
- Version control friendly

## Migration from Old Code

### Old Way (Everything in one file)
```python
# train.py (683 lines!)
# - Data generation
# - Preprocessing
# - Hyperparameter tuning
# - Training
# - Evaluation
# - Saving
# All mixed together!
```

### New Way (Modular)
```python
# Each module is focused
from msme.data.synthetic_data_generator import MSMESyntheticDataGenerator
from msme.data.data_splitter import create_msme_splits
from msme.preprocessing.preprocessor import MSMEPreprocessor
from msme.models.lightgbm_model import MSMECreditScoringModel
from msme.evaluation.evaluator import evaluate_msme_model

# Clear, readable workflow
generator = MSMESyntheticDataGenerator()
df = generator.generate(10000)
train, val, test = create_msme_splits(df)
preprocessor = MSMEPreprocessor()
# ... etc
```

## Technical Details

### LightGBM Configuration
- **Objective**: Binary classification (`default_90dpd` prediction)
- **Number of Trees**: Up to 2000 (with early stopping at 200 rounds)
- **Learning Rate**: 0.01 (slow, stable)
- **Max Depth**: 6 (prevents overfitting)
- **Regularization**: L1=1.0, L2=1.0

### Prediction Flow
1. **Raw Features** → `preprocessor.transform()`
2. **Processed Features** → `model.predict_proba()` → **Raw Probability**
3. **Raw Probability** → `calibrator.transform()` → **Calibrated Probability**
4. **Calibrated Probability** → `probability_to_score()` → **Credit Score**
5. **Credit Score** → `get_risk_tier()` → **Risk Tier**
6. **Risk Tier + Business Data** → `calculate_max_loan_limit()` → **Loan Limit**

### Default Probability → Score Mapping
```
Probability → Score
-----------   -----
0%            900
2%            750
5%            650
12%           550
25%           450
40%           400
60%           350
100%          300
```

## Next Steps

### To Use the Refactored Code:

1. **Train a model**:
```bash
cd credit_scoring_pipeline/msme
python main.py --train --samples 25000 --tune --trials 50
```

2. **Use in your application**:
```python
from credit_scoring_pipeline.msme.main import MSMEPipeline

pipeline = MSMEPipeline()
pipeline.load_model()
result = pipeline.score_application(your_data)
```

3. **Customize**:
- Edit `config/hyperparameters.py` for model params
- Edit `scoring/risk_tier.py` for risk tiers
- Edit `scoring/loan_calculator.py` for loan formulas

## Summary

✅ **Completely refactored** from monolithic files to modular architecture
✅ **Clean separation** of data, preprocessing, training, scoring, rules
✅ **Simple API** for training and scoring
✅ **Production-ready** with clear interfaces
✅ **Well-documented** with comprehensive README
✅ **Easy to maintain** - change one thing in one place
✅ **Easy to extend** - add features without breaking existing code
✅ **Easy to test** - each module is independent

The code is now **professional, readable, and maintainable**! 🚀

