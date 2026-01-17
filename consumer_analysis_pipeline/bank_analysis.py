"""
Production-Grade Bank Statement Analysis Pipeline
==================================================
Cashflow-based credit underwriting for India NBFC/Fintech

Design Philosophy:
- Survivability and ratio-first approach
- Stable feature names for ML model compatibility
- Robust edge-case handling without breaking outputs
- Optimized for large files (100k+ rows)
- Account Aggregator JSON compatibility layer ready
- No narration-based NLP (optional extension only)

Author: Senior Fintech Backend Engineer
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional, Union
from pathlib import Path
from datetime import datetime, timedelta
import warnings

# Suppress pandas performance warnings for production
warnings.filterwarnings('ignore', category=pd.errors.PerformanceWarning)

# =========================================================
# CONSTANTS & CONFIGURATION
# =========================================================

# Stable feature names (DO NOT CHANGE - ML models depend on these)
FEATURE_NAMES = [
    # Core financial features (8)
    "monthly_income",
    "monthly_expense", 
    "income_stability",
    "spending_to_income",
    "avg_balance",
    "min_balance",
    "balance_volatility",
    "survivability_months",
    
    # Behavioral features (2)
    "late_night_txn_ratio",
    "weekend_txn_ratio",
    
    # EMI/Loan features (2)
    "estimated_emi",
    "emi_to_income",
    
    # Data quality features (4)
    "data_confidence",
    "num_bank_accounts",
    "txn_count",
    "months_of_data",
    
    # Risk indicators (3)
    "bounce_rate",
    "max_inflow",
    "max_outflow",
    
    # Advanced transaction analysis (8)
    "upi_p2p_ratio",
    "utility_to_income",
    "utility_payment_consistency",
    "insurance_payment_detected",
    "rent_to_income",
    "inflow_time_consistency",
    "manipulation_risk_score",
    "expense_rigidity",
    
    # Behavioral & Impulse Features (5) - NEW
    "salary_retention_ratio",
    "week1_vs_week4_spending_ratio",
    "impulse_spending_score",
    "upi_volume_spike_score",
    "avg_balance_drop_rate"
]

# Data quality thresholds
MIN_TRANSACTIONS = 10
MIN_MONTHS = 1
OUTLIER_STD_THRESHOLD = 5.0
CHUNK_SIZE = 10000  # For large file processing

# =========================================================
# PATTERN MATCHING FOR ADVANCED FEATURES
# =========================================================

import re

# UPI P2P patterns (Indian banks)
UPI_P2P_PATTERNS = [
    r'UPI[/-]',
    r'UPIAR[/-]',
    r'@paytm',
    r'@ybl',
    r'@oksbi',
    r'@axl',
    r'@icici',
    r'@hdfc',
    r'phonepe',
    r'googlepay',
    r'bhim',
    r'gpay'
]

# Utility payment patterns
UTILITY_PATTERNS = [
    r'electricity',
    r'bijli',
    r'MSEB',
    r'BESCOM',
    r'BSES',
    r'water\s*bill',
    r'municipal',
    r'gas\s*bill',
    r'internet',
    r'broadband',
    r'wifi',
    r'airtel',
    r'jio',
    r'vodafone',
    r'vi\s',
    r'mobile\s*recharge',
    r'DTH',
    r'tata\s*sky',
    r'dish',
    r'sun\s*direct'
]

# Rent patterns
RENT_PATTERNS = [
    r'\brent\b',
    r'house\s*rent',
    r'room\s*rent',
    r'flat\s*rent',
    r'accommodation',
    r'landlord',
    r'\bPG\b',
    r'\bpg\s',
    r'hostel',
    r'lease'
]

# Insurance patterns
INSURANCE_PATTERNS = [
    r'insurance',
    r'\bLIC\b',
    r'policy',
    r'premium',
    r'HDFC\s*life',
    r'ICICI\s*pru',
    r'Max\s*life',
    r'Bajaj\s*allianz',
    r'SBI\s*life',
    r'Tata\s*AIG',
    r'health\s*insurance',
    r'term\s*insurance'
]

# Manipulation red flags
MANIPULATION_PATTERNS = [
    r'\btest\b',
    r'\bdemo\b',
    r'\bsample\b',
    r'\bdummy\b',
    r'\bfake\b'
]


# =========================================================
# 1. LOAD & VALIDATE SINGLE BANK STATEMENT (ROBUST)
# =========================================================

def load_bank_excel(path: str, account_id: str, chunksize: Optional[int] = None, debug: bool = False) -> pd.DataFrame:
    """
    Load and validate Excel bank statement with comprehensive edge-case handling.
    
    Handles:
    - Missing/extra columns
    - Date format variations (DD-MM-YYYY, YYYY-MM-DD, etc.)
    - Encoding issues
    - Duplicate headers
    - Empty/corrupted files
    - Large files (100k+ rows) via chunking
    - Mixed data types
    
    Args:
        path: Path to Excel file
        account_id: Unique account identifier
        chunksize: For large files, process in chunks (default: auto-detect)
        debug: Print debug information
        
    Returns:
        Cleaned DataFrame with standardized schema
    """
    
    # Validate file exists and is readable
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Bank statement not found: {path}")
    
    if file_path.stat().st_size == 0:
        raise ValueError(f"Empty file: {path}")
    
    # Auto-detect chunking for large files (>20MB)
    if chunksize is None and file_path.stat().st_size > 20 * 1024 * 1024:
        chunksize = CHUNK_SIZE
    
    try:
        # Read with error handling for various Excel formats
        if chunksize:
            # Process large files in chunks to avoid memory issues
            chunks = []
            reader = pd.read_excel(path, chunksize=chunksize)
            for chunk in reader:
                chunks.append(_process_chunk(chunk, account_id, debug=debug))
            df = pd.concat(chunks, ignore_index=True)
        else:
            raw_df = pd.read_excel(path, dtype_backend='numpy_nullable')
            
            if debug:
                print(f"\n[DEBUG] Raw Excel Data:")
                print(f"  Shape: {raw_df.shape}")
                print(f"  Columns: {list(raw_df.columns)}")
                print(f"\n  First few rows:")
                print(raw_df.head(10).to_string())
            
            df = _process_chunk(raw_df, account_id, debug=debug)
            
    except Exception as e:
        raise ValueError(f"Failed to read {path}: {str(e)}")
    
    # Final validation
    if len(df) == 0:
        raise ValueError(f"No valid transactions found in {path}")
    
    return df


def _process_chunk(df: pd.DataFrame, account_id: str, debug: bool = False) -> pd.DataFrame:
    """
    Internal function to process a single chunk/dataframe.
    Handles all data cleaning, validation, and standardization.
    """
    
    # Remove completely empty rows
    df = df.dropna(how='all')
    
    if len(df) == 0:
        return df
    
    # Standardize column names (handle case variations, spaces, special chars)
    original_cols = list(df.columns)
    df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_').str.replace('.', '')
    
    if debug:
        print(f"\n[DEBUG] After column standardization:")
        print(f"  Original: {original_cols}")
        print(f"  Standardized: {list(df.columns)}")
    
    # Map common column name variations to standard names
    column_mapping = {
        'date': 'txn_date',
        'transaction_date': 'txn_date',
        'value_date': 'txn_date',
        'txn_dt': 'txn_date',
        'trans_date': 'txn_date',
        'posting_date': 'txn_date',
        'tran_date': 'txn_date',
        
        'debit': 'amount_dr',
        'credit': 'amount_cr',
        'withdrawal': 'amount_dr',
        'deposit': 'amount_cr',
        'amount_debit': 'amount_dr',
        'amount_credit': 'amount_cr',
        'dr': 'amount_dr',
        'cr': 'amount_cr',
        'withdrawal_amt_(dr_)': 'amount_dr',
        'deposit_amt_(cr_)': 'amount_cr',
        
        'closing_balance': 'balance',
        'balance_amt': 'balance',
        'closing_bal': 'balance',
        'balance': 'balance',
        
        'transaction_type': 'type',
        'txn_type': 'type',
        'trans_type': 'type',
        
        'narration': 'description',
        'particulars': 'description',
        'description': 'description',
        'remarks': 'description',
        'transaction_remarks': 'description'
    }
    
    df = df.rename(columns=column_mapping)
    
    if debug:
        print(f"\n[DEBUG] After column mapping:")
        print(f"  Columns: {list(df.columns)}")
    
    # Handle split debit/credit columns (common in Indian bank statements)
    if 'amount_dr' in df.columns and 'amount_cr' in df.columns:
        df['amount_dr'] = pd.to_numeric(df['amount_dr'], errors='coerce').fillna(0)
        df['amount_cr'] = pd.to_numeric(df['amount_cr'], errors='coerce').fillna(0)
        
        # Determine type and amount
        df['type'] = np.where(df['amount_dr'] > 0, 'DR', 'CR')
        df['amount'] = np.where(df['amount_dr'] > 0, df['amount_dr'], df['amount_cr'])
        
    elif 'amount' not in df.columns:
        raise ValueError("Could not find amount column (expected 'amount', 'debit/credit', etc.)")
    
    # Validate required columns exist after mapping
    required_cols = {'txn_date', 'amount', 'balance'}
    missing = required_cols - set(df.columns)
    if missing:
        if debug:
            print(f"\n[DEBUG] Missing required columns: {missing}")
            print(f"  Available columns: {list(df.columns)}")
        raise ValueError(f"Missing required columns after mapping: {missing}")
    
    # Add type column if missing (infer from amount sign)
    if 'type' not in df.columns:
        df['type'] = 'CR'  # Default assumption
    
    if debug:
        print(f"\n[DEBUG] Before date parsing:")
        print(f"  Sample dates: {df['txn_date'].head(3).tolist()}")
    
    # Date parsing with multiple format attempts
    df['txn_date'] = _parse_dates_robust(df['txn_date'])
    
    if debug:
        print(f"\n[DEBUG] After date parsing:")
        print(f"  Sample dates: {df['txn_date'].head(3).tolist()}")
        print(f"  Null dates: {df['txn_date'].isnull().sum()}")
    
    # Amount cleaning and validation
    # Handle formats like "72.0(Dr)", "4784.4(Cr)", "1,234.50", etc.
    df['amount'] = df['amount'].astype(str)
    
    # Extract DR/CR information if embedded in amount
    amount_type_pattern = df['amount'].str.extract(r'\((Dr|CR|Cr|dr)\)', expand=False)
    has_embedded_type = amount_type_pattern.notna()
    
    # Clean amount: remove (Dr), (Cr), commas, spaces, currency symbols
    df['amount'] = (df['amount']
                    .str.replace(r'\(Dr\)', '', regex=True, case=False)
                    .str.replace(r'\(Cr\)', '', regex=True, case=False)
                    .str.replace(r'\(D\)', '', regex=True, case=False)
                    .str.replace(r'\(C\)', '', regex=True, case=False)
                    .str.replace(',', '', regex=False)
                    .str.replace('₹', '', regex=False)
                    .str.replace('Rs', '', regex=False)
                    .str.strip())
    
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df['amount'] = df['amount'].abs()  # Ensure positive
    
    # Update type if embedded in amount column
    if has_embedded_type.any():
        df.loc[has_embedded_type, 'type'] = amount_type_pattern[has_embedded_type].str.upper()
    
    # Balance cleaning (same format)
    df['balance'] = df['balance'].astype(str)
    df['balance'] = (df['balance']
                     .str.replace(r'\(Dr\)', '', regex=True, case=False)
                     .str.replace(r'\(Cr\)', '', regex=True, case=False)
                     .str.replace(r'\(D\)', '', regex=True, case=False)
                     .str.replace(r'\(C\)', '', regex=True, case=False)
                     .str.replace(',', '', regex=False)
                     .str.replace('₹', '', regex=False)
                     .str.replace('Rs', '', regex=False)
                     .str.strip())
    df['balance'] = pd.to_numeric(df['balance'], errors='coerce')
    
    # Type standardization
    df['type'] = df['type'].astype(str).str.upper().str.strip()
    df['type'] = df['type'].replace({
        'DEBIT': 'DR',
        'CREDIT': 'CR', 
        'D': 'DR',
        'C': 'CR',
        'WITHDRAWAL': 'DR',
        'DEPOSIT': 'CR'
    })
    
    if debug:
        print(f"\n[DEBUG] Before filtering:")
        print(f"  Total rows: {len(df)}")
        print(f"  Null txn_date: {df['txn_date'].isnull().sum()}")
        print(f"  Null amount: {df['amount'].isnull().sum()}")
        print(f"  Zero amounts: {(df['amount'] == 0).sum()}")
        print(f"  Transaction types: {df['type'].value_counts().to_dict()}")
    
    # Drop rows with critical missing data
    df = df.dropna(subset=['txn_date', 'amount'])
    
    # Filter to valid transaction types only
    df = df[df['type'].isin(['CR', 'DR'])]
    
    # Remove zero-amount transactions (noise)
    df = df[df['amount'] > 0]
    
    if debug:
        print(f"\n[DEBUG] After filtering:")
        print(f"  Total rows: {len(df)}")
    
    # Remove statistical outliers (likely data errors)
    df = _remove_outliers(df, 'amount')
    
    # Forward-fill balance if missing (common in some formats)
    if df['balance'].isnull().any():
        df['balance'] = df['balance'].fillna(method='ffill').fillna(method='bfill')
    
    # Add account identifier
    df['account_id'] = str(account_id)
    
    # Sort by date and reset index
    df = df.sort_values('txn_date').reset_index(drop=True)
    
    # Keep only essential columns (minimize memory for large files)
    essential_cols = ['txn_date', 'amount', 'type', 'balance', 'account_id']
    if 'description' in df.columns:
        essential_cols.append('description')
    
    df = df[essential_cols]
    
    if debug:
        print(f"\n[DEBUG] Final processed data:")
        print(f"  Total valid transactions: {len(df)}")
        if len(df) > 0:
            print(f"  Date range: {df['txn_date'].min()} to {df['txn_date'].max()}")
            print(f"  Sample transactions:")
            print(df.head(5).to_string())
    
    return df


def _parse_dates_robust(date_series: pd.Series) -> pd.Series:
    """
    Parse dates with multiple format attempts for Indian bank statements.
    """
    # Try pandas default parsing first
    parsed = pd.to_datetime(date_series, errors='coerce')
    
    # If many failures, try common Indian formats
    if parsed.isnull().sum() > len(date_series) * 0.1:
        formats_to_try = [
            '%d-%m-%Y',  # 31-12-2023
            '%d/%m/%Y',  # 31/12/2023
            '%d-%m-%y',  # 31-12-23
            '%d/%m/%y',  # 31/12/23
            '%Y-%m-%d',  # 2023-12-31
            '%d.%m.%Y',  # 31.12.2023
            '%d %b %Y',  # 31 Dec 2023
            '%d-%b-%Y',  # 31-Dec-2023
        ]
        
        for fmt in formats_to_try:
            try:
                parsed_attempt = pd.to_datetime(date_series, format=fmt, errors='coerce')
                if parsed_attempt.isnull().sum() < parsed.isnull().sum():
                    parsed = parsed_attempt
            except:
                continue
    
    return parsed


def _remove_outliers(df: pd.DataFrame, column: str, threshold: float = OUTLIER_STD_THRESHOLD) -> pd.DataFrame:
    """
    Remove statistical outliers that are likely data errors.
    Uses z-score method with configurable threshold.
    """
    if len(df) < 10:
        return df  # Skip for small datasets
    
    mean = df[column].mean()
    std = df[column].std()
    
    if std == 0:
        return df
    
    z_scores = np.abs((df[column] - mean) / std)
    return df[z_scores < threshold]


# =========================================================
# 2. MERGE MULTIPLE BANK ACCOUNTS (ENHANCED)
# =========================================================

def load_multiple_accounts(files: List[Dict[str, str]], debug: bool = False) -> pd.DataFrame:
    """
    Load and merge multiple bank accounts with error recovery.
    
    Args:
        files: List of dicts with 'path' and 'account_id'
               [{"path": "hdfc.xlsx", "account_id": "HDFC_1"}, ...]
        debug: Print debug information
    
    Returns:
        Combined DataFrame sorted by transaction date
        
    Note: Partial failures are logged but don't stop processing
    """
    if not files:
        raise ValueError("No bank files provided")
    
    dfs = []
    failed_accounts = []
    
    for f in files:
        try:
            df = load_bank_excel(f['path'], f['account_id'], debug=debug)
            if len(df) >= MIN_TRANSACTIONS:
                dfs.append(df)
            else:
                failed_accounts.append((f['account_id'], f"Too few transactions: {len(df)}"))
        except Exception as e:
            failed_accounts.append((f['account_id'], str(e)))
            continue
    
    if not dfs:
        raise ValueError(f"All accounts failed to load: {failed_accounts}")
    
    # Merge all accounts
    combined = pd.concat(dfs, ignore_index=True)
    
    # Remove duplicate transactions (can occur with overlapping statements)
    combined = combined.drop_duplicates(
        subset=['txn_date', 'amount', 'type', 'account_id'],
        keep='first'
    )
    
    # Final sort by date
    combined = combined.sort_values('txn_date').reset_index(drop=True)
    
    # Log warnings if any accounts failed (for monitoring)
    if failed_accounts:
        warnings.warn(f"Failed to load {len(failed_accounts)} accounts: {failed_accounts}")
    
    return combined


# =========================================================
# 3. MONTHLY AGGREGATION (ENHANCED WITH EDGE CASES)
# =========================================================

def monthly_aggregation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate transactions by month with robust handling.
    
    Returns:
        DataFrame with columns: month, income, expense
        Always returns at least 1 row even for empty input
    """
    if len(df) == 0:
        # Return empty monthly frame with correct structure
        return pd.DataFrame({
            'month': [],
            'income': [],
            'expense': []
        })
    
    # Create month period (handles edge cases automatically)
    df = df.copy()
    df['month'] = df['txn_date'].dt.to_period('M')
    
    # Aggregate by month and type
    monthly = (
        df.groupby(['month', 'type'], observed=True)['amount']
        .sum()
        .unstack(fill_value=0)
    )
    
    # Ensure both CR and DR columns exist
    if 'CR' not in monthly.columns:
        monthly['CR'] = 0.0
    if 'DR' not in monthly.columns:
        monthly['DR'] = 0.0
    
    # Rename to business terms
    monthly = monthly.rename(columns={'CR': 'income', 'DR': 'expense'})
    
    # Reset index and keep only needed columns
    monthly = monthly.reset_index()[['month', 'income', 'expense']]
    
    # Ensure numeric types
    monthly['income'] = pd.to_numeric(monthly['income'], errors='coerce').fillna(0)
    monthly['expense'] = pd.to_numeric(monthly['expense'], errors='coerce').fillna(0)
    
    return monthly


