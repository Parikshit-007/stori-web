# MSME Credit Scoring - Training Flow

## Complete Step-by-Step Code Walkthrough

This document explains exactly what happens when you run:
```bash
python train.py --data msme_comprehensive_training_data.csv --tune --trials 30
```

---

## Table of Contents
1. [Entry Point](#1-entry-point)
2. [Data Loading](#2-data-loading)
3. [Data Splitting](#3-data-splitting)
4. [Preprocessing](#4-preprocessing)
5. [Hyperparameter Tuning](#5-hyperparameter-tuning)
6. [Model Training](#6-model-training)
7. [Probability Calibration](#7-probability-calibration)
8. [SHAP Initialization](#8-shap-initialization)
9. [Evaluation](#9-evaluation)
10. [Model Saving](#10-model-saving)

---

## 1. Entry Point

### File: `train.py` (lines 662-680)

```python
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
```

**What happens:**
1. Parse command-line arguments
2. Call `main()` function with parsed values

**Flow diagram:**
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Command Line  │ --> │  argparse       │ --> │    main()       │
│   Arguments     │     │  Parsing        │     │    Function     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## 2. Data Loading

### File: `train.py` (lines 570-580)

```python
def main(data_path: str = None, ...):
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate or load data
    if data_path and os.path.exists(data_path):
        print(f"\nLoading data from {data_path}...")
        df = pd.read_csv(data_path)  # <-- YOUR DATA LOADS HERE
    else:
        print(f"\nGenerating {n_samples} synthetic MSME samples...")
        generator = MSMESyntheticDataGenerator(seed=42)
        df = generator.generate(n_samples=n_samples, missing_rate=0.05)
```

**What happens:**
1. Check if CSV file exists at provided path
2. If exists: Load with pandas (`pd.read_csv`)
3. If not: Generate synthetic data with `MSMESyntheticDataGenerator`

**Your data structure:**
```
┌─────────────────────────────────────────────────────────────────────┐
│                    msme_comprehensive_training_data.csv              │
├─────────────────────────────────────────────────────────────────────┤
│ Rows: 10,200 samples                                                 │
│ Columns: 90 features                                                 │
│                                                                      │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ business_segment | industry_code | business_age_years | ...     │ │
│ │ micro_new        | retail        | 3.5                | ...     │ │
│ │ small_trading    | services      | 7.2                | ...     │ │
│ │ ...              | ...           | ...                | ...     │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│ Target Column: default_90dpd (0 or 1)                               │
│ Default Rate: 9.25%                                                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Splitting

### File: `data_prep.py` (lines 1390-1428)

```python
def create_msme_splits(df: pd.DataFrame,
                       target_col: str = 'default_90dpd',
                       timestamp_col: Optional[str] = 'application_date',
                       test_size: float = 0.15,
                       val_size: float = 0.15,
                       random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    
    if timestamp_col and timestamp_col in df.columns:
        # TIME-BASED SPLIT (used for your data)
        df_sorted = df.sort_values(timestamp_col).reset_index(drop=True)
        n = len(df_sorted)
        
        test_idx = int(n * (1 - test_size))        # 85% point
        val_idx = int(test_idx * (1 - val_size / (1 - test_size)))  # 70% point
        
        train_df = df_sorted.iloc[:val_idx].copy()      # First 70%
        val_df = df_sorted.iloc[val_idx:test_idx].copy() # 70-85%
        test_df = df_sorted.iloc[test_idx:].copy()       # Last 15%
```

**What happens:**
1. Sort data by `application_date` (chronological order)
2. Split into 70% train / 15% validation / 15% test
3. This simulates real-world scenario: train on past, test on future

**Split visualization:**
```
Timeline: Jan 2023 ────────────────────────────────────────> Dec 2024

┌──────────────────────┬───────────┬───────────┐
│       TRAIN          │    VAL    │   TEST    │
│      70% = 7140      │15% = 1530 │15% = 1530 │
│   Earlier dates      │  Middle   │  Latest   │
│   (learn from)       │ (tune)    │ (evaluate)│
└──────────────────────┴───────────┴───────────┘

Why time-based?
- Prevents data leakage (no future information in training)
- Mimics real deployment (predict future defaults)
```

---

## 4. Preprocessing

### File: `train.py` (lines 588-609)

```python
# Preprocess
print("\nPreprocessing data...")
preprocessor = MSMEPreprocessor()

# Columns to exclude from features
exclude_cols = ['default_90dpd', 'default_probability_true', 'application_date', 'business_segment']
feature_cols = [c for c in train_df.columns if c not in exclude_cols]

# Fit on training data, transform all sets
train_processed = preprocessor.fit_transform(train_df[feature_cols])
val_processed = preprocessor.transform(val_df[feature_cols])
test_processed = preprocessor.transform(test_df[feature_cols])
```

### File: `data_prep.py` (lines 1334-1356) - The Preprocessor

```python
def fit_transform(self, df: pd.DataFrame, normalize: bool = False) -> pd.DataFrame:
    """Fit preprocessor and transform data"""
    self.fitted = False
    
    df = self._clip_outliers(df)       # Step 1: Clip outliers
    df = self._impute_missing(df)      # Step 2: Fill missing values
    df = self._encode_categoricals(df) # Step 3: Encode categories
    df = self._engineer_features(df)   # Step 4: Create new features
    
    self.fitted = True
    return df
```

**Preprocessing steps:**

### Step 4.1: Clip Outliers
```python
def _clip_outliers(self, df: pd.DataFrame, lower_pct: float = 1, upper_pct: float = 99):
    # For each numeric feature:
    # Clip values to 1st-99th percentile range
    
    # Example for weekly_gtv:
    # Before: [8000, 50000, 100000, ..., 999999999 (outlier)]
    # After:  [8000, 50000, 100000, ..., 50000000 (capped)]
```

### Step 4.2: Impute Missing Values
```python
def _impute_missing(self, df: pd.DataFrame):
    # Numeric: Replace NaN with median
    # Categorical: Replace NaN with mode (most frequent)
    
    # Example:
    # weekly_gtv: [100K, NaN, 200K] → [100K, 150K, 200K] (median=150K)
    # industry_code: ['retail', NaN, 'services'] → ['retail', 'retail', 'services']
```

### Step 4.3: Encode Categorical Features
```python
def _encode_categoricals(self, df: pd.DataFrame):
    # Convert text categories to numbers using LabelEncoder
    
    # legal_entity_type:
    # ['proprietorship', 'partnership', 'llp', 'private_limited']
    # →  [0, 1, 2, 3]
    
    # industry_code:
    # ['retail', 'trading', 'services', 'manufacturing', ...]
    # →  [0, 1, 2, 3, ...]
```

### Step 4.4: Feature Engineering
```python
def _engineer_features(self, df: pd.DataFrame):
    # Create derived features from existing ones
    
    # Cash coverage ratio
    df['cash_coverage_ratio'] = df['avg_bank_balance'] / (df['monthly_gtv'] / 30 + 1)
    
    # Debt to revenue ratio
    df['debt_to_revenue_ratio'] = df['total_debt_amount'] / (df['monthly_gtv'] * 12 + 1)
    
    # Working capital days
    df['working_capital_days'] = df['receivables_aging_days'] - df['payables_aging_days']
    
    # Overall payment discipline (average of payment ratios)
    payment_cols = ['utility_payment_ontime_ratio', 'rent_payment_ontime_ratio', 
                   'supplier_payment_ontime_ratio', 'overdraft_repayment_ontime_ratio']
    df['overall_payment_discipline'] = df[payment_cols].mean(axis=1)
    
    # Overall compliance score
    compliance_cols = ['gst_filing_regularity', 'tax_payment_regularity', 'itr_filed']
    df['overall_compliance_score'] = df[compliance_cols].mean(axis=1)
    
    # Fraud risk indicator
    df['fraud_risk_indicator'] = (df['pan_address_bank_mismatch'] + 
                                 (df['kyc_attempts_count'] > 3).astype(int))
```

**Final feature count:**
```
Original features:    86 (90 columns - 4 excluded)
+ Engineered features: 6
= Total features:     92
```

---

## 5. Hyperparameter Tuning

### File: `train.py` (lines 133-197)

```python
class MSMEOptunaObjective:
    """Optuna objective for MSME model tuning"""
    
    def __call__(self, trial: optuna.Trial) -> float:
        # Suggest hyperparameters
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
            ...
        }
        
        # Train quick model with these params
        model = lgb.train(params, train_data, num_boost_round=1000, ...)
        
        # Return validation AUC (higher is better)
        y_pred = model.predict(self.X_val)
        return roc_auc_score(self.y_val, y_pred)


def run_msme_hyperparameter_tuning(X_train, y_train, X_val, y_val, ...):
    sampler = TPESampler(seed=42)  # Tree-structured Parzen Estimator
    study = optuna.create_study(direction='maximize', sampler=sampler)
    study.optimize(objective, n_trials=n_trials, show_progress_bar=True)
```

**Optuna TPE Algorithm:**
```
┌────────────────────────────────────────────────────────────────────┐
│                  OPTUNA TPE HYPERPARAMETER SEARCH                   │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Trial 1: Random params → AUC = 0.77                                │
│  Trial 2: Random params → AUC = 0.78                                │
│  Trial 3: Random params → AUC = 0.79                                │
│  ...                                                                 │
│  Trial 10: TPE suggests based on history → AUC = 0.80               │
│                                                                      │
│  TPE builds TWO probability distributions:                          │
│  - l(x): Distribution of "good" hyperparameters (top 25% AUC)       │
│  - g(x): Distribution of all hyperparameters                        │
│                                                                      │
│  Next suggestion: maximize l(x)/g(x)                                │
│  (Find params likely to be good but haven't been tried)             │
│                                                                      │
│  Trial 30 (final): Best AUC = 0.8004                                │
│  Best params: {                                                      │
│    'num_leaves': 101,                                               │
│    'max_depth': 9,                                                  │
│    'learning_rate': 0.014,                                          │
│    'feature_fraction': 0.69,                                        │
│    'bagging_fraction': 0.98,                                        │
│    'min_child_samples': 100,                                        │
│    'reg_alpha': 0.39,                                               │
│    'reg_lambda': 0.003                                              │
│  }                                                                   │
└────────────────────────────────────────────────────────────────────┘
```

---

## 6. Model Training

### File: `train.py` (lines 246-282)

```python
def train(self, X_train, y_train, X_val, y_val, ...):
    # Prepare LightGBM datasets
    train_data = lgb.Dataset(
        X_train, label=y_train,
        categorical_feature=self.categorical_features,  # ['legal_entity_type', 'industry_code', ...]
        feature_name=self.feature_names
    )
    val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
    
    # Calculate class weight for imbalanced data
    n_negative = (y_train == 0).sum()  # 6466 non-defaults
    n_positive = (y_train == 1).sum()  # 674 defaults
    scale_pos_weight = n_negative / n_positive  # 9.59
    lgb_params['scale_pos_weight'] = min(scale_pos_weight, 10.0)
    
    # Setup callbacks
    callbacks = [
        lgb.early_stopping(200),  # Stop if no improvement for 200 rounds
        lgb.log_evaluation(100)   # Print progress every 100 rounds
    ]
    
    # TRAIN THE MODEL
    self.model = lgb.train(
        lgb_params,
        train_data,
        num_boost_round=2000,      # Max 2000 trees
        valid_sets=[train_data, val_data],
        valid_names=['train', 'valid'],
        callbacks=callbacks
    )
```

**What happens inside `lgb.train()`:**

```
┌────────────────────────────────────────────────────────────────────┐
│                    LIGHTGBM TRAINING LOOP                           │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  INITIALIZATION:                                                     │
│  ├── F₀(x) = log(p/(1-p)) where p = mean(y_train) = 0.0944          │
│  └── F₀(x) = log(0.0944/0.9056) = -2.26 (log-odds)                  │
│                                                                      │
│  FOR round = 1 to 2000:                                              │
│  │                                                                   │
│  │  STEP 1: Compute Gradients                                       │
│  │  ────────────────────────────────────────────                    │
│  │  For each sample i:                                              │
│  │    pᵢ = sigmoid(F(xᵢ)) = 1/(1 + exp(-F(xᵢ)))                     │
│  │    gᵢ = pᵢ - yᵢ                  # gradient                      │
│  │    hᵢ = pᵢ × (1 - pᵢ)            # hessian                       │
│  │                                                                   │
│  │  STEP 2: Build Histograms (for each feature)                     │
│  │  ────────────────────────────────────────────                    │
│  │  Feature: bounced_cheques_count                                  │
│  │  ┌─────────────────────────────────────────┐                     │
│  │  │ Bin │ Range │ Count │   Σg   │   Σh   │                      │
│  │  │  0  │  0    │ 4231  │ -1.23  │ 380.5  │                      │
│  │  │  1  │  1    │ 1892  │ +0.45  │ 168.3  │                      │
│  │  │  2  │  2    │  823  │ +0.62  │  71.2  │                      │
│  │  │  3  │ 3-5   │  312  │ +0.34  │  26.8  │                      │
│  │  │  4  │ 6+    │   82  │ +0.18  │   6.9  │                      │
│  │  └─────────────────────────────────────────┘                     │
│  │                                                                   │
│  │  STEP 3: Find Best Splits (Leaf-wise)                            │
│  │  ────────────────────────────────────────────                    │
│  │  Current tree structure:                                         │
│  │                                                                   │
│  │          [Root]                                                  │
│  │         /      \                                                 │
│  │      [L1]      [L2]                                              │
│  │     gain=0.18  gain=0.05                                         │
│  │                                                                   │
│  │  Split L1 (highest gain):                                        │
│  │  - Best feature: overdraft_repayment_ontime_ratio                │
│  │  - Best threshold: 0.65                                          │
│  │  - Gain: 0.18                                                    │
│  │                                                                   │
│  │  STEP 4: Compute Leaf Values                                     │
│  │  ────────────────────────────────────────────                    │
│  │  For each leaf j:                                                │
│  │    wⱼ = -Gⱼ / (Hⱼ + λ)                                           │
│  │                                                                   │
│  │  Example leaf (high default risk):                               │
│  │    Gⱼ = +2.3 (positive = under-predicted defaults)               │
│  │    Hⱼ = 45.2                                                     │
│  │    wⱼ = -2.3 / (45.2 + 1.0) = -0.050                             │
│  │    (Negative weight = decrease prediction = WRONG!)              │
│  │                                                                   │
│  │    Wait, let me recalculate:                                     │
│  │    If samples are defaults (y=1) but predicted low (p=0.2):      │
│  │    g = p - y = 0.2 - 1 = -0.8 (NEGATIVE gradient)                │
│  │    Leaf value = -(-0.8) / H = +0.017                             │
│  │    (Positive = increase prediction = CORRECT!)                    │
│  │                                                                   │
│  │  STEP 5: Update Predictions                                      │
│  │  ────────────────────────────────────────────                    │
│  │  F(x) = F(x) + learning_rate × tree_output                       │
│  │  F(x) = -2.26 + 0.014 × (+0.017)                                 │
│  │  F(x) = -2.2597 (slightly higher = more default risk)            │
│  │                                                                   │
│  │  STEP 6: Evaluate on Validation Set                              │
│  │  ────────────────────────────────────────────                    │
│  │  AUC_train = 0.9820                                              │
│  │  AUC_valid = 0.7911                                              │
│  │  Log-loss_valid = 0.3329                                         │
│  │                                                                   │
│  │  Early stopping check:                                           │
│  │  - Best valid AUC so far: 0.7902 (round 12)                      │
│  │  - Current round: 100                                            │
│  │  - Rounds without improvement: 88                                │
│  │  - Threshold: 200                                                │
│  │  - Continue training...                                          │
│  │                                                                   │
│  ROUND 200:                                                          │
│  - AUC_valid = 0.7862 (worse than round 12!)                        │
│  - Rounds without improvement: 188                                   │
│  - Continue...                                                       │
│                                                                      │
│  ROUND 212: Early stopping triggered!                                │
│  - 200 rounds without improvement                                    │
│  - Revert to best model (round 12)                                  │
│                                                                      │
└────────────────────────────────────────────────────────────────────┘

Final model: 12 trees (early stopped from max 2000)
```

---

## 7. Probability Calibration

### File: `train.py` (lines 299-303)

```python
def _calibrate(self, X_val, y_val):
    """Calibrate predictions using Isotonic Regression"""
    raw_probs = self.model.predict(X_val)  # Raw LightGBM outputs
    self.calibrator = IsotonicRegression(out_of_bounds='clip')
    self.calibrator.fit(raw_probs, y_val)  # Learn mapping
```

**Why calibration is needed:**

```
┌────────────────────────────────────────────────────────────────────┐
│                    PROBABILITY CALIBRATION                          │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  PROBLEM: LightGBM outputs are NOT true probabilities               │
│                                                                      │
│  Raw output = 0.15 doesn't mean "15% will actually default"         │
│                                                                      │
│  Example of miscalibration:                                          │
│  ┌────────────────────────────────────────────────────────┐         │
│  │ Raw Prediction │ Actual Default Rate │ Calibrated     │         │
│  │     0.05       │       0.03          │    0.03        │         │
│  │     0.15       │       0.09          │    0.09        │         │
│  │     0.30       │       0.22          │    0.22        │         │
│  │     0.50       │       0.40          │    0.40        │         │
│  └────────────────────────────────────────────────────────┘         │
│                                                                      │
│  Isotonic Regression learns this mapping:                           │
│                                                                      │
│  Actual     │                    ●                                  │
│  Default    │               ●                                       │
│  Rate       │          ●                                            │
│             │      ●                                                │
│             │  ●                                                    │
│             └───────────────────────────                            │
│                  Raw Prediction                                     │
│                                                                      │
│  The line is monotonically increasing (isotonic constraint)         │
│                                                                      │
└────────────────────────────────────────────────────────────────────┘
```

---

## 8. SHAP Initialization

### File: `train.py` (lines 290-292)

```python
# Initialize SHAP explainer
print("Initializing SHAP explainer...")
self.shap_explainer = shap.TreeExplainer(self.model)
```

**What SHAP does:**

```
┌────────────────────────────────────────────────────────────────────┐
│                    SHAP EXPLAINABILITY                              │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  For each prediction, SHAP decomposes it into feature contributions │
│                                                                      │
│  Example MSME (predicted default prob = 0.23):                       │
│                                                                      │
│  Base value (average): 0.0925                                       │
│                                                                      │
│  + bounced_cheques_count = 5:     +0.058  ← Increases risk          │
│  + overdraft_ratio = 0.45:        +0.042  ← Increases risk          │
│  + previous_defaults = 1:         +0.035  ← Increases risk          │
│  + weekly_gtv = 2M:               -0.015  ← Decreases risk          │
│  + gst_filing_regularity = 0.95:  -0.008  ← Decreases risk          │
│  + ... (other features):          +0.025                            │
│  ─────────────────────────────────────────                          │
│  = Final prediction:               0.2295                           │
│                                                                      │
│  SHAP values sum to: prediction - base_value                        │
│  0.2295 - 0.0925 = 0.137 = sum of all SHAP values                   │
│                                                                      │
│  This is used in your API response:                                 │
│  {                                                                   │
│    "explanation": {                                                  │
│      "base_value": -2.30,                                           │
│      "top_positive_features": [                                     │
│        {"feature": "bounced_cheques_count", "shap_value": 0.058}   │
│      ],                                                              │
│      "top_negative_features": [                                     │
│        {"feature": "weekly_gtv", "shap_value": -0.015}             │
│      ]                                                               │
│    }                                                                 │
│  }                                                                   │
│                                                                      │
└────────────────────────────────────────────────────────────────────┘
```

---

## 9. Evaluation

### File: `train.py` (lines 452-551)

```python
def evaluate_msme_model(model, X_test, y_test, output_dir):
    # Get predictions
    y_pred_proba = model.predict_proba(X_test)
    
    # Calculate metrics
    auc = roc_auc_score(y_test, y_pred_proba)
    gini = 2 * auc - 1
    ks_stat, ks_thresh = compute_ks_statistic(y_test.values, y_pred_proba)
    brier = brier_score_loss(y_test, y_pred_proba)
    
    # Convert to credit scores and analyze by bucket
    scores = np.array([msme_prob_to_score(p) for p in y_pred_proba])
    bucket_metrics = compute_risk_bucket_metrics(y_test.values, scores)
```

**Evaluation metrics:**

```
┌────────────────────────────────────────────────────────────────────┐
│                    MODEL EVALUATION METRICS                         │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. AUC-ROC (Area Under ROC Curve): 0.7252                          │
│     ─────────────────────────────────────────                       │
│     Measures ranking ability: probability that a randomly           │
│     chosen defaulter is ranked higher than a non-defaulter          │
│     - 0.5 = Random guessing                                         │
│     - 0.7-0.8 = Good discrimination                                 │
│     - 0.8+ = Excellent                                              │
│                                                                      │
│  2. Gini Coefficient: 0.4503                                        │
│     ─────────────────────────────────────────                       │
│     Gini = 2 × AUC - 1                                              │
│     - 0 = No discrimination                                         │
│     - 1 = Perfect discrimination                                    │
│                                                                      │
│  3. KS Statistic: 0.3582                                            │
│     ─────────────────────────────────────────                       │
│     Maximum separation between cumulative distributions             │
│     of defaulters and non-defaulters                                │
│     - > 0.3 = Good separation                                       │
│     - > 0.4 = Very good                                             │
│                                                                      │
│  4. Brier Score: 0.0794                                             │
│     ─────────────────────────────────────────                       │
│     Mean squared error of probability predictions                   │
│     - Lower is better                                               │
│     - < 0.1 is good for rare events                                 │
│                                                                      │
│  5. Risk Bucket Analysis:                                           │
│     ─────────────────────────────────────────                       │
│     ┌─────────────┬───────┬─────────────┐                          │
│     │ Score Range │ Count │ Default Rate│                          │
│     ├─────────────┼───────┼─────────────┤                          │
│     │ 300-449     │  119  │    25.2%    │ ← Very High Risk         │
│     │ 450-549     │  426  │    15.3%    │ ← High Risk              │
│     │ 550-649     │  421  │     7.4%    │ ← Medium Risk            │
│     │ 750-900     │  564  │     2.7%    │ ← Very Low Risk          │
│     └─────────────┴───────┴─────────────┘                          │
│                                                                      │
│     Good model: Default rate decreases as score increases           │
│                                                                      │
└────────────────────────────────────────────────────────────────────┘
```

---

## 10. Model Saving

### File: `train.py` (lines 627-652)

```python
# Save model
model.save(os.path.join(output_dir, 'msme_credit_scoring_model.joblib'))
preprocessor.save(os.path.join(output_dir, 'msme_preprocessor.joblib'))

# Save feature list
with open(os.path.join(output_dir, 'feature_list.json'), 'w') as f:
    json.dump({
        'features': list(train_processed.columns),
        'categorical_features': categorical_features,
        'target': 'default_90dpd'
    }, f, indent=2)

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
```

**Saved artifacts:**

```
msme_model_artifacts/
├── msme_credit_scoring_model.joblib   # The trained model
│   ├── model (LightGBM Booster)
│   ├── calibrator (IsotonicRegression)
│   ├── params (hyperparameters)
│   ├── feature_names (list of 92 features)
│   └── training_metrics
│
├── msme_preprocessor.joblib           # The preprocessor
│   ├── feature_bounds (outlier clip values)
│   ├── imputers (median/mode values)
│   ├── encoders (label encoders for categoricals)
│   └── scalers (if normalization enabled)
│
├── feature_list.json                  # Feature metadata
├── training_config.json               # Full training record
│
└── evaluation/
    ├── feature_importance.png         # Top 25 features bar chart
    ├── calibration_plot.png           # Calibration curve
    ├── shap_summary.png               # SHAP beeswarm plot
    └── evaluation_metrics.json        # All metrics
```

---

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     MSME CREDIT SCORING TRAINING PIPELINE                    │
└─────────────────────────────────────────────────────────────────────────────┘

     ┌──────────────────┐
     │  1. Load CSV     │
     │  10,200 samples  │
     └────────┬─────────┘
              │
              ▼
     ┌──────────────────┐
     │  2. Split Data   │
     │  Train/Val/Test  │
     │  70% / 15% / 15% │
     └────────┬─────────┘
              │
              ▼
     ┌──────────────────┐
     │  3. Preprocess   │
     │  • Clip outliers │
     │  • Impute missing│
     │  • Encode cats   │
     │  • Engineer feats│
     └────────┬─────────┘
              │
              ▼
     ┌──────────────────┐
     │  4. Tune Params  │
     │  Optuna (30 runs)│
     │  Best AUC: 0.80  │
     └────────┬─────────┘
              │
              ▼
     ┌──────────────────┐
     │  5. Train Model  │
     │  LightGBM GBDT   │
     │  12 trees        │
     │  (early stopped) │
     └────────┬─────────┘
              │
              ▼
     ┌──────────────────┐
     │  6. Calibrate    │
     │  Isotonic Regr.  │
     └────────┬─────────┘
              │
              ▼
     ┌──────────────────┐
     │  7. Init SHAP    │
     │  TreeExplainer   │
     └────────┬─────────┘
              │
              ▼
     ┌──────────────────┐
     │  8. Evaluate     │
     │  AUC: 0.725      │
     │  KS: 0.358       │
     └────────┬─────────┘
              │
              ▼
     ┌──────────────────┐
     │  9. Save Model   │
     │  .joblib files   │
     └──────────────────┘
```

---

*Next: See [HYPERPARAMETERS_GUIDE.md](./HYPERPARAMETERS_GUIDE.md) for detailed parameter explanations*


