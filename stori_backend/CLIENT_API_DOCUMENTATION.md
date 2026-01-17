# Stori Credit Scoring API - Developer Documentation
====================================================

**Welcome to Stori Credit Scoring API**

Transform your lending business with AI-powered credit risk assessment in minutes, not months.

---

## 🎯 What is Stori API?

Stori API is a comprehensive **credit scoring platform** that helps lenders make better, faster lending decisions. Our API provides:

✅ **Instant Credit Assessment** - Get credit scores in seconds  
✅ **AI-Powered Analysis** - Machine learning models trained on millions of data points  
✅ **Comprehensive Coverage** - Consumer loans & MSME/Business loans  
✅ **Explainable Results** - Understand why a score was given  
✅ **Easy Integration** - RESTful APIs with JSON  

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Get Your API Key

Contact your system administrator or request API credentials through your organization's onboarding process.

You'll receive:
```
API Key: stori_abc123def456ghi789...
Base URL: https://mycfo.club/stori/api
```

### Step 2: Make Your First API Call

```bash
curl -X POST "https://mycfo.club/stori/api/customer/bank-statement/analyze-json/" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "John Doe",
    "customer_pan": "ABCDE1234F",
    "bank_statement_data": { ... }
  }'
```

### Step 3: Get Your Credit Score

That's it! You'll receive a comprehensive credit assessment.

---

## 📊 API Products

We offer two main products:

### 1. Consumer Credit Scoring API
**For Personal Loans, Credit Cards, Auto Loans**

Analyzes:
- Bank statements (38+ financial metrics)
- Income Tax Returns
- Credit bureau reports
- Assets & investments

**Output:** Credit score (300-900), risk tier, default probability

### 2. MSME Credit Scoring API
**For Business Loans, Working Capital, Overdraft**

Analyzes:
- GST returns (revenue, compliance)
- Director's personal banking
- Business bank statements
- Vendor relationships

**Output:** Credit score (300-900), risk tier, DSCR, recommended loan amount

---

## 🔐 Authentication

All API requests require an API Key in the header:

```http
X-API-Key: stori_your_api_key_here
Content-Type: application/json
```

**Keep your API key secure!** Never expose it in client-side code.

---

## 🏦 Consumer Credit Scoring

### Overview

Assess creditworthiness for personal loan applicants in 4 simple steps:

```
Step 1: Bank Statement → Get 38 financial features
Step 2: ITR Analysis → Verify income
Step 3: Credit Report → Check credit history
Step 4: Combine All → Get final credit score
```

---

### API 1: Bank Statement Analysis

**What it does:** Analyzes bank transactions to extract 38+ financial features including income stability, spending patterns, EMI obligations, and risk indicators.

**Endpoint:**
```
POST https://mycfo.club/stori/api/customer/bank-statement/analyze-json/
```

