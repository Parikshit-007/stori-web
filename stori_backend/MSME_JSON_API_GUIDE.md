# MSME JSON API Guide
====================

## ✅ Sab JSON mein milega!

Consumer flow की तरह, MSME के लिए भी **pure JSON APIs** बना दिए हैं।

---

## 🎯 Complete JSON-Based Flow

### 1. GST Analysis (Already JSON)
```bash
POST /api/msme/gst/uploads/
```

```json
{
  "gstin": "29ABCDE1234F1Z5",
  "return_type": "gstr3b",
  "return_period": "12-2025",
  "financial_year": "2025-26",
  "file": "base64_encoded_file_or_json_data",
  "gst_data": {
    "taxable_turnover": 5000000,
    "total_tax_liability": 900000,
    "total_tax_paid": 900000,
    "vendors": [
      {
        "gstin": "27XXXXX1234X1Z5",
        "total_amount": 100000,
        "verified": true,
        "months_active": 12
      }
    ],
    "b2b": [...],
    "b2c": [...],
    "hsn_codes": ["84", "85"],
    "locations": [...]
  }
}
```

**Then Analyze:**
```bash
POST /api/msme/gst/uploads/{id}/analyze/
```

```json
{
  "itr_data": {
    "total_revenue": 6000000,
    "net_profit": 500000
  },
  "platform_sales_data": {
    "total_sales": 4800000,
    "platform": "Shopify"
  },
  "filing_history": [
    {
      "return_period": "11-2025",
      "status": "filed_on_time",
      "days_delay": 0
    },
    {
      "return_period": "10-2025",
      "status": "filed_late",
      "days_delay": 5
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "compliance_score": 85,
    "risk_level": "low",
    "total_revenue_fy": 5000000,
    "gst_filing_regularity": 90.0,
    "vendor_verification_rate": 95.5,
    "summary": {
      "filing_discipline": {...},
      "revenue_analysis": {...},
      "tax_compliance": {...},
      "vendor_analysis": {...}
    }
  }
}
```

---

### 2. Director Personal Banking (JSON - Consumer Flow Reuse)
```bash
POST /api/msme/director-banking/analyze-json/
```

```json
{
  "director_name": "Rajesh Kumar",
  "director_pan": "ABCDE1234F",
  "bank_name": "HDFC Bank",
  "account_type": "savings",
  "bank_statement_data": {
    "account_number": "XXXX1234",
    "statement_period": {
      "from": "2025-01-01",
      "to": "2025-12-31"
    },
    "transactions": [
      {
        "date": "2025-01-15",
        "description": "Salary Credit",
        "amount": 150000,
        "type": "credit",
        "balance": 200000,
        "category": "salary"
      },
      {
        "date": "2025-01-16",
        "description": "Rent Payment",
        "amount": 20000,
        "type": "debit",
        "balance": 180000,
        "category": "rent"
      },
      {
        "date": "2025-01-18",
        "description": "UPI Transfer",
        "amount": 5000,
        "type": "debit",
        "balance": 175000,
        "category": "p2p"
      }
    ]
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Director bank statement analyzed successfully",
  "data": {
    "director_name": "Rajesh Kumar",
    "director_pan": "ABCDE1234F",
    "overall_score": 75,
    "risk_category": "low",
    "summary": {
      "monthly_income": 150000,
      "monthly_expense": 80000,
      "avg_balance": 200000,
      "income_stability": 0.85,
      "estimated_emi": 25000,
      "is_stable": true
    },
    "features": {
      "monthly_income": 150000,
      "monthly_expense": 80000,
      "income_stability": 0.85,
      "spending_to_income": 53.33,
      "avg_balance": 200000,
      "min_balance": 50000,
      "balance_volatility": 15.5,
      "survivability_months": 2.5,
      "late_night_txn_ratio": 0.05,
      "weekend_txn_ratio": 0.15,
      "estimated_emi": 25000,
      "emi_to_income": 16.67,
      "data_confidence": 0.9,
      "num_bank_accounts": 1,
      "txn_count": 250,
      "months_of_data": 12,
      "bounce_rate": 0,
      "max_inflow": 150000,
      "max_outflow": 25000,
      "upi_p2p_ratio": 0.25,
      "utility_to_income": 5.0,
      "utility_payment_consistency": 0.95,
      "insurance_payment_detected": true,
      "rent_to_income": 13.33,
      "inflow_time_consistency": 0.9,
      "manipulation_risk_score": 0,
      "expense_rigidity": 0.6,
      "salary_retention_ratio": 0.7,
      "week1_vs_week4_spending_ratio": 1.2,
      "impulse_spending_score": 0.15,
      "upi_volume_spike_score": 0.1,
      "avg_balance_drop_rate": 0.05
    },
    "msme_metrics": {
      "assets_derived": {
        "mutual_funds": 0,
        "fixed_deposits": 0,
        "stocks": 0
      },
      "liabilities_derived": {
        "personal_loans": 900000,
        "credit_cards": 0
      },
      "regular_p2p_transactions": false,
      "income_volatility": 15.5,
      "subscriptions": [],
      "savings_consistency_score": 0.47,
      "is_stable": true,
      "income_change_percentage": 15.5
    },
    "result_id": 123
  }
}
```