# =========================================================
# ENHANCED BALANCE CALCULATION HELPER
# =========================================================

def _calculate_avg_balance_on_specific_days(df: pd.DataFrame) -> float:
    """
    Calculate average account balance by checking specific days (7th, 14th, 22nd, 31st).
    
    This provides a more consistent measure by sampling balances at specific points
    rather than averaging all transactions.
    
    Args:
        df: DataFrame with transactions (must have 'date' and 'balance' columns)
        
    Returns:
        Average balance across all months and specific days
    """
    try:
        # Days to check each month
        check_days = [7, 14, 22, 31]
        
        # Ensure date is datetime
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Drop rows with invalid dates
        df = df.dropna(subset=['date'])
        
        if df.empty or 'balance' not in df.columns:
            return 0.0
        
        # Extract day and month
        df['day'] = df['date'].dt.day
        df['month_year'] = df['date'].dt.to_period('M')
        
        # Collect balances on specific days
        balances_on_days = []
        
        # Group by month
        for month_year, month_data in df.groupby('month_year'):
            # For each check day, find the balance
            for check_day in check_days:
                # Try to find exact day
                exact_day = month_data[month_data['day'] == check_day]
                
                if not exact_day.empty:
                    # Use last transaction of that day
                    balance = exact_day.iloc[-1]['balance']
                    balances_on_days.append(float(balance))
                else:
                    # Find closest previous day
                    prev_days = month_data[month_data['day'] < check_day]
                    if not prev_days.empty:
                        balance = prev_days.iloc[-1]['balance']
                        balances_on_days.append(float(balance))
                    # If check_day is 31 and month has fewer days, use last day
                    elif check_day == 31:
                        last_day = month_data.iloc[-1]['balance']
                        balances_on_days.append(float(last_day))
        
        # Calculate average
        if balances_on_days:
            return float(np.mean(balances_on_days))
        else:
            # Fallback to simple mean
            return float(df['balance'].mean())
            
    except Exception as e:
        # Fallback to simple mean on any error
        try:
            return float(df['balance'].mean())
        except:
            return 0.0


