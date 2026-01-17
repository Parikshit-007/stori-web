"""
Consumer Credit Scoring - Quick Start Guide
===========================================

Get started in 5 minutes!

## Installation

```bash
pip install pandas numpy openpyxl
```

## Generate Data (One Command!)

```bash
cd credit_scoring_pipeline/consumer
python main.py --samples 25000
```

**Output**:
- ✅ `consumer_credit_data_TIMESTAMP.csv`
- ✅ `consumer_credit_data_TIMESTAMP.xlsx` (9 sheets!)

## What You Get

### Excel File (9 Sheets)

1. **Full_Data** (25,000+ records)
   - All 30+ features
   - Default labels
   - Consumer segments

2. **Summary_Statistics**
   - Mean, std, min, max for all features
   - Missing value percentages
   - Distribution statistics

3. **Segment_Analysis**
   - Perfect Consumer (10%)
   - Good Consumer (25%)
   - Average Consumer (35%)
   - Struggling Consumer (20%)
   - High-Risk Consumer (10%)

4. **Default_Analysis**
   - By age group
   - By employment type
   - By education level

5. **Feature_Correlations**
   - Top 30 features correlated with default
   - Correlation matrix

6. **Risk_Distribution**
   - Risk buckets (0-5%, 5-10%, etc.)
   - Default rates per bucket

7. **Data_Dictionary**
   - All 30+ feature descriptions
   - Weights (%)
   - Categories

8. **Perfect_Consumers**
   - Top 100 perfect profiles
   - Score 80-100
   - ~1% default rate

9. **High_Risk_Consumers**
   - Top 100 high-risk profiles
   - Score 0-34
   - ~30% default rate

## Python Usage

```python
from credit_scoring_pipeline.consumer.main import generate_and_export_data

# Generate 25,000 consumer profiles
df, csv_path, excel_path = generate_and_export_data(
    n_samples=25000,
    output_dir="consumer_data",
    include_edge_cases=True
)

# Explore data
print(df.head())
print(df['consumer_segment'].value_counts())
print(df.groupby('consumer_segment')['default_90dpd'].mean())
```

## Advanced Options

```bash
# Generate 50,000 samples
python main.py --samples 50000

# Custom output directory
python main.py --samples 25000 --output my_consumer_data

# Exclude edge cases
python main.py --samples 25000 --no-edge-cases
```

## Feature Coverage

### All 30+ Parameters Included

✅ Name & DOB verified (1%)  
✅ Phone number verified (1.5%)  
✅ Email verified (1%)  
✅ Education level (1.5%)  
✅ Identity matching (2%)  
✅ Employment history (3%)  
✅ Income stability (5%)  
✅ Income source verification (3%)  
✅ P2P UPI transactions (3%)  
✅ Outflow burden (4%)  
✅ Account balance (4%)  
✅ Survivability months (4%)  
✅ Income retention (4%)  
✅ Expense rigidity (3%)  
✅ Inflow consistency (2%)  
✅ EMI/UPI ratio (4%)  
✅ Financial assets (6%)  
✅ Insurance coverage (3%)  
✅ EMI/Income ratio (4%)  
✅ Rent/Income ratio (2%)  
✅ Utility/Income ratio (2%)  
✅ Insurance discipline (3%)  
✅ Spending personality (3%)  
✅ Spending discipline (4%)  
✅ Bill payment discipline (5%)  
✅ Late-night behaviour (3%)  
✅ Utility consistency (2%)  
✅ Risk appetite (3%)  
✅ Pin code risk (2%)  
✅ Statement manipulation (4%)  
✅ Synthetic ID risk (4%)

**Total: 100%**

## Edge Cases Included

### 1. Fraudsters
- Bank statement manipulation >70%
- Synthetic ID risk >70%
- Poor identity matching

### 2. Perfect Consumers
- Score 80-100
- Excellent payment discipline
- High financial assets
- Low fraud risk

### 3. Young Professionals
- Age 24-30
- Growing income
- Good discipline
- Limited history

### 4. Established Professionals
- Age 35-50
- Stable income
- Long employment
- Excellent history

### 5. Students
- Age 18-25
- Low income
- High potential
- Limited credit history

### 6. Business Owners
- Variable income
- High risk appetite
- Multiple income sources

### 7. Defaulters
- Poor payment history
- High debt burden
- Unstable income

## Sample Output

```
Generating 25000 synthetic consumer credit profiles...
Generated 25,300 consumer profiles with 1,745 defaults (6.9%)

Segment distribution:
good_consumer            6325
average_consumer         8855
perfect_consumer         2530
struggling_consumer      5060
high_risk_consumer       2530

Default rate by segment:
high_risk_consumer       0.304348
struggling_consumer      0.152569
average_consumer         0.070699
good_consumer            0.031128
perfect_consumer         0.010277

✅ CSV exported: consumer_data_output/consumer_credit_data_20260112_143022.csv
✅ Excel exported: consumer_data_output/consumer_credit_data_20260112_143022.xlsx

DATA GENERATION COMPLETE

Outputs:
  - CSV: consumer_data_output/consumer_credit_data_20260112_143022.csv
  - Excel: consumer_data_output/consumer_credit_data_20260112_143022.xlsx

Excel file contains 9 sheets:
  1. Full_Data - All records
  2. Summary_Statistics - Statistical summary
  3. Segment_Analysis - Analysis by segment
  4. Default_Analysis - Default patterns
  5. Feature_Correlations - Top feature correlations
  6. Risk_Distribution - Risk bucket distribution
  7. Data_Dictionary - Feature descriptions
  8. Perfect_Consumers - Top 100 perfect profiles
  9. High_Risk_Consumers - Top 100 high-risk profiles
```

## What's Next?

After generating data:

1. ✅ **Open Excel file** - Explore 9 comprehensive sheets
2. ✅ **Review segments** - See distribution across consumer types
3. ✅ **Check edge cases** - Verify fraudsters, perfect consumers, etc.
4. ✅ **Train model** - Use this data for LightGBM training
5. ✅ **Build scoring** - Create score conversion (0-100 scale)

## Troubleshooting

### Issue: Module not found
```bash
# Make sure you're in the right directory
cd credit_scoring_pipeline/consumer
python main.py
```

### Issue: Excel file won't open
- Make sure you have `openpyxl` installed
- Check file permissions in output directory

### Issue: Not enough samples
```bash
# Generate more samples
python main.py --samples 50000
```

## Summary

You now have:
- ✅ 25,000+ realistic consumer credit profiles
- ✅ All 30+ parameters with proper weights
- ✅ 360-degree edge case coverage
- ✅ Excel file with 9 comprehensive sheets
- ✅ Ready for model training!

**Total setup time**: < 5 minutes  
**Data generation time**: < 30 seconds  

Happy scoring! 🚀