---

### 3. Business Banking (JSON)
```bash
POST /api/msme/business-banking/analyze-json/
```

```json
{
  "business_name": "ABC Traders",
  "gstin": "29ABCDE1234F1Z5",
  "bank_name": "ICICI Bank",
  "account_type": "current",
  "bank_statement_data": {
    "account_number": "XXXX5678",
    "statement_period": {
      "from": "2025-01-01",
      "to": "2025-12-31"
    },
    "transactions": [
      {
        "date": "2025-01-05",
        "description": "Customer Payment - INV001",
        "amount": 50000,
        "type": "credit",
        "balance": 500000,
        "category": "revenue"
      },
      {
        "date": "2025-01-10",
        "description": "Vendor Payment - Supplier A",
        "amount": 30000,
        "type": "debit",
        "balance": 470000,
        "category": "vendor"
      },
      {
        "date": "2025-01-15",
        "description": "Salary Payment",
        "amount": 100000,
        "type": "debit",
        "balance": 370000,
        "category": "salary"
      },
      {
        "date": "2025-01-20",
        "description": "Rent Payment",
        "amount": 25000,
        "type": "debit",
        "balance": 345000,
        "category": "rent"
      },
      {
        "date": "2025-01-25",
        "description": "UPI - Payment Gateway Collection",
        "amount": 80000,
        "type": "credit",
        "balance": 425000,
        "category": "revenue"
      }
    ]
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Business bank statement analyzed successfully",
  "data": {
    "business_name": "ABC Traders",
    "gstin": "29ABCDE1234F1Z5",
    "cashflow_health_score": 80,
    "business_risk_category": "low",
    "summary": {
      "average_bank_balance": 500000,
      "monthly_inflow": 2000000,
      "monthly_outflow": 1800000,
      "inflow_outflow_ratio": 1.11,
      "estimated_monthly_revenue": 1800000,
      "total_transactions": 365
    },
    "features": {
      "average_bank_balance": 500000,
      "min_balance": 100000,
      "max_balance": 800000,
      "balance_trend": "stable",
      "negative_balance_days": 0,
      "balance_volatility": 12.5,
      "total_inflow": 24000000,
      "total_outflow": 21600000,
      "net_cashflow": 2400000,
      "monthly_inflow": 2000000,
      "monthly_outflow": 1800000,
      "inflow_outflow_ratio": 1.11,
      "estimated_monthly_revenue": 1800000,
      "revenue_consistency_score": 0.7,
      "mom_revenue_growth": 5.2,
      "total_transactions": 365,
      "credit_transactions": 200,
      "debit_transactions": 165,
      "avg_transaction_value": 120000,
      "monthly_operating_expenses": 1800000,
      "salary_payments": 100000,
      "rent_payments": 25000,
      "vendor_payments": 500000,
      "bounce_count": 0,
      "bounce_rate": 0,
      "circular_transaction_detected": false,
      "months_of_data": 12
    },
    "result_id": 456
  }
}
```

---

## 🔥 Complete MSME Application (JSON Only)

### Step 1: Create Application
```bash
POST /api/msme/applications/
```

```json
{
  "company_name": "ABC Traders",
  "msme_category": "small"
}
```

### Step 2: Submit All Data (JSON Format)
```bash
POST /api/msme/applications/{id}/analyze/
```

```json
{
  "director_data": {
    "name": "Rajesh Kumar",
    "age": 45,
    "pan": "ABCDE1234F",
    "phone": "9876543210",
    "address": "123 Main St, Mumbai",
    "personal_bank_data": {
      "transactions": [...]
    }
  },
  
  "business_data": {
    "industry": "Retail",
    "legal_entity_type": "proprietorship",
    "business_vintage_years": 5,
    "msme_category": "small"
  },
  
  "bank_data": {
    "business_bank_statement": {
      "transactions": [...]
    }
  },
  
  "gst_data": {
    "gstin": "29ABCDE1234F1Z5",
    "total_revenue": 5000000,
    "vendors": [...],
    "filing_history": [...]
  },
  
  "verification_data": {
    "gstin": "29ABCDE1234F1Z5",
    "pan": "ABCDE1234F",
    "gstin_valid": true
  },
  
  "revenue_data": {
    "monthly_gtv": 200000,
    "weekly_gtv": 50000
  },
  
  "kyc_data": {
    "pan_verified": true,
    "aadhaar_verified": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Analysis completed successfully",
  "data": {
    "application_id": 1,
    "credit_score": 720,
    "risk_tier": "near_prime",
    "default_probability": 0.08,
    "section_scores": {
      "director": 75,
      "business_identity": 80,
      "revenue": 85,
      "cashflow": 80,
      "credit": 70,
      "compliance": 90,
      "fraud": 95,
      "external": 75,
      "vendor": 80
    },
    "section_results": {
      "director": {
        "personal_banking": {...},
        "behavioral_signals": {...},
        "financial_stability": {...}
      },
      "cashflow": {
        "balance_metrics": {...},
        "inflow_outflow": {...}
      },
      "compliance": {
        "gst_itr_discipline": {...},
        "mismatch_checks": {...}
      }
    }
  }
}
```