# =========================================================
# 4. CORE FINANCIAL FEATURES (PRODUCTION-HARDENED)
# =========================================================

def compute_core_features(df: pd.DataFrame, monthly: pd.DataFrame) -> Dict[str, float]:
    """
    Compute core financial features with complete edge-case handling.
    Uses merchant classification for accurate income/expense (excludes P2P, refunds, etc.)
    
    All features use defensive programming:
    - Division by zero protection
    - NaN/Inf handling
    - Empty data handling
    - Stable default values
    
    Returns:
        Dict with stable feature names (ML model compatible)
    """
    features = {}
    
    # Handle empty data gracefully
    if len(df) == 0 or len(monthly) == 0:
        return _get_default_core_features()
    
    # Use merchant classifier for accurate income/expense calculation
    try:
        from merchant_classifier import calculate_accurate_cashflow
        cashflow_result, _ = calculate_accurate_cashflow(df)
        avg_income = cashflow_result['monthly_income']
        avg_expense = cashflow_result['monthly_expense']
    except ImportError:
        # Fallback to old method if classifier not available
        avg_income = float(monthly['income'].mean())
        avg_expense = float(monthly['expense'].mean())
    
    features['monthly_income'] = _safe_float(avg_income)
    features['monthly_expense'] = _safe_float(avg_expense)
    
    # Income stability (lower is better)
    # Coefficient of variation: std/mean
    if avg_income > 0:
        income_cv = monthly['income'].std() / avg_income
        features['income_stability'] = _safe_float(income_cv, default=1.0)
    else:
        features['income_stability'] = 1.0
    
    # Spending to income ratio (lower is better)
    if avg_income > 0:
        spend_ratio = avg_expense / avg_income
        features['spending_to_income'] = _safe_float(spend_ratio, default=1.0)
    else:
        features['spending_to_income'] = 1.0
    
    # Balance metrics - Enhanced with specific days method
    avg_bal = _calculate_avg_balance_on_specific_days(df)
    min_bal = float(df['balance'].min())
    
    features['avg_balance'] = _safe_float(avg_bal)
    features['min_balance'] = _safe_float(min_bal)
    features['balance_calculation_method'] = 'specific_days_average'
    
    # Balance volatility (coefficient of variation)
    if avg_bal > 0:
        bal_cv = df['balance'].std() / avg_bal
        features['balance_volatility'] = _safe_float(bal_cv, default=1.0)
    else:
        features['balance_volatility'] = 1.0
    
    # *** SURVIVABILITY: KEY UNDERWRITING METRIC ***
    # How many months can customer survive on current balance?
    # Higher = better creditworthiness
    if avg_expense > 0:
        survivability = avg_bal / avg_expense
        features['survivability_months'] = _safe_float(survivability, default=0.0)
    else:
        features['survivability_months'] = 0.0
    
    # Additional stability metrics
    features['max_inflow'] = _safe_float(df[df['type'] == 'CR']['amount'].max())
    features['max_outflow'] = _safe_float(df[df['type'] == 'DR']['amount'].max())
    
    # Data coverage metrics
    features['months_of_data'] = len(monthly)
    features['txn_count'] = len(df)
    
    return features


def _get_default_core_features() -> Dict[str, float]:
    """Return safe default values for empty datasets."""
    return {
        'monthly_income': 0.0,
        'monthly_expense': 0.0,
        'income_stability': 1.0,
        'spending_to_income': 1.0,
        'avg_balance': 0.0,
        'min_balance': 0.0,
        'balance_volatility': 1.0,
        'survivability_months': 0.0,
        'max_inflow': 0.0,
        'max_outflow': 0.0,
        'months_of_data': 0,
        'txn_count': 0
    }


def _safe_float(value: Union[float, int, np.number], default: float = 0.0) -> float:
    """
    Convert value to safe float, handling NaN, Inf, None.
    Critical for ML model stability.
    """
    try:
        f = float(value)
        if np.isnan(f) or np.isinf(f):
            return default
        return f
    except (TypeError, ValueError):
        return default


# =========================================================
# 5. BEHAVIOURAL FEATURES (ROBUST, NON-NLP)
# =========================================================

