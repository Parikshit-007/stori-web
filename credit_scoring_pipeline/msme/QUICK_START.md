"""
MSME Credit Scoring Pipeline - Quick Start Guide
================================================

## 🚀 Get Started in 5 Minutes

### Prerequisites
```bash
pip install pandas numpy scikit-learn lightgbm optuna shap matplotlib joblib
```

### 1. Train a Model (One Command!)

```bash
cd credit_scoring_pipeline/msme
python main.py --train --samples 25000 --tune --trials 50
```

This will:
- ✅ Generate 25,000 synthetic MSME samples
- ✅ Split into train/val/test
- ✅ Run hyperparameter tuning (50 trials)
- ✅ Train LightGBM model
- ✅ Calibrate probabilities
- ✅ Evaluate on test set
- ✅ Save model artifacts

**Output**: `msme_model_artifacts/` directory with trained model


### 2. Score Applications (Python API)

```python
from credit_scoring_pipeline.msme.main import MSMEPipeline
import pandas as pd

# Initialize pipeline
pipeline = MSMEPipeline()
pipeline.load_model()

# Prepare application data
application = pd.DataFrame({
    'business_age_years': [5.0],
    'weekly_gtv': [350000],
    'monthly_gtv': [1400000],
    'industry_code': ['retail'],
    'legal_entity_type': ['proprietorship'],
    'bounced_cheques_count': [0],
    'gst_filing_regularity': [0.95],
    'overdraft_repayment_ontime_ratio': [0.90],
    # ... add other required features
})

# Score
result = pipeline.score_application(application)

# Results
print(f"Credit Score: {result['credit_score']}")
print(f"Risk Tier: {result['risk_tier']}")
print(f"Eligible: {result['eligible']}")
print(f"Recommended Limit: ₹{result['recommended_limit']:,.0f}")
print(f"Interest Rate: {result['interest_rate_range']['min']}-{result['interest_rate_range']['max']}%")
```


### 3. Use Individual Modules

#### Generate Synthetic Data
```python
from credit_scoring_pipeline.msme.data.synthetic_data_generator import MSMESyntheticDataGenerator

generator = MSMESyntheticDataGenerator(seed=42)
df = generator.generate(n_samples=10000, missing_rate=0.05)
df.to_csv('msme_data.csv', index=False)
```

#### Split Data
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

#### Preprocess Features
```python
from credit_scoring_pipeline.msme.preprocessing.preprocessor import MSMEPreprocessor

preprocessor = MSMEPreprocessor()

# Fit on training data
train_processed = preprocessor.fit_transform(train_df)

# Transform validation/test data
val_processed = preprocessor.transform(val_df)
test_processed = preprocessor.transform(test_df)

# Save preprocessor
preprocessor.save('preprocessor.joblib')
```

#### Train Model
```python
from credit_scoring_pipeline.msme.models.lightgbm_model import MSMECreditScoringModel

model = MSMECreditScoringModel()
model.train(
    train_processed, y_train,
    val_processed, y_val,
    categorical_features=[],
    tune_hyperparams=True,
    n_tuning_trials=50
)

# Save model
model.save('model.joblib')
```

#### Evaluate Model
```python
from credit_scoring_pipeline.msme.evaluation.evaluator import evaluate_msme_model

results = evaluate_msme_model(
    model,
    test_processed,
    y_test,
    output_dir='evaluation_results'
)

print(f"AUC: {results['auc']:.4f}")
print(f"Gini: {results['gini']:.4f}")
print(f"KS Statistic: {results['ks_statistic']:.4f}")
```

#### Score Conversion
```python
from credit_scoring_pipeline.msme.scoring.probability_to_score import msme_prob_to_score
from credit_scoring_pipeline.msme.scoring.risk_tier import get_risk_tier

# Get probability from model
prob = model.predict_proba(X_new)[0]

# Convert to score
score = msme_prob_to_score(prob)

# Get risk tier
tier = get_risk_tier(score)

print(f"Probability: {prob:.2%}")
print(f"Score: {score}")
print(f"Tier: {tier.name}")
print(f"Eligible: {tier.eligible}")
```

#### Calculate Loan Limit
```python
from credit_scoring_pipeline.msme.scoring.loan_calculator import calculate_max_loan_limit
from credit_scoring_pipeline.msme.scoring.risk_tier import get_risk_tier

tier = get_risk_tier(score)

limits = calculate_max_loan_limit(
    annual_turnover=16_800_000,  # ₹1.68 Cr
    monthly_surplus=200_000,      # ₹2 Lakhs
    risk_tier_multiplier=tier.turnover_multiplier,
    dscr_required=tier.dscr_required,
    current_assets=8_000_000,     # ₹80 Lakhs
    current_liabilities=4_000_000, # ₹40 Lakhs
    existing_debt=1_000_000       # ₹10 Lakhs
)

print(f"Turnover Method: ₹{limits['turnover_method']:,.0f}")
print(f"Cash Flow Method: ₹{limits['cash_flow_method']:,.0f}")
print(f"MPBF Method: ₹{limits['mpbf_method']:,.0f}")
print(f"Recommended: ₹{limits['recommended_limit']:,.0f}")
```


## 📊 Understanding Results

### Credit Score Ranges
| Score     | Tier       | Default Risk | Eligible |
|-----------|------------|--------------|----------|
| 750-900   | Prime      | 0-2%         | ✅ Yes   |
| 650-749   | Near Prime | 2-5%         | ✅ Yes   |
| 550-649   | Standard   | 5-12%        | ✅ Yes   |
| 450-549   | Subprime   | 12-25%       | ✅ Yes   |
| 300-449   | High Risk  | 25%+         | ❌ No    |

### Risk Tier Parameters
| Tier       | Turnover Multiplier | Interest Rate | DSCR | Max Tenure |
|------------|---------------------|---------------|------|------------|
| Prime      | 40%                 | 10-14%        | 1.20 | 24 months  |
| Near Prime | 30%                 | 13-16%        | 1.35 | 18 months  |
| Standard   | 25%                 | 15-19%        | 1.50 | 12 months  |
| Subprime   | 15%                 | 18-22%        | 1.75 | 12 months  |
| High Risk  | 0%                  | 22-26%        | 2.00 | 6 months   |


## 🔧 Customization

### Change Hyperparameters
Edit `config/hyperparameters.py`:
```python
DEFAULT_MSME_LGB_PARAMS = {
    'n_estimators': 3000,      # Change number of trees
    'learning_rate': 0.005,    # Slower learning
    'max_depth': 8,            # Deeper trees
    # ... other params
}
```

### Modify Risk Tiers
Edit `scoring/risk_tier.py`:
```python
RISK_TIERS = {
    'prime': RiskTier(
        name='Prime',
        min_score=750,
        max_score=900,
        turnover_multiplier=0.45,  # Change this
        interest_rate_min=9.0,     # Or this
        # ... other params
    ),
    # ... other tiers
}
```

### Adjust Score Mapping
Edit `scoring/probability_to_score.py`:
```python
def probability_to_score(prob):
    breakpoints = [
        (0.00, 900),
        (0.015, 800),  # Adjust breakpoints
        (0.03, 700),
        # ... other breakpoints
    ]
    # ... conversion logic
```


## 📝 Production Deployment

### 1. Save Artifacts
```python
# Training phase
model.save('artifacts/model.joblib')
preprocessor.save('artifacts/preprocessor.joblib')
```

### 2. Load in Production
```python
# Production API
from msme.main import MSMEPipeline

# Initialize once (at startup)
pipeline = MSMEPipeline(model_dir='artifacts')
pipeline.load_model()

# Score many applications
for application in applications:
    result = pipeline.score_application(application)
    save_to_database(result)
```

### 3. Create REST API (FastAPI Example)
```python
from fastapi import FastAPI
from msme.main import MSMEPipeline
import pandas as pd

app = FastAPI()
pipeline = MSMEPipeline()
pipeline.load_model()

@app.post("/score")
async def score_application(data: dict):
    df = pd.DataFrame([data])
    result = pipeline.score_application(df)
    return result
```


## 🐛 Troubleshooting

### Issue: Model not loading
```python
# Check if files exist
import os
print(os.path.exists('msme_model_artifacts/msme_credit_scoring_model.joblib'))
print(os.path.exists('msme_model_artifacts/msme_preprocessor.joblib'))
```

### Issue: Missing features
```python
# Check required features
from msme.config.feature_config import MSME_FEATURE_SCHEMA
print(list(MSME_FEATURE_SCHEMA.keys()))
```

### Issue: Poor model performance
1. Increase training samples: `--samples 50000`
2. Run more tuning trials: `--trials 100`
3. Check data quality in synthetic generator
4. Verify feature engineering logic


## 📚 Next Steps

1. **Read Documentation**:
   - `docs/README.md` - Full documentation
   - `ARCHITECTURE_DIAGRAM.md` - System architecture
   - `REFACTORING_SUMMARY.md` - Refactoring details

2. **Explore Code**:
   - Start with `main.py` - Simple entry point
   - Review `scoring/` modules - Scoring logic
   - Check `models/lightgbm_model.py` - ML model

3. **Customize**:
   - Modify `config/` for parameters
   - Update `scoring/risk_tier.py` for business rules
   - Extend `preprocessing/feature_engineering.py` for new features

4. **Deploy**:
   - Create REST API with FastAPI/Flask
   - Set up batch scoring pipeline
   - Implement monitoring and logging


## ✅ Summary

You now have:
- ✅ Clean, modular codebase
- ✅ Trained LightGBM model
- ✅ Simple Python API for scoring
- ✅ Comprehensive documentation
- ✅ Production-ready architecture

**Need help?** Check the documentation or contact the ML Engineering Team.

Happy scoring! 🚀


