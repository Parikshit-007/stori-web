# MSME Credit Scoring Pipeline v2.0

Production-ready Gradient Boosting Machine (GBM) credit scoring system for Micro, Small, and Medium Enterprises (MSMEs), with integrated overdraft limit recommendation engine.

## 🎯 Key Features

- **Credit Score Prediction**: 300-900 score range with 90-DPD default probability
- **65+ Parameters**: Comprehensive feature set based on industry standards
- **Business Segment Scoring**: Tailored weights for 6 MSME segments
- **Overdraft Engine**: Industry-standard limit calculation using 3 methods
- **SHAP Explainability**: Feature importance and individual explanations
- **Production API**: FastAPI with authentication and monitoring

## 📊 Scoring Methodology

### Hybrid Approach
```
Final_Score = α × GBM_Prediction + (1-α) × Segment_Subscore
```
- Default α = 0.7 (GBM weight)
- Segment_Subscore uses exact parameter weights from specification

### Parameter Categories & Weights

| Category | Weight | Key Parameters |
|----------|--------|----------------|
| **A. Business Identity** | 10% | Legal entity (0.5), Business age (2), Industry (2), GSTIN/PAN (1) |
| **B. Revenue Performance** | 20% | Weekly GTV (7), Bank balance (4), Transactions (3), Growth (2) |
| **C. Cash Flow & Banking** | 25% | Inflow-outflow ratio (4), Cash buffer (3), Overdraft (3) |
| **D. Credit & Repayment** | 22% | On-time repayment (4), Bounced cheques (3), Utility payments (3) |
| **E. Compliance** | 12% | Tax payments (2), Outstanding taxes (2), GST filing (1.5) |
| **F. Fraud Verification** | 7% | Funds verification (2), Insurance (2), KYC mismatch (1) |
| **G. External Signals** | 4% | Social media (1.5), Economic health (1), Customer concentration (1) |

**Total: 100 weight points across 65+ parameters**

## 🏦 Overdraft Limit Calculation

### Methods Used (Industry Standard)

1. **Turnover Method (RBI Recommended)**
   ```
   Limit = Annual_Turnover × Risk_Multiplier
   ```
   | Score | Tier | Multiplier |
   |-------|------|------------|
   | 750+ | Prime | 40% |
   | 650-749 | Near Prime | 30% |
   | 550-649 | Standard | 25% |
   | 450-549 | Subprime | 15% |

2. **MPBF Method (Tandon Committee)**
   ```
   MPBF = 0.75 × (Current_Assets - Current_Liabilities) - Existing_Debt
   ```

3. **Cash Flow Coverage Method**
   ```
   Limit = (Monthly_Surplus / DSCR_Required) / 0.03
   ```

### MSME Category Limits (RBI Guidelines)

| Category | Min Limit | Max Limit |
|----------|-----------|-----------|
| Micro | ₹50,000 | ₹25 Lakh |
| Small | ₹1 Lakh | ₹1 Crore |
| Medium | ₹5 Lakh | ₹5 Crore |

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd credit_scoring_pipeline/msme
pip install -r requirements.txt
```

### 2. Generate Synthetic Data & Train Model

```bash
python data_prep.py
python train.py
```

### 3. Start API Server

```bash
python app.py --port 8001
```

### 4. Test API Endpoints

**Health Check:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8001/api/health" -Method Get
```

**Score Business:**
```powershell
$headers = @{
    "Authorization" = "Bearer msme_dev_token_12345"
    "Content-Type" = "application/json"
}

$body = @{
    features = @{
        business_age_years = 3.5
        weekly_gtv = 2500000
        overdraft_repayment_ontime_ratio = 0.92
        bounced_cheques_count = 1
        gst_filing_regularity = 0.95
    }
    business_segment = "small_trading"
} | ConvertTo-Json -Depth 3

Invoke-RestMethod -Uri "http://localhost:8001/api/score" -Method Post -Headers $headers -Body $body
```

**Calculate Overdraft:**
```powershell
$headers = @{
    "Authorization" = "Bearer msme_dev_token_12345"
    "Content-Type" = "application/json"
}

$body = @{
    credit_score = 720
    monthly_gtv = 2500000
    business_age_years = 3.5
    industry = "trading"
    msme_category = "small"
    existing_debt = 500000
    cash_flow_health_score = 0.8
    payment_discipline_score = 0.85
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/api/overdraft/calculate" -Method Post -Headers $headers -Body $body
```

## 📁 File Structure

```
msme/
├── README.md              # This file
├── FORMULAS.md            # Detailed formula documentation
├── requirements.txt       # Python dependencies
├── feature_config.json    # Parameter weights & configuration
├── algorithms.py          # Mathematical formulas & scoring logic
├── data_prep.py          # Data preparation & synthetic generation
├── train.py              # Model training pipeline
├── score.py              # Scoring function with blending
├── overdraft_engine.py   # Overdraft limit calculation
└── app.py                # FastAPI application
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/score` | POST | Score MSME business |
| `/api/explain` | POST | Get SHAP explanation |
| `/api/segments` | GET | List business segments |
| `/api/categories` | GET | List scoring categories |
| `/api/overdraft/calculate` | POST | Calculate overdraft limit |
| `/api/overdraft/quick-estimate` | POST | Quick limit estimate |
| `/api/score-with-overdraft` | POST | Combined scoring + overdraft |
| `/api/overdraft/tiers` | GET | Get eligibility tiers |