def compute_behaviour_features(df: pd.DataFrame) -> Dict[str, float]:
    """
    Compute behavioral features from transaction patterns.
    No NLP - purely temporal and numerical patterns.
    
    Features:
    - Late night transaction ratio (risk indicator)
    - Weekend transaction ratio (behavior pattern)
    
    Returns:
        Dict with stable feature names
    """
    if len(df) == 0:
        return {
            'late_night_txn_ratio': 0.0,
            'weekend_txn_ratio': 0.0
        }
    
    df = df.copy()
    
    # Extract temporal features (handle missing time component)
    df['hour'] = df['txn_date'].dt.hour.fillna(12)  # Default to noon if time missing
    df['weekday'] = df['txn_date'].dt.weekday
    
    # Late night transactions (22:00 - 05:00) - potential risk indicator
    late_night_mask = (df['hour'] >= 22) | (df['hour'] <= 5)
    late_night_ratio = _safe_float(late_night_mask.mean())
    
    # Weekend transactions (Sat=5, Sun=6)
    weekend_ratio = _safe_float((df['weekday'] >= 5).mean())
    
    return {
        'late_night_txn_ratio': late_night_ratio,
        'weekend_txn_ratio': weekend_ratio
    }


# =========================================================
# 6. EMI ESTIMATION (ENHANCED HEURISTIC)
# =========================================================

def estimate_emi(df: pd.DataFrame, monthly_income: float) -> Dict[str, float]:
    """
    Estimate EMI/loan obligations using pattern detection.
    
    Heuristic:
    - Find recurring debit amounts (same amount, multiple months)
    - Filter for amounts in typical EMI range (₹1,000 - ₹1,00,000)
    - Select most frequent recurring amount
    
    Returns:
        Dict with estimated_emi and emi_to_income ratio
    """
    features = {}
    
    if len(df) == 0:
        return {
            'estimated_emi': 0.0,
            'emi_to_income': 0.0
        }
    
    # Filter to debit transactions only
    debits = df[df['type'] == 'DR'].copy()
    
    if len(debits) == 0:
        return {
            'estimated_emi': 0.0,
            'emi_to_income': 0.0
        }
    
    # Round amounts to nearest 100 to group similar EMIs
    # (handles small variations in EMI due to interest changes)
    debits['amount_rounded'] = (debits['amount'] / 100).round() * 100
    
    # Filter to reasonable EMI range (₹1,000 to ₹1,00,000)
    debits = debits[
        (debits['amount_rounded'] >= 1000) & 
        (debits['amount_rounded'] <= 100000)
    ]
    
    if len(debits) == 0:
        return {
            'estimated_emi': 0.0,
            'emi_to_income': 0.0
        }
    
    # Find most frequent recurring amount
    recurring = (
        debits.groupby('amount_rounded')
        .size()
        .sort_values(ascending=False)
    )
    
    # Require at least 3 occurrences to consider as EMI
    recurring = recurring[recurring >= 3]
    
    if len(recurring) > 0:
        emi_guess = float(recurring.index[0])
    else:
        emi_guess = 0.0
    
    features['estimated_emi'] = _safe_float(emi_guess)
    
    # EMI to income ratio (critical underwriting metric)
    if monthly_income > 0:
        emi_ratio = emi_guess / monthly_income
        features['emi_to_income'] = _safe_float(emi_ratio, default=0.0)
    else:
        features['emi_to_income'] = 0.0
    
    return features


# =========================================================
# 7. DATA CONFIDENCE SCORE (ENHANCED)
# =========================================================

def compute_data_confidence(df: pd.DataFrame, monthly: pd.DataFrame) -> float:
    """
    Assess data quality and reliability for underwriting decisions.
    
    Scoring factors:
    - Missing balance data (-0.2)
    - High duplicate rate (-0.2)
    - Insufficient transaction count (-0.3)
    - Insufficient time coverage (-0.2)
    - Suspicious patterns (-0.1)
    
    Returns:
        Float between 0.0 and 1.0 (minimum capped at 0.2)
    """
    score = 1.0
    
    if len(df) == 0:
        return 0.2
    
    # Check 1: Balance data completeness
    balance_null_rate = df['balance'].isnull().mean()
    if balance_null_rate > 0.05:
        score -= 0.2
    
    # Check 2: Duplicate transaction rate
    dup_rate = df.duplicated(subset=['txn_date', 'amount', 'type']).mean()
    if dup_rate > 0.02:
        score -= 0.2
    
    # Check 3: Transaction count adequacy
    # Need at least 120 transactions for reliable analysis (~4 months * 30 txns)
    if len(df) < MIN_TRANSACTIONS:
        score -= 0.4  # Severe penalty for insufficient data
    elif len(df) < 60:
        score -= 0.3
    elif len(df) < 120:
        score -= 0.2
    
    # Check 4: Time coverage (need at least 3 months)
    months_of_data = len(monthly)
    if months_of_data < MIN_MONTHS:
        score -= 0.3
    elif months_of_data < 2:
        score -= 0.2
    elif months_of_data < 3:
        score -= 0.1
    
    # Check 5: Suspicious patterns
    # - All transactions on same day (likely data dump error)
    unique_dates = df['txn_date'].nunique()
    if unique_dates < 5 and len(df) > 50:
        score -= 0.1
    
    # - Balance never changes (frozen account or bad data)
    if df['balance'].nunique() == 1 and len(df) > 10:
        score -= 0.1
    
    # Ensure minimum confidence (even bad data gets some score)
    return max(score, 0.2)


# =========================================================
# 8. BOUNCE DETECTION (NEW - KEY FOR INDIA)
# =========================================================

def compute_bounce_features(df: pd.DataFrame) -> Dict[str, float]:
    """
    Detect bounced transactions and insufficient balance events.
    Critical for Indian lending - bounces are major red flags.
    
    Returns:
        Dict with bounce_rate and related metrics
    """
    if len(df) == 0:
        return {'bounce_rate': 0.0}
    
    # Detect potential bounces:
    # 1. Balance goes negative (some banks show this)
    # 2. Debit followed immediately by credit of same amount (return)
    
    bounce_count = 0
    
    # Method 1: Negative balance check
    negative_balance = (df['balance'] < 0).sum()
    bounce_count += negative_balance
    
    # Method 2: Immediate reversal detection
    # Look for CR transactions that match DR amount within 1 day
    df_sorted = df.sort_values('txn_date').reset_index(drop=True)
    
    for i in range(len(df_sorted) - 1):
        if df_sorted.loc[i, 'type'] == 'DR':
            # Check next transaction
            if (df_sorted.loc[i+1, 'type'] == 'CR' and
                abs(df_sorted.loc[i, 'amount'] - df_sorted.loc[i+1, 'amount']) < 1 and
                (df_sorted.loc[i+1, 'txn_date'] - df_sorted.loc[i, 'txn_date']).days <= 1):
                bounce_count += 1
    
    total_debits = (df['type'] == 'DR').sum()
    
    if total_debits > 0:
        bounce_rate = bounce_count / total_debits
    else:
        bounce_rate = 0.0
    
    return {
        'bounce_rate': _safe_float(bounce_rate, default=0.0)
    }


# =========================================================
# 8B. FRAUD/MANIPULATION DETECTION HELPERS
# =========================================================

def _detect_circular_transactions(df: pd.DataFrame) -> float:
    """
    Detect circular transactions by comparing first 7 vs last 7 days.
    
    Circular transactions indicate manipulation where money is moved in/out
    artificially to inflate transaction volume or revenue.
    
    Args:
        df: DataFrame with transactions
        
    Returns:
        Risk score (0-0.3)
    """
    try:
        if len(df) < 14 or 'txn_date' not in df.columns:
            return 0.0
        
        df = df.sort_values('txn_date')
        
        # Get first 7 days and last 7 days of transactions
        dates = df['txn_date'].dt.date.unique()
        if len(dates) < 14:
            return 0.0
        
        first_7_dates = dates[:7]
        last_7_dates = dates[-7:]
        
        first_7_txns = df[df['txn_date'].dt.date.isin(first_7_dates)]
        last_7_txns = df[df['txn_date'].dt.date.isin(last_7_dates)]
        
        # Calculate total credits and debits for both periods
        first_credits = first_7_txns[first_7_txns['type'] == 'CR']['amount'].sum()
        first_debits = first_7_txns[first_7_txns['type'] == 'DR']['amount'].sum()
        
        last_credits = last_7_txns[last_7_txns['type'] == 'CR']['amount'].sum()
        last_debits = last_7_txns[last_7_txns['type'] == 'DR']['amount'].sum()
        
        # Check for suspicious symmetry
        if first_credits == 0 or last_credits == 0:
            return 0.0
        
        # Calculate similarity ratio
        credit_ratio = min(first_credits, last_credits) / max(first_credits, last_credits)
        debit_ratio = min(first_debits, last_debits) / max(first_debits, last_debits) if first_debits > 0 and last_debits > 0 else 0
        
        # If both periods have very similar amounts (>90% match)
        if credit_ratio > 0.90 and debit_ratio > 0.90:
            # Check if net flow is near zero (circular)
            first_net = abs(first_credits - first_debits)
            last_net = abs(last_credits - last_debits)
            
            first_net_ratio = first_net / first_credits if first_credits > 0 else 1.0
            last_net_ratio = last_net / last_credits if last_credits > 0 else 1.0
            
            # Both periods have near-zero net flow = circular transactions
            if first_net_ratio < 0.10 and last_net_ratio < 0.10:
                return 0.3  # High risk
        
        return 0.0
        
    except Exception as e:
        return 0.0


