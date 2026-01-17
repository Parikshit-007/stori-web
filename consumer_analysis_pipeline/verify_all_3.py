import pandas as pd
from pathlib import Path
from merchant_classifier import calculate_accurate_cashflow

# Define the 4 bank statements
accounts = [
    {
        'name': 'HDFC1',
        'path': 'bank_statements/Acct Statement_3109_12012026_12.56.48.xlsx'
    },
    {
        'name': 'HDFC2',
        'path': 'bank_statements/Acct Statement_3109_12012026_12.58.44.xlsx'
    },
    {
        'name': 'UNION1',
        'path': 'bank_statements/Union Bank statement - Nishil (1).xlsx'
    },
    {
        'name': 'UNION2',
        'path': 'bank_statements/nishil-union2024-2025.xlsx'
    }
]

print("="*100)
print("DETAILED INCOME VERIFICATION ACROSS ALL 4 BANK ACCOUNTS")
print("="*100)

total_income = 0
total_months = 0
all_income_txns = []

for acc in accounts:
    print(f"\n{'='*100}")
    print(f"ACCOUNT: {acc['name']} - {Path(acc['path']).name}")
    print("="*100)
    
    # Load statement
    df = pd.read_excel(acc['path'])
    
    # Standardize columns based on format
    if 'Date' in df.columns and 'Remarks' in df.columns:  # Union Bank format
        df['type'] = df['Amount'].astype(str).apply(lambda x: 'CR' if 'Cr' in str(x) else 'DR')
        df['amount'] = df['Amount'].astype(str).str.replace(r'[^\d.]', '', regex=True)
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        df = df.rename(columns={'Date': 'txn_date', 'Remarks': 'description', 'Balance': 'balance'})
        df['balance'] = df['balance'].astype(str).str.replace(r'[^\d.]', '', regex=True)
        df['balance'] = pd.to_numeric(df['balance'], errors='coerce')
        df['txn_date'] = pd.to_datetime(df['txn_date'], format='%d-%m-%Y', errors='coerce')
    else:  # HDFC format (already converted)
        df['txn_date'] = pd.to_datetime(df['txn_date'], errors='coerce')
    
    # Drop invalid rows
    df = df.dropna(subset=['txn_date', 'amount', 'type'])
    
    print(f"\nTotal transactions: {len(df)}")
    print(f"Date range: {df['txn_date'].min().strftime('%d-%b-%Y')} to {df['txn_date'].max().strftime('%d-%b-%Y')}")
    
    # Calculate accurate cashflow
    result, df_classified = calculate_accurate_cashflow(df)
    
    print(f"Months covered: {result['total_months']:.2f}")
    print(f"\nMonthly Income: Rs {result['monthly_income']:,.2f}")
    print(f"Monthly Expense: Rs {result['monthly_expense']:,.2f}")
    
    # Show income transactions
    income_txns = df_classified[df_classified['is_income'] == True].copy()
    print(f"\n{'-'*100}")
    print(f"INCOME TRANSACTIONS DETECTED ({len(income_txns)} transactions):")
    print("-"*100)
    
    if len(income_txns) > 0:
        for idx, row in income_txns.iterrows():
            print(f"  {row['txn_date'].strftime('%d-%b-%Y')}: Rs {row['amount']:>10,.2f} - {row['description'][:70]}")
            all_income_txns.append({
                'account': acc['name'],
                'date': row['txn_date'],
                'amount': row['amount'],
                'description': row['description']
            })
        
        total_income_amount = income_txns['amount'].sum()
        print(f"\n  TOTAL INCOME (this account): Rs {total_income_amount:,.2f}")
    else:
        print("  NO SALARY INCOME DETECTED")
    
    # Show excluded transactions
    excluded_txns = df_classified[df_classified['category'] == 'EXCLUDED'].copy()
    if len(excluded_txns) > 0:
        print(f"\n{'-'*100}")
        print(f"EXCLUDED FROM INCOME ({len(excluded_txns)} transactions - trading/dividends/refunds):")
        print("-"*100)
        for idx, row in excluded_txns.head(10).iterrows():
            print(f"  {row['txn_date'].strftime('%d-%b-%Y')}: Rs {row['amount']:>10,.2f} - {row['description'][:70]}")
        if len(excluded_txns) > 10:
            print(f"  ... and {len(excluded_txns) - 10} more excluded transactions")
    
    total_income += result['monthly_income'] * result['total_months']
    total_months += result['total_months']

print("\n" + "="*100)
print("OVERALL SUMMARY - ALL 4 ACCOUNTS COMBINED")
print("="*100)

print(f"\nTotal months covered: {total_months:.2f}")
print(f"Total income detected: Rs {total_income:,.2f}")
print(f"Average monthly income: Rs {total_income / total_months:,.2f}")

print(f"\n{'-'*100}")
print(f"ALL INCOME TRANSACTIONS ({len(all_income_txns)}):")
print("-"*100)

# Sort by date
all_income_txns_df = pd.DataFrame(all_income_txns)
if len(all_income_txns_df) > 0:
    all_income_txns_df = all_income_txns_df.sort_values('date')
    
    for idx, row in all_income_txns_df.iterrows():
        print(f"[{row['account']}] {row['date'].strftime('%d-%b-%Y')}: Rs {row['amount']:>10,.2f} - {row['description'][:60]}")
    
    print(f"\nTOTAL: Rs {all_income_txns_df['amount'].sum():,.2f}")

print("\n" + "="*100)
print("VERIFICATION COMPLETE")
print("="*100)

