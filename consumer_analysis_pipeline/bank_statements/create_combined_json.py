"""
Create Combined Bank Statement JSON from Multiple Files
Reads all bank statements, removes duplicates, and creates JSON for API testing
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime

# Directory containing bank statements
BASE_DIR = Path(__file__).parent

# All bank statement files
FILES = [
    {
        'path': BASE_DIR / 'Acct Statement_3109_12012026_12.56.48.xlsx',
        'bank': 'HDFC Bank',
        'account_number': '50100548903109',
        'ifsc': 'HDFC0000000'
    },
    {
        'path': BASE_DIR / 'Acct Statement_3109_12012026_12.58.44.xlsx',
        'bank': 'HDFC Bank',
        'account_number': '50100548903109',
        'ifsc': 'HDFC0000000'
    },
    {
        'path': BASE_DIR / 'nishil-union2024-2025.xlsx',
        'bank': 'Union Bank of India',
        'account_number': '310901010057819',
        'ifsc': 'UBIN0531099'
    },
    {
        'path': BASE_DIR / 'Union Bank statement - Nishil (1).xlsx',
        'bank': 'Union Bank of India',
        'account_number': '310901010057819',
        'ifsc': 'UBIN0531099'
    }
]

def parse_date(date_val):
    """Parse date from various formats"""
    if pd.isna(date_val):
        return None
    
    if isinstance(date_val, datetime):
        # Validate date is reasonable (between 2000 and now+1 year)
        if date_val.year < 2000 or date_val.year > datetime.now().year + 1:
            return None
        return date_val.strftime('%Y-%m-%d')
    
    # Try to parse string dates
    try:
        if isinstance(date_val, str):
            # Try DD/MM/YY format
            if '/' in date_val:
                parts = date_val.split('/')
                if len(parts) == 3:
                    day, month, year = parts
                    # Handle 2-digit year
                    if len(year) == 2:
                        year = '20' + year if int(year) < 50 else '19' + year
                    parsed_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    # Validate
                    dt = pd.to_datetime(parsed_date)
                    if dt.year < 2000 or dt.year > datetime.now().year + 1:
                        return None
                    return parsed_date
        
        # Let pandas handle it
        dt = pd.to_datetime(date_val)
        # Validate
        if dt.year < 2000 or dt.year > datetime.now().year + 1:
            return None
        return dt.strftime('%Y-%m-%d')
    except:
        return None

def read_bank_statement(file_info):
    """Read a single bank statement file"""
    print(f"\nReading: {file_info['path'].name}")
    
    if not file_info['path'].exists():
        print(f"   [ERROR] File not found!")
        return []
    
    try:
        # Try reading Excel file
        df = pd.read_excel(file_info['path'], sheet_name=0)
        
        print(f"   [OK] Read {len(df)} rows")
        print(f"   Columns: {df.columns.tolist()}")
        
        # Identify columns (handle different formats)
        transactions = []
        
        # Common column name variations
        date_cols = ['Transaction Date', 'Date', 'Txn Date', 'date', 'Value Date', 'Posting Date', 'txn_date']
        desc_cols = ['Description', 'Narration', 'Particulars', 'description', 'Details', 'Remarks']
        debit_cols = ['Debit', 'Withdrawal', 'Dr', 'debit', 'Debit Amount']
        credit_cols = ['Credit', 'Deposit', 'Cr', 'credit', 'Credit Amount']
        balance_cols = ['Balance', 'Closing Balance', 'balance', 'Available Balance']
        amount_col_options = ['Amount', 'amount']  # Union Bank uses single 'Amount' column
        
        # Find actual column names
        date_col = next((c for c in df.columns if c in date_cols), None)
        desc_col = next((c for c in df.columns if c in desc_cols), None)
        debit_col = next((c for c in df.columns if c in debit_cols), None)
        credit_col = next((c for c in df.columns if c in credit_cols), None)
        balance_col = next((c for c in df.columns if c in balance_cols), None)
        amount_col = next((c for c in df.columns if c in amount_col_options), None)
        
        if not date_col:
            print(f"   [WARNING] No date column found!")
            print(f"   Available columns: {df.columns.tolist()}")
            return []
        
        print(f"   Mapped columns:")
        print(f"      Date: {date_col}")
        print(f"      Description: {desc_col}")
        print(f"      Debit: {debit_col}")
        print(f"      Credit: {credit_col}")
        print(f"      Balance: {balance_col}")
        print(f"      Amount: {amount_col}")
        
        # Helper function to clean amount strings
        def clean_amount(value):
            """Clean amount strings like '13413.94(Cr)' or '72.0(Dr)'"""
            if pd.isna(value):
                return 0.0, None
            
            value_str = str(value).strip()
            
            # Check if it's already a number
            try:
                return float(value_str), None
            except ValueError:
                pass
            
            # Check for (Cr) or (Dr) suffix
            is_credit = '(Cr)' in value_str or '(cr)' in value_str
            is_debit = '(Dr)' in value_str or '(dr)' in value_str
            
            # Remove (Cr)/(Dr) and parse
            value_clean = value_str.replace('(Cr)', '').replace('(cr)', '').replace('(Dr)', '').replace('(dr)', '').strip()
            
            try:
                amount = float(value_clean)
                txn_type = 'CR' if is_credit else ('DR' if is_debit else None)
                return amount, txn_type
            except ValueError:
                return 0.0, None
        
        for idx, row in df.iterrows():
            # Skip empty rows
            if pd.isna(row.get(date_col)):
                continue
            
            date = parse_date(row.get(date_col))
            if not date:
                continue
            
            # Get description
            description = str(row.get(desc_col, '')) if desc_col else ''
            
            # Skip if description is invalid
            if not description or description.lower() in ['nan', 'none', '']:
                continue
            
            # Handle different file formats
            debit = 0.0
            credit = 0.0
            balance = 0.0
            
            # Case 1: Already has type column (processed files)
            if 'type' in df.columns and pd.notna(row.get('type')):
                if row.get('type') == 'CR':
                    credit = float(row.get('amount', 0)) if 'amount' in df.columns else 0.0
                else:
                    debit = float(row.get('amount', 0)) if 'amount' in df.columns else 0.0
                balance = float(row.get('balance', 0)) if 'balance' in df.columns and pd.notna(row.get('balance')) else 0.0
            
            # Case 2: Has separate debit/credit columns
            elif debit_col and credit_col:
                debit = float(row.get(debit_col, 0)) if pd.notna(row.get(debit_col)) else 0.0
                credit = float(row.get(credit_col, 0)) if pd.notna(row.get(credit_col)) else 0.0
                if balance_col and pd.notna(row.get(balance_col)):
                    balance, _ = clean_amount(row.get(balance_col))
            
            # Case 3: Has single Amount column (Union Bank format)
            elif amount_col:
                amount_val = row.get(amount_col)
                amount, txn_type = clean_amount(amount_val)
                
                if txn_type == 'CR':
                    credit = amount
                elif txn_type == 'DR':
                    debit = amount
                else:
                    # If no type indicator, assume debit if negative, credit if positive
                    if amount < 0:
                        debit = abs(amount)
                    else:
                        credit = amount
                
                if balance_col and pd.notna(row.get(balance_col)):
                    balance, _ = clean_amount(row.get(balance_col))
            
            # Skip if both debit and credit are 0
            if debit == 0 and credit == 0:
                continue
            
            # Skip extreme outliers (> 10 lakh for consumer accounts)
            max_reasonable_amount = 1000000  # 10 lakh
            if debit > max_reasonable_amount or credit > max_reasonable_amount:
                print(f"   [WARNING] Skipping outlier transaction: debit={debit}, credit={credit}")
                continue
            
            transaction = {
                'date': date,
                'description': description.strip(),
                'debit': debit,
                'credit': credit,
                'balance': balance
            }
            
            transactions.append(transaction)
        
        print(f"   [SUCCESS] Extracted {len(transactions)} valid transactions")
        return transactions
        
    except Exception as e:
        print(f"   [ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def remove_duplicates(transactions):
    """Remove duplicate transactions"""
    print(f"\nRemoving duplicates...")
    print(f"   Before: {len(transactions)} transactions")
    
    # Create a set of unique transactions (date + amount + type)
    seen = set()
    unique_transactions = []
    
    for txn in transactions:
        # Create a unique key
        key = (
            txn['date'],
            txn['debit'],
            txn['credit'],
            txn['balance']
        )
        
        if key not in seen:
            seen.add(key)
            unique_transactions.append(txn)
    
    print(f"   After: {len(unique_transactions)} unique transactions")
    print(f"   Removed: {len(transactions) - len(unique_transactions)} duplicates")
    
    return unique_transactions

def main():
    """Main function to create combined JSON"""
    print("="*80)
    print("BANK STATEMENT JSON CREATOR")
    print("="*80)
    
    all_transactions = []
    
    # Read all files
    for file_info in FILES:
        transactions = read_bank_statement(file_info)
        all_transactions.extend(transactions)
    
    print(f"\nTotal transactions collected: {len(all_transactions)}")
    
    # Remove duplicates
    unique_transactions = remove_duplicates(all_transactions)
    
    # Sort by date
    unique_transactions.sort(key=lambda x: x['date'])
    
    # Get account info (use first file's info)
    account_info = {
        'account_number': FILES[0]['account_number'],
        'bank_name': FILES[0]['bank'],
        'ifsc': FILES[0]['ifsc'],
        'holder_name': 'Nishil'
    }
    
    # Create final JSON
    json_data = {
        'transactions': unique_transactions,
        'account_info': account_info
    }
    
    # Print summary
    print(f"\nSummary:")
    print(f"   Total Unique Transactions: {len(unique_transactions)}")
    if unique_transactions:
        print(f"   Date Range: {unique_transactions[0]['date']} to {unique_transactions[-1]['date']}")
        total_credits = sum(t['credit'] for t in unique_transactions)
        total_debits = sum(t['debit'] for t in unique_transactions)
        print(f"   Total Credits: Rs. {total_credits:,.2f}")
        print(f"   Total Debits: Rs. {total_debits:,.2f}")
    
    # Save to JSON file
    output_file = BASE_DIR / 'combined_bank_statement.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n[SUCCESS] JSON file created: {output_file}")
    print(f"\nFile is ready to use with API:")
    print(f"   POST http://localhost:8000/api/customer/bank-statement/analyze-json/")
    print(f"   Header: X-API-Key: stori_6CFocXsPyo4tJDxq8MkVE6Iy-aii0_7eN59VJvUlfmU")
    print(f"   Body: {output_file.name}")
    
    # Save first 50 transactions as sample (for testing)
    if len(unique_transactions) > 50:
        sample_data = {
            'transactions': unique_transactions[:50],
            'account_info': account_info
        }
        sample_file = BASE_DIR / 'sample_bank_statement.json'
        with open(sample_file, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, indent=2, ensure_ascii=False)
        print(f"\nSample file (50 transactions) created: {sample_file}")
    
    print("\n" + "="*80)
    print("DONE!")
    print("="*80)

if __name__ == '__main__':
    main()