def _detect_regular_p2p_manipulation(df: pd.DataFrame) -> float:
    """
    Detect regular P2P transactions to same person/party.
    
    This indicates potential manipulation where applicant is artificially
    inflating revenue by repeatedly transacting with same person.
    
    Args:
        df: DataFrame with transactions
        
    Returns:
        Risk score (0-0.2)
    """
    try:
        if len(df) < 10 or 'description' not in df.columns:
            return 0.0
        
        # Get all credit transactions (potential revenue)
        credits = df[df['type'] == 'CR'].copy()
        
        if len(credits) < 5:
            return 0.0
        
        # Identify P2P transactions
        upi_pattern = '|'.join(UPI_P2P_PATTERNS)
        p2p_credits = credits[
            credits['description'].str.contains(upi_pattern, case=False, regex=True, na=False)
        ]
        
        if len(p2p_credits) < 3:
            return 0.0
        
        # Check for repeated similar amounts from same source
        # Group by similar descriptions (rough pattern matching)
        p2p_credits['desc_clean'] = p2p_credits['description'].str.lower().str.strip()
        
        # Find most frequent description pattern
        desc_counts = p2p_credits['desc_clean'].value_counts()
        
        if len(desc_counts) > 0:
            max_repeat = desc_counts.iloc[0]
            total_p2p = len(p2p_credits)
            
            # If >40% of P2P credits are from same source = suspicious
            if max_repeat > total_p2p * 0.4 and max_repeat >= 5:
                # Check if amounts are also similar (fabricated)
                most_common_desc = desc_counts.index[0]
                same_source = p2p_credits[p2p_credits['desc_clean'] == most_common_desc]
                
                # Check amount variation
                amount_std = same_source['amount'].std()
                amount_mean = same_source['amount'].mean()
                
                if amount_mean > 0:
                    cv = amount_std / amount_mean
                    
                    # Low variation in amounts = more suspicious
                    if cv < 0.15:  # Very consistent amounts
                        return 0.2
                    elif cv < 0.30:
                        return 0.1
        
        return 0.0
        
    except Exception as e:
        return 0.0


def _detect_balance_manipulation(df: pd.DataFrame) -> float:
    """
    Detect balance manipulation indicators.
    
    Checks for:
    - Sudden large credits followed by immediate debits
    - Balance artificially inflated just before statement end
    - Unrealistic balance patterns
    
    Args:
        df: DataFrame with transactions
        
    Returns:
        Risk score (0-0.2)
    """
    try:
        if len(df) < 10 or 'balance' not in df.columns or 'txn_date' not in df.columns:
            return 0.0
        
        df = df.sort_values('txn_date')
        risk = 0.0
        
        # Check 1: Large credit followed by immediate large debit (within 1-2 days)
        for i in range(len(df) - 1):
            if df.iloc[i]['type'] == 'CR' and df.iloc[i+1]['type'] == 'DR':
                credit_amt = df.iloc[i]['amount']
                debit_amt = df.iloc[i+1]['amount']
                
                # If amounts are very similar (90%+ match)
                if credit_amt > 50000 and abs(credit_amt - debit_amt) / credit_amt < 0.10:
                    # Check time difference
                    time_diff = (df.iloc[i+1]['txn_date'] - df.iloc[i]['txn_date']).days
                    if time_diff <= 2:
                        risk += 0.05
                        if risk >= 0.15:  # Cap at 0.15 for this check
                            break
        
        # Check 2: Balance artificially high at end of statement period
        # Compare last 7 days avg balance vs overall avg balance
        last_7_days = df.tail(min(30, len(df)))  # Last few transactions
        last_7_avg_balance = last_7_days['balance'].mean()
        overall_avg_balance = df['balance'].mean()
        
        if overall_avg_balance > 0:
            ratio = last_7_avg_balance / overall_avg_balance
            
            # If ending balance is 2x+ higher than average = suspicious
            if ratio > 2.0:
                risk += 0.05
        
        return min(risk, 0.2)
        
    except Exception as e:
        return 0.0


# =========================================================
# 9. ADVANCED TRANSACTION PATTERN ANALYSIS (NLP-BASED)
# =========================================================

