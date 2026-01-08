"""Quick script to view synthetic data"""
import pandas as pd

df = pd.read_csv('msme_synthetic_data.csv')

print("=" * 60)
print("MSME SYNTHETIC DATA SUMMARY")
print("=" * 60)
print(f"Total Rows: {len(df)}")
print(f"Total Columns: {len(df.columns)}")
print(f"File Size: ~1.2 MB")
print(f"Default Rate: {df['default_90dpd'].mean()*100:.1f}%")

print("\n" + "=" * 60)
print("ALL COLUMNS (90)")
print("=" * 60)
for i, col in enumerate(df.columns, 1):
    print(f"{i:2}. {col}")

print("\n" + "=" * 60)
print("SAMPLE DATA (First 5 rows, key columns)")
print("=" * 60)
key_cols = [
    'business_segment', 
    'weekly_gtv', 
    'business_age_years', 
    'overdraft_repayment_ontime_ratio', 
    'bounced_cheques_count',
    'gst_filing_regularity',
    'default_90dpd'
]
print(df[key_cols].head(5).to_string())

print("\n" + "=" * 60)
print("BUSINESS SEGMENT DISTRIBUTION")
print("=" * 60)
print(df['business_segment'].value_counts())

print("\n" + "=" * 60)
print("DEFAULT RATE BY SEGMENT")
print("=" * 60)
print(df.groupby('business_segment')['default_90dpd'].mean().apply(lambda x: f"{x*100:.1f}%"))

