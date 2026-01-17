# Production Deployment Guide
==============================

## 🚀 Production URL

```
Base URL: https://mycfo.club/stori/api
```

---

## 📋 Quick Reference

### Consumer APIs

```bash
# Bank Statement Analysis
POST https://mycfo.club/stori/api/customer/bank-statement/analyze-json/

# ITR Analysis
POST https://mycfo.club/stori/api/customer/itr/analyze-json/

# Credit Report Analysis
POST https://mycfo.club/stori/api/customer/credit-report/analyze-json/

# Asset Analysis
POST https://mycfo.club/stori/api/customer/assets/analyze-json/

# Final Credit Scoring
POST https://mycfo.club/stori/api/customer/credit-scoring/score/
```

### MSME APIs

```bash
# GST Analysis
POST https://mycfo.club/stori/api/msme/gst/uploads/
POST https://mycfo.club/stori/api/msme/gst/uploads/{id}/analyze/

# Director Personal Banking
POST https://mycfo.club/stori/api/msme/director-banking/analyze-json/

# Business Banking
POST https://mycfo.club/stori/api/msme/business-banking/analyze-json/

# MSME Application & Scoring
POST https://mycfo.club/stori/api/msme/applications/
POST https://mycfo.club/stori/api/msme/applications/{id}/analyze/
POST https://mycfo.club/stori/api/msme/applications/quick_score/
```

---

## 🔑 Authentication

All requests require API Key in header:

```http
X-API-Key: stori_your_production_api_key_here
Content-Type: application/json
```

---

## 🧪 Test Production API

### Quick Test (cURL)

```bash
# Test Authentication
curl -X GET "https://mycfo.club/stori/api/customer/bank-statement/" \
  -H "X-API-Key: stori_your_api_key_here" \
  -H "Content-Type: application/json"

# Test Consumer Bank Analysis
curl -X POST "https://mycfo.club/stori/api/customer/bank-statement/analyze-json/" \
  -H "X-API-Key: stori_your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Test User",
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
          "amount": 100000,
          "type": "credit",
          "balance": 150000,
          "category": "salary"
        }
      ]
    }
  }'
```

### Python Test

```python
import requests

BASE_URL = "https://mycfo.club/stori/api"
API_KEY = "stori_your_api_key_here"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Test Consumer Bank Statement Analysis
data = {
    "customer_name": "Test User",
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
                "amount": 100000,
                "type": "credit",
                "balance": 150000,
                "category": "salary"
            }
        ]
    }
}

response = requests.post(
    f"{BASE_URL}/customer/bank-statement/analyze-json/",
    headers=headers,
    json=data
)

print(response.json())
```

### JavaScript/Node.js Test

```javascript
const BASE_URL = 'https://mycfo.club/stori/api';
const API_KEY = 'stori_your_api_key_here';

const headers = {
  'X-API-Key': API_KEY,
  'Content-Type': 'application/json'
};

const data = {
  customer_name: 'Test User',
  customer_pan: 'ABCDE1234F',
  bank_name: 'HDFC Bank',
  account_type: 'savings',
  bank_statement_data: {
    account_number: 'XXXX1234',
    statement_period: {
      from: '2025-01-01',
      to: '2025-12-31'
    },
    transactions: [
      {
        date: '2025-01-15',
        description: 'Salary Credit',
        amount: 100000,
        type: 'credit',
        balance: 150000,
        category: 'salary'
      }
    ]
  }
};

fetch(`${BASE_URL}/customer/bank-statement/analyze-json/`, {
  method: 'POST',
  headers: headers,
  body: JSON.stringify(data)
})
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
```

---

## 📦 Postman Setup for Production

### Step 1: Import Collection
1. Open Postman
2. Import `MSME_Postman_Collection.json`

### Step 2: Import Production Environment
1. Import `MSME_Postman_Environment_Production.json`
2. Select "MSME - Production" environment
3. Update `api_key` with your production API key

### Step 3: Test
1. Select any request
2. Click "Send"
3. Check response

---

## 🔐 Security Checklist

### ✅ Before Going Live

- [ ] **Generate Production API Key**
  ```bash
  python manage.py generate_api_key production "Production Key"
  ```

- [ ] **Enable HTTPS Only**
  - All requests must use HTTPS
  - HTTP requests will be rejected

- [ ] **Set CORS Origins**
  ```python
  # settings.py
  CORS_ALLOWED_ORIGINS = [
      'https://yourdomain.com',
      'https://app.yourdomain.com'
  ]
  ```

