"""
JSON-based Bank Statement Analysis Views
For Account Aggregator integration - accepts JSON directly
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.utils import timezone
import pandas as pd
import json

from .analyzer import (
    compute_core_features, compute_behaviour_features,
    compute_advanced_features, compute_impulse_behavioral_features,
    estimate_emi, compute_bounce_features, monthly_aggregation
)
try:
    from apps.customer.credit_report_analysis.liability_detector import detect_liabilities_simple
except ImportError:
    # Fallback if module not available
    def detect_liabilities_simple(*args, **kwargs):
        return {
            'total_liabilities': 0.0,
            'total_monthly_emi': 0.0,
            'active_loans': [],
            'credit_cards': [],
            'liability_sources': {'from_bank_statement': False},
            'debt_ratios': {},
            'risk_indicators': {}
        }


def extract_transactions_from_aa_format(data):
    """
    Extract transactions from Account Aggregator JSON format.
    
    The AA format has structure:
    {
        "banks": [
            {
                "accounts": [
                    {
                        "fraud_analysis": [
                            {
                                "transactions": [
                                    {
                                        "amount": 100.0,
                                        "balance": 1000.0,
                                        "transaction_date": "2022-01-01",
                                        "narration": "Description",
                                        "category": "Category"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    Returns:
        List of transactions in standard format
        Account info dict
    """
    transactions = []
    account_info = {}
    seen_transactions = set()  # For deduplication
    
    # Check if this is AA format
    if 'banks' not in data:
        return None, None
    
    # Track all accounts for multi-account support
    all_accounts = []
    
    # Extract from all banks and accounts
    for bank in data.get('banks', []):
        bank_name = bank.get('bank', 'Unknown Bank')
        
        for account in bank.get('accounts', []):
            account_num = account.get('account_number', '')
            account_ifsc = account.get('ifsc_code', '')
            holder_name = account.get('customer_info', {}).get('holders', [{}])[0].get('name', '') if account.get('customer_info', {}).get('holders') else ''
            
            # Store account info for each account
            all_accounts.append({
                'account_number': account_num,
                'bank_name': bank_name,
                'ifsc': account_ifsc,
                'holder_name': holder_name
            })
            
            # Extract account info from first account (for backward compatibility)
            if not account_info:
                account_info = {
                    'account_number': account_num,
                    'bank_name': bank_name,
                    'ifsc': account_ifsc,
                    'holder_name': holder_name
                }
            
            # Extract transactions from fraud_analysis OR transactions array
            # Some formats have transactions directly in account
            account_transactions = []
            
            # Method 1: Check fraud_analysis
            for fraud_item in account.get('fraud_analysis', []):
                account_transactions.extend(fraud_item.get('transactions', []))
            
            # Method 2: Check direct transactions array (if fraud_analysis not present)
            if not account_transactions:
                account_transactions = account.get('transactions', [])
            
            for txn in account_transactions:
                    # Create unique key for deduplication
                    # Handle different date field names: transaction_date, date, transaction_timestamp
                    txn_date = txn.get('transaction_date') or txn.get('date') or txn.get('transaction_timestamp', '')
                    if isinstance(txn_date, str) and ' ' in txn_date:
                        txn_date = txn_date.split()[0]  # Extract date part if timestamp
                    
                    # Include bank and account in key to avoid false duplicates between different accounts
                    txn_key = (
                        txn_date,
                        txn.get('amount'),
                        txn.get('narration', ''),
                        txn.get('balance'),
                        bank_name,  # Include bank name to distinguish between accounts
                        account_num  # Include account number
                    )
                    
                    if txn_key in seen_transactions:
                        continue
                    seen_transactions.add(txn_key)
                    
                    # Convert to standard format
                    amount = float(txn.get('amount', 0))
                    category = str(txn.get('category', '')).lower()
                    narration = str(txn.get('narration', ''))
                    
                    # Handle different date field names
                    txn_date = txn.get('transaction_date') or txn.get('date') or txn.get('transaction_timestamp', '')
                    if isinstance(txn_date, str) and ' ' in txn_date:
                        txn_date = txn_date.split()[0]  # Extract date part if timestamp
                    
                    # Determine debit/credit based on category and narration
                    debit = 0.0
                    credit = 0.0
                    
                    # Check category first
                    debit_categories = ['debit', 'withdrawal', 'payment', 'expense', 'charge', 'fee', 
                                       'cash withdrawal', 'transfer to', 'interest paid', 'int.pd']
                    credit_categories = ['credit', 'deposit', 'salary', 'income', 'refund', 
                                        'cash deposit', 'transfer from', 'transfer in', 
                                        'interest received', 'interest recd']
                    
                    if any(dc in category for dc in debit_categories):
                        debit = abs(amount)
                    elif any(cc in category for cc in credit_categories):
                        credit = abs(amount)
                    else:
                        # Check narration
                        narration_lower = narration.lower()
                        if any(kw in narration_lower for kw in ['paid', 'debit', 'withdrawal', 'payment', 'charge', 'fee', 'wdl', 'sent']):
                            debit = abs(amount)
                        elif any(kw in narration_lower for kw in ['credit', 'deposit', 'salary', 'income', 'refund', 'received', 'credited', 'dep']):
                            credit = abs(amount)
                        else:
                            # Default: positive amount = credit, negative = debit
                            if amount < 0:
                                debit = abs(amount)
                            else:
                                credit = abs(amount)
                    
                    # Create amount field - use the larger of debit or credit
                    # This helps with compatibility with code that expects amount
                    amount_value = max(debit, credit) if (debit > 0 or credit > 0) else abs(amount)
                    
                    standard_txn = {
                        'date': txn_date,
                        'description': narration,
                        'debit': debit,
                        'credit': credit,
                        'amount': amount_value,  # Add amount field for compatibility
                        'balance': float(txn.get('balance', 0)) if txn.get('balance') else 0.0,
                        'category': category
                    }
                    
                    # Add account identifier to transaction for multi-account tracking
                    standard_txn['account_id'] = f"{bank_name}_{account_num}"
                    standard_txn['bank_name'] = bank_name
                    
                    transactions.append(standard_txn)
    
    # If multiple accounts found, update account_info to reflect this
    if len(all_accounts) > 1:
        # Keep first account as primary, but add multi-account info
        account_info['multiple_accounts'] = True
        account_info['total_accounts'] = len(all_accounts)
        account_info['all_accounts'] = all_accounts
        # Combine bank names
        bank_names = list(set([acc['bank_name'] for acc in all_accounts]))
        if len(bank_names) > 1:
            account_info['bank_name'] = ', '.join(bank_names)  # Show all banks
        else:
            account_info['bank_name'] = bank_names[0] if bank_names else account_info.get('bank_name', '')
    else:
        account_info['multiple_accounts'] = False
        account_info['total_accounts'] = 1
    
    return transactions, account_info


class BankStatementJSONAnalysisView(APIView):
    """
    Direct JSON analysis for Account Aggregator data
    No file upload needed - accepts JSON directly
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Analyze bank statement from JSON data
        
        Request Body:
        {
            "transactions": [
                {
                    "date": "2024-01-15",
                    "description": "UPI Payment",
                    "debit": 500.0,
                    "credit": 0.0,
                    "balance": 10000.0
                },
                ...
            ],
            "account_info": {
                "account_number": "1234567890",
                "bank_name": "HDFC Bank",
                "ifsc": "HDFC0001234",
                "holder_name": "John Doe"
            }
        }
        """
        try:
            data = request.data
            
            # Validate input is a dictionary
            if not isinstance(data, dict):
                return Response({
                    'success': False,
                    'message': f'Invalid data type. Expected JSON object (dictionary), got {type(data).__name__}. Please send JSON object with "transactions" array, not a plain array.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Extract transactions - try standard format first
            transactions = data.get('transactions', [])
            account_info = data.get('account_info', {})
            
            # If no transactions in standard format, try Account Aggregator format
            if not transactions:
                aa_transactions, aa_account_info = extract_transactions_from_aa_format(data)
                if aa_transactions is not None:  # None means not AA format, [] means AA format but no transactions
                    transactions = aa_transactions
                    if aa_account_info:
                        account_info = aa_account_info
                elif 'banks' in data:
                    # It's AA format but no transactions found
                    return Response({
                        'success': False,
                        'message': 'Account Aggregator format detected but no transactions found in fraud_analysis sections'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            if not transactions:
                return Response({
                    'success': False,
                    'message': 'No transactions found in JSON data. Expected either: 1) top-level "transactions" array, or 2) Account Aggregator format with "banks" -> "accounts" -> "fraud_analysis" -> "transactions"'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Convert to DataFrame - ensure clean data structure
            try:
                df = pd.DataFrame(transactions)
                # Reset index to avoid any index conflicts
                df = df.reset_index(drop=True)
            except Exception as e:
                return Response({
                    'success': False,
                    'message': f'Failed to create DataFrame from transactions: {str(e)}. Please check transaction data format.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Remove any duplicate columns (pandas can create these in some cases)
            df = df.loc[:, ~df.columns.duplicated()]
            
            # Remove duplicate transactions based on key fields to avoid conflicts
            if len(df) > 0:
                # Identify key columns for deduplication
                dedup_cols = []
                if 'date' in df.columns:
                    dedup_cols.append('date')
                elif 'transaction_date' in df.columns:
                    dedup_cols.append('transaction_date')
                
                if 'amount' in df.columns:
                    dedup_cols.append('amount')
                elif 'debit' in df.columns and 'credit' in df.columns:
                    dedup_cols.extend(['debit', 'credit'])
                
                if 'description' in df.columns:
                    dedup_cols.append('description')
                elif 'narration' in df.columns:
                    dedup_cols.append('narration')
                
                if dedup_cols:
                    initial_count = len(df)
                    df = df.drop_duplicates(subset=dedup_cols, keep='first').reset_index(drop=True)
                    if initial_count != len(df):
                        print(f"[DEBUG] Removed {initial_count - len(df)} duplicate transactions")
            
            # Normalize column names - support multiple formats
            # Check for ALL possible column name variations and create unified columns
            # Keep original columns, just add normalized ones (don't replace)
            
            # Date column variations - check all possibilities
            date_columns = ['date', 'transaction_date', 'txn_date', 'transactionDate', 'TransactionDate', 'Date', 'DATE', 
                          'transactionDate', 'TxnDate', 'TXN_DATE', 'trans_date', 'TransDate']
            date_col = None
            # Check all variations, prioritize exact match 'date' first
            for col in date_columns:
                if col in df.columns:
                    date_col = col
                    break
            
            # Create normalized 'date' column only if it doesn't exist and we found a variation
            if 'date' not in df.columns and date_col:
                df['date'] = df[date_col]
            elif date_col and date_col != 'date' and 'date' not in df.columns:
                df['date'] = df[date_col]
            
            # Description/Narration column variations - check all possibilities
            desc_columns = ['description', 'narration', 'desc', 'nar', 'Description', 'Narration', 'DESCRIPTION', 'NARRATION', 
                          'remarks', 'Remarks', 'detail', 'Detail', 'transaction_description', 'transactionDescription',
                          'TransactionDescription', 'NARRATION', 'narration_text', 'NarrationText', 'txn_desc', 'TxnDesc']
            desc_col = None
            for col in desc_columns:
                if col in df.columns:
                    desc_col = col
                    break
            
            # Create normalized 'description' column only if it doesn't exist
            if 'description' not in df.columns and desc_col:
                df['description'] = df[desc_col]
            elif desc_col and desc_col != 'description' and 'description' not in df.columns:
                df['description'] = df[desc_col]
            
            # Amount column variations - check all possibilities
            amount_columns = ['amount', 'Amount', 'AMOUNT', 'transaction_amount', 'transactionAmount', 'amt', 'Amt',
                           'TransactionAmount', 'AMT', 'txn_amount', 'TxnAmount', 'value', 'Value', 'VALUE']
            amount_col = None
            for col in amount_columns:
                if col in df.columns:
                    amount_col = col
                    break
            
            # Create normalized 'amount' column only if it doesn't exist
            if 'amount' not in df.columns:
                if amount_col:
                    df['amount'] = df[amount_col]
                elif 'debit' in df.columns and 'credit' in df.columns:
                    # If we have debit/credit but no amount, create amount from them
                    df['amount'] = df['debit'].fillna(0) + df['credit'].fillna(0)
            
            # Balance column variations - check all possibilities
            balance_columns = ['balance', 'Balance', 'BALANCE', 'current_balance', 'currentBalance', 'bal', 'Bal', 
                             'closing_balance', 'closingBalance', 'available_balance', 'availableBalance',
                             'CurrentBalance', 'BAL', 'closingBalance', 'ClosingBalance', 'running_balance', 'RunningBalance']
            balance_col = None
            for col in balance_columns:
                if col in df.columns:
                    balance_col = col
                    break
            
            # Create normalized 'balance' column only if it doesn't exist
            if 'balance' not in df.columns and balance_col:
                df['balance'] = df[balance_col]
            elif balance_col and balance_col != 'balance' and 'balance' not in df.columns:
                df['balance'] = df[balance_col]
            
            # Debit column variations - check all possibilities
            debit_columns = ['debit', 'Debit', 'DEBIT', 'amount_dr', 'amountDr', 'dr', 'Dr', 'DR', 'withdrawal', 'Withdrawal',
                           'AmountDr', 'AMOUNT_DR', 'debit_amount', 'DebitAmount', 'withdraw', 'Withdraw', 'WITHDRAWAL']
            debit_col = None
            for col in debit_columns:
                if col in df.columns:
                    debit_col = col
                    break
            
            # Create normalized 'debit' column only if it doesn't exist
            if 'debit' not in df.columns and debit_col:
                df['debit'] = df[debit_col]
            elif debit_col and debit_col != 'debit' and 'debit' not in df.columns:
                df['debit'] = df[debit_col]
            
            # Credit column variations - check all possibilities
            credit_columns = ['credit', 'Credit', 'CREDIT', 'amount_cr', 'amountCr', 'cr', 'Cr', 'CR', 'deposit', 'Deposit',
                            'AmountCr', 'AMOUNT_CR', 'credit_amount', 'CreditAmount', 'DEPOSIT', 'deposit_amount', 'DepositAmount']
            credit_col = None
            for col in credit_columns:
                if col in df.columns:
                    credit_col = col
                    break
            
            # Create normalized 'credit' column only if it doesn't exist
            if 'credit' not in df.columns and credit_col:
                df['credit'] = df[credit_col]
            elif credit_col and credit_col != 'credit' and 'credit' not in df.columns:
                df['credit'] = df[credit_col]
            
            # Category column variations - check all possibilities
            category_columns = ['category', 'Category', 'CATEGORY', 'type', 'Type', 'TYPE', 'transaction_type', 
                              'transactionType', 'txn_type', 'txnType', 'TransactionType', 'TXN_TYPE',
                              'transaction_category', 'TransactionCategory', 'txn_category', 'TxnCategory']
            category_col = None
            for col in category_columns:
                if col in df.columns:
                    category_col = col
                    break
            
            # Create normalized 'category' column only if it doesn't exist
            if 'category' not in df.columns and category_col:
                df['category'] = df[category_col]
            elif category_col and category_col != 'category' and 'category' not in df.columns:
                df['category'] = df[category_col]
            
            # Handle amount-based format (single amount column instead of separate debit/credit)
            # Check if we need to derive debit/credit from amount column
            needs_debit_credit_derivation = 'amount' in df.columns and ('debit' not in df.columns or 'credit' not in df.columns)
            
            if needs_debit_credit_derivation:
                # Convert amount to numeric
                df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
                
                # Initialize flags
                df['is_debit'] = False
                df['is_credit'] = False
                
                # Strategy: 
                # 1. If amount is negative, it's a debit (explicit negative = debit)
                # 2. If amount is positive, check category and narration to determine type
                # 3. For analysis: debit = negative, credit = positive (amount_signed column)
                
                # First, handle explicit negative amounts (these are debits)
                df.loc[df['amount'] < 0, 'is_debit'] = True
                df.loc[df['amount'] > 0, 'is_credit'] = True  # Default positive to credit, may be overridden
                
                # Check narration first (most reliable indicator)
                if 'description' in df.columns:
                    narration_debit_keywords = ['paid', 'debit', 'withdrawal', 'payment', 'charge', 'fee', 'int.pd', 'interest paid',
                                              'int pd', 'intpd', 'interest.pd', 'interest.paid', 'withdraw', 'transfer out',
                                              'sent', 'paid to', 'payment to', 'charges', 'penalty', 'fine']
                    narration_credit_keywords = ['credit', 'deposit', 'salary', 'income', 'refund', 'received', 'interest received',
                                                'interest recd', 'interest rec', 'transfer in', 'credited', 'deposited',
                                                'salary credit', 'income credit', 'refund received']
                    
                    narration_lower = df['description'].astype(str).str.lower()
                    
                    # Check for debit keywords in narration
                    narration_is_debit = narration_lower.str.contains('|'.join(narration_debit_keywords), na=False, case=False, regex=True)
                    # Check for credit keywords in narration
                    narration_is_credit = narration_lower.str.contains('|'.join(narration_credit_keywords), na=False, case=False, regex=True)
                    
                    # Override based on narration (narration takes priority)
                    df.loc[narration_is_debit & (df['amount'] >= 0), 'is_debit'] = True
                    df.loc[narration_is_debit & (df['amount'] >= 0), 'is_credit'] = False
                    df.loc[narration_is_credit & (df['amount'] >= 0), 'is_credit'] = True
                    df.loc[narration_is_credit & (df['amount'] >= 0), 'is_debit'] = False
                
                # Then check category if narration didn't help
                if 'category' in df.columns:
                    debit_categories = ['debit', 'withdrawal', 'payment', 'expense', 'charge', 'fee', 'withdrawal', 'transfer out',
                                      'interest paid', 'interest.paid', 'int.pd', 'penalty', 'fine']
                    credit_categories = ['credit', 'deposit', 'salary', 'income', 'refund', 'deposit', 'transfer in',
                                       'interest received', 'interest.received', 'interest recd', 'interest rec']
                    
                    df['category_lower'] = df['category'].astype(str).str.lower()
                    category_debit = df['category_lower'].isin(debit_categories)
                    category_credit = df['category_lower'].isin(credit_categories)
                    
                    # Special handling for "Interest" category - check narration
                    interest_mask = df['category_lower'] == 'interest'
                    if 'description' in df.columns:
                        # If narration contains "paid" or "pd", it's a debit
                        narration_lower = df['description'].astype(str).str.lower()
                        interest_paid = narration_lower.str.contains('paid|pd|int.pd', na=False, case=False, regex=True)
                        interest_received = narration_lower.str.contains('received|recd|rec|interest rec', na=False, case=False, regex=True)
                        
                        df.loc[interest_mask & interest_paid & (df['amount'] >= 0), 'is_debit'] = True
                        df.loc[interest_mask & interest_paid & (df['amount'] >= 0), 'is_credit'] = False
                        df.loc[interest_mask & interest_received & (df['amount'] >= 0), 'is_credit'] = True
                        df.loc[interest_mask & interest_received & (df['amount'] >= 0), 'is_debit'] = False
                    
                    # Use category if narration didn't classify it
                    unclassified = (df['amount'] >= 0) & ~df['is_debit'] & ~df['is_credit']
                    df.loc[unclassified & category_debit, 'is_debit'] = True
                    df.loc[unclassified & category_debit, 'is_credit'] = False
                    df.loc[unclassified & category_credit, 'is_credit'] = True
                    df.loc[unclassified & category_credit, 'is_debit'] = False
                
                # Ensure no transaction is both debit and credit
                df.loc[df['is_debit'] & df['is_credit'], 'credit'] = False
                df.loc[df['is_debit'] & df['is_credit'], 'is_credit'] = False
                
                # Create signed amount: negative for debit, positive for credit
                # This is what the user wants - debit as minus, credit as plus
                df['amount_signed'] = df.apply(
                    lambda row: -abs(row['amount']) if row['is_debit'] else abs(row['amount']), 
                    axis=1
                )
                
                # Create debit and credit columns (positive values for analyzer compatibility)
                if 'debit' not in df.columns:
                    df['debit'] = df.apply(lambda row: abs(row['amount']) if row['is_debit'] else 0, axis=1)
                if 'credit' not in df.columns:
                    df['credit'] = df.apply(lambda row: abs(row['amount']) if row['is_credit'] else 0, axis=1)
            else:
                # We have separate debit/credit columns, ensure they're numeric
                if 'debit' in df.columns:
                    df['debit'] = pd.to_numeric(df['debit'], errors='coerce').fillna(0)
                if 'credit' in df.columns:
                    df['credit'] = pd.to_numeric(df['credit'], errors='coerce').fillna(0)
                
                # Create signed amount from existing debit/credit columns
                # Debit = negative, Credit = positive
                df['amount_signed'] = df['credit'] - df['debit']
            
            # Ensure required columns exist
            required_cols = ['date', 'balance']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            # Check if we have either (debit, credit) or amount
            has_debit_credit = 'debit' in df.columns and 'credit' in df.columns
            has_amount = 'amount' in df.columns
            
            if missing_cols:
                return Response({
                    'success': False,
                    'message': f'Missing required columns: {missing_cols}. Available columns: {list(df.columns)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not has_debit_credit and not has_amount:
                return Response({
                    'success': False,
                    'message': 'Missing amount columns. Need either (debit, credit) or (amount) column. Available columns: ' + str(list(df.columns))
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Ensure amount_signed exists (should have been created above)
            if 'amount_signed' not in df.columns:
                if 'debit' in df.columns and 'credit' in df.columns:
                    df['amount_signed'] = df['credit'] - df['debit']
                elif 'amount' in df.columns:
                    # Fallback: use amount as-is (assuming it's already signed)
                    df['amount_signed'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
                else:
                    df['amount_signed'] = 0
            
            # Convert date column
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.dropna(subset=['date'])
            
            # Filter out invalid dates (before 2000 or after today)
            from datetime import datetime
            min_valid_date = pd.Timestamp('2000-01-01')
            max_valid_date = pd.Timestamp(datetime.now()) + pd.Timedelta(days=30)  # Allow 30 days in future
            
            print(f"[DEBUG] Before date filter: {len(df)} rows")
            print(f"[DEBUG] Date range: {df['date'].min()} to {df['date'].max()}")
            
            df = df[(df['date'] >= min_valid_date) & (df['date'] <= max_valid_date)]
            
            print(f"[DEBUG] After date filter: {len(df)} rows")
            if len(df) > 0:
                print(f"[DEBUG] Valid date range: {df['date'].min()} to {df['date'].max()}")
            
            if len(df) == 0:
                return Response({
                    'success': False,
                    'message': 'No valid transactions found after date filtering. Please check transaction dates.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Convert numeric columns
            if 'debit' in df.columns:
                df['debit'] = pd.to_numeric(df['debit'], errors='coerce').fillna(0)
            if 'credit' in df.columns:
                df['credit'] = pd.to_numeric(df['credit'], errors='coerce').fillna(0)
            df['balance'] = pd.to_numeric(df['balance'], errors='coerce').fillna(0)
            
            # If we created debit/credit from amount, ensure they're set
            if 'amount_signed' in df.columns:
                # Ensure debit and credit columns exist
                if 'debit' not in df.columns:
                    df['debit'] = 0
                if 'credit' not in df.columns:
                    df['credit'] = 0
            
            # Remove rows with invalid descriptions (NaN, empty, etc.)
            # But don't drop rows if description is missing - it's optional
            if 'description' in df.columns:
                # Only filter if description exists and is explicitly invalid
                df = df[df['description'].notna() | (df['description'].isna())]  # Keep NaN rows
                df = df[(df['description'].astype(str).str.strip() != '') | (df['description'].isna())]
                df = df[(df['description'].astype(str).str.lower() != 'nan') | (df['description'].isna())]
                print(f"[DEBUG] After description filter: {len(df)} rows")
            
            # Remove extreme outliers (amounts > 10 lakh for consumer accounts)
            max_reasonable_amount = 1000000  # 10 lakh
            outlier_mask = ((df['debit'] > max_reasonable_amount) | (df['credit'] > max_reasonable_amount))
            outliers = df[outlier_mask]
            
            if len(outliers) > 0:
                print(f"[DEBUG] Removing {len(outliers)} outlier transactions with amounts > Rs.{max_reasonable_amount:,}")
                print(f"[DEBUG] Outlier amounts: {outliers[['debit', 'credit']].to_dict('records')}")
            
            df = df[~outlier_mask]
            
            if len(df) == 0:
                return Response({
                    'success': False,
                    'message': 'No valid transactions found after data quality checks'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Rename columns to match analyzer expectations
            column_renames = {
                'date': 'txn_date',
                'debit': 'amount_dr',
                'credit': 'amount_cr'
            }
            
            # Only rename columns that exist
            df = df.rename(columns={k: v for k, v in column_renames.items() if k in df.columns})
            
            # Create unified 'amount' and 'type' columns (required by analyzer)
            # If we have amount_signed (from amount-based format), use that
            if 'amount_signed' in df.columns:
                # Use signed amount: negative = debit, positive = credit
                # Use .copy() to avoid conflicts when assigning to existing columns
                df = df.copy()
                df['amount'] = df['amount_signed'].abs()  # Absolute value for amount
                df['type'] = df['amount_signed'].apply(lambda x: 'DR' if x < 0 else 'CR')
                # Ensure amount_dr and amount_cr exist for analyzer
                if 'amount_dr' not in df.columns:
                    df['amount_dr'] = df.apply(lambda row: abs(row['amount_signed']) if row['amount_signed'] < 0 else 0, axis=1)
                if 'amount_cr' not in df.columns:
                    df['amount_cr'] = df.apply(lambda row: abs(row['amount_signed']) if row['amount_signed'] > 0 else 0, axis=1)
            else:
                # Original format with separate debit/credit columns
                # Use .copy() to avoid conflicts when assigning to existing columns
                df = df.copy()
                if 'amount_cr' in df.columns and 'amount_dr' in df.columns:
                    df['amount'] = df['amount_cr'].where(df['amount_cr'] > 0, df['amount_dr'])
                    df['type'] = df['amount_cr'].apply(lambda x: 'CR' if x > 0 else 'DR')
                elif 'amount' in df.columns:
                    # Fallback: use amount column if debit/credit not available
                    # Convert to numeric first, then process
                    amount_series = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
                    df['type'] = amount_series.apply(lambda x: 'CR' if x > 0 else 'DR')
                    df['amount'] = amount_series.abs()
                    df['amount_dr'] = df.apply(lambda row: abs(row['amount']) if row['type'] == 'DR' else 0, axis=1)
                    df['amount_cr'] = df.apply(lambda row: abs(row['amount']) if row['type'] == 'CR' else 0, axis=1)
            
            # Keep description if present (optional for analyzer)
            # Already in df if it was in transactions
            
            # Add account_id column - use account_id from transaction if available (for multi-account)
            if 'account_id' in df.columns:
                # Already has account_id from extraction
                pass
            elif 'bank_name' in df.columns:
                # Create account_id from bank_name and account_number
                df['account_id'] = df.apply(
                    lambda row: f"{row.get('bank_name', 'Unknown')}_{account_info.get('account_number', 'default')}",
                    axis=1
                )
            else:
                # Fallback: use account_number from account_info
                df['account_id'] = account_info.get('account_number', 'default')
            
            # Compute monthly aggregation
            monthly_df = monthly_aggregation(df)
            
            # Extract all feature groups
            core_features = compute_core_features(df, monthly_df)
            behaviour_features = compute_behaviour_features(df)
            emi_features = estimate_emi(df, core_features.get('monthly_income', 0))
            bounce_features = compute_bounce_features(df)
            advanced_features = compute_advanced_features(
                df,
                core_features.get('monthly_income', 0),
                core_features.get('monthly_expense', 0),
                emi_features.get('estimated_emi', 0)
            )
            impulse_features = compute_impulse_behavioral_features(
                df,
                core_features.get('monthly_income', 0),
                core_features.get('monthly_expense', 0)
            )
            
            # Merge all features
            features = {
                **core_features,
                **behaviour_features,
                **emi_features,
                **bounce_features,
                **advanced_features,
                **impulse_features
            }
            
            # Detect liabilities from bank statement
            liabilities = detect_liabilities_simple(
                credit_report_data=None,  # No credit report in this endpoint
                bank_statement_df=df,
                monthly_income=core_features.get('monthly_income', 0)
            )
            
            # Add liability features
            features['detected_liabilities'] = {
                'total_liabilities': liabilities.get('total_liabilities', 0),
                'total_monthly_emi': liabilities.get('total_monthly_emi', 0),
                'active_loans_count': len(liabilities.get('active_loans', [])),
                'credit_cards_count': len(liabilities.get('credit_cards', [])),
                'liability_source': 'bank_statement'
            }
            
            # Create summary - include multi-account info
            unique_accounts = df['account_id'].nunique() if 'account_id' in df.columns else 1
            unique_banks = df['bank_name'].nunique() if 'bank_name' in df.columns else 1
            
            summary = {
                'total_transactions': len(df),
                'total_credits': core_features.get('total_credits', 0),
                'total_debits': core_features.get('total_debits', 0),
                'average_balance': core_features.get('avg_balance', 0),
                'monthly_income': core_features.get('avg_monthly_credits', 0),
                'monthly_expense': core_features.get('avg_monthly_debits', 0),
                'account_number': account_info.get('account_number', ''),
                'bank_name': account_info.get('bank_name', ''),  # Will show combined if multiple
                'ifsc': account_info.get('ifsc', ''),
                'holder_name': account_info.get('holder_name', ''),
                'analysis_date': str(timezone.now()),
                'date_range': {
                    'start': str(df['txn_date'].min()),
                    'end': str(df['txn_date'].max()),
                    'days': (df['txn_date'].max() - df['txn_date'].min()).days
                },
                'multiple_accounts': account_info.get('multiple_accounts', False),
                'total_accounts': account_info.get('total_accounts', 1),
                'total_banks': unique_banks
            }
            
            # Add account breakdown if multiple accounts
            if account_info.get('multiple_accounts', False) and 'account_id' in df.columns:
                account_breakdown = []
                for acc_id in df['account_id'].unique():
                    acc_df = df[df['account_id'] == acc_id]
                    acc_info_dict = {
                        'account_id': acc_id,
                        'bank_name': acc_df['bank_name'].iloc[0] if 'bank_name' in acc_df.columns else 'Unknown',
                        'transaction_count': len(acc_df),
                        'total_credits': float(acc_df['amount_cr'].sum()) if 'amount_cr' in acc_df.columns else 0,
                        'total_debits': float(acc_df['amount_dr'].sum()) if 'amount_dr' in acc_df.columns else 0
                    }
                    account_breakdown.append(acc_info_dict)
                summary['account_breakdown'] = account_breakdown
            
            # Transaction insights - handle both credit/debit columns
            if 'description' in df.columns:
                top_credits = df[df['type'] == 'CR'].nlargest(5, 'amount')[['txn_date', 'description', 'amount']].to_dict('records')
                top_debits = df[df['type'] == 'DR'].nlargest(5, 'amount')[['txn_date', 'description', 'amount']].to_dict('records')
            else:
                top_credits = df[df['type'] == 'CR'].nlargest(5, 'amount')[['txn_date', 'amount']].to_dict('records')
                top_debits = df[df['type'] == 'DR'].nlargest(5, 'amount')[['txn_date', 'amount']].to_dict('records')
            
            return Response({
                'success': True,
                'message': 'Bank statement analyzed successfully',
                'data': {
                    'features': features,
                    'summary': summary,
                    'liabilities': liabilities,  # Add comprehensive liability data
                    'insights': {
                        'top_credits': top_credits,
                        'top_debits': top_debits,
                        'transaction_count': len(df),
                        'unique_months': monthly_df.shape[0] if not monthly_df.empty else 0
                    }
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Analysis failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

