"""
Excel Exporter for Consumer Credit Scoring Data
===============================================

Exports synthetic data to Excel with multiple sheets and formatting.

Author: ML Engineering Team
Version: 1.0.0
"""

import pandas as pd
import numpy as np
from typing import Optional
from datetime import datetime


class ConsumerDataExcelExporter:
    """Export consumer credit data to Excel with multiple sheets"""
    
    def __init__(self):
        pass
    
    def export_comprehensive_report(
        self,
        df: pd.DataFrame,
        filepath: str = "consumer_credit_data.xlsx"
    ):
        """
        Export comprehensive Excel report with multiple sheets.
        
        Args:
            df: DataFrame with consumer credit data
            filepath: Output Excel file path
        """
        print(f"Exporting {len(df)} records to Excel: {filepath}")
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            
            # Sheet 1: Full Data
            df.to_excel(writer, sheet_name='Full_Data', index=False)
            
            # Sheet 2: Summary Statistics
            summary_df = self._create_summary_stats(df)
            summary_df.to_excel(writer, sheet_name='Summary_Statistics')
            
            # Sheet 3: Segment Analysis
            segment_df = self._create_segment_analysis(df)
            segment_df.to_excel(writer, sheet_name='Segment_Analysis', index=False)
            
            # Sheet 4: Default Analysis
            default_df = self._create_default_analysis(df)
            default_df.to_excel(writer, sheet_name='Default_Analysis', index=False)
            
            # Sheet 5: Feature Correlations (top 30)
            corr_df = self._create_correlation_matrix(df)
            corr_df.to_excel(writer, sheet_name='Feature_Correlations')
            
            # Sheet 6: Risk Distribution
            risk_df = self._create_risk_distribution(df)
            risk_df.to_excel(writer, sheet_name='Risk_Distribution', index=False)
            
            # Sheet 7: Data Dictionary
            data_dict_df = self._create_data_dictionary()
            data_dict_df.to_excel(writer, sheet_name='Data_Dictionary', index=False)
            
            # Sheet 8: Perfect Consumers (Score 80-100)
            perfect_df = df[df['consumer_segment'] == 'perfect_consumer'].head(100)
            perfect_df.to_excel(writer, sheet_name='Perfect_Consumers', index=False)
            
            # Sheet 9: High Risk Consumers (Score 0-34)
            high_risk_df = df[df['consumer_segment'] == 'high_risk_consumer'].head(100)
            high_risk_df.to_excel(writer, sheet_name='High_Risk_Consumers', index=False)
            
            print(f"[SUCCESS] Excel file created: {filepath}")
            print(f"   - 9 sheets with comprehensive analysis")
            print(f"   - {len(df)} total records")
    
    def _create_summary_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create summary statistics"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        summary = df[numeric_cols].describe().T
        summary['missing_%'] = (df[numeric_cols].isnull().sum() / len(df) * 100)
        return summary
    
    def _create_segment_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze by consumer segment"""
        segment_stats = df.groupby('consumer_segment').agg({
            'default_90dpd': ['count', 'mean'],
            'monthly_income': ['mean', 'median'],
            'bill_payment_discipline': 'mean',
            'spending_discipline_index': 'mean',
            'total_financial_assets': 'mean',
            'default_probability_true': 'mean'
        }).reset_index()
        
        segment_stats.columns = [
            'Segment', 'Count', 'Default_Rate',
            'Avg_Income', 'Median_Income',
            'Avg_Bill_Payment_Discipline',
            'Avg_Spending_Discipline',
            'Avg_Financial_Assets',
            'Avg_Default_Probability'
        ]
        
        return segment_stats
    
    def _create_default_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze defaults"""
        default_analysis = []
        
        # By age group
        df['age_group'] = pd.cut(df['age'], bins=[18, 25, 35, 45, 55, 75],
                                  labels=['18-25', '26-35', '36-45', '46-55', '56+'])
        age_default = df.groupby('age_group')['default_90dpd'].agg(['count', 'mean']).reset_index()
        age_default['category'] = 'Age Group'
        age_default.columns = ['Group', 'Count', 'Default_Rate', 'Category']
        default_analysis.append(age_default)
        
        # By employment type
        emp_default = df.groupby('employment_type')['default_90dpd'].agg(['count', 'mean']).reset_index()
        emp_default['category'] = 'Employment Type'
        emp_default.columns = ['Group', 'Count', 'Default_Rate', 'Category']
        default_analysis.append(emp_default)
        
        # By education level
        edu_default = df.groupby('education_level')['default_90dpd'].agg(['count', 'mean']).reset_index()
        edu_default['category'] = 'Education Level'
        edu_default.columns = ['Group', 'Count', 'Default_Rate', 'Category']
        default_analysis.append(edu_default)
        
        return pd.concat(default_analysis, ignore_index=True)
    
    def _create_correlation_matrix(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create correlation matrix for top features"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        # Get correlations with default
        correlations = df[numeric_cols].corr()['default_90dpd'].sort_values(ascending=False)
        
        # Top 30 features
        top_features = correlations.abs().nlargest(30).index.tolist()
        
        return df[top_features].corr()
    
    def _create_risk_distribution(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create risk distribution bins"""
        bins = [0, 0.05, 0.10, 0.15, 0.20, 0.30, 1.0]
        labels = ['0-5%', '5-10%', '10-15%', '15-20%', '20-30%', '30%+']
        
        df['risk_bucket'] = pd.cut(df['default_probability_true'], bins=bins, labels=labels)
        
        risk_dist = df.groupby('risk_bucket', observed=True).agg({
            'default_90dpd': ['count', 'sum', 'mean'],
            'monthly_income': 'mean',
            'spending_discipline_index': 'mean'
        }).reset_index()
        
        risk_dist.columns = [
            'Risk_Bucket', 'Count', 'Defaults', 'Default_Rate',
            'Avg_Income', 'Avg_Spending_Discipline'
        ]
        
        return risk_dist
    
    def _create_data_dictionary(self) -> pd.DataFrame:
        """Create data dictionary"""
        data_dict = {
            'Feature': [
                'name_dob_verified', 'phone_number_verified', 'email_verified',
                'education_level', 'identity_matching', 'employment_history_score',
                'monthly_income_stability', 'income_source_verification',
                'regular_p2p_upi_transactions', 'monthly_outflow_burden',
                'avg_account_balance', 'survivability_months', 'income_retention_ratio',
                'expense_rigidity', 'inflow_time_consistency', 'emi_to_monthly_upi_amount',
                'total_financial_assets', 'insurance_coverage', 'emi_to_income_ratio',
                'rent_to_income_ratio', 'utility_to_income_ratio',
                'insurance_payment_discipline', 'spending_personality_score',
                'spending_discipline_index', 'bill_payment_discipline',
                'late_night_payment_behaviour', 'utility_payment_consistency',
                'risk_appetite_score', 'pin_code_risk_score',
                'bank_statement_manipulation', 'synthetic_id_risk',
                'default_90dpd', 'default_probability_true'
            ],
            'Description': [
                'Name and DOB verification status (0/1)',
                'Phone number verification status (0/1)',
                'Email verification status (0/1)',
                'Education level category',
                'Identity matching score (0-1)',
                'Employment history quality score (0-1)',
                'Monthly income stability score (0-1)',
                'Income source verification score (0-1)',
                'Regular P2P UPI transaction score (0-1)',
                'Monthly outflow burden ratio',
                'Average account balance (INR)',
                'Financial survivability in months',
                'Income retention ratio',
                'Expense rigidity score (0-1)',
                'Inflow time consistency score (0-1)',
                'EMI to monthly UPI amount ratio',
                'Total financial assets (INR)',
                'Insurance coverage score (0-1)',
                'EMI to income ratio',
                'Rent to income ratio',
                'Utility to income ratio',
                'Insurance payment discipline (0-1)',
                'Spending personality score (0-1)',
                'Spending discipline index (0-1)',
                'Bill payment discipline (0-1)',
                'Late-night payment behaviour score (0-1)',
                'Utility payment consistency (0-1)',
                'Risk appetite score (0-1, lower is riskier)',
                'Pin code risk score (0-1, higher is better)',
                'Bank statement manipulation risk (0-1)',
                'Synthetic ID risk score (0-1)',
                'Default flag: 90 days past due (0/1)',
                'True default probability (0-1)'
            ],
            'Weight_%': [
                1.0, 1.5, 1.0, 1.5, 2.0, 3.0, 5.0, 3.0, 3.0, 4.0,
                4.0, 4.0, 4.0, 3.0, 2.0, 4.0, 6.0, 3.0, 4.0, 2.0,
                2.0, 3.0, 3.0, 4.0, 5.0, 3.0, 2.0, 3.0, 2.0, 4.0,
                4.0, 0, 0
            ],
            'Category': [
                'Identity & Verification', 'Identity & Verification', 'Identity & Verification',
                'Identity & Verification', 'Identity & Verification', 'Employment & Income',
                'Employment & Income', 'Employment & Income', 'Employment & Income',
                'Cash Flow & Banking', 'Cash Flow & Banking', 'Cash Flow & Banking',
                'Cash Flow & Banking', 'Cash Flow & Banking', 'Cash Flow & Banking',
                'Cash Flow & Banking', 'Financial Assets', 'Financial Assets',
                'Debt Burden', 'Debt Burden', 'Debt Burden', 'Debt Burden',
                'Behavioral Patterns', 'Behavioral Patterns', 'Behavioral Patterns',
                'Behavioral Patterns', 'Behavioral Patterns', 'Risk & Fraud',
                'Risk & Fraud', 'Risk & Fraud', 'Risk & Fraud', 'Target', 'Target'
            ]
        }
        
        return pd.DataFrame(data_dict)


def export_consumer_data_to_excel(
    df: pd.DataFrame,
    filepath: str = "consumer_credit_synthetic_data.xlsx"
):
    """
    Convenience function to export consumer data to Excel.
    
    Args:
        df: DataFrame with consumer credit data
        filepath: Output Excel file path
    """
    exporter = ConsumerDataExcelExporter()
    exporter.export_comprehensive_report(df, filepath)


if __name__ == "__main__":
    # Test with sample data
    from ..data.synthetic_data_generator import ConsumerSyntheticDataGenerator
    
    generator = ConsumerSyntheticDataGenerator(seed=42)
    df = generator.generate(n_samples=5000, include_edge_cases=True)
    
    export_consumer_data_to_excel(df, "consumer_credit_test.xlsx")
    print("[SUCCESS] Test export completed!")