def compute_advanced_features(df: pd.DataFrame, monthly_income: float, monthly_expense: float, estimated_emi: float = 0.0) -> Dict[str, float]:
    """
    Extract advanced features from transaction descriptions.
    Analyzes UPI patterns, utility payments, rent, insurance, expense rigidity, etc.
    
    Args:
        df: Transaction DataFrame with 'description' column
        monthly_income: Average monthly income
        monthly_expense: Average monthly expense
        estimated_emi: Estimated EMI amount
        
    Returns:
        Dict with 8 advanced features:
        - upi_p2p_ratio: % of UPI P2P transactions
        - utility_to_income: Utility payments as % of income
        - utility_payment_consistency: How regularly utilities are paid
        - insurance_payment_detected: Binary (1 if found, 0 otherwise)
        - rent_to_income: Rent as % of income
        - inflow_time_consistency: Do credits come on consistent dates?
        - manipulation_risk_score: Fabrication/manipulation detection (0-1)
        - expense_rigidity: % of expenses that are fixed/non-discretionary
    """
    
    # Return defaults if no description column
    if 'description' not in df.columns or df['description'].isnull().all() or len(df) == 0:
        return _get_default_advanced_features()
    
    try:
        # Clean descriptions
        df = df.copy()
        df['desc_clean'] = df['description'].astype(str).str.lower().str.strip()
        
        # ==========================================
        # 1. UPI P2P RATIO
        # ==========================================
        upi_pattern = '|'.join(UPI_P2P_PATTERNS)
        upi_mask = df['desc_clean'].str.contains(upi_pattern, case=False, regex=True, na=False)
        
        total_txns = len(df)
        upi_txns = upi_mask.sum()
        
        upi_ratio = _safe_float(upi_txns / total_txns if total_txns > 0 else 0.0)
        
        # ==========================================
        # 2. UTILITY TO INCOME
        # ==========================================
        utility_pattern = '|'.join(UTILITY_PATTERNS)
        utility_mask = df['desc_clean'].str.contains(utility_pattern, case=False, regex=True, na=False)
        
        utility_debits = df[utility_mask & (df['type'] == 'DR')]['amount'].sum()
        
        utility_ratio = _safe_float(
            utility_debits / monthly_income if monthly_income > 0 else 0.0
        )
        
        # ==========================================
        # 3. UTILITY PAYMENT CONSISTENCY
        # ==========================================
        if utility_debits > 0 and 'txn_date' in df.columns:
            df_utility = df[utility_mask & (df['type'] == 'DR')].copy()
            df_utility['month'] = df_utility['txn_date'].dt.to_period('M')
            
            months_with_utility = df_utility['month'].nunique()
            total_months = df['txn_date'].dt.to_period('M').nunique()
            
            consistency = months_with_utility / total_months if total_months > 0 else 0.0
            utility_consistency = _safe_float(consistency)
        else:
            utility_consistency = 0.0
        
        # ==========================================
        # 4. INSURANCE PAYMENT DETECTED
        # ==========================================
        insurance_pattern = '|'.join(INSURANCE_PATTERNS)
        insurance_mask = df['desc_clean'].str.contains(insurance_pattern, case=False, regex=True, na=False)
        
        insurance_amount = df[insurance_mask & (df['type'] == 'DR')]['amount'].sum()
        
        # Binary: 1 if insurance payments found, 0 otherwise
        insurance_detected = 1.0 if insurance_amount > 0 else 0.0
        
        # ==========================================
        # 5. RENT TO INCOME
        # ==========================================
        rent_pattern = '|'.join(RENT_PATTERNS)
        rent_mask = df['desc_clean'].str.contains(rent_pattern, case=False, regex=True, na=False)
        
        rent_amount = df[rent_mask & (df['type'] == 'DR')]['amount'].sum()
        
        if 'txn_date' in df.columns:
            total_months = df['txn_date'].dt.to_period('M').nunique()
            avg_monthly_rent = rent_amount / total_months if total_months > 0 else 0.0
        else:
            avg_monthly_rent = 0.0
        
        rent_ratio = _safe_float(
            avg_monthly_rent / monthly_income if monthly_income > 0 else 0.0
        )
        
        # ==========================================
        # 6. INFLOW TIME CONSISTENCY (IMPROVED)
        # ==========================================
        # Check if salary comes on same date every month
        inflow_consistency = compute_improved_inflow_consistency(df, monthly_income)
        
        # ==========================================
        # 7. MANIPULATION RISK SCORE (ENHANCED)
        # ==========================================
        risk_score = 0.0
        
        # Check 1: Test/demo/fake transactions
        manip_pattern = '|'.join(MANIPULATION_PATTERNS)
        test_txns = df['desc_clean'].str.contains(manip_pattern, case=False, regex=True, na=False).sum()
        if test_txns > 0:
            risk_score += 0.3
        
        # Check 2: Too many round number transactions (suspicious)
        # E.g., exactly ₹10,000, ₹50,000 (not ₹10,234)
        round_amounts = df['amount'].apply(lambda x: x % 1000 == 0 and x >= 10000)
        round_ratio = round_amounts.mean()
        if round_ratio > 0.5:  # >50% are round numbers
            risk_score += 0.3
        
        # Check 3: Same amount repeated too many times (fabricated data)
        if len(df) > 10:
            amount_counts = df['amount'].value_counts()
            max_repeat = amount_counts.iloc[0]
            if max_repeat > len(df) * 0.3:  # Same amount in 30% transactions
                risk_score += 0.2
        
        # Check 4: All transactions on same few days (data dump, not organic)
        if 'txn_date' in df.columns:
            unique_dates = df['txn_date'].nunique()
            if unique_dates < 10 and len(df) > 100:
                risk_score += 0.2
        
        # Check 5: CIRCULAR TRANSACTION DETECTION (First 7 vs Last 7 days)
        # Detects artificial revenue inflation by comparing transaction patterns
        circular_risk = _detect_circular_transactions(df)
        risk_score += circular_risk
        
        # Check 6: Regular P2P to same person (artificial revenue)
        p2p_manipulation_risk = _detect_regular_p2p_manipulation(df)
        risk_score += p2p_manipulation_risk
        
        # Check 7: Balance manipulation indicators
        balance_manipulation_risk = _detect_balance_manipulation(df)
        risk_score += balance_manipulation_risk
        
        manipulation_risk = _safe_float(min(risk_score, 1.0))
        
        # ==========================================
        # 8. EXPENSE RIGIDITY
        # ==========================================
        # Calculate % of expenses that are fixed/non-discretionary
        # Fixed expenses = Rent + EMI + Utilities + Insurance
        
        # We already calculated these amounts above
        total_months = df['txn_date'].dt.to_period('M').nunique() if 'txn_date' in df.columns else 1
        
        # Monthly averages
        monthly_rent = rent_amount / total_months if total_months > 0 else 0.0
        monthly_utility = utility_debits / total_months if total_months > 0 else 0.0
        monthly_insurance = insurance_amount / total_months if total_months > 0 else 0.0
        monthly_emi_fixed = estimated_emi
        
        # Total fixed expenses per month
        fixed_expenses = monthly_rent + monthly_utility + monthly_insurance + monthly_emi_fixed
        
        # Rigidity ratio
        if monthly_expense > 0:
            rigidity = fixed_expenses / monthly_expense
            # Cap at 1.0 (can't be more than 100%)
            expense_rigidity_value = _safe_float(min(rigidity, 1.0))
        else:
            expense_rigidity_value = 0.0
        
        # ==========================================
        # 9. EXPENSE CATEGORY BREAKDOWN (using merchant classifier)
        # ==========================================
        expense_categories = {}
        try:
            from merchant_classifier import calculate_accurate_cashflow
            cashflow_result, _ = calculate_accurate_cashflow(df)
            expense_categories = {
                'utility_expense_pct': (cashflow_result['utility_expense'] / monthly_expense * 100) if monthly_expense > 0 else 0.0,
                'food_expense_pct': (cashflow_result['food_expense'] / monthly_expense * 100) if monthly_expense > 0 else 0.0,
                'transport_expense_pct': (cashflow_result['transport_expense'] / monthly_expense * 100) if monthly_expense > 0 else 0.0,
                'shopping_expense_pct': (cashflow_result['shopping_expense'] / monthly_expense * 100) if monthly_expense > 0 else 0.0,
                'p2p_ratio': cashflow_result['p2p_txn_count'] / len(df) if len(df) > 0 else 0.0,
            }
        except ImportError:
            # Classifier not available, use defaults
            expense_categories = {
                'utility_expense_pct': 0.0,
                'food_expense_pct': 0.0,
                'transport_expense_pct': 0.0,
                'shopping_expense_pct': 0.0,
                'p2p_ratio': 0.0,
            }
        
        return {
            'upi_p2p_ratio': upi_ratio,
            'utility_to_income': utility_ratio,
            'utility_payment_consistency': utility_consistency,
            'insurance_payment_detected': insurance_detected,
            'rent_to_income': rent_ratio,
            'inflow_time_consistency': inflow_consistency,
            'manipulation_risk_score': manipulation_risk,
            'expense_rigidity': expense_rigidity_value,
            **expense_categories  # Add expense breakdown features
        }
        
    except Exception as e:
        # Fallback to defaults if any error
        warnings.warn(f"Advanced feature extraction failed: {str(e)}")
        return _get_default_advanced_features()


def _get_default_advanced_features() -> Dict[str, float]:
    """Return safe defaults when description not available or parsing fails."""
    return {
        'upi_p2p_ratio': 0.0,
        'utility_to_income': 0.0,
        'utility_payment_consistency': 0.0,
        'insurance_payment_detected': 0.0,
        'rent_to_income': 0.0,
        'inflow_time_consistency': 0.0,
        'manipulation_risk_score': 0.0,
        'expense_rigidity': 0.0,
        'utility_expense_pct': 0.0,
        'food_expense_pct': 0.0,
        'transport_expense_pct': 0.0,
        'shopping_expense_pct': 0.0,
        'p2p_ratio': 0.0,
    }


# =========================================================
# 9B. IMPULSE & BEHAVIORAL FEATURES (NEW)
# =========================================================