- [ ] **Enable Rate Limiting**
  - Monitor API usage
  - Set appropriate limits

- [ ] **Setup Monitoring**
  - API response times
  - Error rates
  - Success rates

- [ ] **Backup Strategy**
  - Database backups
  - Regular snapshots

- [ ] **API Key Rotation**
  - Rotate keys every 90 days
  - Keep audit logs

---

## 📊 Production Endpoints Summary

### Consumer Flow (5 APIs)

| API | Endpoint | Purpose |
|-----|----------|---------|
| Bank Statement | `/customer/bank-statement/analyze-json/` | 38 financial features |
| ITR Analysis | `/customer/itr/analyze-json/` | Income validation |
| Credit Report | `/customer/credit-report/analyze-json/` | Credit history |
| Asset Analysis | `/customer/assets/analyze-json/` | Asset verification |
| Credit Scoring | `/customer/credit-scoring/score/` | Final score (0-850) |

### MSME Flow (4 APIs)

| API | Endpoint | Purpose |
|-----|----------|---------|
| GST Analysis | `/msme/gst/uploads/` + `/analyze/` | Revenue & compliance |
| Director Banking | `/msme/director-banking/analyze-json/` | Personal stability |
| Business Banking | `/msme/business-banking/analyze-json/` | Cash flow health |
| MSME Scoring | `/msme/applications/quick_score/` | Final score (0-850) |

---

## 🎯 Integration Example (Production)

### Complete Consumer Flow

```python
import requests
import json

BASE_URL = "https://mycfo.club/stori/api"
API_KEY = "stori_your_production_api_key_here"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Step 1: Bank Statement Analysis
bank_data = {
    "customer_name": "Rahul Sharma",
    "customer_pan": "ABCDE1234F",
    "bank_name": "HDFC Bank",
    "account_type": "savings",
    "bank_statement_data": {
        # ... transaction data
    }
}

bank_response = requests.post(
    f"{BASE_URL}/customer/bank-statement/analyze-json/",
    headers=headers,
    json=bank_data
)
bank_result = bank_response.json()

# Store in database
db.save('bank_analysis', bank_result)

# Step 2: ITR Analysis
itr_data = {
    "customer_name": "Rahul Sharma",
    "customer_pan": "ABCDE1234F",
    "assessment_year": "2024-25",
    "itr_data": {
        # ... ITR data
    }
}

itr_response = requests.post(
    f"{BASE_URL}/customer/itr/analyze-json/",
    headers=headers,
    json=itr_data
)
itr_result = itr_response.json()

# Store in database
db.save('itr_analysis', itr_result)

# Step 3: Credit Report Analysis
credit_data = {
    "customer_name": "Rahul Sharma",
    "customer_pan": "ABCDE1234F",
    "bureau": "CIBIL",
    "credit_report_data": {
        # ... credit report data
    }
}

credit_response = requests.post(
    f"{BASE_URL}/customer/credit-report/analyze-json/",
    headers=headers,
    json=credit_data
)
credit_result = credit_response.json()

# Store in database
db.save('credit_analysis', credit_result)

# Step 4: Asset Analysis
asset_data = {
    "customer_name": "Rahul Sharma",
    "customer_pan": "ABCDE1234F",
    "assets_data": {
        # ... asset data
    }
}

asset_response = requests.post(
    f"{BASE_URL}/customer/assets/analyze-json/",
    headers=headers,
    json=asset_data
)
asset_result = asset_response.json()

# Store in database
db.save('asset_analysis', asset_result)

# Step 5: Combine & Get Final Score
scoring_data = {
    "customer_name": "Rahul Sharma",
    "customer_pan": "ABCDE1234F",
    "customer_type": "salaried",
    "loan_amount": 500000,
    "loan_tenure_months": 24,
    "bank_statement_features": bank_result['data']['features'],
    "itr_features": itr_result['data']['features'],
    "credit_report_features": credit_result['data']['features'],
    "asset_features": asset_result['data']['features']
}

score_response = requests.post(
    f"{BASE_URL}/customer/credit-scoring/score/",
    headers=headers,
    json=scoring_data
)
final_score = score_response.json()

# Store final score
db.save('final_credit_score', final_score)

print(f"Final Credit Score: {final_score['data']['credit_score']}")
print(f"Risk Tier: {final_score['data']['risk_tier']}")
print(f"Approval: {final_score['data']['approval_recommendation']}")
```

