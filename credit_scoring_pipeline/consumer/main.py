"""
Consumer Credit Scoring Pipeline - Main Orchestrator
====================================================

Complete end-to-end pipeline for consumer credit scoring.

Author: ML Engineering Team
Version: 1.0.0
"""

import os
import sys
import pandas as pd
import argparse
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.synthetic_data_generator import ConsumerSyntheticDataGenerator
from utils.excel_exporter import export_consumer_data_to_excel


def generate_and_export_data(
    n_samples: int = 25000,
    output_dir: str = "consumer_data_output",
    include_edge_cases: bool = True
):
    """
    Generate synthetic consumer data and export to Excel.
    
    Args:
        n_samples: Number of samples to generate
        output_dir: Output directory
        include_edge_cases: Whether to include edge cases
    """
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 70)
    print("CONSUMER CREDIT SCORING - SYNTHETIC DATA GENERATION")
    print("=" * 70)
    
    # Generate data
    generator = ConsumerSyntheticDataGenerator(seed=42)
    df = generator.generate(n_samples=n_samples, include_edge_cases=include_edge_cases)
    
    # Export to CSV
    csv_path = os.path.join(output_dir, f"consumer_credit_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    df.to_csv(csv_path, index=False)
    print(f"\n[SUCCESS] CSV exported: {csv_path}")
    
    # Export to Excel (comprehensive)
    excel_path = os.path.join(output_dir, f"consumer_credit_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
    export_consumer_data_to_excel(df, excel_path)
    print(f"\n[SUCCESS] Excel exported: {excel_path}")
    
    # Print summary
    print("\n" + "=" * 70)
    print("DATA GENERATION SUMMARY")
    print("=" * 70)
    print(f"Total samples: {len(df)}")
    print(f"Default rate: {df['default_90dpd'].mean()*100:.2f}%")
    print(f"\nSegment distribution:")
    print(df['consumer_segment'].value_counts())
    print(f"\nDefault rate by segment:")
    print(df.groupby('consumer_segment')['default_90dpd'].mean().sort_values(ascending=False))
    print(f"\nEmployment type distribution:")
    print(df['employment_type'].value_counts())
    print(f"\nEducation level distribution:")
    print(df['education_level'].value_counts())
    
    # Feature coverage check
    print(f"\n" + "=" * 70)
    print("FEATURE COVERAGE CHECK")
    print("=" * 70)
    
    key_features = [
        'name_dob_verified', 'phone_number_verified', 'email_verified',
        'employment_history_score', 'monthly_income_stability',
        'bill_payment_discipline', 'spending_discipline_index',
        'total_financial_assets', 'bank_statement_manipulation',
        'synthetic_id_risk'
    ]
    
    print("\nKey feature statistics:")
    for feature in key_features:
        if feature in df.columns:
            mean_val = df[feature].mean()
            std_val = df[feature].std()
            print(f"  {feature}: mean={mean_val:.3f}, std={std_val:.3f}")
    
    # Edge case coverage
    if include_edge_cases:
        print(f"\n" + "=" * 70)
        print("EDGE CASE COVERAGE")
        print("=" * 70)
        print(f"Perfect consumers (score 90-100): {(df['consumer_segment'] == 'perfect_consumer').sum()}")
        print(f"High risk consumers (score 0-34): {(df['consumer_segment'] == 'high_risk_consumer').sum()}")
        
        # Fraud indicators
        high_fraud_risk = (
            (df['bank_statement_manipulation'] > 0.7) |
            (df['synthetic_id_risk'] > 0.7)
        ).sum()
        print(f"High fraud risk profiles: {high_fraud_risk}")
        
        # Income extremes
        print(f"High income (>100k): {(df['monthly_income'] > 100000).sum()}")
        print(f"Low income (<20k): {(df['monthly_income'] < 20000).sum()}")
        
        # Behavioral extremes
        print(f"Excellent payment discipline (>0.95): {(df['bill_payment_discipline'] > 0.95).sum()}")
        print(f"Poor payment discipline (<0.5): {(df['bill_payment_discipline'] < 0.5).sum()}")
    
    print("\n" + "=" * 70)
    print("DATA GENERATION COMPLETE")
    print("=" * 70)
    print(f"\nOutputs:")
    print(f"  - CSV: {csv_path}")
    print(f"  - Excel: {excel_path}")
    print(f"\nExcel file contains 9 sheets:")
    print(f"  1. Full_Data - All records")
    print(f"  2. Summary_Statistics - Statistical summary")
    print(f"  3. Segment_Analysis - Analysis by segment")
    print(f"  4. Default_Analysis - Default patterns")
    print(f"  5. Feature_Correlations - Top feature correlations")
    print(f"  6. Risk_Distribution - Risk bucket distribution")
    print(f"  7. Data_Dictionary - Feature descriptions")
    print(f"  8. Perfect_Consumers - Top 100 perfect profiles")
    print(f"  9. High_Risk_Consumers - Top 100 high-risk profiles")
    
    return df, csv_path, excel_path


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Consumer Credit Scoring - Data Generation & Export'
    )
    parser.add_argument(
        '--samples', 
        type=int, 
        default=25000,
        help='Number of samples to generate (default: 25000)'
    )
    parser.add_argument(
        '--output', 
        type=str, 
        default='consumer_data_output',
        help='Output directory (default: consumer_data_output)'
    )
    parser.add_argument(
        '--no-edge-cases', 
        action='store_true',
        help='Exclude edge case scenarios'
    )
    
    args = parser.parse_args()
    
    # Generate and export data
    generate_and_export_data(
        n_samples=args.samples,
        output_dir=args.output,
        include_edge_cases=not args.no_edge_cases
    )


if __name__ == "__main__":
    main()