**Input Format:**
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
        "description": "Salary Credit",
        "amount": 120000,
        "type": "credit",
        "balance": 150000
      },
      {
        "date": "2025-01-16",
        "description": "Rent Payment",
        "amount": 18000,
        "type": "debit",
        "balance": 132000
      }
    ]
  }
}
```

**What You Get:**
```json
{
  "success": true,
  "data": {
    "features": {
      "monthly_income": 120000,
      "monthly_expense": 65000,
      "income_stability": 0.92,
      "avg_balance": 110000,
      "estimated_emi": 22000,
      "bounce_rate": 0,
      // ... 32 more features
    }
  }
}
```

**💡 Key Metrics:**
- **Monthly Income** - Average monthly inflow
- **Income Stability** - How consistent is the income (0-1)
- **Spending Ratio** - Expenses as % of income
- **EMI Burden** - Existing loan obligations
- **Bounce Rate** - Payment failures
- **Manipulation Risk** - Fraud indicators

---

### API 2: ITR Analysis

**What it does:** Validates income from Income Tax Returns and checks tax compliance.

**Endpoint:**
```
POST https://mycfo.club/stori/api/customer/itr/analyze-json/
```

**Input Format:**
```json
{
  "customer_name": "Rahul Sharma",
  "customer_pan": "ABCDE1234F",
  "assessment_year": "2024-25",
  "itr_data": {
    "itr_type": "ITR-1",
    "gross_total_income": 1440000,
    "taxable_income": 1290000,
    "tax_paid": 185000,
    "income_sources": [
      {
        "source": "salary",
        "amount": 1440000
      }
    ]
  }
}
```

**What You Get:**
```json
{
  "success": true,
  "data": {
    "features": {
      "annual_income": 1440000,
      "monthly_income_itr": 120000,
      "tax_compliance_score": 0.98,
      "filing_on_time": true
    }
  }
}
```

**💡 Key Metrics:**
- **Annual Income** - Declared income
- **Tax Compliance** - Filing discipline
- **Income Match** - Compare with bank statement

---

### API 3: Credit Report Analysis

**What it does:** Analyzes credit bureau report (CIBIL/Experian) for credit history and existing obligations.

**Endpoint:**
```
POST https://mycfo.club/stori/api/customer/credit-report/analyze-json/
```

**Input Format:**
```json
{
  "customer_name": "Rahul Sharma",
  "customer_pan": "ABCDE1234F",
  "bureau": "CIBIL",
  "credit_report_data": {
    "credit_score": 760,
    "accounts": [
      {
        "account_type": "home_loan",
        "current_balance": 3800000,
        "emi_amount": 22000,
        "dpd_history": [0, 0, 0, 0, 0, 0]
      }
    ],
    "enquiries": 2
  }
}
```

**What You Get:**
```json
{
  "success": true,
  "data": {
    "features": {
      "credit_score": 760,
      "total_debt": 3845000,
      "current_emi": 22000,
      "credit_utilization": 22.5,
      "dpd_last_6_months": 0
    }
  }
}
```

**💡 Key Metrics:**
- **Credit Score** - Bureau score
- **Total Debt** - All existing loans
- **EMI Obligations** - Monthly payments
- **DPD** - Days past due (late payments)

---

### API 4: Final Credit Score

**What it does:** Combines all analyses to generate final credit score and loan recommendation.

**Endpoint:**
```
POST https://mycfo.club/stori/api/customer/credit-scoring/score/
```

**Input Format:**
```json
{
  "customer_name": "Rahul Sharma",
  "customer_pan": "ABCDE1234F",
  "loan_amount": 500000,
  "loan_tenure_months": 24,
  
  "bank_statement_features": { /* from API 1 */ },
  "itr_features": { /* from API 2 */ },
  "credit_report_features": { /* from API 3 */ },
  "asset_features": { /* optional */ }
}
```

**What You Get:**
```json
{
  "success": true,
  "data": {
    "credit_score": 745,
    "risk_tier": "prime",
    "default_probability": 0.045,
    "approval_recommendation": "approve",
    
    "loan_details": {
      "approved_amount": 500000,
      "recommended_interest_rate": 10.5,
      "monthly_emi": 23100
    },
    
    "foir_analysis": {
      "current_obligations": 22000,
      "new_emi": 23100,
      "total_obligations": 45100,
      "foir": 37.58,
      "foir_status": "acceptable"
    },
    
    "positive_factors": [
      "High income stability (0.92)",
      "Good credit score (760)",
      "Zero bounces"
    ],
    
    "risk_factors": [
      "High FOIR after new loan (37.58%)"
    ]
  }
}
```

**💡 Key Outputs:**
- **Credit Score (300-900)** - Higher is better
- **Risk Tier** - Prime, Near-Prime, Standard, Subprime
- **Approval Recommendation** - Approve/Reject/Review
- **Default Probability** - Likelihood of default (%)
- **FOIR** - Fixed Obligations to Income Ratio
- **Explainability** - Why this score?

---

## 🏢 MSME Credit Scoring

### Overview

Assess creditworthiness for business loan applicants in 3 simple steps:

```
Step 1: GST Analysis → Revenue & compliance
Step 2: Director Banking → Personal stability
Step 3: Business Banking → Cash flow health
→ Get final credit score + DSCR
```

---

### API 1: GST Analysis

**What it does:** Analyzes GST returns to assess business revenue, tax compliance, and vendor relationships.

**Endpoint:**
```
POST https://mycfo.club/stori/api/msme/gst/uploads/
POST https://mycfo.club/stori/api/msme/gst/uploads/{id}/analyze/
```

**Input Format:**
```json
{
  "gstin": "29ABCDE1234F1Z5",
  "return_type": "gstr3b",
  "return_period": "12-2025",
  "gst_data": {
    "taxable_turnover": 8000000,
    "total_tax_liability": 1440000,
    "total_tax_paid": 1440000,
    "vendors": [
      {
        "gstin": "27XXXXX1234X1Z5",
        "total_amount": 500000,
        "verified": true
      }
    ]
  }
}
```

**What You Get:**
```json
{
  "success": true,
  "data": {
    "compliance_score": 88,
    "risk_level": "low",
    
    "filing_discipline": {
      "gst_filing_regularity": 87.5,
      "on_time_filings": 10,
      "late_filings": 2
    },
    
    "revenue_analysis": {
      "total_revenue_fy": 8000000,
      "avg_monthly_revenue": 666667,
      "mom_revenue_growth": 4.35
    },
    
    "vendor_analysis": {
      "total_vendors": 15,
      "verified_vendors": 14,
      "vendor_verification_rate": 93.3
    }
  }
}
```

**💡 Key Metrics:**
- **Compliance Score (0-100)** - Tax filing discipline
- **Revenue Trends** - MoM and QoQ growth
- **Vendor Health** - Verified supplier relationships
- **Outstanding Tax** - Pending GST payments

---

### API 2: Director Personal Banking

**What it does:** Analyzes director's personal bank statement (same 38 features as consumer).

**Endpoint:**
```
POST https://mycfo.club/stori/api/msme/director-banking/analyze-json/
```

**Input Format:**
```json
{
  "director_name": "Rajesh Kumar",
  "director_pan": "ABCDE1234F",
  "bank_statement_data": {
    "transactions": [
      {
        "date": "2025-01-15",
        "description": "Salary",
        "amount": 180000,
        "type": "credit",
        "balance": 250000
      }
    ]
  }
}
```

**What You Get:**
```json
{
  "success": true,
  "data": {
    "overall_score": 82,
    "risk_category": "low",
    
    "summary": {
      "monthly_income": 180000,
      "income_stability": 0.88,
      "avg_balance": 220000,
      "is_stable": true
    },
    
    "features": {
      // ... all 38 features
    }
  }
}
```

**💡 Key Metrics:**
- **Director's Income** - Personal financial strength
- **Stability** - Consistent income flow
- **Personal EMI** - Existing obligations
- **Financial Discipline** - Bounce rate, savings

---

### API 3: Business Banking

**What it does:** Analyzes business current account for cash flow and operational health.

**Endpoint:**
```
POST https://mycfo.club/stori/api/msme/business-banking/analyze-json/
```

**Input Format:**
```json
{
  "business_name": "ABC Traders Pvt Ltd",
  "gstin": "29ABCDE1234F1Z5",
  "bank_statement_data": {
    "transactions": [
      {
        "date": "2025-01-05",
        "description": "Customer Payment",
        "amount": 125000,
        "type": "credit",
        "balance": 850000
      }
    ]
  }
}
```

**What You Get:**
```json
{
  "success": true,
  "data": {
    "cashflow_health_score": 85,
    "business_risk_category": "low",
    
    "summary": {
      "average_bank_balance": 780000,
      "monthly_inflow": 3200000,
      "monthly_outflow": 2850000,
      "inflow_outflow_ratio": 1.12
    }
  }
}
```

**💡 Key Metrics:**
- **Cash Flow Health (0-100)** - Business liquidity
- **Inflow/Outflow Ratio** - Should be > 1.0
- **Average Balance** - Working capital
- **Bounce Rate** - Payment failures

---

### API 4: MSME Final Score

**What it does:** Combines all MSME analyses for final credit score.

**Endpoint:**
```
POST https://mycfo.club/stori/api/msme/applications/quick_score/
```

**Input Format:**
```json
{
  "company_name": "ABC Traders Pvt Ltd",
  "loan_amount": 2000000,
  "loan_tenure_months": 36,
  
  "gst_data": { /* from API 1 */ },
  "director_data": { /* from API 2 */ },
  "bank_data": { /* from API 3 */ }
}
```

**What You Get:**
```json
{
  "success": true,
  "data": {
    "final_credit_score": 735,
    "risk_tier": "near_prime",
    "approval_recommendation": "approve_with_conditions",
    
    "loan_details": {
      "approved_amount": 1800000,
      "recommended_interest_rate": 12.5,
      "monthly_emi": 59850
    },
    
    "dscr_analysis": {
      "annual_net_income": 4200000,
      "total_annual_obligations": 934200,
      "dscr": 4.5,
      "dscr_status": "excellent"
    },
    
    "positive_factors": [
      "Strong cash flow (1.12)",
      "High GST compliance (88)",
      "Director financially stable"
    ]
  }
}
```

**💡 Key Outputs:**
- **Credit Score (300-900)** - Business creditworthiness
- **DSCR** - Debt Service Coverage Ratio (should be > 1.25)
- **Approved Amount** - Recommended loan amount
- **Interest Rate** - Risk-based pricing
- **Conditions** - Any requirements

---

## 💡 Integration Guide

### Typical Integration Flow

#### For Consumer Loans:

```javascript
// Step 1: Collect customer data
const customerData = {
  name: "Rahul Sharma",
  pan: "ABCDE1234F",
  bankStatement: [...],
  itr: {...},
  creditReport: {...}
};

