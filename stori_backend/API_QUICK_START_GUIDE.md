# Stori API - Quick Start Guide
================================

**Go from zero to production in 15 minutes** ⚡

---

## 🎯 What You'll Need

```
✅ API Key (contact: sales@mycfo.club)
✅ Base URL: https://mycfo.club/stori/api
✅ Customer/Business data in JSON format
```

---

## 🚀 Consumer Loans (4 Steps)

### 1. Bank Statement → Get 38 Features
```bash
POST https://mycfo.club/stori/api/customer/bank-statement/analyze-json/

{
  "customer_name": "Rahul Sharma",
  "customer_pan": "ABCDE1234F",
  "bank_statement_data": {
    "transactions": [...]
  }
}

→ Returns: monthly_income, income_stability, emi, bounce_rate, etc.
```

### 2. ITR → Verify Income
```bash
POST https://mycfo.club/stori/api/customer/itr/analyze-json/

{
  "customer_pan": "ABCDE1234F",
  "itr_data": {...}
}

→ Returns: annual_income, tax_compliance_score
```

### 3. Credit Report → Check History
```bash
POST https://mycfo.club/stori/api/customer/credit-report/analyze-json/

{
  "customer_pan": "ABCDE1234F",
  "credit_report_data": {...}
}

→ Returns: credit_score, total_debt, dpd_history
```

### 4. Final Score → Make Decision
```bash
POST https://mycfo.club/stori/api/customer/credit-scoring/score/

{
  "customer_pan": "ABCDE1234F",
  "loan_amount": 500000,
  "bank_statement_features": {...},
  "itr_features": {...},
  "credit_report_features": {...}
}

→ Returns: 
   credit_score: 745
   risk_tier: "prime"
   approval: "approve"
   monthly_emi: 23100
```

---

## 🏢 Business Loans (3 Steps)

### 1. GST → Revenue & Compliance
```bash
POST https://mycfo.club/stori/api/msme/gst/uploads/
POST https://mycfo.club/stori/api/msme/gst/uploads/{id}/analyze/

{
  "gstin": "29ABCDE1234F1Z5",
  "gst_data": {...}
}

→ Returns: compliance_score, revenue, vendor_verification_rate
```

### 2. Director Banking → Personal Stability
```bash
POST https://mycfo.club/stori/api/msme/director-banking/analyze-json/

{
  "director_pan": "ABCDE1234F",
  "bank_statement_data": {...}
}

→ Returns: 38 features (same as consumer)
```

### 3. Final Score → DSCR + Decision
```bash
POST https://mycfo.club/stori/api/msme/applications/quick_score/

{
  "company_name": "ABC Traders",
  "loan_amount": 2000000,
  "gst_data": {...},
  "director_data": {...},
  "bank_data": {...}
}

→ Returns:
   credit_score: 735
   dscr: 4.5
   approved_amount: 1800000
```

---

## 🔑 Authentication

**Every request needs:**
```http
X-API-Key: stori_your_api_key_here
Content-Type: application/json
```

---

## 📊 Key Metrics Explained

### Consumer
- **Credit Score**: 300-900 (higher = better)
- **Income Stability**: 0-1 (>0.8 = stable)
- **FOIR**: Fixed Obligations / Income (<50% = safe)
- **Bounce Rate**: 0% = excellent

### MSME
- **Compliance Score**: 0-100 (>80 = good)
- **DSCR**: Debt Service Coverage (>1.25 = safe)
- **Cash Flow Ratio**: Inflow/Outflow (>1.1 = healthy)
- **Vendor Verification**: >80% = strong supply chain

---

## ✅ Decision Rules (Simple)

### Consumer Approval Criteria
```
✓ Credit Score > 650
✓ Income Stability > 0.7
✓ FOIR < 50%
✓ Bounce Rate = 0
✓ No DPD in last 6 months
→ APPROVE
```

### MSME Approval Criteria
```
✓ Credit Score > 650
✓ DSCR > 1.25
✓ GST Compliance > 75
✓ Cash Flow Ratio > 1.0
✓ Director Score > 60
→ APPROVE
```

---

## 🐛 Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Wrong API key | Check API key |
| 400 Bad Request | Invalid JSON | Validate input format |
| 429 Rate Limit | Too many requests | Slow down |
| 500 Server Error | Server issue | Retry after 5 sec |

---

## 💻 Code Example

```python
import requests

API_KEY = "stori_your_key_here"
BASE_URL = "https://mycfo.club/stori/api"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Consumer: Bank Analysis
response = requests.post(
    f"{BASE_URL}/customer/bank-statement/analyze-json/",
    headers=headers,
    json={
        "customer_name": "Test User",
        "customer_pan": "ABCDE1234F",
        "bank_statement_data": {...}
    }
)

result = response.json()
print(f"Income: {result['data']['features']['monthly_income']}")
print(f"Stability: {result['data']['features']['income_stability']}")
```

---

## 📞 Support

- **Sales:** sales@mycfo.club
- **Technical:** api-support@mycfo.club
- **Docs:** https://mycfo.club/stori/docs

---

## 🎯 Quick Checklist

- [ ] Get API key
- [ ] Test with Postman
- [ ] Integrate Step 1 (Bank/GST)
- [ ] Integrate Step 2 (ITR/Director)
- [ ] Integrate Step 3 (Credit/Business)
- [ ] Integrate Step 4 (Final Score)
- [ ] Test end-to-end
- [ ] Go live!

---

**That's it! Start integrating →**

*Need help? Email: api-support@mycfo.club*

