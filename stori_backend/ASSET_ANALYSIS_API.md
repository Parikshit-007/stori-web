# Asset Analysis API Documentation

## Overview

Asset Analysis API processes Account Aggregator (AA) JSON data to analyze all consumer assets and calculate the highest quantified amount value.

## Endpoint

**POST** `/api/customer/asset-analysis/analyze-json/`

## Authentication

Use `X-API-Key` header with your API key.

```
X-API-Key: stori_xxxxxxxxxxxxx
```

## Request Format

Send Account Aggregator JSON with the following structure:

```json
{
  "demat": {
    "holdings": [
      {
        "companyName": "Reliance Industries",
        "symbol": "RELIANCE",
        "quantity": 100,
        "currentValue": 250000.0,
        "investedValue": 200000.0,
        "ltp": 2500.0,
        "exchange": "NSE"
      }
    ]
  },
  "mutual_funds": {
    "folios": [
      {
        "amc": "HDFC",
        "schemes": [
          {
            "schemeName": "HDFC Equity Fund",
            "units": 1000.0,
            "currentValue": 50000.0,
            "investedValue": 45000.0
          }
        ]
      }
    ]
  },
  "fixed_deposits": {
    "fixed_deposits": [
      {
        "bank": "HDFC Bank",
        "type": "BANK_FD",
        "principal": 100000.0,
        "maturityAmount": 110000.0,
        "interestRate": 7.5,
        "maturityDate": "2025-12-31"
      }
    ]
  },
  "gold": {
    "holdings": [
      {
        "type": "DIGITAL",
        "name": "Digital Gold",
        "units": 10.0,
        "currentValue": 60000.0,
        "investedValue": 55000.0
      },
      {
        "type": "ETF",
        "name": "Gold ETF",
        "units": 50.0,
        "currentValue": 30000.0,
        "investedValue": 28000.0
      }
    ]
  },
  "real_estate": {
    "properties": [
      {
        "type": "RESIDENTIAL",
        "location": "Mumbai",
        "currentValue": 5000000.0,
        "purchasePrice": 4000000.0,
        "outstandingLoan": 2000000.0
      }
    ]
  },
  "insurance": {
    "policies": [
      {
        "type": "LIC",
        "policyName": "LIC Endowment Plan",
        "hasInvestmentValue": true,
        "surrenderValue": 200000.0,
        "totalPremiumPaid": 150000.0,
        "maturityValue": 300000.0,
        "maturityDate": "2030-12-31"
      }
    ]
  },
  "provident_fund": {
    "pf_accounts": [
      {
        "type": "EPF",
        "accountNumber": "EPF123456",
        "currentBalance": 500000.0,
        "totalContribution": 400000.0,
        "employeeContribution": 200000.0,
        "employerContribution": 200000.0
      }
    ]
  },
  "other_investments": {
    "investments": [
      {
        "type": "BONDS",
        "name": "Government Bonds",
        "currentValue": 100000.0,
        "investedValue": 95000.0
      },
      {
        "type": "CRYPTO",
        "name": "Bitcoin",
        "currentValue": 50000.0,
        "investedValue": 30000.0
      }
    ]
  }
}
```

## Supported Asset Types

### 1. Stocks & Equity (Demat)
- **Source**: `demat` or `stocks` in JSON
- **Fields**: holdings array with companyName, symbol, quantity, currentValue, investedValue, ltp, exchange

### 2. Mutual Funds (CAMS)
- **Source**: `mutual_funds` or `cams` in JSON
- **Fields**: folios array with schemes containing schemeName, units, currentValue, investedValue

### 3. Fixed Deposits
- **Source**: `fixed_deposits` or `fds` in JSON
- **Fields**: fixed_deposits array with bank, type (BANK_FD/CORPORATE_FD), principal, maturityAmount, interestRate

### 4. Gold
- **Source**: `gold` in JSON
- **Note**: Only processes DIGITAL, ETF, SGB types. PHYSICAL gold is excluded.
- **Fields**: holdings array with type, name, units/weightGrams, currentValue, investedValue

### 5. Real Estate
- **Source**: `real_estate` or `properties` in JSON
- **Note**: Manual input field
- **Fields**: properties array with type, location, currentValue, purchasePrice, outstandingLoan

### 6. Insurance
- **Source**: `insurance` in JSON
- **Note**: Only policies with investment value (LIC, ULIPs). Term insurance excluded.
- **Fields**: policies array with type, policyName, hasInvestmentValue, surrenderValue, totalPremiumPaid, maturityValue, maturityDate
- **Future**: dueDate and latePayment fields reserved for future use

### 7. Provident Fund
- **Source**: `provident_fund` or `pf` in JSON
- **Types**: EPF, PPF, VPF
- **Note**: Excluded from survivability calculation
- **Fields**: pf_accounts array with type, accountNumber, currentBalance, totalContribution

### 8. Other Investments
- **Source**: `other_investments` in JSON
- **Types**: BONDS, NPS, CRYPTO
- **Note**: NPS and BONDS excluded from survivability. Only CRYPTO included.
- **Fields**: investments array with type, name, currentValue, investedValue

