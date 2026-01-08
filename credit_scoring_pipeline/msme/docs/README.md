# MSME Credit Scoring - Technical Documentation

## 📚 Documentation Index

This folder contains comprehensive technical documentation for the MSME Credit Scoring model training pipeline.

---

## Documents

### 1. [LIGHTGBM_DEEP_DIVE.md](./LIGHTGBM_DEEP_DIVE.md)
**Full Algorithm Explanation**

Learn how LightGBM works under the hood:
- ✅ Gradient Boosting fundamentals
- ✅ Histogram-based data splitting (255 bins)
- ✅ Leaf-wise (best-first) tree growth
- ✅ Exclusive Feature Bundling (EFB)
- ✅ Gradient-based One-Side Sampling (GOSS)
- ✅ Mathematical formulations
- ✅ Why LightGBM is perfect for credit scoring

---

### 2. [TRAINING_FLOW.md](./TRAINING_FLOW.md)
**Step-by-Step Code Walkthrough**

Understand exactly what happens when you run training:
- ✅ Entry point and argument parsing
- ✅ Data loading from CSV
- ✅ Time-based train/val/test splitting
- ✅ Preprocessing pipeline (clip, impute, encode, engineer)
- ✅ Optuna hyperparameter tuning
- ✅ LightGBM training loop
- ✅ Probability calibration
- ✅ SHAP explainability initialization
- ✅ Model evaluation and metrics
- ✅ Artifact saving

---

### 3. [HYPERPARAMETERS_GUIDE.md](./HYPERPARAMETERS_GUIDE.md)
**Complete Parameter Reference**

Every hyperparameter explained:
- ✅ Objective & metric parameters
- ✅ Tree structure (num_leaves, max_depth, min_child_samples)
- ✅ Learning parameters (learning_rate, n_estimators)
- ✅ Regularization (reg_alpha, reg_lambda)
- ✅ Sampling (feature_fraction, bagging_fraction)
- ✅ Class imbalance handling (scale_pos_weight)
- ✅ Training control (early_stopping)
- ✅ Tuning recommendations

---

## Quick Start

### Running Training

```bash
# Basic training with default parameters
python train.py

# Training with custom data and hyperparameter tuning
python train.py --data msme_comprehensive_training_data.csv --tune --trials 30

# Full options
python train.py \
    --data msme_comprehensive_training_data.csv \
    --output msme_model_artifacts \
    --samples 25000 \
    --tune \
    --trials 50
```

### Generating Synthetic Data

```bash
python generate_comprehensive_data.py
```

This creates `msme_comprehensive_training_data.csv` with:
- 10,200 samples
- All risk levels (very low → very high)
- 7 edge case scenarios

---

## Model Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    MSME CREDIT SCORING PIPELINE                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐       │
│   │    INPUT    │────▶│ PREPROCESSOR │────▶│  LIGHTGBM   │       │
│   │  92 Features│     │ Clip/Impute/ │     │   12 Trees  │       │
│   │             │     │ Encode/Eng.  │     │  (boosted)  │       │
│   └─────────────┘     └─────────────┘     └──────┬──────┘       │
│                                                   │               │
│                                                   ▼               │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐       │
│   │   OUTPUT    │◀────│  BLENDING   │◀────│ CALIBRATOR  │       │
│   │ Score: 544  │     │ GBM + Segment│     │  Isotonic   │       │
│   │ Risk: High  │     │  Subscores  │     │ Regression  │       │
│   └─────────────┘     └─────────────┘     └─────────────┘       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Files

| File | Purpose |
|------|---------|
| `train.py` | Model training pipeline |
| `score.py` | Scoring functions and weights |
| `data_prep.py` | Data preprocessing |
| `app.py` | FastAPI scoring endpoint |
| `generate_comprehensive_data.py` | Synthetic data generator |

---

## Performance Summary

| Metric | Value |
|--------|-------|
| Validation AUC | 0.8022 |
| Test AUC | 0.7252 |
| KS Statistic | 0.3582 |
| Default Rate | 9.25% |
| Features | 92 |
| Final Trees | 12 |

### Risk Bucket Separation

| Score Range | Risk Level | Default Rate |
|-------------|------------|--------------|
| 750-900 | Very Low | 2.7% |
| 650-749 | Low | - |
| 550-649 | Medium | 7.4% |
| 450-549 | High | 15.3% |
| 300-449 | Very High | 25.2% |

---

## Need Help?

1. **Understanding the algorithm?** → Read [LIGHTGBM_DEEP_DIVE.md](./LIGHTGBM_DEEP_DIVE.md)
2. **Following the code?** → Read [TRAINING_FLOW.md](./TRAINING_FLOW.md)
3. **Tuning parameters?** → Read [HYPERPARAMETERS_GUIDE.md](./HYPERPARAMETERS_GUIDE.md)

---

*Last updated: January 2026*