// Step 2: Call APIs sequentially
const bankAnalysis = await fetch('/customer/bank-statement/analyze-json/', {
  method: 'POST',
  headers: {
    'X-API-Key': 'YOUR_API_KEY',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    customer_name: customerData.name,
    customer_pan: customerData.pan,
    bank_statement_data: customerData.bankStatement
  })
});

const itrAnalysis = await fetch('/customer/itr/analyze-json/', {...});
const creditAnalysis = await fetch('/customer/credit-report/analyze-json/', {...});

// Step 3: Get final score
const finalScore = await fetch('/customer/credit-scoring/score/', {
  method: 'POST',
  body: JSON.stringify({
    customer_name: customerData.name,
    customer_pan: customerData.pan,
    loan_amount: 500000,
    loan_tenure_months: 24,
    bank_statement_features: bankAnalysis.data.features,
    itr_features: itrAnalysis.data.features,
    credit_report_features: creditAnalysis.data.features
  })
});

// Step 4: Make decision
if (finalScore.data.approval_recommendation === 'approve') {
  approveLoan();
} else {
  rejectLoan();
}
```

#### For MSME Loans:

```javascript
// Step 1: Collect business data
const businessData = {
  name: "ABC Traders",
  gstin: "29ABCDE1234F1Z5",
  gstReturns: {...},
  directorBankStatement: [...],
  businessBankStatement: [...]
};

