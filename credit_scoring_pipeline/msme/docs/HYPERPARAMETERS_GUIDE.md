# LightGBM Hyperparameters Guide - MSME Credit Scoring

## Complete Reference for All Parameters Used

This guide explains every hyperparameter in your MSME credit scoring model, why each value was chosen, and how to tune them.

---

## Table of Contents
1. [Quick Reference Table](#quick-reference-table)
2. [Objective & Metric Parameters](#objective--metric-parameters)
3. [Tree Structure Parameters](#tree-structure-parameters)
4. [Learning Parameters](#learning-parameters)
5. [Regularization Parameters](#regularization-parameters)
6. [Sampling Parameters](#sampling-parameters)
7. [Class Imbalance Parameters](#class-imbalance-parameters)
8. [Training Control Parameters](#training-control-parameters)
9. [Tuning Recommendations](#tuning-recommendations)

---

## Quick Reference Table

| Parameter | Your Value | Range | Purpose |
|-----------|------------|-------|---------|
| `objective` | `binary` | - | Binary classification |
| `metric` | `['auc', 'binary_logloss']` | - | Evaluation metrics |
| `boosting_type` | `gbdt` | `gbdt`, `dart`, `goss` | Boosting algorithm |
| `num_leaves` | `31→101` | 20-200 | Tree complexity |
| `max_depth` | `6→9` | 4-15 | Max tree depth |
| `learning_rate` | `0.01→0.014` | 0.001-0.3 | Step size |
| `feature_fraction` | `0.8→0.69` | 0.5-1.0 | Features per tree |
| `bagging_fraction` | `0.8→0.98` | 0.5-1.0 | Samples per tree |
| `bagging_freq` | `3→8` | 1-10 | Bagging frequency |
| `min_child_samples` | `50→100` | 10-200 | Min samples in leaf |
| `reg_alpha` | `1.0→0.39` | 0-10 | L1 regularization |
| `reg_lambda` | `1.0→0.003` | 0-10 | L2 regularization |
| `n_estimators` | `2000` | 100-5000 | Max boosting rounds |
| `early_stopping_rounds` | `200` | 50-500 | Patience |
| `scale_pos_weight` | `9.59` | Auto | Class balance |

*Values with `→` show: default → after Optuna tuning*

---

## Objective & Metric Parameters

### `objective`: `'binary'`

**What it does:** Defines the loss function to optimize.

```python
'objective': 'binary'  # For classification (default/no-default)
```

**Options for classification:**
| Value | Use Case | Loss Function |
|-------|----------|---------------|
| `binary` | Two classes (0/1) | Binary cross-entropy |
| `multiclass` | Multiple classes | Multi-class log loss |
| `cross_entropy` | Probability labels | Cross-entropy |

**For credit scoring:** Always use `binary` for default prediction.

---

### `metric`: `['auc', 'binary_logloss']`

**What it does:** Metrics to evaluate during training.

```python
'metric': ['auc', 'binary_logloss']
```

**Available metrics:**
| Metric | Formula | Best Value | Use When |
|--------|---------|------------|----------|
| `auc` | Area Under ROC | 1.0 | Ranking matters |
| `binary_logloss` | -Σ[y×log(p) + (1-y)×log(1-p)] | 0.0 | Probability calibration matters |
| `binary_error` | Error rate | 0.0 | Simple accuracy |
| `average_precision` | PR-AUC | 1.0 | Imbalanced data |

**For credit scoring:** Use `auc` as primary (ranking is crucial), `binary_logloss` as secondary (monitors calibration).

---

### `boosting_type`: `'gbdt'`

**What it does:** Chooses the boosting algorithm.

```python
'boosting_type': 'gbdt'  # Gradient Boosting Decision Tree
```

**Options:**
| Type | Description | Speed | Accuracy | Best For |
|------|-------------|-------|----------|----------|
| `gbdt` | Traditional gradient boosting | Medium | Best | Most cases |
| `dart` | Dropouts during training | Slow | Good | Overfitting prevention |
| `goss` | Gradient-based One-Side Sampling | Fast | Good | Large datasets |
| `rf` | Random Forest (no boosting) | Fast | Lower | Baseline |

**For credit scoring:** `gbdt` provides best accuracy. Use `goss` if training is too slow.

---

## Tree Structure Parameters

### `num_leaves`: `31 → 101` (after tuning)

**What it does:** Maximum number of leaves in each tree.

```python
'num_leaves': 101  # After Optuna tuning
```

**How it affects the model:**

```
num_leaves = 8 (simple):
        [Root]
       /      \
    [A]        [B]
   / \        / \
 [1] [2]    [3] [4]
     
Only captures simple patterns like:
"If bounced_cheques > 3, high risk"


num_leaves = 31 (moderate):
Can capture patterns like:
"If bounced_cheques > 3 AND overdraft_ratio < 0.6 
 AND business_age < 2, very high risk"


num_leaves = 101 (complex):
Can capture intricate interactions:
"If (bounced_cheques > 3 OR previous_defaults > 0)
 AND overdraft_ratio < 0.6
 AND NOT (business_age > 5 AND gstin_verified = 1)
 AND weekly_gtv < 500000, extremely high risk"
```

**Tuning guide:**
| Dataset Size | Recommended `num_leaves` |
|--------------|-------------------------|
| < 1,000 | 8-16 |
| 1,000-10,000 | 16-63 |
| 10,000-100,000 | 31-127 |
| > 100,000 | 63-255 |

**Your model:** With 10,200 samples, `num_leaves=101` is aggressive but controlled by regularization.

---

### `max_depth`: `6 → 9` (after tuning)

**What it does:** Maximum depth of each tree (limits tree height).

```python
'max_depth': 9
```

**Interaction with `num_leaves`:**

```
max_depth=6 can have at most 2^6 = 64 leaves
max_depth=9 can have at most 2^9 = 512 leaves

BUT with num_leaves=101:
- Actual leaves: min(101, 2^9) = 101
- Creates asymmetric trees (leaf-wise growth)
```

**Why limit depth?**
- Deep trees memorize training data (overfitting)
- Shallow trees capture general patterns

**Relationship:**
```
For balanced tree: num_leaves ≈ 2^max_depth
For asymmetric (LightGBM default): num_leaves < 2^max_depth

Your config: 101 < 2^9 = 512 ✓ (asymmetric, leaf-wise)
```

---

### `min_child_samples` / `min_data_in_leaf`: `50 → 100`

**What it does:** Minimum samples required in each leaf.

```python
'min_child_samples': 100  # After tuning
'min_data_in_leaf': 50    # Same purpose
```

**How it prevents overfitting:**

```
BAD: min_child_samples=5
Leaf with 5 samples, 3 defaults → 60% default rate
This is noise! Not a real pattern.


GOOD: min_child_samples=100
Leaf with 100 samples, 35 defaults → 35% default rate
This is statistically significant!
```

**Statistical justification:**
```
For 95% confidence interval on proportion:
CI = p ± 1.96 × sqrt(p(1-p)/n)

With n=100, p=0.35:
CI = 0.35 ± 0.093 = [0.26, 0.44]

With n=10, p=0.35:
CI = 0.35 ± 0.30 = [0.05, 0.65]  ← Too wide!
```

**Tuning guide:**
| Default Rate | Min Samples | Rationale |
|--------------|-------------|-----------|
| < 5% | 50-100 | Need more to see rare events |
| 5-15% | 30-50 | Moderate |
| > 15% | 20-30 | Enough signal |

---

## Learning Parameters

### `learning_rate`: `0.01 → 0.014`

**What it does:** Shrinks contribution of each tree.

```python
'learning_rate': 0.014  # After tuning
```

**Mathematical effect:**
```
F_new(x) = F_old(x) + learning_rate × tree_output

With learning_rate = 1.0 (no shrinkage):
F_new = F_old + 1.0 × tree   # Full update, fast but overfit

With learning_rate = 0.01 (your default):
F_new = F_old + 0.01 × tree  # 1% update, slow but robust
```

**Trade-off:**
```
┌──────────────────────────────────────────────────────────────┐
│          LEARNING RATE VS NUMBER OF TREES                    │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  learning_rate=0.1, n_estimators=100                         │
│  → Fast training, potential overfitting                       │
│                                                               │
│  learning_rate=0.01, n_estimators=1000                       │
│  → Slow training, better generalization (YOUR CHOICE)         │
│                                                               │
│  Rule: learning_rate × n_estimators ≈ constant               │
│                                                               │
│  Your setup: 0.014 × 2000 = 28 (effective trees)             │
│  But early stopped at 12 trees                                │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

### `n_estimators`: `2000`

**What it does:** Maximum number of boosting rounds (trees).

```python
'n_estimators': 2000  # Maximum trees to build
```

**With early stopping:**
```
Set high (2000) and let early_stopping find optimal number.

Your model stopped at 12 trees because:
- Validation AUC peaked at round 12
- No improvement for 200 rounds
- Final model uses 12 trees only
```

---

## Regularization Parameters

### `reg_alpha` (L1): `1.0 → 0.39`

**What it does:** L1 regularization on leaf weights.

```python
'reg_alpha': 0.39  # After tuning (was 1.0)
```

**Mathematical effect:**
```
Objective = Loss + reg_alpha × Σ|wⱼ|

Where wⱼ = leaf weights

L1 pushes small weights to EXACTLY zero:
- Before: weights = [0.5, 0.3, 0.001, -0.002, 0.4]
- After:  weights = [0.45, 0.25, 0, 0, 0.35]

Effect: Feature selection (zeroes out unimportant splits)
```

---

### `reg_lambda` (L2): `1.0 → 0.003`

**What it does:** L2 regularization on leaf weights.

```python
'reg_lambda': 0.003  # After tuning (was 1.0)
```

**Mathematical effect:**
```
Objective = Loss + reg_lambda × Σ(wⱼ)²

L2 shrinks ALL weights toward zero:
- Before: weights = [0.5, 0.3, 0.001, -0.002, 0.4]
- After:  weights = [0.4, 0.24, 0.0008, -0.0016, 0.32]

Effect: Smoother predictions (no extreme values)
```

**Your tuned values:**
```
reg_alpha = 0.39 (moderate L1)
reg_lambda = 0.003 (very low L2)

Interpretation: Model prefers feature selection (L1) 
over weight shrinkage (L2)
```

---

## Sampling Parameters

### `feature_fraction`: `0.8 → 0.69`

**What it does:** Fraction of features used for each tree.

```python
'feature_fraction': 0.69  # Use 69% of features per tree
```

**How it works:**
```
With 92 features and feature_fraction=0.69:
Each tree randomly selects: int(92 × 0.69) = 63 features

Tree 1 uses: {bounced_cheques, weekly_gtv, overdraft_ratio, ...} (63 features)
Tree 2 uses: {business_age, gst_filing, bank_balance, ...} (different 63 features)

Benefits:
1. Reduces overfitting (trees see different views)
2. Decorrelates trees (ensemble diversity)
3. Faster training (fewer features to evaluate)
```

---

### `bagging_fraction`: `0.8 → 0.98`

**What it does:** Fraction of samples used for each tree.

```python
'bagging_fraction': 0.98  # Use 98% of samples per tree
```

**How it works:**
```
With 7,140 training samples and bagging_fraction=0.98:
Each tree randomly selects: int(7140 × 0.98) = 6,997 samples

Tree 1 trains on: {sample_1, sample_2, ..., sample_6997}
Tree 2 trains on: {sample_3, sample_5, ..., sample_7001} (different selection)
```

**Your tuned value (0.98):** Nearly all samples used, minimal variance from bagging.

---

### `bagging_freq`: `3 → 8`

**What it does:** How often to apply bagging.

```python
'bagging_freq': 8  # Apply bagging every 8 trees
```

**Effect:**
```
bagging_freq=1: Different samples for EVERY tree (maximum randomness)
bagging_freq=8: Same samples for 8 consecutive trees, then resample

Your value (8): Moderate randomness, reduces training variance
```

---

## Class Imbalance Parameters

### `scale_pos_weight`: `9.59` (auto-calculated)

**What it does:** Weights positive class (defaults) higher.

```python
# Calculated in your code:
n_negative = 6466  # Non-defaulters
n_positive = 674   # Defaulters
scale_pos_weight = 6466 / 674 = 9.59
```

**Effect on loss function:**
```
Standard loss:
L = -[y × log(p) + (1-y) × log(1-p)]

With scale_pos_weight=9.59:
L = -[9.59 × y × log(p) + (1-y) × log(1-p)]

Each defaulter contributes 9.59× more to the loss!

Effectively makes training set:
- 6466 non-defaulters (unchanged)
- 674 × 9.59 = 6463 virtual defaulters

Result: Balanced learning
```

---

### `is_unbalance`: `False`

**What it does:** Alternative automatic balancing.

```python
'is_unbalance': False  # Don't use; using scale_pos_weight instead
```

**Comparison:**
| Method | How It Works | Control |
|--------|--------------|---------|
| `scale_pos_weight` | Manual weight ratio | Full control |
| `is_unbalance=True` | Auto calculates weight | Less control |

**Your choice:** `scale_pos_weight` for explicit control.

---

## Training Control Parameters

### `early_stopping_rounds`: `200`

**What it does:** Stops training if no improvement for N rounds.

```python
'early_stopping_rounds': 200
```

**How it works:**
```
Round 1:  Val AUC = 0.750  ← Best so far
Round 2:  Val AUC = 0.780  ← New best!
...
Round 12: Val AUC = 0.790  ← New best!
Round 13: Val AUC = 0.788  (not better)
Round 14: Val AUC = 0.785  (not better)
...
Round 212: Val AUC = 0.762 (200 rounds without improvement!)

EARLY STOP! Revert to model from round 12.
```

**Why 200?**
- Too small (50): Might stop too early
- Too large (500): Wastes compute
- 200: Good balance for your data size

---

### `verbose`: `-1`

**What it does:** Controls logging.

```python
'verbose': -1  # Suppress all output
```

**Options:**
| Value | Effect |
|-------|--------|
| `-1` | No output |
| `0` | Warnings only |
| `1` | Info level |
| `> 1` | Debug level |

---

### `random_state`: `42`

**What it does:** Seed for reproducibility.

```python
'random_state': 42
```

**Ensures:**
- Same train/val split each run
- Same feature/sample selection for bagging
- Same results every time

---

### `n_jobs`: `-1`

**What it does:** Number of parallel threads.

```python
'n_jobs': -1  # Use all available CPU cores
```

**Options:**
| Value | Effect |
|-------|--------|
| `-1` | All cores |
| `1` | Single thread |
| `N` | Use N cores |

---

## Tuning Recommendations

### For Better Accuracy:

```python
# Start with these, then tune:
params = {
    'num_leaves': 31,           # Start conservative
    'max_depth': -1,            # No limit initially
    'learning_rate': 0.05,      # Moderate
    'n_estimators': 1000,
    'early_stopping_rounds': 100
}

# Tune order:
# 1. num_leaves (20-127)
# 2. max_depth (5-15)
# 3. min_child_samples (20-100)
# 4. learning_rate (0.01-0.1)
# 5. feature_fraction (0.6-1.0)
# 6. bagging_fraction (0.6-1.0)
# 7. reg_alpha (0-10)
# 8. reg_lambda (0-10)
```

### For Faster Training:

```python
params = {
    'boosting_type': 'goss',    # Gradient-based sampling
    'num_leaves': 31,           # Keep small
    'max_depth': 6,
    'learning_rate': 0.1,       # Higher = fewer trees needed
    'feature_fraction': 0.6,    # Fewer features per tree
    'bagging_fraction': 0.7,
    'n_jobs': -1
}
```

### For Preventing Overfitting:

```python
params = {
    'num_leaves': 15,           # Fewer leaves
    'max_depth': 4,             # Shallow trees
    'min_child_samples': 100,   # More samples per leaf
    'learning_rate': 0.01,      # Slower learning
    'feature_fraction': 0.5,    # Less features
    'bagging_fraction': 0.5,    # Less samples
    'reg_alpha': 2.0,           # Strong L1
    'reg_lambda': 2.0           # Strong L2
}
```

---

## Your Final Tuned Parameters

After Optuna optimization (30 trials):

```python
TUNED_PARAMS = {
    # Objective
    'objective': 'binary',
    'metric': ['auc', 'binary_logloss'],
    'boosting_type': 'gbdt',
    
    # Tree Structure (Optuna tuned)
    'num_leaves': 101,          # Complex trees (was 31)
    'max_depth': 9,             # Deeper allowed (was 6)
    'min_child_samples': 100,   # More conservative (was 50)
    
    # Learning (Optuna tuned)
    'learning_rate': 0.014,     # Slightly faster (was 0.01)
    
    # Sampling (Optuna tuned)
    'feature_fraction': 0.69,   # 69% features (was 0.8)
    'bagging_fraction': 0.98,   # Nearly all samples (was 0.8)
    'bagging_freq': 8,          # Every 8 trees (was 3)
    
    # Regularization (Optuna tuned)
    'reg_alpha': 0.39,          # Moderate L1 (was 1.0)
    'reg_lambda': 0.003,        # Very low L2 (was 1.0)
    
    # Class Balance (auto-calculated)
    'scale_pos_weight': 9.59,
    
    # Training Control
    'n_estimators': 2000,
    'early_stopping_rounds': 200,
    
    # System
    'verbose': -1,
    'random_state': 42,
    'n_jobs': -1
}
```

**Result:**
- Validation AUC: 0.8022
- Test AUC: 0.7252
- Final trees: 12 (early stopped)
- Good risk separation across buckets

---

## Parameter Interaction Summary

```
┌────────────────────────────────────────────────────────────────────┐
│                  PARAMETER INTERACTIONS                             │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  COMPLEXITY ←→ REGULARIZATION                                       │
│  ┌─────────────────┐     ┌─────────────────┐                        │
│  │ ↑ num_leaves    │ ←→ │ ↑ reg_alpha     │                        │
│  │ ↑ max_depth     │     │ ↑ reg_lambda    │                        │
│  │ ↓ min_child     │     │ ↑ min_child     │                        │
│  └─────────────────┘     └─────────────────┘                        │
│  More complexity needs more regularization!                          │
│                                                                      │
│  SPEED ←→ ACCURACY                                                  │
│  ┌─────────────────┐     ┌─────────────────┐                        │
│  │ ↑ learning_rate │ ←→ │ ↓ n_estimators  │                        │
│  │ ↓ bagging_frac  │     │ ↓ accuracy      │                        │
│  │ ↓ feature_frac  │     │                 │                        │
│  └─────────────────┘     └─────────────────┘                        │
│  Faster training usually means less accuracy!                        │
│                                                                      │
│  VARIANCE ←→ BIAS                                                   │
│  ┌─────────────────┐     ┌─────────────────┐                        │
│  │ Deep trees      │ ←→ │ Shallow trees   │                        │
│  │ Many leaves     │     │ Few leaves      │                        │
│  │ Low min_child   │     │ High min_child  │                        │
│  │ HIGH VARIANCE   │     │ HIGH BIAS       │                        │
│  └─────────────────┘     └─────────────────┘                        │
│  Find the sweet spot for your data!                                  │
│                                                                      │
└────────────────────────────────────────────────────────────────────┘
```

---

*For algorithm details, see [LIGHTGBM_DEEP_DIVE.md](./LIGHTGBM_DEEP_DIVE.md)*
*For code walkthrough, see [TRAINING_FLOW.md](./TRAINING_FLOW.md)*


