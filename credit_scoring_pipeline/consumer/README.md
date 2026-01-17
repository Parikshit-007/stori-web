"""
Consumer Credit Scoring Pipeline
=================================

Complete credit scoring system for individual consumers with 30+ parameters.

## Overview

This pipeline generates realistic synthetic consumer credit data with:
- ✅ **30+ parameters** with proper weights (totaling 100%)
- ✅ **Realistic scenarios** covering all consumer segments
- ✅ **Edge cases** including fraudsters, perfect consumers, defaulters
- ✅ **360-degree coverage** of behavioral, financial, and risk factors
- ✅ **Excel export** with 9 comprehensive sheets

## Feature Categories

### A. Identity & Verification (7%)
1. Name & DOB verified (1%)
2. Phone number verified (1.5%)
3. Email verified (1%)
4. Education level (1.5%)
5. Identity matching (2%)

### B. Employment & Income (14%)
6. Employment history score (3%)
7. Monthly income stability (5%)
8. Income source verification (3%)
9. Regular P2P UPI transactions (3%)

### C. Cash Flow & Banking (24%)
10. Monthly outflow burden (4%)
11. Average account balance (4%)
12. Survivability months (4%)
13. Income retention ratio (4%)
14. Expense rigidity (3%)
15. Inflow time consistency (2%)
16. EMI ÷ Monthly UPI amount (4%)

### D. Financial Assets & Insurance (9%)
17. Total financial assets (6%)
18. Insurance coverage (3%)

### E. Debt Burden (11%)
19. EMI ÷ Income ratio (4%)
20. Rent ÷ Income ratio (2%)
21. Utility ÷ Income ratio (2%)
22. Insurance payment discipline (3%)

### F. Behavioral Patterns (17%)
23. Spending personality score (3%)
24. Spending discipline index (4%)
25. Bill payment discipline (5%)
26. Late-night payment behaviour (3%)
27. Utility payment consistency (2%)

### G. Risk & Fraud (18%)
28. Risk appetite score (3%)
29. Pin code risk score (2%)
30. Bank statement manipulation (4%)
31. Synthetic ID risk (4%)

## Consumer Segments

### 1. Perfect Consumer (10% of data)
- **Score**: 80-100
- **Default Rate**: ~1%
- **Characteristics**:
  - High income (₹80k-200k/month)
  - Excellent payment discipline (>95%)
  - Strong financial assets
  - Very low fraud risk
  - Stable employment history

### 2. Good Consumer (25% of data)
- **Score**: 65-79
- **Default Rate**: ~3%
- **Characteristics**:
  - Good income (₹30k-80k/month)
  - Good payment discipline (75-90%)
  - Moderate financial assets
  - Low fraud risk
  - Stable income

### 3. Average Consumer (35% of data)
- **Score**: 50-64
- **Default Rate**: ~7%
- **Characteristics**:
  - Average income (₹20k-50k/month)
  - Fair payment discipline (60-75%)
  - Some financial assets
  - Moderate fraud risk
  - Variable income

### 4. Struggling Consumer (20% of data)
- **Score**: 35-49
- **Default Rate**: ~15%
- **Characteristics**:
  - Lower income (₹15k-35k/month)
  - Poor payment discipline (40-60%)
  - Limited financial assets
  - Higher fraud risk
  - Unstable income

### 5. High-Risk Consumer (10% of data)
- **Score**: 0-34
- **Default Rate**: ~30%
- **Characteristics**:
  - Low income (₹10k-25k/month)
  - Very poor payment discipline (<40%)
  - No financial assets
  - High fraud risk
  - Very unstable income

## Edge Cases Covered

### Fraudsters
- High bank statement manipulation (>70%)
- High synthetic ID risk (>70%)
- Poor identity matching (<30%)
- Multiple device fingerprint changes
- Low cross-platform consistency

### Young Professionals
- Age 24-30
- Higher education (undergraduate/postgraduate)
- Growing income
- Short employment history
- Good payment discipline but limited credit history

### Established Professionals
- Age 35-50
- Long employment tenure
- Stable income
- Diversified financial assets
- Excellent payment history

### Students
- Age 18-25
- Low income
- High potential
- Limited credit history
- Family support indicators

### Business Owners
- Variable income
- High risk appetite
- Multiple income sources
- Complex financial structure

## Quick Start

### 1. Generate Data

```bash
cd credit_scoring_pipeline/consumer
python main.py --samples 25000 --output consumer_data_output
```

This will generate:
- ✅ CSV file with all data
- ✅ Excel file with 9 comprehensive sheets

### 2. Use in Python

```python
from credit_scoring_pipeline.consumer.main import generate_and_export_data

# Generate 25,000 samples
df, csv_path, excel_path = generate_and_export_data(
    n_samples=25000,
    output_dir="consumer_data",
    include_edge_cases=True
)

print(f"Generated {len(df)} consumer profiles")
print(f"CSV: {csv_path}")
print(f"Excel: {excel_path}")
```

### 3. Generate Specific Segment

```python
from credit_scoring_pipeline.consumer.data.synthetic_data_generator import ConsumerSyntheticDataGenerator

generator = ConsumerSyntheticDataGenerator(seed=42)
df = generator.generate(n_samples=10000, include_edge_cases=True)

# Filter for specific segment
perfect_consumers = df[df['consumer_segment'] == 'perfect_consumer']
high_risk_consumers = df[df['consumer_segment'] == 'high_risk_consumer']
```

## Excel Export

The Excel file contains 9 sheets:

1. **Full_Data** - All generated records with all features
2. **Summary_Statistics** - Descriptive statistics for all numeric features
3. **Segment_Analysis** - Analysis by consumer segment
4. **Default_Analysis** - Default patterns by age, employment, education
5. **Feature_Correlations** - Correlation matrix of top 30 features
6. **Risk_Distribution** - Distribution across risk buckets
7. **Data_Dictionary** - Complete feature descriptions and weights
8. **Perfect_Consumers** - Top 100 perfect consumer profiles
9. **High_Risk_Consumers** - Top 100 high-risk consumer profiles

## Data Quality

### Realism Features
- ✅ Income follows log-normal distribution
- ✅ Expenses correlated with income and discipline
- ✅ Payment behavior linked to financial stability
- ✅ Fraud indicators properly inverted with trust signals
- ✅ Age-appropriate features (young vs old consumers)
- ✅ Employment type affects income stability
- ✅ Education level impacts income potential

### Edge Case Coverage
- ✅ Perfect consumers with 90-100 score
- ✅ Fraudsters with synthetic IDs
- ✅ Young professionals with potential
- ✅ Established professionals with history
- ✅ Students with low income
- ✅ Business owners with variable income
- ✅ Defaulters with poor history
- ✅ Extreme income cases (very high/low)
- ✅ Excellent vs poor payment discipline

### Validation
- ✅ All weights sum to 100%
- ✅ Default rate matches segment (1% to 30%)
- ✅ Features are properly correlated
- ✅ No impossible combinations
- ✅ Realistic distributions

## Directory Structure

```
consumer/
├── config/
│   ├── feature_weights.py      # Parameter weights (30+ features)
│   ├── constants.py             # Risk tiers, categories, constants
│   └── hyperparameters.py       # LightGBM hyperparameters
├── data/
│   └── synthetic_data_generator.py  # Comprehensive data generation
├── utils/
│   └── excel_exporter.py        # Excel export with 9 sheets
├── main.py                      # Main orchestrator
└── README.md                    # This file
```

## Sample Data

```python
# Example consumer profile
{
    'age': 32,
    'monthly_income': 55000,
    'employment_type': 'salaried_private',
    'education_level': 'undergraduate',
    'bill_payment_discipline': 0.88,
    'spending_discipline_index': 0.82,
    'total_financial_assets': 450000,
    'avg_account_balance': 75000,
    'emi_to_income_ratio': 0.25,
    'bank_statement_manipulation': 0.05,
    'synthetic_id_risk': 0.08,
    'default_probability_true': 0.045,
    'default_90dpd': 0,
    'consumer_segment': 'good_consumer'
}
```

## Next Steps

1. **Train Model**: Use this data to train LightGBM model
2. **Score Conversion**: Map probability → score (0-100)
3. **Risk Tiering**: Classify into Excellent/Good/Fair/Poor/Very Poor
4. **Deployment**: Create scoring API

## Support

For questions or issues, contact ML Engineering Team.

---

**Version**: 1.0.0  
**Author**: ML Engineering Team  
**Last Updated**: 2026-01-12