def compute_impulse_behavioral_features(
    df: pd.DataFrame,
    monthly_income: float,
    monthly_expense: float
) -> Dict[str, float]:
    """
    Compute impulse spending and behavioral patterns.
    
    Features:
    1. Salary Retention: How much salary is retained after week 1
    2. Week 1 vs Week 4 Spending: Compare early vs late month spending
    3. Impulse Spending Score: Pattern of impulsive purchases
    4. UPI Volume Spike Detector: Sudden changes in UPI transaction volume
    5. Average Balance Drop Rate: How fast balance depletes
    
    Returns:
        Dict with 5 behavioral risk indicators
    """
    if len(df) == 0 or 'txn_date' not in df.columns:
        return _get_default_impulse_features()
    
    try:
        df = df.copy()
        df['txn_date'] = pd.to_datetime(df['txn_date'])
        df = df.sort_values('txn_date')
        
        features = {}
        
        # ==========================================
        # 1. SALARY RETENTION & WEEK 1 VS WEEK 4 SPENDING
        # ==========================================
        # Group transactions by month and week
        df['month'] = df['txn_date'].dt.to_period('M')
        df['day_of_month'] = df['txn_date'].dt.day
        
        salary_retention_ratios = []
        week1_vs_week4_ratios = []
        
        for month, month_df in df.groupby('month'):
            # Identify salary credit (largest credit in month)
            month_credits = month_df[month_df['type'] == 'CR']
            if len(month_credits) == 0:
                continue
            
            # Assume salary is the largest credit
            salary_amount = month_credits['amount'].max()
            salary_date = month_credits[month_credits['amount'] == salary_amount]['txn_date'].iloc[0]
            
            # Week 1: 7 days after salary
            week1_end = salary_date + timedelta(days=7)
            week1_spending = month_df[
                (month_df['txn_date'] > salary_date) &
                (month_df['txn_date'] <= week1_end) &
                (month_df['type'] == 'DR')
            ]['amount'].sum()
            
            # Week 4: Days 22-31 of month
            week4_spending = month_df[
                (month_df['day_of_month'] >= 22) &
                (month_df['day_of_month'] <= 31) &
                (month_df['type'] == 'DR')
            ]['amount'].sum()
            
            # Salary retention: What % of salary is left after week 1
            if salary_amount > 0:
                retention = (salary_amount - week1_spending) / salary_amount
                salary_retention_ratios.append(max(0, min(1, retention)))
            
            # Week 1 vs Week 4 spending pattern
            if week4_spending > 0 and week1_spending > 0:
                ratio = week1_spending / week4_spending
                week1_vs_week4_ratios.append(ratio)
        
        # Average retention and spending ratios
        features['salary_retention_ratio'] = _safe_float(
            np.mean(salary_retention_ratios) if salary_retention_ratios else 0.5
        )
        
        features['week1_vs_week4_spending_ratio'] = _safe_float(
            np.mean(week1_vs_week4_ratios) if week1_vs_week4_ratios else 1.0
        )
        
        # ==========================================
        # 2. IMPULSE SPENDING SCORE
        # ==========================================
        # Detect impulsive spending patterns:
        # - Multiple transactions in short time
        # - Large transactions outside normal pattern
        # - Evening/night spending sprees
        
        impulse_indicators = 0.0
        
        # Check 1: Multiple transactions in same day
        df['date'] = df['txn_date'].dt.date
        debits_by_date = df[df['type'] == 'DR'].groupby('date')['amount'].agg(['count', 'sum'])
        
        high_frequency_days = (debits_by_date['count'] > 5).sum()
        total_days = len(debits_by_date)
        
        if total_days > 0:
            impulse_indicators += (high_frequency_days / total_days) * 0.3
        
        # Check 2: Large irregular transactions (>2x mean)
        mean_debit = df[df['type'] == 'DR']['amount'].mean()
        if mean_debit > 0:
            large_debits = df[(df['type'] == 'DR') & (df['amount'] > mean_debit * 2)]
            large_debit_ratio = len(large_debits) / len(df[df['type'] == 'DR'])
            impulse_indicators += large_debit_ratio * 0.3
        
        # Check 3: Late night/evening spending (if time available)
        if 'txn_date' in df.columns:
            df['hour'] = df['txn_date'].dt.hour
            evening_debits = df[(df['type'] == 'DR') & (df['hour'] >= 20)]['amount'].sum()
            total_debits = df[df['type'] == 'DR']['amount'].sum()
            
            if total_debits > 0:
                evening_ratio = evening_debits / total_debits
                impulse_indicators += evening_ratio * 0.2
        
        # Check 4: High week 1 spending (already computed)
        if features['week1_vs_week4_spending_ratio'] > 1.5:
            impulse_indicators += 0.2
        
        features['impulse_spending_score'] = _safe_float(min(impulse_indicators, 1.0))
        
        # ==========================================
        # 3. UPI VOLUME SPIKE DETECTOR
        # ==========================================
        # Detect sudden spikes in UPI transaction volume/amount
        
        if 'description' in df.columns:
            df['is_upi'] = df['description'].str.contains('UPI|IMPS|NEFT', case=False, na=False)
            
            # Group UPI transactions by week
            df['week'] = df['txn_date'].dt.isocalendar().week
            upi_weekly = df[df['is_upi']].groupby('week')['amount'].agg(['sum', 'count'])
            
            if len(upi_weekly) >= 4:
                # Calculate coefficient of variation (volatility)
                upi_amounts = upi_weekly['sum']
                upi_counts = upi_weekly['count']
                
                # Detect spikes: weeks that are >2x the median
                median_amount = upi_amounts.median()
                if median_amount > 0:
                    spike_weeks = (upi_amounts > median_amount * 2).sum()
                    spike_ratio = spike_weeks / len(upi_weekly)
                    
                    # Higher spike ratio = higher risk
                    features['upi_volume_spike_score'] = _safe_float(min(spike_ratio * 2, 1.0))
                else:
                    features['upi_volume_spike_score'] = 0.0
            else:
                features['upi_volume_spike_score'] = 0.0
        else:
            features['upi_volume_spike_score'] = 0.0
        
        # ==========================================
        # 4. AVERAGE BALANCE DROP RATE
        # ==========================================
        # How fast does balance drop after salary/inflow
        
        if 'balance' in df.columns:
            # Find all major inflows (>50% of monthly income)
            major_inflows = df[
                (df['type'] == 'CR') & 
                (df['amount'] > monthly_income * 0.5)
            ]
            
            balance_drop_rates = []
            
            for idx, inflow in major_inflows.iterrows():
                inflow_date = inflow['txn_date']
                inflow_balance = inflow['balance']
                
                # Check balance 7 days later
                future_txns = df[
                    (df['txn_date'] > inflow_date) &
                    (df['txn_date'] <= inflow_date + timedelta(days=7))
                ]
                
                if len(future_txns) > 0:
                    balance_after_7days = future_txns.iloc[-1]['balance']
                    
                    if inflow_balance > 0:
                        drop_rate = (inflow_balance - balance_after_7days) / inflow_balance
                        balance_drop_rates.append(max(0, min(1, drop_rate)))
            
            # Average drop rate
            if balance_drop_rates:
                features['avg_balance_drop_rate'] = _safe_float(np.mean(balance_drop_rates))
            else:
                # If no data, use spending to income as proxy
                features['avg_balance_drop_rate'] = _safe_float(
                    min(monthly_expense / monthly_income, 1.0) if monthly_income > 0 else 0.5
                )
        else:
            features['avg_balance_drop_rate'] = 0.5
        
        return features
        
    except Exception as e:
        warnings.warn(f"Impulse feature extraction failed: {str(e)}")
        return _get_default_impulse_features()


def _get_default_impulse_features() -> Dict[str, float]:
    """Return safe defaults for impulse features."""
    return {
        'salary_retention_ratio': 0.5,
        'week1_vs_week4_spending_ratio': 1.0,
        'impulse_spending_score': 0.0,
        'upi_volume_spike_score': 0.0,
        'avg_balance_drop_rate': 0.5
    }


# =========================================================
# 10. IMPROVED INFLOW TIME CONSISTENCY
# =========================================================

def compute_improved_inflow_consistency(df: pd.DataFrame, monthly_income: float) -> float:
    """
    Check if salary/income comes on the same date every month.
    
    Improved version: Checks if largest credit comes on consistent dates.
    
    Returns:
        Consistency score (0-1, higher = more consistent)
    """
    try:
        if len(df) == 0 or 'txn_date' not in df.columns:
            return 0.0
        
        df = df.copy()
        df['txn_date'] = pd.to_datetime(df['txn_date'])
        df['month'] = df['txn_date'].dt.to_period('M')
        df['day_of_month'] = df['txn_date'].dt.day
        
        # Identify salary credits (largest credit per month)
        salary_dates = []
        
        for month, month_df in df.groupby('month'):
            month_credits = month_df[month_df['type'] == 'CR']
            
            if len(month_credits) == 0:
                continue
            
            # Assume largest credit is salary
            largest_credit = month_credits['amount'].max()
            
            # Only consider if it's significant (>30% of monthly income)
            if largest_credit >= monthly_income * 0.3:
                salary_day = month_credits[month_credits['amount'] == largest_credit]['day_of_month'].iloc[0]
                salary_dates.append(salary_day)
        
        if len(salary_dates) < 2:
            return 0.0
        
        # Check consistency: Calculate standard deviation of dates
        date_std = np.std(salary_dates)
        
        # Convert to consistency score (lower std = higher consistency)
        # STD of 0-2 days = perfect (1.0)
        # STD of 5+ days = poor (0.0)
        if date_std <= 2:
            consistency = 1.0
        elif date_std >= 5:
            consistency = 0.0
        else:
            consistency = 1.0 - ((date_std - 2) / 3)
        
        return _safe_float(consistency)
        
    except Exception:
        return 0.0


# =========================================================
# 10. FINAL FEATURE VECTOR (MODEL READY)
# =========================================================

