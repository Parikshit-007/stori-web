# MSME Credit Scoring - Detailed Formulas & Algorithms

## Table of Contents
1. [Credit Score Calculation](#credit-score-calculation)
2. [Parameter Scoring Formulas](#parameter-scoring-formulas)
3. [Overdraft Limit Calculation](#overdraft-limit-calculation)
4. [Industry Standard References](#industry-standard-references)

---

## Credit Score Calculation

### Overall Scoring Formula

```
Final_Score = α × GBM_Score + (1-α) × Segment_Subscore
```

Where:
- **α (alpha)** = 0.7 (configurable blending weight)
- **GBM_Score** = Gradient Boosting Model prediction probability
- **Segment_Subscore** = Rule-based weighted score using exact parameters

### Probability to Score Mapping

| Default Probability | Credit Score |
|---------------------|--------------|
| 0.00%               | 900          |
| 2.00%               | 750          |
| 5.00%               | 650          |
| 12.00%              | 550          |
| 25.00%              | 450          |
| 40.00%              | 400          |
| 60.00%              | 350          |
| 100.00%             | 300          |

Formula for interpolation:
```python
score = s1 + (s2 - s1) × (prob - p1) / (p2 - p1)
```

---

## Parameter Scoring Formulas

### Category A: Business Identity & Registration (10%)

#### 1. Legal Entity Type (Weight: 0.5)
```
Score = CategoryScore(entity_type)

CategoryScores:
  public_limited    = 1.0
  private_limited   = 0.9
  llp               = 0.8
  partnership       = 0.6
  proprietorship    = 0.4
  trust/society     = 0.5
  unregistered      = 0.0
```

#### 2. Business Formation Date / Age (Weight: 2.0)
```
score = piecewise_linear(business_age_years)

Breakpoints:
  0-1 years   → 0.0 - 0.3
  1-2 years   → 0.3 - 0.5
  2-3 years   → 0.5 - 0.65
  3-5 years   → 0.65 - 0.8
  5-10 years  → 0.8 - 0.95
  10+ years   → 0.95 - 1.0
```

#### 3. GSTIN/PAN Verification (Weight: 1.0)
```
if both_verified AND names_match:
    score = 1.0
elif both_verified AND minor_mismatch:
    score = 0.5
elif one_verified:
    score = 0.4
else:
    score = 0.0
```

#### 4. Industry Risk (Weight: 2.0)
```
IndustryRiskScores:
  healthcare     = 0.90
  technology     = 0.85
  manufacturing  = 0.75
  services       = 0.70
  trading        = 0.65
  retail         = 0.55
  hospitality    = 0.40
  construction   = 0.35
  agriculture    = 0.30
```

---

### Category B: Revenue & Business Performance (20%)

#### 1. Weekly GTV - Gross Transaction Value (Weight: 7.0)
```python
# Normalize based on MSME category
if msme_category == 'micro':
    score = min(1.0, weekly_gtv / 2_500_000)
elif msme_category == 'small':
    score = min(1.0, weekly_gtv / 10_000_000)
elif msme_category == 'medium':
    score = min(1.0, weekly_gtv / 50_000_000)
```

#### 2. Transaction Count & Value (Weight: 3.0)
```
count_score = min(1.0, daily_transactions / 100)
value_score = gaussian(avg_txn_value, optimal_for_industry, std_dev)

score = 0.6 × count_score + 0.4 × value_score
```

#### 3. Revenue Concentration (Weight: 1.0) - Herfindahl-Hirschman Index
```
HHI = Σ(daily_share²) for each day

# Lower HHI = more diversified = better
score = 1 - min(1.0, (HHI - 0.14) / 0.86)

# 0.14 is HHI for perfectly uniform distribution across 7 days
```

#### 4. Refund/Chargeback Rate (Weight: 2.0)
```python
if chargeback_rate > 0.05:
    score = 0.0  # Critical - high fraud risk
elif chargeback_rate > 0.02:
    score = 0.3
elif chargeback_rate > 0.01:
    score = 0.6
else:
    score = 1.0 - (chargeback_rate × 20)
```

#### 5. Revenue Growth Rate (Weight: 2.0)
```
mom_score = sigmoid(growth_mom, center=0.05, scale=0.10)
qoq_score = sigmoid(growth_qoq, center=0.15, scale=0.20)

score = 0.6 × mom_score + 0.4 × qoq_score

# Penalize high volatility
if std_dev(monthly_growth) > 0.3:
    score *= 0.8
```

Sigmoid Function:
```
f(x) = 1 / (1 + exp(-(x - center) / scale))
```

#### 6. Bank Balance & Trend (Weight: 4.0)
```
coverage_months = avg_balance / monthly_expenses
balance_score = min(1.0, coverage_months / 3)

trend_score = sigmoid(balance_trend, center=0, scale=0.2)

score = 0.75 × balance_score + 0.25 × trend_score
```

#### 7. Operational Leverage Ratio (Weight: 2.0)
```
OL = (Revenue - Variable_Costs) / Operating_Income

if OL > 3.0:   score = 0.2
elif OL > 2.0: score = 0.4
elif OL > 1.5: score = 0.6
elif OL > 1.0: score = 0.8
else:          score = 1.0
```

---

### Category C: Cash Flow & Banking (25%)

#### 1. Weekly Inflow-Outflow Ratio (Weight: 4.0)
```python
if ratio < 0.80:
    score = 0.0   # Critical cash flow problem
elif ratio < 0.95:
    score = 0.3   # Concerning
elif ratio < 1.05:
    score = 0.6   # Neutral
elif ratio < 1.20:
    score = 0.85  # Good
else:
    score = 1.0   # Excellent
```

#### 2. Cash Buffer Days (Weight: 3.0)
```
buffer_days = avg_cash_balance / daily_operating_expenses

if buffer_days < 7:   score = 0.2
elif buffer_days < 15: score = 0.4
elif buffer_days < 30: score = 0.6
elif buffer_days < 60: score = 0.8
else:                  score = 1.0
```

#### 3. Overdraft Days & Amount (Weight: 3.0)
```
days_score = max(0, 1 - overdraft_days / 30)
amount_ratio = overdraft_amount / monthly_gtv
amount_score = max(0, 1 - amount_ratio × 5)

score = 0.5 × days_score + 0.5 × amount_score
```

#### 4. Cash Balance Volatility (Weight: 1.0)
```
CV = std_dev / avg_balance  # Coefficient of Variation

if CV > 1.0:   score = 0.2
elif CV > 0.5: score = 0.5
elif CV > 0.3: score = 0.75
else:          score = 1.0
```

#### 5. Negative Balance Days (Weight: 2.0)
```python
if negative_days == 0:
    score = 1.0
elif negative_days <= 3:
    score = 0.8
elif negative_days <= 7:
    score = 0.5
elif negative_days <= 15:
    score = 0.2
else:
    score = 0.0
```

---

### Category D: Credit & Repayment (22%)

#### 1. Bounced Cheques (Weight: 3.0)
```python
if bounce_count == 0:
    score = 1.0
elif bounce_count == 1:
    score = 0.7
elif bounce_count == 2:
    score = 0.4
elif bounce_count <= 5:
    score = 0.1
else:
    score = 0.0

# Additional penalty for high bounce rate
if bounce_rate > 0.1:
    score *= 0.5
```

#### 2. On-Time Repayment Ratio (Weight: 4.0) - **STRONGEST INDICATOR**
```python
if ratio >= 0.95:
    score = 1.0
elif ratio >= 0.90:
    score = 0.85
elif ratio >= 0.80:
    score = 0.65
elif ratio >= 0.70:
    score = 0.40
elif ratio >= 0.50:
    score = 0.15
else:
    score = 0.0
```

#### 3. Previous Defaults/Write-offs (Weight: 2.0)
```python
if defaults == 0 and writeoffs == 0:
    score = 1.0
elif writeoffs > 0:
    score = 0.0  # Any writeoff is critical
elif defaults == 1:
    score = 0.3
elif defaults == 2:
    score = 0.1
else:
    score = 0.0

# Recency adjustment
if last_default_months > 36:
    score = min(1.0, score + 0.2)
```

#### 4. Utility Payment Behavior (Weight: 3.0)
```
base_score = on_time_ratio²

# Days before due adjustment
if avg_days_before_due > 5:
    score = base_score × 1.1
elif avg_days_before_due < 0:  # Late payments
    score = base_score × max(0.5, 1 + avg_days_before_due × 0.05)
else:
    score = base_score
```

---

### Category E: Compliance & Taxation (12%)

#### 1. GST Filing Regularity (Weight: 1.5)
```
compliance_rate = gst_filed_on_time / total_gst_periods

if compliance_rate >= 0.95: score = 1.0
elif compliance_rate >= 0.85: score = 0.8
elif compliance_rate >= 0.70: score = 0.5
else: score = 0.2
```

#### 2. GST vs Platform Sales Mismatch (Weight: 1.5)
```
mismatch = |gst_sales - platform_sales| / platform_sales

if mismatch < 0.05:   score = 1.0   # Acceptable
elif mismatch < 0.15: score = 0.7   # Minor discrepancy
elif mismatch < 0.30: score = 0.4   # Concerning
else:                 score = 0.0   # Major fraud risk
```

---

### Category F: Fraud & Verification (7%)

#### 1. KYC Completion Behavior (Weight: 0.5)
```python
if kyc_attempts == 1:
    score = 1.0
elif kyc_attempts == 2:
    score = 0.8
elif kyc_attempts == 3:
    score = 0.5
else:
    score = 0.2

# Time to complete adjustment
if days_to_complete > 7:
    score *= 0.8
```

#### 2. Device/IP Consistency (Weight: 1.0)
```
unique_devices = count_unique_devices_90_days

if unique_devices == 1:   score = 1.0
elif unique_devices == 2: score = 0.9
elif unique_devices <= 3: score = 0.7
else:                     score = 0.4

if fraud_device_detected:
    score = 0.0
```

---

## Overdraft Limit Calculation

### Method 1: Turnover Method (RBI Recommended)

```
OD_Limit = Annual_Turnover × Risk_Tier_Multiplier
```

| Credit Score | Risk Tier   | Multiplier |
|--------------|-------------|------------|
| 750-900      | Prime       | 40%        |
| 650-749      | Near Prime  | 30%        |
| 550-649      | Standard    | 25%        |
| 450-549      | Subprime    | 15%        |
| <450         | High Risk   | 0%         |

### Method 2: MPBF - Tandon Committee Method

```
Working_Capital_Gap = Current_Assets - Current_Liabilities

MPBF = 0.75 × Working_Capital_Gap - Existing_Bank_Debt
```

The borrower must contribute 25% from long-term sources.

### Method 3: Cash Flow Coverage Method

```
Monthly_Surplus = Cash_Inflows - Cash_Outflows - Existing_EMI

Serviceable_EMI = Monthly_Surplus / DSCR_Required

OD_Limit = Serviceable_EMI / 0.03
```

(Assumes EMI ~3% of principal per month)

### Final Limit Calculation

```python
# Take minimum of all methods (conservative approach)
base_limit = min(turnover_limit, mpbf_limit, cashflow_limit)

# Apply adjustments
adjusted_limit = base_limit
adjusted_limit *= vintage_adjustment    # 0.50 to 1.20
adjusted_limit *= industry_adjustment   # 0.75 to 1.10
adjusted_limit *= cashflow_health_adj   # 0.70 to 1.10
adjusted_limit *= payment_discipline    # 0.80 to 1.10

# Apply MSME category limits
final_limit = clip(adjusted_limit, msme_min, msme_max)
```

### MSME Category Limits (RBI Guidelines)

| Category | Minimum     | Maximum        |
|----------|-------------|----------------|
| Micro    | ₹50,000     | ₹25,00,000     |
| Small    | ₹1,00,000   | ₹1,00,00,000   |
| Medium   | ₹5,00,000   | ₹5,00,00,000   |

### Interest Rate Pricing

```
Final_Rate = Base_Rate + Risk_Premium + Vintage_Adj + Industry_Adj - Behavior_Discount

Base_Rate by Tier:
  Prime       = 10.5%
  Near Prime  = 13.0%
  Standard    = 16.0%
  Subprime    = 20.0%

Adjustments:
  Vintage (0-1 yr)   = +2.0%
  Vintage (5+ yr)    = -1.0%
  Industry (high risk) = +1.5%
  Good payment history = -1.0%
```

### Debt Service Coverage Ratio (DSCR)

```
DSCR = Net_Operating_Income / Total_Debt_Service
```

| DSCR Value | Assessment |
|------------|------------|
| < 1.0      | Cannot service debt |
| 1.0 - 1.2  | Marginal |
| 1.2 - 1.5  | Acceptable |
| ≥ 1.5      | Good |

### EMI Calculation

```
EMI = P × r × (1+r)^n / ((1+r)^n - 1)

Where:
  P = Principal amount
  r = Monthly interest rate (annual_rate / 12 / 100)
  n = Number of monthly installments
```

---

## Industry Standard References

1. **RBI Guidelines** - Master Circular on MSME Lending
2. **Basel III** - Capital Adequacy Requirements
3. **CGTMSE** - Credit Guarantee Trust Guidelines
4. **Tandon Committee** - Working Capital Assessment
5. **IND AS 109** - Expected Credit Loss Model
6. **CIBIL MSME Rank** - Methodology Reference

---

## Weight Summary Table

| Category | Weight | Top Parameters (by weight) |
|----------|--------|---------------------------|
| A - Identity | 10% | Industry (2), Business Age (2), GSTIN/PAN (1) |
| B - Revenue | 20% | Weekly GTV (7), Bank Balance (4), Transactions (3) |
| C - Cash Flow | 25% | Inflow-Outflow (4), OD Days (3), Cash Buffer (3) |
| D - Repayment | 22% | On-time Repayment (4), Bounced Cheques (3), Utilities (3) |
| E - Compliance | 12% | Tax Payments (2), Outstanding Taxes (2), GST (1.5) |
| F - Fraud | 7% | Funds Verification (2), Insurance (2), KYC Mismatch (1) |
| G - External | 4% | Social Media (1.5), Local Economy (1), Customer Conc. (1) |

**Total: 100 weight points**