### Complete MSME Flow

```python
# Step 1: GST Analysis
gst_upload_data = {
    "gstin": "29ABCDE1234F1Z5",
    "return_type": "gstr3b",
    "return_period": "12-2025",
    "financial_year": "2025-26",
    "file_type": "json",
    "gst_data": {
        # ... GST data
    }
}

gst_upload_response = requests.post(
    f"{BASE_URL}/msme/gst/uploads/",
    headers=headers,
    json=gst_upload_data
)
gst_upload_id = gst_upload_response.json()['id']

# Analyze GST
gst_analyze_data = {
    "itr_data": {...},
    "platform_sales_data": {...},
    "filing_history": [...]
}

gst_response = requests.post(
    f"{BASE_URL}/msme/gst/uploads/{gst_upload_id}/analyze/",
    headers=headers,
    json=gst_analyze_data
)
gst_result = gst_response.json()

# Store in database
db.save('gst_analysis', gst_result)

# Step 2: Director Banking Analysis
director_data = {
    "director_name": "Rajesh Kumar",
    "director_pan": "ABCDE1234F",
    "bank_name": "HDFC Bank",
    "account_type": "savings",
    "bank_statement_data": {
        # ... transactions
    }
}

director_response = requests.post(
    f"{BASE_URL}/msme/director-banking/analyze-json/",
    headers=headers,
    json=director_data
)
director_result = director_response.json()

# Store in database
db.save('director_analysis', director_result)

# Step 3: Business Banking Analysis
business_data = {
    "business_name": "ABC Traders Pvt Ltd",
    "gstin": "29ABCDE1234F1Z5",
    "bank_name": "ICICI Bank",
    "account_type": "current",
    "bank_statement_data": {
        # ... transactions
    }
}

business_response = requests.post(
    f"{BASE_URL}/msme/business-banking/analyze-json/",
    headers=headers,
    json=business_data
)
business_result = business_response.json()

# Store in database
db.save('business_analysis', business_result)

# Step 4: Combine & Get Final Score
msme_scoring_data = {
    "company_name": "ABC Traders Pvt Ltd",
    "msme_category": "small",
    "loan_amount": 2000000,
    "loan_tenure_months": 36,
    "director_data": {
        "name": director_result['data']['director_name'],
        "pan": director_result['data']['director_pan'],
        "personal_bank_features": director_result['data']['features']
    },
    "gst_data": {
        "gstin": gst_result['data']['gstin'],
        "compliance_score": gst_result['data']['compliance_score'],
        # ... other GST features
    },
    "bank_data": {
        "cashflow_health_score": business_result['data']['cashflow_health_score'],
        # ... other business features
    },
    "business_data": {...},
    "verification_data": {...}
}

msme_score_response = requests.post(
    f"{BASE_URL}/msme/applications/quick_score/",
    headers=headers,
    json=msme_scoring_data
)
final_msme_score = msme_score_response.json()

# Store final score
db.save('final_msme_score', final_msme_score)

print(f"Final Credit Score: {final_msme_score['data']['final_credit_score']}")
print(f"Risk Tier: {final_msme_score['data']['risk_tier']}")
print(f"Approval: {final_msme_score['data']['approval_recommendation']}")
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. CORS Error
```
Error: CORS policy blocked
Solution: Contact admin to whitelist your domain
```

#### 2. 401 Unauthorized
```
Error: Invalid API key
Solution: 
- Check API key is correct
- Ensure key is active
- Generate new key if needed
```

#### 3. 429 Rate Limit
```
Error: Too many requests
Solution:
- Implement exponential backoff
- Reduce request frequency
- Upgrade to higher tier
```

#### 4. 500 Internal Error
```
Error: Server error
Solution:
- Check request format
- Verify all required fields
- Contact support if persists
```

---

## 📞 Support

**Production Support:**
- Email: api-support@mycfo.club
- Documentation: https://mycfo.club/stori/docs
- Status Page: https://mycfo.club/stori/status

**API Key Management:**
- Generate keys via Django admin
- Contact admin for production keys

---

## 🎉 Ready for Production!

✅ **Base URL:** `https://mycfo.club/stori/api`
✅ **Documentation:** Complete
✅ **Postman Collection:** Updated
✅ **Test Examples:** Provided
✅ **Security:** Guidelines included

**Start integrating!** 🚀

---

*Last updated: January 17, 2026*  
*Production URL: https://mycfo.club/stori/api*