## 📈 Risk Buckets

| Score Range | Risk Level | Default Rate | Decision |
|-------------|------------|--------------|----------|
| 750-900 | Very Low | 2% | Fast Track Approval |
| 650-749 | Low | 5% | Approve |
| 550-649 | Medium | 12% | Conditional Approval |
| 450-549 | High | 25% | Manual Review |
| 300-449 | Very High | 40% | Decline |

## 🔑 Authentication

Use Bearer token authentication:
```
Authorization: Bearer msme_dev_token_12345
```

Available tokens:
- `msme_dev_token_12345` - Development
- `msme_prod_token_67890` - Production
- `msme_test_token_abcde` - Testing

## 📊 Key Formulas

### Credit Score Formula
```python
# Blend GBM prediction with segment subscore
segment_risk = 1 - segment_subscore  # Higher subscore = lower risk
final_prob = alpha * gbm_prob + (1 - alpha) * segment_risk

# Map probability to score (300-900)
score = probability_to_score(final_prob)
```

### Top Parameter Scoring

**On-Time Repayment (Weight: 4.0) - Strongest Indicator:**
```python
if ratio >= 0.95: score = 1.0
elif ratio >= 0.90: score = 0.85
elif ratio >= 0.80: score = 0.65
elif ratio >= 0.70: score = 0.40
elif ratio >= 0.50: score = 0.15
else: score = 0.0
```

**Weekly GTV (Weight: 7.0):**
```python
# Normalize by MSME category
if category == 'micro': score = min(1.0, gtv / 2_500_000)
elif category == 'small': score = min(1.0, gtv / 10_000_000)
elif category == 'medium': score = min(1.0, gtv / 50_000_000)
```

**Inflow-Outflow Ratio (Weight: 4.0):**
```python
if ratio < 0.80: score = 0.0   # Critical
elif ratio < 0.95: score = 0.3 # Concerning
elif ratio < 1.05: score = 0.6 # Neutral
elif ratio < 1.20: score = 0.85 # Good
else: score = 1.0              # Excellent
```

### Overdraft Interest Rate
```
Final_Rate = Base_Rate + Risk_Premium + Vintage_Adj + Industry_Adj - Behavior_Discount

Example for Prime (750+):
  Base: 10.5% + 0% (no premium) + (-0.5% for 5yr) + (-0.5% for tech) - 1% (good behavior)
  = 8.5% final rate
```

### DSCR Calculation
```
DSCR = Net_Operating_Income / Total_Debt_Service

Required by Tier:
  Prime: ≥ 1.10
  Near Prime: ≥ 1.20
  Standard: ≥ 1.30
  Subprime: ≥ 1.50
```

## 📚 Reference Standards

- **RBI Guidelines** - Master Circular on MSME Lending
- **Basel III** - Capital Adequacy Requirements
- **CGTMSE** - Credit Guarantee Trust for MSMEs
- **Tandon Committee** - Working Capital Assessment (MPBF)
- **IND AS 109** - Expected Credit Loss Model
- **CIBIL MSME Rank** - Methodology Reference

## 🔄 Monitoring & Retraining

| Metric | Threshold | Action |
|--------|-----------|--------|
| PSI (Population Stability) | > 0.20 | Alert & investigate |
| Feature Drift | > 0.10 | Review feature |
| Calibration Drift | > 5% | Recalibrate |
| Retraining | Every 60 days | Scheduled |

## 📝 Sample Response

### Credit Score Response
```json
{
  "score": 695,
  "prob_default_90dpd": 0.0712,
  "risk_category": "Low Risk",
  "recommended_decision": "Approve",
  "business_segment": "Small Enterprise - Trading",
  "component_scores": {
    "gbm_prediction": 0.0823,
    "segment_subscore": 0.7124,
    "alpha": 0.7
  },
  "category_contributions": {
    "A_business_identity": 0.0087,
    "B_revenue_performance": 0.0412,
    "C_cashflow_banking": 0.0523
  }
}
```

### Overdraft Response
```json
{
  "eligibility": "eligible",
  "risk_tier": "near_prime",
  "recommended_limit": 720000,
  "interest_rate": 12.5,
  "calculation_methods": {
    "turnover_method": 900000,
    "cash_flow_method": 850000,
    "mpbf_method": 720000
  },
  "dscr": 1.45,
  "collateral_required": false,
  "conditions": ["Personal guarantee required"]
}
```

## 🛡️ Important Notes

1. **100% Accuracy Disclaimer**: While the system uses comprehensive parameters and industry-standard formulas, credit scoring inherently involves prediction uncertainty. The model is designed for optimal accuracy within statistical bounds.

2. **Regulatory Compliance**: Ensure compliance with local RBI and financial regulations when deploying in production.

3. **Data Privacy**: All business data should be handled according to data protection regulations.

4. **Model Updates**: Regular retraining is recommended as economic conditions and business patterns evolve.

## 📞 Support

For technical support or questions about the scoring methodology, refer to:
- `FORMULAS.md` - Detailed mathematical formulas
- `algorithms.py` - Python implementation of all formulas
- `feature_config.json` - Complete parameter configuration

---

**Version**: 2.0.0  
**Last Updated**: December 2024  
**Author**: ML Engineering Team