## Response Format

```json
{
  "success": true,
  "message": "Assets analyzed successfully",
  "data": {
    "analysis": {
      "total_asset_value": 1000000.0,
      "total_invested_value": 800000.0,
      "survivability_asset_value": 600000.0,
      "portfolio_returns_pct": 25.0,
      "num_assets": 10,
      "num_asset_types": 5,
      "highest_quantified_amount": {
        "value": 500000.0,
        "asset_type": "STOCKS",
        "asset_name": "Reliance Industries",
        "subtype": "NSE"
      },
      "liquid_assets": 300000.0,
      "semi_liquid_assets": 200000.0,
      "illiquid_assets": 500000.0,
      "liquidity_ratio": 0.3,
      "stocks_value": 250000.0,
      "mutual_funds_value": 50000.0,
      "fixed_deposits_value": 110000.0,
      "gold_value": 90000.0,
      "real_estate_value": 5000000.0,
      "insurance_value": 200000.0,
      "provident_fund_value": 500000.0,
      "bonds_value": 100000.0,
      "nps_value": 0.0,
      "crypto_value": 50000.0,
      "assets": [
        {
          "type": "STOCKS",
          "subtype": "NSE",
          "name": "Reliance Industries",
          "symbol": "RELIANCE",
          "quantity": 100,
          "current_value": 250000.0,
          "invested_value": 200000.0,
          "returns_pct": 25.0
        }
      ]
    },
    "summary": {
      "total_assets": 10,
      "total_value": 1000000.0,
      "survivability_value": 600000.0,
      "highest_asset": {
        "value": 500000.0,
        "asset_type": "STOCKS",
        "asset_name": "Reliance Industries",
        "subtype": "NSE"
      },
      "liquidity_breakdown": {
        "liquid": 300000.0,
        "semi_liquid": 200000.0,
        "illiquid": 500000.0,
        "liquidity_ratio": 0.3
      },
      "asset_type_breakdown": {
        "stocks": 250000.0,
        "mutual_funds": 50000.0,
        "fixed_deposits": 110000.0,
        "gold": 90000.0,
        "real_estate": 5000000.0,
        "insurance": 200000.0,
        "provident_fund": 500000.0,
        "bonds": 100000.0,
        "nps": 0.0,
        "crypto": 50000.0
      },
      "portfolio_returns_pct": 25.0
    },
    "processed_at": "2026-01-16T14:30:00.123456+00:00"
  }
}
```

## Key Features

### 1. Highest Quantified Amount
- Calculates the asset with the highest current value
- For stocks, considers quantity × LTP if available
- Returns asset type, name, and subtype

### 2. Survivability Calculation
- Excludes: PPF, EPF, VPF, NPS, BONDS from survivability
- Includes: Stocks, Mutual Funds, FDs, Gold (Digital/ETF), Real Estate, Insurance, Crypto

### 3. Liquidity Analysis
- **Liquid** (≤7 days): Stocks, Liquid Funds, Gold Digital/ETF, Crypto
- **Semi-liquid** (8-90 days): FDs, Bonds, Insurance
- **Illiquid** (>90 days): Real Estate, PPF, EPF, NPS

### 4. Asset Type Breakdown
- Separate values for each asset type
- Portfolio returns calculation
- Detailed asset list with returns percentage

## Error Handling

```json
{
  "success": false,
  "message": "Asset analysis failed: <error message>"
}
```

## Example Usage

### Python
```python
import requests

url = "http://localhost:8000/api/customer/asset-analysis/analyze-json/"
headers = {
    "X-API-Key": "stori_xxxxxxxxxxxxx",
    "Content-Type": "application/json"
}

# Get data from Account Aggregator
aa_data = {
    "demat": {...},
    "mutual_funds": {...},
    # ... other asset types
}

response = requests.post(url, headers=headers, json=aa_data)
result = response.json()

if result['success']:
    highest_asset = result['data']['analysis']['highest_quantified_amount']
    print(f"Highest asset: {highest_asset['asset_name']} - Rs {highest_asset['value']}")
```

### cURL
```bash
curl -X POST http://localhost:8000/api/customer/asset-analysis/analyze-json/ \
  -H "X-API-Key: stori_xxxxxxxxxxxxx" \
  -H "Content-Type: application/json" \
  -d @aa_data.json
```

## Notes

1. **Gold**: Only Digital, ETF, and SGB are processed. Physical gold is excluded.
2. **Survivability**: PPF, EPF, VPF, NPS, and Bonds are excluded from survivability calculation.
3. **Insurance**: Only policies with investment value are included (excludes term insurance).
4. **Real Estate**: Manual input field - not from AA.
5. **Future Features**: Insurance due date and late payment tracking (reserved for future implementation).

## Integration with Credit Scoring

The asset analysis results can be used to:
- Increase average balance calculation
- Determine collateral capacity
- Assess financial strength
- Calculate survivability months
- Evaluate asset diversification