// Step 2: Call APIs
const gstAnalysis = await callGSTAPI(businessData.gstReturns);
const directorAnalysis = await callDirectorBankingAPI(businessData.directorBankStatement);
const businessAnalysis = await callBusinessBankingAPI(businessData.businessBankStatement);

// Step 3: Get final score
const finalScore = await fetch('/msme/applications/quick_score/', {
  method: 'POST',
  body: JSON.stringify({
    company_name: businessData.name,
    loan_amount: 2000000,
    gst_data: gstAnalysis.data,
    director_data: directorAnalysis.data,
    bank_data: businessAnalysis.data
  })
});

// Step 4: Make decision based on DSCR and credit score
if (finalScore.data.dscr_analysis.dscr > 1.25 && 
    finalScore.data.final_credit_score > 650) {
  approveLoan();
}
```

---

## 🔒 Security & Best Practices

### 1. API Key Security
```
✅ Store API key in environment variables
✅ Never commit API key to version control
✅ Use separate keys for development and production
❌ Never expose API key in client-side JavaScript
```

### 2. Data Privacy
```
✅ All data is encrypted in transit (HTTPS)
✅ We don't store customer data without consent
✅ GDPR & data protection compliant
✅ You own your data
```

### 3. Error Handling
```javascript
try {
  const response = await fetch(API_URL, options);
  const data = await response.json();
  
  if (!data.success) {
    // Handle error
    console.error(data.message);
    showErrorToUser(data.message);
  }
} catch (error) {
  // Network error
  console.error('API call failed:', error);
  retryWithBackoff();
}
```

### 4. Rate Limiting

The API implements rate limiting to ensure fair usage. If you exceed your rate limit, you'll receive an HTTP 429 response. Implement exponential backoff in your code to handle rate limit errors gracefully.

```javascript
async function callApiWithRetry(url, options, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url, options);
      if (response.status === 429) {
        const waitTime = Math.pow(2, i) * 1000; // Exponential backoff
        await new Promise(resolve => setTimeout(resolve, waitTime));
        continue;
      }
      return response;
    } catch (error) {
      if (i === maxRetries - 1) throw error;
    }
  }
}
```

---

## 📊 Response Formats

### Success Response
```json
{
  "success": true,
  "message": "Analysis completed successfully",
  "data": {
    // Response data
  },
  "metadata": {
    "timestamp": "2026-01-17T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Validation error",
  "error": {
    "code": "VALIDATION_ERROR",
    "details": {
      "bank_statement_data": ["This field is required"]
    }
  }
}
```

### Common Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| `INVALID_API_KEY` | API key is invalid | Check your API key |
| `VALIDATION_ERROR` | Input validation failed | Check request format |
| `INSUFFICIENT_DATA` | Not enough data | Provide more transactions |
| `RATE_LIMIT_EXCEEDED` | Too many requests | Implement retry with exponential backoff |

---

*Last Updated: January 17, 2026*  
*Version: 1.0.0*
