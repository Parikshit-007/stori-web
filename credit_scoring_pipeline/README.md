# Credit Scoring Pipeline

A production-ready Gradient Boosting Machine (GBM) credit scoring pipeline that predicts 90-DPD default probability, produces calibrated probabilities, and maps them to credit scores (300–900). The system blends GBM model outputs with persona-driven weight subscores.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Usage](#usage)
5. [API Reference](#api-reference)
6. [Persona Weights & Category Scoring](#persona-weights--category-scoring)
7. [Model Training](#model-training)
8. [Evaluation Metrics](#evaluation-metrics)
9. [Monitoring & Governance](#monitoring--governance)
10. [Bias & Fairness](#bias--fairness)

---

## Overview

### Key Features

- **LightGBM-based credit scoring** with careful categorical handling
- **5 Persona Types** with customized weight distributions:
  - New-to-Credit (NTC)
  - Gig Worker / Freelancer
  - Salaried Professional
  - Credit-Experienced Borrower
  - Mass Affluent / High Asset
- **7 Scoring Categories** (A-G) with specific feature mappings
- **SHAP Explainability** for global and individual predictions
- **Calibrated Probabilities** using isotonic regression
- **Credit Score Mapping** (300-900) with piecewise linear calibration
- **FastAPI REST API** with bearer token authentication

### Score Components

1. **GBM Model Prediction**: Raw probability from LightGBM model
2. **Persona Subscore**: Weighted aggregation of normalized features by category
3. **Blended Score**: `final_prob = α × gbm_pred + (1-α) × (1 - persona_subscore)`

---

## Architecture

```
credit_scoring_pipeline/
├── data_prep.py          # Data schema, synthetic generator, preprocessing
├── train.py              # Training pipeline with hyperparameter tuning
├── score.py              # Scoring functions with persona blending
├── app.py                # FastAPI application
├── feature_config.json   # Feature configuration and weights
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

---

## Installation

### Prerequisites

- Python 3.8+
- pip or conda

### Setup

```bash
# Clone or navigate to the project
cd credit_scoring_pipeline

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## Usage

### 1. Train the Model

```bash
# Train with synthetic data (default)
python train.py --samples 20000 --output model_artifacts

# Train with hyperparameter tuning
python train.py --samples 20000 --tune --trials 50 --output model_artifacts

# Train with custom data
python train.py --data path/to/your/data.csv --output model_artifacts
```

### 2. Score Users

```python
from score import CreditScorer

# Initialize scorer with trained model
scorer = CreditScorer(
    model_path='model_artifacts/credit_scoring_model.joblib',
    preprocessor_path='model_artifacts/preprocessor.joblib',
    alpha=0.7  # GBM weight (default 0.7)
)

# Score a user
features = {
    'monthly_income': 75000,
    'avg_account_balance': 150000,
    'income_stability_score': 0.85,
    'repayment_ontime_ratio': 0.92,
    'credit_card_utilization': 0.35,
    'budgeting_score': 0.7,
    # ... more features
}

result = scorer.score_user(features, persona='salaried_professional')
print(f"Credit Score: {result['score']}")
print(f"Default Probability: {result['prob_default_90dpd']}")
print(f"Risk Category: {result['risk_category']}")
```

### 3. Start the API

```bash
# Start API server
python app.py --host 0.0.0.0 --port 8000

# With auto-reload for development
python app.py --reload
```

### 4. API Usage

```bash
# Health check
curl http://localhost:8000/api/health

# Score a user (requires auth token)
curl -X POST http://localhost:8000/api/score \
  -H "Authorization: Bearer dev_token_12345" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "monthly_income": 75000,
      "repayment_ontime_ratio": 0.92,
      "credit_card_utilization": 0.35
    },
    "persona": "salaried_professional",
    "alpha": 0.7
  }'
```

---

## API Reference

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/model/info` | GET | Model metadata |
| `/api/score` | POST | Score a user |
| `/api/explain` | POST | Get SHAP explanation |
| `/api/features/{id}` | GET | Get user features (stub) |
| `/api/personas` | GET | List available personas |
| `/api/categories` | GET | List scoring categories |

### Authentication

Use Bearer token in Authorization header:
```
Authorization: Bearer dev_token_12345
```

Development tokens:
- `dev_token_12345` (developer)
- `test_token_abcde` (tester)

---

## Persona Weights & Category Scoring

### How Persona Subscore is Computed

1. **Normalize Raw Features**: Each feature is normalized to [0,1] using domain-specific bounds. Higher normalized value = lower risk.

2. **Aggregate by Parameter Group**: Features are grouped into parameter groups (e.g., `income_proxies`, `utility_payments`).

3. **Compute Category Scores**: Parameter groups are weighted within each category using persona-specific intra-weights.

4. **Compute Persona Subscore**: 
   ```
   persona_subscore = Σ(category_score × category_weight)
   ```

5. **Blend with GBM**:
   ```
   final_prob = α × gbm_prob + (1-α) × (1 - persona_subscore)
   ```
   Note: `(1 - persona_subscore)` converts the "goodness" score to a risk probability.

### Category Weights (Default)

| Category | Weight | Description |
|----------|--------|-------------|
| A: Identity & Demographics | 10% | Name, phone, email, location, education, employment |
| B: Income & Cash Flow | 25% | Income, balance, ITR, employability, PPF |
| C: Assets & Liabilities | 20% | Loans, credit cards, LIC, FD, assets |
| D: Spending & Behavioral | 25% | Spending patterns, subscriptions, financial habits |
| E: Transactions & Repayments | 15% | UPI, utility, repayment behavior |
| F: Fraud & Identity | 5% | Face match, fraud history, verification |
| G: Family & Network | 5% | Spouse/family credit, dependents |

### Persona-Specific Adjustments

Each persona redistributes weights based on what's most predictive:

| Persona | Focus Areas |
|---------|-------------|
| New-to-Credit | Income (35%), Behavioral (30%), Identity (15%) |
| Gig Worker | Income (40%), Behavioral (25%), Transactions (14%) |
| Salaried | Income (30%), Assets (25%), Transactions (15%) |
| Credit Experienced | Assets (40%), Income (20%), Transactions (15%) |
| Mass Affluent | Assets (45%), Income (20%), Transactions (15%) |

---

## Model Training

### Training Pipeline

1. **Data Loading**: Load from file or generate synthetic data
2. **Time-Based Split**: Train (70%), Validation (15%), Test (15%)
3. **Preprocessing**: Imputation, outlier clipping, encoding
4. **Hyperparameter Tuning**: Optuna with TPE sampler
5. **Model Training**: LightGBM with early stopping
6. **Calibration**: Isotonic regression on validation set
7. **Evaluation**: AUC, KS, Gini, calibration, risk buckets
8. **Artifact Export**: Model, preprocessor, config files

### Hyperparameters (Default)

```python
{
    'objective': 'binary',
    'boosting_type': 'gbdt',
    'num_leaves': 31,
    'max_depth': 6,
    'learning_rate': 0.05,
    'feature_fraction': 0.8,
    'bagging_fraction': 0.8,
    'reg_alpha': 0.1,
    'reg_lambda': 0.1,
    'n_estimators': 500,
    'early_stopping_rounds': 50
}
```

---

## Evaluation Metrics

### Core Metrics

- **AUC-ROC**: Area under ROC curve
- **Gini Coefficient**: 2 × AUC - 1
- **KS Statistic**: Max separation between TPR and FPR
- **Brier Score**: Calibration quality

### Precision at K

- Precision@5%: Capture rate in top 5% of predictions
- Precision@10%, 20%, 30%

### Risk Bucket Analysis

| Score Range | Risk Level | Expected Default Rate |
|-------------|------------|----------------------|
| 800-900 | Very Low | ~2% |
| 700-799 | Low | ~5% |
| 600-699 | Medium | ~10% |
| 500-599 | High | ~20% |
| 300-499 | Very High | ~35% |

---

## Monitoring & Governance

### Recommended Monitoring

1. **Population Stability Index (PSI)**
   - Threshold: 0.25
   - Check frequency: Daily/Weekly
   - Trigger retraining if exceeded

2. **Feature Distribution Drift**
   - Monitor mean, std, percentiles
   - Threshold: 10% drift in key features
   - Alert channels: Email, Slack

3. **Calibration Monitoring**
   - Check Brier score weekly
   - Compare predicted vs actual by decile
   - Recalibrate if drift > 5%

4. **Label Delay Handling**
   - 90 DPD requires 90+ days observation
   - Use proxy labels for faster feedback
   - Maintain label currency < 30 days

### Retraining Schedule

- **Regular Retraining**: Every 90 days
- **Triggered Retraining**: When PSI > 0.25
- **Emergency Retraining**: Significant performance drop

### Governance Checklist

- [ ] Model documentation updated
- [ ] Performance metrics logged
- [ ] A/B testing completed
- [ ] Stakeholder approval obtained
- [ ] Rollback plan documented
- [ ] Monitoring dashboards active

---

## Bias & Fairness

### Sensitive Features

The following features may introduce bias and require monitoring:

- `location_tier`: Geographic discrimination risk
- `education_level`: Educational bias
- `employment_type`: Employment discrimination
- `dependents_count`: Family status bias

### Fairness Checks

1. **Demographic Parity**: Score distributions by group
2. **Equal Opportunity**: TPR equality across groups
3. **Calibration Parity**: Predicted vs actual by group

### Mitigation Strategies

1. Exclude sensitive features from model (if legally required)
2. Post-hoc calibration per demographic group
3. Regularization to reduce feature importance
4. Synthetic minority oversampling (if applicable)

### Monitoring Code Example

```python
def check_score_parity(scores, groups):
    """Check if score distributions differ significantly by group"""
    from scipy import stats
    
    group_scores = {}
    for group in np.unique(groups):
        group_scores[group] = scores[groups == group]
    
    # Perform KS test between groups
    groups_list = list(group_scores.keys())
    for i in range(len(groups_list)):
        for j in range(i+1, len(groups_list)):
            ks_stat, p_val = stats.ks_2samp(
                group_scores[groups_list[i]],
                group_scores[groups_list[j]]
            )
            if p_val < 0.05:
                print(f"WARNING: Significant difference between {groups_list[i]} and {groups_list[j]}")
```

---

## Blending & Calibration Explanation

### How Persona Weights and GBM Outputs are Blended

The credit scoring system uses a two-component approach to generate final scores:

**Component 1: GBM Model Prediction**
The LightGBM model learns patterns directly from historical data to predict 90-day default probability. It processes all normalized features and outputs a calibrated probability. The model captures complex non-linear relationships and feature interactions that may not be explicitly encoded in the persona weights.

**Component 2: Persona Subscore**
The persona subscore provides a domain-knowledge-driven assessment based on:
- Feature normalization using domain-specific bounds
- Parameter group aggregation (averaging features within logical groups)
- Category-level weighting (using persona-specific importance weights)
- Final aggregation: weighted sum across all 7 categories (A-G)

The subscore represents a "goodness" metric where higher values indicate lower risk. This is converted to a risk probability using `(1 - persona_subscore)`.

**Blending Formula**
```
final_prob = α × gbm_prediction + (1-α) × (1 - persona_subscore)
```

Default α = 0.7, meaning:
- 70% weight on the data-driven GBM model
- 30% weight on the domain-knowledge persona subscore

This blending allows the system to:
1. Leverage ML's pattern recognition capabilities
2. Incorporate expert domain knowledge through persona weights
3. Handle edge cases where one component may be more reliable
4. Provide interpretable category-level contributions

**Calibration to Credit Score**
The final probability is mapped to a 300-900 credit score using piecewise linear interpolation calibrated on holdout data. Lower probability → Higher score, with breakpoints aligned to expected default rates in each risk bucket.

---

## License

MIT License - See LICENSE file for details.

## Support

For issues or questions, please open a GitHub issue or contact the ML Engineering team.


