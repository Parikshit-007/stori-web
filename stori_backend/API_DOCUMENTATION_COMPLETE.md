# Stori NBFC - Complete API Documentation
==========================================

**Version:** 1.0.0  
**Last Updated:** January 2026  
**Environment:** Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [API Architecture](#api-architecture)
4. [Consumer Flow](#consumer-flow)
5. [MSME Flow](#msme-flow)
6. [Credit Scoring Integration](#credit-scoring-integration)
7. [Error Handling](#error-handling)
8. [Rate Limits](#rate-limits)
9. [Best Practices](#best-practices)
10. [Appendix](#appendix)

---

## Overview

### What is Stori NBFC API?

Stori NBFC provides a comprehensive credit scoring platform for both **Consumer** and **MSME** lending. The API enables:

- **Consumer Credit Scoring**: Personal loan underwriting based on bank statements, ITR, credit reports, and assets
- **MSME Credit Scoring**: Business loan underwriting based on GST returns, director's personal banking, business banking, and compliance data
- **Real-time Analysis**: Instant credit risk assessment with explainable AI
- **Modular Design**: Use individual analysis APIs or complete end-to-end flow

### Base URL

```
Production: https://mycfo.club/stori/api
Local Dev:  http://localhost:8000
```

### API Versioning

```
Current Version: v1
Endpoint Format: /api/{module}/{resource}/
```

---

## Authentication

### API Key Authentication

All API requests require authentication using API Key in request headers.

#### Header Format
```http
X-API-Key: stori_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### Generate API Key

```bash
# Django Management Command
python manage.py generate_api_key <username> <key_name>

# Example
python manage.py generate_api_key admin "Production Key"
```

#### Response
```json
{
  "success": true,
  "api_key": "stori_abc123def456ghi789jkl012mno345pqr678stu",
  "user": "admin",
  "key_name": "Production Key",
  "created_at": "2026-01-17T10:30:00Z"
}
```

### Security Best Practices

1. **Never expose API keys** in client-side code
2. **Use environment variables** to store keys
3. **Rotate keys regularly** (every 90 days recommended)
4. **Use HTTPS** in production
5. **Implement IP whitelisting** for additional security

---

## API Architecture

### Data Flow Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     API Request Flow                         │
└─────────────────────────────────────────────────────────────┘

1. CONSUMER FLOW:
   ├── Bank Statement Analysis → Store JSON
   ├── ITR Analysis → Store JSON
   ├── Credit Report Analysis → Store JSON
   ├── Asset Analysis → Store JSON
   └── Combine All JSONs → Credit Scoring API → Final Score

2. MSME FLOW:
   ├── GST Analysis → Store JSON
   ├── Director Personal Banking → Store JSON
   ├── Business Banking Analysis → Store JSON
   ├── Business Identity Verification → Store JSON
   └── Combine All JSONs → Credit Scoring API → Final Score
```

### Response Format

All API responses follow this structure:

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    // Response data
  },
  "metadata": {
    "timestamp": "2026-01-17T10:30:00Z",
    "request_id": "req_abc123",
    "version": "v1"
  }
}
```

### Error Response Format

```json
{
  "success": false,
  "message": "Error description",
  "error": {
    "code": "ERROR_CODE",
    "details": "Detailed error message"
  },
  "metadata": {
    "timestamp": "2026-01-17T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

---

## Consumer Flow

### Overview

Consumer flow analyzes personal financial data to determine creditworthiness for personal loans.

### Step 1: Bank Statement Analysis

**Endpoint:** `POST /api/customer/bank-statement/analyze-json/`

**Purpose:** Extract 38 financial features from bank statement data

**Headers:**
```http
Content-Type: application/json
X-API-Key: stori_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Request Body:**
```json
{
  "customer_name": "Rahul Sharma",
  "customer_pan": "ABCDE1234F",
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
        "description": "Salary Credit - TechCorp India",
        "amount": 120000,
        "type": "credit",
        "balance": 150000,
        "category": "salary"
      },
      {
        "date": "2025-01-16",
        "description": "Rent Payment",
        "amount": 18000,
        "type": "debit",
        "balance": 132000,
        "category": "rent"
      },
      {
        "date": "2025-01-18",
        "description": "EMI - Home Loan HDFC",
        "amount": 22000,
        "type": "debit",
        "balance": 110000,
        "category": "emi"
      },
      {
        "date": "2025-01-20",
        "description": "Electricity Bill BESCOM",
        "amount": 2500,
        "type": "debit",
        "balance": 107500,
        "category": "utility"
      }
    ]
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Bank statement analyzed successfully",
  "data": {
    "analysis_id": "bank_123456",
    "customer_name": "Rahul Sharma",
    "customer_pan": "ABCDE1234F",
    "features": {
      "monthly_income": 120000,
      "monthly_expense": 65000,
      "income_stability": 0.92,
      "spending_to_income": 54.17,
      "avg_balance": 110000,
      "min_balance": 45000,
      "balance_volatility": 12.5,
      "survivability_months": 1.69,
      "late_night_txn_ratio": 0.03,
      "weekend_txn_ratio": 0.12,
      "estimated_emi": 22000,
      "emi_to_income": 18.33,
      "data_confidence": 0.95,
      "num_bank_accounts": 1,
      "txn_count": 285,
      "months_of_data": 12,
      "bounce_rate": 0,
      "max_inflow": 120000,
      "max_outflow": 22000,
      "upi_p2p_ratio": 0.15,
      "utility_to_income": 2.92,
      "utility_payment_consistency": 0.98,
      "insurance_payment_detected": true,
      "rent_to_income": 15.0,
      "inflow_time_consistency": 0.95,
      "manipulation_risk_score": 0.02,
      "expense_rigidity": 0.65,
      "salary_retention_ratio": 0.72,
      "week1_vs_week4_spending_ratio": 1.15,
      "impulse_spending_score": 0.08,
      "upi_volume_spike_score": 0.05,
      "avg_balance_drop_rate": 0.12
    }
  }
}
```

**💾 Store This JSON:**
```javascript
// Store in your database or state management
const bankAnalysisResult = response.data;
```

---

### Step 2: ITR Analysis

**Endpoint:** `POST /api/customer/itr/analyze-json/`

**Purpose:** Analyze Income Tax Returns for income validation

**Request Body:**
```json
{
  "customer_name": "Rahul Sharma",
  "customer_pan": "ABCDE1234F",
  "assessment_year": "2024-25",
  "itr_data": {
    "itr_type": "ITR-1",
    "filing_date": "2025-07-31",
    "gross_total_income": 1440000,
    "total_deductions": 150000,
    "taxable_income": 1290000,
    "tax_paid": 185000,
    "refund_amount": 0,
    "income_sources": [
      {
        "source": "salary",
        "amount": 1440000,
        "employer": "TechCorp India Pvt Ltd"
      }
    ],
    "deductions": {
      "section_80C": 150000,
      "section_80D": 25000,
      "standard_deduction": 50000
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "ITR analyzed successfully",
  "data": {
    "analysis_id": "itr_123456",
    "features": {
      "annual_income": 1440000,
      "monthly_income_itr": 120000,
      "income_source_diversity": 1,
      "tax_compliance_score": 0.98,
      "deduction_ratio": 0.104,
      "income_stability": 0.95,
      "filing_on_time": true
    }
  }
}
```

**💾 Store This JSON:**
```javascript
const itrAnalysisResult = response.data;
```

---

### Step 3: Credit Report Analysis

**Endpoint:** `POST /api/customer/credit-report/analyze-json/`

**Purpose:** Analyze credit bureau report for credit history

**Request Body:**
```json
{
  "customer_name": "Rahul Sharma",
  "customer_pan": "ABCDE1234F",
  "bureau": "CIBIL",
  "report_date": "2026-01-15",
  "credit_report_data": {
    "credit_score": 760,
    "accounts": [
      {
        "account_type": "home_loan",
        "lender": "HDFC Bank",
        "sanction_amount": 5000000,
        "current_balance": 3800000,
        "emi_amount": 22000,
        "dpd_history": [0, 0, 0, 0, 0, 0],
        "account_status": "active"
      },
      {
        "account_type": "credit_card",
        "lender": "ICICI Bank",
        "credit_limit": 200000,
        "current_balance": 45000,
        "utilization": 22.5,
        "dpd_history": [0, 0, 0, 0, 0, 0],
        "account_status": "active"
      }
    ],
    "enquiries": 2,
    "last_enquiry_date": "2025-12-01"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Credit report analyzed successfully",
  "data": {
    "analysis_id": "credit_123456",
    "features": {
      "credit_score": 760,
      "total_accounts": 2,
      "active_accounts": 2,
      "total_debt": 3845000,
      "current_emi": 22000,
      "credit_utilization": 22.5,
      "dpd_last_6_months": 0,
      "enquiries_last_6_months": 2,
      "oldest_account_age_months": 36,
      "credit_mix_score": 0.85
    }
  }
}
```

**💾 Store This JSON:**
```javascript
const creditReportResult = response.data;
```

---

### Step 4: Asset Analysis

**Endpoint:** `POST /api/customer/assets/analyze-json/`

**Purpose:** Analyze customer assets (mutual funds, FDs, stocks, etc.)

**Request Body:**
```json
{
  "customer_name": "Rahul Sharma",
  "customer_pan": "ABCDE1234F",
  "assets_data": {
    "mutual_funds": [
      {
        "fund_name": "SBI Bluechip Fund",
        "units": 1000,
        "current_nav": 85.5,
        "current_value": 85500,
        "invested_value": 75000
      }
    ],
    "fixed_deposits": [
      {
        "bank": "HDFC Bank",
        "amount": 500000,
        "maturity_date": "2026-12-31",
        "interest_rate": 7.5
      }
    ],
    "stocks": [
      {
        "symbol": "RELIANCE",
        "quantity": 50,
        "current_price": 2450,
        "current_value": 122500
      }
    ],
    "ppf_balance": 350000,
    "epf_balance": 450000
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Assets analyzed successfully",
  "data": {
    "analysis_id": "asset_123456",
    "features": {
      "total_assets": 1508000,
      "liquid_assets": 708000,
      "illiquid_assets": 800000,
      "mutual_fund_value": 85500,
      "fixed_deposit_value": 500000,
      "stock_value": 122500,
      "ppf_value": 350000,
      "epf_value": 450000,
      "asset_diversity_score": 0.85
    }
  }
}
```

**💾 Store This JSON:**
```javascript
const assetAnalysisResult = response.data;
```

---

### Step 5: Combine & Score (Consumer)

**Endpoint:** `POST /api/customer/credit-scoring/score/`

**Purpose:** Combine all analyses and generate final credit score

**Request Body:**
```json
{
  "customer_name": "Rahul Sharma",
  "customer_pan": "ABCDE1234F",
  "customer_type": "salaried",
  "loan_amount": 500000,
  "loan_tenure_months": 24,
  
  "bank_statement_features": {
    "monthly_income": 120000,
    "monthly_expense": 65000,
    "income_stability": 0.92,
    "spending_to_income": 54.17,
    "avg_balance": 110000,
    "min_balance": 45000,
    "balance_volatility": 12.5,
    "survivability_months": 1.69,
    "late_night_txn_ratio": 0.03,
    "weekend_txn_ratio": 0.12,
    "estimated_emi": 22000,
    "emi_to_income": 18.33,
    "data_confidence": 0.95,
    "num_bank_accounts": 1,
    "txn_count": 285,
    "months_of_data": 12,
    "bounce_rate": 0,
    "max_inflow": 120000,
    "max_outflow": 22000,
    "upi_p2p_ratio": 0.15,
    "utility_to_income": 2.92,
    "utility_payment_consistency": 0.98,
    "insurance_payment_detected": true,
    "rent_to_income": 15.0,
    "inflow_time_consistency": 0.95,
    "manipulation_risk_score": 0.02,
    "expense_rigidity": 0.65,
    "salary_retention_ratio": 0.72,
    "week1_vs_week4_spending_ratio": 1.15,
    "impulse_spending_score": 0.08,
    "upi_volume_spike_score": 0.05,
    "avg_balance_drop_rate": 0.12
  },
  
  "itr_features": {
    "annual_income": 1440000,
    "monthly_income_itr": 120000,
    "tax_compliance_score": 0.98
  },
  
  "credit_report_features": {
    "credit_score": 760,
    "total_debt": 3845000,
    "current_emi": 22000,
    "credit_utilization": 22.5,
    "dpd_last_6_months": 0
  },
  
  "asset_features": {
    "total_assets": 1508000,
    "liquid_assets": 708000
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Credit scoring completed",
  "data": {
    "scoring_id": "score_123456",
    "customer_name": "Rahul Sharma",
    "customer_pan": "ABCDE1234F",
    
    "credit_score": 745,
    "risk_tier": "prime",
    "default_probability": 0.045,
    "approval_recommendation": "approve",
    
    "loan_details": {
      "requested_amount": 500000,
      "approved_amount": 500000,
      "recommended_interest_rate": 10.5,
      "recommended_tenure_months": 24,
      "monthly_emi": 23100
    },
    
    "foir_analysis": {
      "current_obligations": 22000,
      "new_emi": 23100,
      "total_obligations": 45100,
      "monthly_income": 120000,
      "foir": 37.58,
      "foir_status": "acceptable"
    },
    
    "risk_factors": [
      {
        "factor": "High FOIR after new loan",
        "impact": "medium",
        "value": 37.58
      }
    ],
    
    "positive_factors": [
      {
        "factor": "High income stability",
        "impact": "high",
        "value": 0.92
      },
      {
        "factor": "Good credit score",
        "impact": "high",
        "value": 760
      },
      {
        "factor": "Zero bounces",
        "impact": "medium",
        "value": 0
      }
    ],
    
    "shap_explanation": {
      "top_positive_features": [
        {"feature": "income_stability", "contribution": 0.15},
        {"feature": "credit_score", "contribution": 0.12},
        {"feature": "bounce_rate", "contribution": 0.08}
      ],
      "top_negative_features": [
        {"feature": "existing_emi", "contribution": -0.05},
        {"feature": "spending_to_income", "contribution": -0.03}
      ]
    }
  }
}
```

**💾 Store Final Result:**
```javascript
const finalCreditScore = response.data;
```

---

## MSME Flow

### Overview

MSME flow analyzes business financial data including GST returns, director's personal banking, business banking, and compliance.

### Step 1: GST Analysis

**Endpoint:** `POST /api/msme/gst/uploads/`  
**Then:** `POST /api/msme/gst/uploads/{id}/analyze/`

**Purpose:** Analyze GST returns for revenue, compliance, and vendor analysis

**Request Body (Upload):**
```json
{
  "gstin": "29ABCDE1234F1Z5",
  "return_type": "gstr3b",
  "return_period": "12-2025",
  "financial_year": "2025-26",
  "file_type": "json",
  "gst_data": {
    "taxable_turnover": 8000000,
    "total_tax_liability": 1440000,
    "total_tax_paid": 1440000,
    "outstanding_tax": 0,
    "itc_claimed": 240000,
    "itc_utilized": 230000,
    "itc_balance": 10000,
    "total_revenue": 8000000,
    
    "vendors": [
      {
        "gstin": "27XXXXX1234X1Z5",
        "name": "Supplier A Ltd",
        "total_amount": 500000,
        "verified": true,
        "months_active": 12
      },
      {
        "gstin": "19YYYYY5678Y2Z6",
        "name": "Supplier B Pvt Ltd",
        "total_amount": 350000,
        "verified": true,
        "months_active": 10
      },
      {
        "gstin": "07ZZZZZ9012Z3Z7",
        "name": "Supplier C",
        "total_amount": 200000,
        "verified": false,
        "months_active": 6
      }
    ],
    
    "hsn_codes": ["84", "85", "87"],
    "sac_codes": [],
    
    "locations": [
      {
        "state": "Karnataka",
        "gstin": "29ABCDE1234F1Z5",
        "city": "Bangalore"
      }
    ],
    
    "payment_history": [
      {"month": "12-2025", "on_time": true, "amount": 120000},
      {"month": "11-2025", "on_time": true, "amount": 115000},
      {"month": "10-2025", "on_time": false, "amount": 110000, "delay_days": 3}
    ]
  }
}
```

**Request Body (Analyze):**
```json
{
  "itr_data": {
    "total_revenue": 9600000,
    "net_profit": 960000,
    "total_expenses": 8640000
  },
  "platform_sales_data": {
    "total_sales": 7800000,
    "platform": "Amazon & Flipkart",
    "currency": "INR"
  },
  "filing_history": [
    {"return_period": "11-2025", "status": "filed_on_time", "days_delay": 0},
    {"return_period": "10-2025", "status": "filed_late", "days_delay": 3},
    {"return_period": "09-2025", "status": "filed_on_time", "days_delay": 0},
    {"return_period": "08-2025", "status": "filed_on_time", "days_delay": 0}
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "GST analysis completed",
  "data": {
    "analysis_id": "gst_123456",
    "gstin": "29ABCDE1234F1Z5",
    
    "compliance_score": 88,
    "risk_level": "low",
    
    "filing_discipline": {
      "gst_filing_regularity": 87.5,
      "total_expected_filings": 12,
      "actual_filings": 12,
      "late_filings": 2,
      "missed_filings": 0,
      "on_time_filings": 10,
      "avg_delay_days": 0.5
    },
    
    "revenue_analysis": {
      "total_revenue_fy": 8000000,
      "avg_monthly_revenue": 666667,
      "mom_revenue_growth": 4.35,
      "qoq_revenue_growth": 8.5,
      "revenue_volatility": 15.2
    },
    
    "tax_compliance": {
      "total_gst_liability": 1440000,
      "total_gst_paid": 1440000,
      "outstanding_gst": 0,
      "tax_payment_regularity": 1.0
    },
    
    "mismatch_checks": {
      "gst_r1_revenue": 8000000,
      "itr_revenue": 9600000,
      "gst_r1_itr_mismatch": 16.67,
      "mismatch_flag": true,
      "platform_sales": 7800000,
      "gst_platform_sales_mismatch": 2.5
    },
    
    "itc_analysis": {
      "total_itc_claimed": 240000,
      "total_itc_utilized": 230000,
      "itc_balance": 10000,
      "itc_to_revenue_ratio": 3.0
    },
    
    "vendor_analysis": {
      "total_vendors": 3,
      "verified_vendors": 2,
      "vendor_verification_rate": 66.67,
      "top_vendor_concentration": 47.62,
      "top_3_vendor_concentration": 100.0,
      "long_term_vendors_count": 2,
      "long_term_vendor_percentage": 66.67
    },
    
    "industry_analysis": {
      "industry": "Machinery & Electronics",
      "effective_gst_rate": 18.0
    },
    
    "risk_assessment": {
      "risk_flags": [
        {
          "type": "gst_itr_mismatch",
          "severity": "high",
          "value": 16.67,
          "message": "GST-ITR mismatch: 16.7%"
        }
      ],
      "risk_level": "medium",
      "risk_score": 75
    }
  }
}
```

**💾 Store This JSON:**
```javascript
const gstAnalysisResult = response.data;
```

---

### Step 2: Director Personal Banking Analysis

**Endpoint:** `POST /api/msme/director-banking/analyze-json/`

**Purpose:** Analyze director's personal bank statement (same as consumer flow - 38 features)

**Request Body:**
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
        "description": "Salary Credit - ABC Traders",
        "amount": 180000,
        "type": "credit",
        "balance": 250000,
        "category": "salary"
      },
      {
        "date": "2025-01-16",
        "description": "Rent Payment",
        "amount": 30000,
        "type": "debit",
        "balance": 220000,
        "category": "rent"
      },
      {
        "date": "2025-01-20",
        "description": "EMI - Car Loan",
        "amount": 18000,
        "type": "debit",
        "balance": 202000,
        "category": "emi"
      }
    ]
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Director bank statement analyzed",
  "data": {
    "analysis_id": "director_123456",
    "director_name": "Rajesh Kumar",
    "director_pan": "ABCDE1234F",
    
    "overall_score": 82,
    "risk_category": "low",
    
    "summary": {
      "monthly_income": 180000,
      "monthly_expense": 85000,
      "avg_balance": 220000,
      "income_stability": 0.88,
      "estimated_emi": 18000,
      "is_stable": true
    },
    
    "features": {
      "monthly_income": 180000,
      "monthly_expense": 85000,
      "income_stability": 0.88,
      "spending_to_income": 47.22,
      "avg_balance": 220000,
      "min_balance": 120000,
      "balance_volatility": 18.5,
      "survivability_months": 2.59,
      "late_night_txn_ratio": 0.02,
      "weekend_txn_ratio": 0.10,
      "estimated_emi": 18000,
      "emi_to_income": 10.0,
      "data_confidence": 0.96,
      "num_bank_accounts": 1,
      "txn_count": 312,
      "months_of_data": 12,
      "bounce_rate": 0,
      "max_inflow": 180000,
      "max_outflow": 30000,
      "upi_p2p_ratio": 0.12,
      "utility_to_income": 3.5,
      "utility_payment_consistency": 0.97,
      "insurance_payment_detected": true,
      "rent_to_income": 16.67,
      "inflow_time_consistency": 0.93,
      "manipulation_risk_score": 0.01,
      "expense_rigidity": 0.68,
      "salary_retention_ratio": 0.75,
      "week1_vs_week4_spending_ratio": 1.08,
      "impulse_spending_score": 0.06,
      "upi_volume_spike_score": 0.04,
      "avg_balance_drop_rate": 0.09
    },
    
    "msme_metrics": {
      "assets_derived": {
        "mutual_funds": 0,
        "fixed_deposits": 0,
        "stocks": 0
      },
      "liabilities_derived": {
        "personal_loans": 648000,
        "credit_cards": 0
      },
      "regular_p2p_transactions": false,
      "income_volatility": 18.5,
      "savings_consistency_score": 0.53,
      "is_stable": true,
      "income_change_percentage": 18.5
    }
  }
}
```

**💾 Store This JSON:**
```javascript
const directorBankingResult = response.data;
```

---

### Step 3: Business Banking Analysis

**Endpoint:** `POST /api/msme/business-banking/analyze-json/`

**Purpose:** Analyze business current account for cash flow and business health

**Request Body:**
```json
{
  "business_name": "ABC Traders Pvt Ltd",
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
        "amount": 125000,
        "type": "credit",
        "balance": 850000,
        "category": "revenue"
      },
      {
        "date": "2025-01-08",
        "description": "Customer Payment - INV002",
        "amount": 95000,
        "type": "credit",
        "balance": 945000,
        "category": "revenue"
      },
      {
        "date": "2025-01-10",
        "description": "Vendor Payment - Supplier A",
        "amount": 75000,
        "type": "debit",
        "balance": 870000,
        "category": "vendor"
      },
      {
        "date": "2025-01-15",
        "description": "Salary Payment - Staff",
        "amount": 180000,
        "type": "debit",
        "balance": 690000,
        "category": "salary"
      },
      {
        "date": "2025-01-18",
        "description": "Rent Payment",
        "amount": 45000,
        "type": "debit",
        "balance": 645000,
        "category": "rent"
      },
      {
        "date": "2025-01-20",
        "description": "UPI Collection - Online Orders",
        "amount": 180000,
        "type": "credit",
        "balance": 825000,
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
  "message": "Business banking analyzed",
  "data": {
    "analysis_id": "business_123456",
    "business_name": "ABC Traders Pvt Ltd",
    "gstin": "29ABCDE1234F1Z5",
    
    "cashflow_health_score": 85,
    "business_risk_category": "low",
    
    "summary": {
      "average_bank_balance": 780000,
      "monthly_inflow": 3200000,
      "monthly_outflow": 2850000,
      "inflow_outflow_ratio": 1.12,
      "estimated_monthly_revenue": 2880000,
      "total_transactions": 428
    },
    
    "features": {
      "average_bank_balance": 780000,
      "min_balance": 420000,
      "max_balance": 1200000,
      "balance_trend": "stable",
      "negative_balance_days": 0,
      "balance_volatility": 22.5,
      "total_inflow": 38400000,
      "total_outflow": 34200000,
      "net_cashflow": 4200000,
      "monthly_inflow": 3200000,
      "monthly_outflow": 2850000,
      "inflow_outflow_ratio": 1.12,
      "estimated_monthly_revenue": 2880000,
      "revenue_consistency_score": 0.78,
      "mom_revenue_growth": 6.5,
      "total_transactions": 428,
      "credit_transactions": 245,
      "debit_transactions": 183,
      "avg_transaction_value": 156735,
      "monthly_operating_expenses": 2850000,
      "salary_payments": 180000,
      "rent_payments": 45000,
      "vendor_payments": 1200000,
      "bounce_count": 0,
      "bounce_rate": 0,
      "circular_transaction_detected": false,
      "months_of_data": 12
    }
  }
}
```

**💾 Store This JSON:**
```javascript
const businessBankingResult = response.data;
```

---

### Step 4: Combine & Score (MSME)

**Endpoint:** `POST /api/msme/applications/{id}/analyze/`  
**Or:** `POST /api/msme/applications/quick_score/`

**Purpose:** Combine all MSME analyses and generate final credit score

**Request Body:**
```json
{
  "company_name": "ABC Traders Pvt Ltd",
  "msme_category": "small",
  "loan_amount": 2000000,
  "loan_tenure_months": 36,
  
  "director_data": {
    "name": "Rajesh Kumar",
    "age": 45,
    "pan": "ABCDE1234F",
    "phone": "9876543210",
    "address": "123 MG Road, Bangalore",
    "personal_bank_features": {
      "monthly_income": 180000,
      "monthly_expense": 85000,
      "income_stability": 0.88,
      "avg_balance": 220000,
      "estimated_emi": 18000,
      "bounce_rate": 0,
      "manipulation_risk_score": 0.01,
      "is_stable": true
    }
  },
  
  "business_data": {
    "industry": "Retail & Trading",
    "legal_entity_type": "private_limited",
    "business_vintage_years": 8,
    "msme_category": "small"
  },
  
  "gst_data": {
    "gstin": "29ABCDE1234F1Z5",
    "compliance_score": 88,
    "total_revenue_fy": 8000000,
    "avg_monthly_revenue": 666667,
    "gst_filing_regularity": 87.5,
    "vendor_verification_rate": 66.67,
    "outstanding_gst": 0
  },
  
  "bank_data": {
    "cashflow_health_score": 85,
    "average_bank_balance": 780000,
    "monthly_inflow": 3200000,
    "monthly_outflow": 2850000,
    "inflow_outflow_ratio": 1.12,
    "bounce_rate": 0
  },
  
  "verification_data": {
    "gstin": "29ABCDE1234F1Z5",
    "pan": "ABCDE1234F",
    "gstin_valid": true,
    "pan_valid": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "MSME credit scoring completed",
  "data": {
    "scoring_id": "msme_score_123456",
    "company_name": "ABC Traders Pvt Ltd",
    "gstin": "29ABCDE1234F1Z5",
    
    "final_credit_score": 735,
    "risk_tier": "near_prime",
    "default_probability": 0.062,
    "approval_recommendation": "approve_with_conditions",
    
    "loan_details": {
      "requested_amount": 2000000,
      "approved_amount": 1800000,
      "recommended_interest_rate": 12.5,
      "recommended_tenure_months": 36,
      "monthly_emi": 59850,
      "processing_fee": 36000,
      "collateral_required": false
    },
    
    "section_scores": {
      "director": 82,
      "business_identity": 78,
      "revenue": 85,
      "cashflow": 85,
      "credit": 72,
      "compliance": 88,
      "fraud": 95,
      "external": 70,
      "vendor": 75
    },
    
    "dscr_analysis": {
      "annual_business_income": 38400000,
      "annual_business_expenses": 34200000,
      "annual_net_income": 4200000,
      "existing_obligations": 216000,
      "new_emi": 59850,
      "total_annual_obligations": 934200,
      "dscr": 4.5,
      "dscr_status": "excellent"
    },
    
    "risk_factors": [
      {
        "factor": "GST-ITR revenue mismatch",
        "impact": "medium",
        "value": "16.67%"
      },
      {
        "factor": "Medium vendor verification rate",
        "impact": "low",
        "value": "66.67%"
      }
    ],
    
    "positive_factors": [
      {
        "factor": "Strong cash flow",
        "impact": "high",
        "value": 1.12
      },
      {
        "factor": "High GST compliance",
        "impact": "high",
        "value": 88
      },
      {
        "factor": "Director financial stability",
        "impact": "high",
        "value": 82
      },
      {
        "factor": "Zero bounces",
        "impact": "medium",
        "value": 0
      }
    ],
    
    "conditions": [
      "Quarterly financial review required",
      "GST filing compliance to be maintained",
      "Director to provide personal guarantee"
    ]
  }
}
```

**💾 Store Final Result:**
```javascript
const finalMSMEScore = response.data;
```

---

## Credit Scoring Integration

### How to Combine All Analyses

#### For Consumer:

```javascript
// Step 1: Collect all analysis JSONs
const consumerCreditScoreInput = {
  customer_name: "Rahul Sharma",
  customer_pan: "ABCDE1234F",
  customer_type: "salaried",
  loan_amount: 500000,
  loan_tenure_months: 24,
  
  // From Step 1: Bank Statement Analysis
  bank_statement_features: bankAnalysisResult.data.features,
  
  // From Step 2: ITR Analysis
  itr_features: itrAnalysisResult.data.features,
  
  // From Step 3: Credit Report Analysis
  credit_report_features: creditReportResult.data.features,
  
  // From Step 4: Asset Analysis
  asset_features: assetAnalysisResult.data.features
};

// Step 2: Call credit scoring API
const response = await fetch('/api/customer/credit-scoring/score/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'stori_xxxxxxxxxxxxxxxx'
  },
  body: JSON.stringify(consumerCreditScoreInput)
});

const finalScore = await response.json();
```

#### For MSME:

```javascript
// Step 1: Collect all analysis JSONs
const msmeCreditScoreInput = {
  company_name: "ABC Traders Pvt Ltd",
  msme_category: "small",
  loan_amount: 2000000,
  loan_tenure_months: 36,
  
  // From GST Analysis
  gst_data: {
    gstin: gstAnalysisResult.data.gstin,
    compliance_score: gstAnalysisResult.data.compliance_score,
    total_revenue_fy: gstAnalysisResult.data.revenue_analysis.total_revenue_fy,
    avg_monthly_revenue: gstAnalysisResult.data.revenue_analysis.avg_monthly_revenue,
    gst_filing_regularity: gstAnalysisResult.data.filing_discipline.gst_filing_regularity,
    vendor_verification_rate: gstAnalysisResult.data.vendor_analysis.vendor_verification_rate,
    outstanding_gst: gstAnalysisResult.data.tax_compliance.outstanding_gst
  },
  
  // From Director Banking Analysis
  director_data: {
    name: directorBankingResult.data.director_name,
    pan: directorBankingResult.data.director_pan,
    personal_bank_features: directorBankingResult.data.features
  },
  
  // From Business Banking Analysis
  bank_data: {
    cashflow_health_score: businessBankingResult.data.cashflow_health_score,
    average_bank_balance: businessBankingResult.data.features.average_bank_balance,
    monthly_inflow: businessBankingResult.data.features.monthly_inflow,
    monthly_outflow: businessBankingResult.data.features.monthly_outflow,
    inflow_outflow_ratio: businessBankingResult.data.features.inflow_outflow_ratio,
    bounce_rate: businessBankingResult.data.features.bounce_rate
  },
  
  // Business details
  business_data: {
    industry: "Retail & Trading",
    legal_entity_type: "private_limited",
    business_vintage_years: 8
  },
  
  // Verification
  verification_data: {
    gstin: "29ABCDE1234F1Z5",
    pan: "ABCDE1234F",
    gstin_valid: true,
    pan_valid: true
  }
};

// Step 2: Call MSME credit scoring API
const response = await fetch('/api/msme/applications/quick_score/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'stori_xxxxxxxxxxxxxxxx'
  },
  body: JSON.stringify(msmeCreditScoreInput)
});

const finalScore = await response.json();
```

---

## Error Handling

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Invalid API key |
| 403 | Forbidden - Access denied |
| 404 | Not Found |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |

### Error Response Structure

```json
{
  "success": false,
  "message": "Validation error",
  "error": {
    "code": "VALIDATION_ERROR",
    "details": {
      "bank_statement_data": ["This field is required"],
      "customer_pan": ["Invalid PAN format"]
    }
  },
  "metadata": {
    "timestamp": "2026-01-17T10:30:00Z",
    "request_id": "req_error_123"
  }
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| `INVALID_API_KEY` | API key is invalid or expired |
| `VALIDATION_ERROR` | Request validation failed |
| `INSUFFICIENT_DATA` | Not enough data for analysis |
| `ANALYSIS_FAILED` | Analysis process failed |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `DUPLICATE_REQUEST` | Request already processed |

---

## Rate Limits

### Production Limits

| Plan | Requests per Minute | Requests per Day |
|------|---------------------|------------------|
| Free | 10 | 100 |
| Basic | 60 | 10,000 |
| Pro | 300 | 100,000 |
| Enterprise | Custom | Custom |

### Rate Limit Headers

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1642432800
```

### Handling Rate Limits

```javascript
if (response.status === 429) {
  const retryAfter = response.headers.get('Retry-After');
  console.log(`Rate limit exceeded. Retry after ${retryAfter} seconds`);
  
  // Implement exponential backoff
  await sleep(retryAfter * 1000);
  return retryRequest();
}
```

---

## Best Practices

### 1. Store Analysis Results

**Always store intermediate analysis results** before calling credit scoring API:

```javascript
// ✅ Good Practice
const bankResult = await analyzeBankStatement(data);
await database.save('bank_analysis', bankResult);

const itrResult = await analyzeITR(data);
await database.save('itr_analysis', itrResult);

const finalScore = await getCreditScore({
  bank_features: bankResult.data.features,
  itr_features: itrResult.data.features
});
```

### 2. Error Recovery

Implement retry logic with exponential backoff:

```javascript
async function apiCallWithRetry(apiFunction, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await apiFunction();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await sleep(Math.pow(2, i) * 1000);
    }
  }
}
```

### 3. Validate Before Sending

```javascript
function validateBankStatement(data) {
  if (!data.transactions || data.transactions.length < 10) {
    throw new Error('Minimum 10 transactions required');
  }
  
  if (!data.customer_pan || !/^[A-Z]{5}[0-9]{4}[A-Z]$/.test(data.customer_pan)) {
    throw new Error('Invalid PAN format');
  }
  
  return true;
}
```

### 4. Use Webhooks for Async Processing

For large datasets, use webhooks:

```javascript
// Send analysis request
const response = await fetch('/api/customer/bank-statement/analyze-async/', {
  method: 'POST',
  headers: {
    'X-API-Key': apiKey,
    'X-Webhook-URL': 'https://yourapp.com/webhooks/analysis-complete'
  },
  body: JSON.stringify(data)
});

// Webhook will be called when analysis completes
```

### 5. Security

```javascript
// ✅ Never log sensitive data
console.log('Analyzing...', { 
  customer_id: data.customer_id,
  // ❌ Don't log: pan, account_number, etc.
});

// ✅ Use environment variables
const API_KEY = process.env.STORI_API_KEY;

// ✅ Validate SSL certificates
const agent = new https.Agent({
  rejectUnauthorized: true
});
```

---

## Appendix

### A. Transaction Categories

| Category | Description | Examples |
|----------|-------------|----------|
| `salary` | Salary credits | "Salary Credit", "Payroll" |
| `rent` | Rent payments | "Rent Payment", "House Rent" |
| `emi` | Loan EMIs | "EMI - Home Loan", "Car Loan EMI" |
| `utility` | Utility bills | "Electricity Bill", "Water Bill" |
| `p2p` | Peer-to-peer transfers | "UPI Transfer", "NEFT to Friend" |
| `insurance` | Insurance premiums | "LIC Premium", "Health Insurance" |
| `investment` | Investments | "Mutual Fund SIP", "SBI FD" |
| `revenue` | Business revenue | "Customer Payment", "Sales" |
| `vendor` | Vendor payments | "Supplier Payment", "Purchase" |

### B. PAN Format

```
Format: ABCDE1234F
- 5 letters (uppercase)
- 4 digits
- 1 letter (uppercase)

Regex: ^[A-Z]{5}[0-9]{4}[A-Z]$
```

### C. GSTIN Format

```
Format: 29ABCDE1234F1Z5
- 2 digits (state code)
- 10 characters (PAN)
- 1 digit (entity number)
- 1 letter (Z by default)
- 1 check digit

Regex: ^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$
```

### D. Sample Date Formats

```json
{
  "ISO 8601": "2025-01-15T10:30:00Z",
  "Date Only": "2025-01-15",
  "Indian Format": "15-01-2025",
  "Period": "12-2025" // MM-YYYY for GST
}
```

### E. Support & Contact

- **Documentation:** https://docs.storinbfc.com
- **API Status:** https://status.storinbfc.com
- **Support Email:** api-support@storinbfc.com
- **Developer Portal:** https://developers.storinbfc.com

---

## Quick Reference Card

### Consumer Flow
```
1. POST /api/customer/bank-statement/analyze-json/
2. POST /api/customer/itr/analyze-json/
3. POST /api/customer/credit-report/analyze-json/
4. POST /api/customer/assets/analyze-json/
5. POST /api/customer/credit-scoring/score/
```

### MSME Flow
```
1. POST /api/msme/gst/uploads/ + analyze/
2. POST /api/msme/director-banking/analyze-json/
3. POST /api/msme/business-banking/analyze-json/
4. POST /api/msme/applications/quick_score/
```

### Authentication
```http
X-API-Key: stori_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

**End of Documentation**

*Last updated: January 17, 2026*  
*Version: 1.0.0*  
*© 2026 Stori NBFC. All rights reserved.*