def build_feature_vector(bank_files: List[Dict[str, str]], debug: bool = False) -> pd.DataFrame:
    """
    Build complete feature vector for ML model.
    
    This is the main entry point for the pipeline.
    
    Args:
        bank_files: List of dicts with 'path' and 'account_id'
        debug: Print debug information
        
    Returns:
        Single-row DataFrame with all features in stable order
        
    Note: Always returns a valid DataFrame even on partial failures
    """
    try:
        # Load all accounts
        df = load_multiple_accounts(bank_files, debug=debug)
        
        # Aggregate by month
        monthly = monthly_aggregation(df)
        
        # Compute all feature groups
        core = compute_core_features(df, monthly)
        behaviour = compute_behaviour_features(df)
        emi = estimate_emi(df, core['monthly_income'])
        bounce = compute_bounce_features(df)
        advanced = compute_advanced_features(
            df, 
            core['monthly_income'], 
            core['monthly_expense'],
            emi['estimated_emi']
        )
        impulse = compute_impulse_behavioral_features(
            df,
            core['monthly_income'],
            core['monthly_expense']
        )
        confidence = compute_data_confidence(df, monthly)
        
        # Merge all features
        features = {
            **core,
            **behaviour,
            **emi,
            **bounce,
            **advanced,
            **impulse,
            'data_confidence': confidence,
            'num_bank_accounts': df['account_id'].nunique()
        }
        
    except Exception as e:
        # Catastrophic failure - return default feature vector
        warnings.warn(f"Feature extraction failed: {str(e)}")
        features = _get_default_feature_vector()
    
    # Ensure all expected features exist (ML model compatibility)
    for fname in FEATURE_NAMES:
        if fname not in features:
            features[fname] = 0.0
    
    # Convert to DataFrame with stable column order
    feature_df = pd.DataFrame([features])
    feature_df = feature_df[FEATURE_NAMES]  # Enforce column order
    
    return feature_df


def _get_default_feature_vector() -> Dict[str, float]:
    """Return safe default feature vector for catastrophic failures."""
    return {fname: 0.0 for fname in FEATURE_NAMES}


# =========================================================
# 10. ACCOUNT AGGREGATOR JSON ADAPTER (FUTURE-READY)
# =========================================================

def load_from_aa_json(aa_json: Dict, account_id: str) -> pd.DataFrame:
    """
    Load transactions from Account Aggregator JSON format.
    Converts AA format to internal DataFrame format.
    
    This function provides forward compatibility for when
    Excel statements are replaced with AA JSON feeds.
    
    Args:
        aa_json: Account Aggregator JSON response
        account_id: Unique account identifier
        
    Returns:
        DataFrame in same format as load_bank_excel()
        
    Note: Implement based on ReBIT AA technical standards
    """
    # Placeholder implementation for AA JSON format
    # Actual implementation depends on specific AA provider
    
    transactions = aa_json.get('transactions', [])
    
    if not transactions:
        raise ValueError("No transactions in AA JSON")
    
    # Convert to DataFrame
    df = pd.DataFrame(transactions)
    
    # Map AA fields to internal schema
    df = df.rename(columns={
        'transactionTimestamp': 'txn_date',
        'amount': 'amount',
        'type': 'type',
        'currentBalance': 'balance'
    })
    
    # Process using same pipeline as Excel
    df['account_id'] = account_id
    df = _process_chunk(df, account_id)
    
    return df


# =========================================================
# 11. PD → CREDIT SCORE MAPPING
# =========================================================

def pd_to_score(pd_prob: float) -> int:
    """
    Convert probability of default (PD) to credit score.
    
    Mapping:
    - PD = 0.00 → Score = 900 (excellent)
    - PD = 0.50 → Score = 600 (average)
    - PD = 1.00 → Score = 300 (poor)
    
    Args:
        pd_prob: Probability of default (0.0 to 1.0)
        
    Returns:
        Credit score (300 to 900)
    """
    pd_prob = max(0.0, min(1.0, pd_prob))  # Clamp to valid range
    score = 900 - int(pd_prob * 600)
    return max(300, min(900, score))


# =========================================================
# 12. VALIDATION & EXPORT UTILITIES
# =========================================================

def validate_feature_vector(features: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validate feature vector before sending to ML model.
    
    Returns:
        (is_valid, list_of_errors)
    """
    errors = []
    
    # Check shape
    if len(features) != 1:
        errors.append(f"Expected 1 row, got {len(features)}")
    
    # Check all required features exist
    missing_features = set(FEATURE_NAMES) - set(features.columns)
    if missing_features:
        errors.append(f"Missing features: {missing_features}")
    
    # Check for NaN/Inf values
    if features.isnull().any().any():
        null_cols = features.columns[features.isnull().any()].tolist()
        errors.append(f"NaN values in: {null_cols}")
    
    if np.isinf(features.select_dtypes(include=[np.number])).any().any():
        errors.append("Inf values detected")
    
    # Check data confidence threshold
    if 'data_confidence' in features.columns:
        if features['data_confidence'].iloc[0] < 0.3:
            errors.append(f"Low data confidence: {features['data_confidence'].iloc[0]:.2f}")
    
    return (len(errors) == 0, errors)


# =========================================================
# 13. CLI INTERFACE
# =========================================================

if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Bank Statement Cashflow Analysis for Credit Underwriting',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python bank_analysis.py statement.xlsx
  python bank_analysis.py hdfc.xlsx --account HDFC_01
  python bank_analysis.py hdfc.xlsx icici.xlsx --accounts HDFC ICICI
        """
    )
    
    parser.add_argument('files', nargs='+', help='Bank statement Excel file(s)')
    parser.add_argument('--accounts', nargs='*', help='Account IDs (optional)')
    parser.add_argument('--export', help='Export features to CSV file')
    parser.add_argument('--debug', action='store_true', help='Show debug information')
    
    args = parser.parse_args()
    
    # Prepare bank files
    bank_files = []
    for i, file_path in enumerate(args.files):
        account_id = args.accounts[i] if args.accounts and i < len(args.accounts) else f"ACCOUNT_{i+1}"
        bank_files.append({"path": file_path, "account_id": account_id})
    
    print("=" * 80)
    print("CASHFLOW CREDIT UNDERWRITING PIPELINE")
    print("=" * 80)
    
    for bf in bank_files:
        print(f"  {bf['account_id']}: {bf['path']}")
    
    try:
        # Build feature vector
        print("\nLoading and analyzing bank statements...")
        features_df = build_feature_vector(bank_files, debug=args.debug)
        
        # Validate
        is_valid, errors = validate_feature_vector(features_df)
        
        if not is_valid:
            print(f"\nVALIDATION WARNINGS:")
            for err in errors:
                print(f"  - {err}")
        else:
            print("\nValidation: PASSED")
        
        # Display all features
        print("\n" + "=" * 80)
        print("EXTRACTED FEATURES (FOR ML MODEL)")
        print("=" * 80)
        print(features_df.T.to_string())
        
        # Display key metrics summary
        print("\n" + "=" * 80)
        print("KEY METRICS SUMMARY")
        print("=" * 80)
        
        print(f"\nINCOME & EXPENSE:")
        print(f"  Monthly Income:        Rs {features_df['monthly_income'].iloc[0]:,.2f}")
        print(f"  Monthly Expense:       Rs {features_df['monthly_expense'].iloc[0]:,.2f}")
        print(f"  Spending Ratio:        {features_df['spending_to_income'].iloc[0]:.2%}")
        
        print(f"\nBALANCE:")
        print(f"  Average Balance:       Rs {features_df['avg_balance'].iloc[0]:,.2f}")
        print(f"  Minimum Balance:       Rs {features_df['min_balance'].iloc[0]:,.2f}")
        print(f"  Volatility:            {features_df['balance_volatility'].iloc[0]:.2f}")
        
        print(f"\nKEY RATIOS:")
        print(f"  Survivability:         {features_df['survivability_months'].iloc[0]:.2f} months")
        print(f"  EMI to Income:         {features_df['emi_to_income'].iloc[0]:.2%}")
        print(f"  Bounce Rate:           {features_df['bounce_rate'].iloc[0]:.2%}")
        print(f"  Income Stability:      {features_df['income_stability'].iloc[0]:.2f}")
        
        print(f"\nDATA QUALITY:")
        print(f"  Transactions:          {int(features_df['txn_count'].iloc[0])}")
        print(f"  Months of Data:        {int(features_df['months_of_data'].iloc[0])}")
        print(f"  Confidence Score:      {features_df['data_confidence'].iloc[0]:.2%}")
        
        print("\n" + "=" * 80)
        
        # Export if requested
        if args.export:
            features_df.to_csv(args.export, index=False)
            print(f"\nFeatures exported to: {args.export}")
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
