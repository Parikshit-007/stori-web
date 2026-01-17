import pandas as pd
from pathlib import Path

files = [
    r"Acct Statement_3109_12012026_12.56.48.xls",
    r"Acct Statement_3109_12012026_12.58.44.xls",
]

for f in files:
    # Read with header row at index 20 (0-based), where HDFC table starts
    df = pd.read_excel(f, header=20)

    # Drop header/separator rows like '********' and blanks
    dcol = df['Date']
    mask = dcol.notna() & (dcol.astype(str).str.strip() != '') & (dcol.astype(str).str.strip() != '********')
    df = df[mask]

    # Standardize column names
    df.columns = df.columns.str.strip().str.lower()

    def find_col(df, candidates):
        for c in candidates:
            if c in df.columns:
                return df[c]
        # fallback: empty series with same length
        return pd.Series([None] * len(df))

    # Map key columns with fallbacks
    txn_date = find_col(df, ['date', 'txn date', 'value dt', 'value date'])
    withdrawal = find_col(df, ['withdrawal amt.', 'withdrawal amount', 'withdrawal', 'debit'])
    deposit = find_col(df, ['deposit amt.', 'deposit amount', 'deposit', 'credit'])
    balance = find_col(df, ['closing balance', 'balance'])
    description = find_col(df, ['narration', 'description', 'particulars', 'details'])

    # Build amount/type
    withdraw = pd.to_numeric(withdrawal, errors='coerce').fillna(0)
    deposit = pd.to_numeric(deposit, errors='coerce').fillna(0)

    df['amount'] = withdraw.where(withdraw > 0, deposit)
    df['type'] = ['DR' if w > 0 else 'CR' if d > 0 else '' for w, d in zip(withdraw, deposit)]
    df['txn_date'] = pd.to_datetime(txn_date, errors='coerce')
    df['balance'] = pd.to_numeric(balance, errors='coerce')
    df['description'] = description

    # Keep only needed cols
    keep = ['txn_date', 'amount', 'type', 'balance', 'description']
    df = df[keep]

    # Drop empty rows and zero amounts
    df = df.dropna(subset=['txn_date', 'amount', 'type'])
    df = df[df['amount'] > 0]

    out = Path(f).with_suffix('.xlsx')
    df.to_excel(out, index=False)
    print(f"Written: {out}")