---

## 📋 API Endpoints Summary

### JSON-Based APIs (No File Upload)

#### GST Analysis
```
POST /api/msme/gst/uploads/              # Upload GST data (JSON)
POST /api/msme/gst/uploads/{id}/analyze/ # Analyze with additional data
```

#### Director Personal Banking
```
POST /api/msme/director-banking/analyze-json/  # Direct JSON analysis
```

#### Business Banking
```
POST /api/msme/business-banking/analyze-json/  # Direct JSON analysis
```

#### Complete Application
```
POST /api/msme/applications/              # Create
POST /api/msme/applications/{id}/analyze/ # Complete analysis (JSON)
POST /api/msme/applications/quick_score/  # Quick score (JSON, no save)
```

---

## 🎯 Transaction Format

### Required Fields in Transactions:
```json
{
  "date": "2025-01-15",          // Required: ISO date format
  "description": "Salary Credit", // Optional but recommended
  "amount": 150000,               // Required: Transaction amount
  "type": "credit",               // Required: "credit" or "debit"
  "balance": 200000,              // Required: Balance after transaction
  "category": "salary"            // Optional: For better analysis
}
```

### Optional Categories:
- **Income:** `salary`, `business_income`, `interest`, `refund`
- **Expenses:** `rent`, `utility`, `emi`, `vendor`, `salary_payment`
- **Transfers:** `p2p`, `internal_transfer`
- **Investments:** `mutual_fund`, `fd`, `stocks`

---

## ✅ Complete Example Workflow (Python)

```python
import requests

API_KEY = "your_api_key"
BASE_URL = "http://localhost:8000/api"
headers = {"X-API-Key": API_KEY}

# 1. Create Application
app_data = {
    "company_name": "ABC Traders",
    "msme_category": "small"
}
response = requests.post(f"{BASE_URL}/msme/applications/", json=app_data, headers=headers)
app_id = response.json()['id']

# 2. Director Personal Banking Analysis
director_data = {
    "director_name": "Rajesh Kumar",
    "director_pan": "ABCDE1234F",
    "bank_name": "HDFC Bank",
    "account_type": "savings",
    "bank_statement_data": {
        "account_number": "XXXX1234",
        "statement_period": {"from": "2025-01-01", "to": "2025-12-31"},
        "transactions": [
            {"date": "2025-01-15", "description": "Salary", "amount": 150000, "type": "credit", "balance": 200000},
            # ... more transactions
        ]
    }
}
response = requests.post(
    f"{BASE_URL}/msme/director-banking/analyze-json/",
    json=director_data,
    headers=headers
)
director_score = response.json()['data']['overall_score']
print(f"Director Score: {director_score}")

# 3. Business Banking Analysis
business_data = {
    "business_name": "ABC Traders",
    "gstin": "29ABCDE1234F1Z5",
    "bank_name": "ICICI Bank",
    "account_type": "current",
    "bank_statement_data": {
        "account_number": "XXXX5678",
        "statement_period": {"from": "2025-01-01", "to": "2025-12-31"},
        "transactions": [
            {"date": "2025-01-05", "description": "Customer Payment", "amount": 50000, "type": "credit", "balance": 500000},
            # ... more transactions
        ]
    }
}
response = requests.post(
    f"{BASE_URL}/msme/business-banking/analyze-json/",
    json=business_data,
    headers=headers
)
business_score = response.json()['data']['cashflow_health_score']
print(f"Business Score: {business_score}")

# 4. GST Analysis
gst_data = {
    "gstin": "29ABCDE1234F1Z5",
    "return_type": "gstr3b",
    "return_period": "12-2025",
    "financial_year": "2025-26",
    "gst_data": {
        "taxable_turnover": 5000000,
        "total_tax_liability": 900000,
        "total_tax_paid": 900000,
        "vendors": [],
        # ... more GST data
    }
}
response = requests.post(f"{BASE_URL}/msme/gst/uploads/", json=gst_data, headers=headers)
gst_upload_id = response.json()['id']

response = requests.post(f"{BASE_URL}/msme/gst/uploads/{gst_upload_id}/analyze/", headers=headers)
gst_score = response.json()['data']['compliance_score']
print(f"GST Score: {gst_score}")

print("✅ All analyses complete!")
```

---

## 🎉 Summary

✅ **GST Analysis** - JSON format (already done)
✅ **Director Banking** - JSON format (reuses consumer flow)
✅ **Business Banking** - JSON format (cash flow analysis)
✅ **Complete Integration** - All JSON, no file uploads needed

**Sab kuch JSON mein!** Consumer flow ki tarah! 🚀

