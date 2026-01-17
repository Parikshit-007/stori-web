# MSME Postman Collection Guide
===============================

## 📦 Files Created

1. **`MSME_Postman_Collection.json`** - Complete API collection
2. **`MSME_Postman_Environment.json`** - Environment variables

---

## 🚀 How to Import in Postman

### Step 1: Import Collection
1. Open Postman
2. Click **Import** button (top left)
3. Drag & drop **`MSME_Postman_Collection.json`**
4. Click **Import**

### Step 2: Import Environment
1. Click **Environments** (left sidebar)
2. Click **Import**
3. Drag & drop **`MSME_Postman_Environment.json`**
4. Select **MSME - Local Development** environment (top right dropdown)

### Step 3: Update API Key
1. Click **Environments** → **MSME - Local Development**
2. Update `api_key` value with your actual API key
3. Save

---

## 📋 Collection Structure

### 1. MSME Application (6 requests)
```
├── Create MSME Application
├── Get All Applications
├── Get Application Details
├── Complete MSME Analysis
├── Get Analysis Result
└── Quick Score (No Save)
```

### 2. GST Analysis (6 requests)
```
├── Upload GST Return (JSON)
├── Analyze GST Return
├── Get GST Analysis Result
├── Get All GST Results
├── Get GST Summary by GSTIN
└── Get Filing Regularity
```

### 3. Director Personal Banking (3 requests)
```
├── Analyze Director Banking (JSON)
├── Get Director Banking Summary
└── Get All Director Results
```

### 4. Business Banking (2 requests)
```
├── Analyze Business Banking (JSON)
└── Get All Business Banking Results
```

**Total: 17 API requests with examples**

---

## 🎯 Quick Test Flow

### Step 1: Create Application
```
POST /api/msme/applications/
```
Response saves `application_id` in environment

### Step 2: Analyze Director Banking
```
POST /api/msme/director-banking/analyze-json/
```
JSON body with bank transactions included

### Step 3: Analyze Business Banking
```
POST /api/msme/business-banking/analyze-json/
```
JSON body with business transactions included

### Step 4: Upload & Analyze GST
```
POST /api/msme/gst/uploads/
POST /api/msme/gst/uploads/{{gst_upload_id}}/analyze/
```

### Step 5: Get Complete Analysis
```
GET /api/msme/applications/{{application_id}}/analysis_result/
```

---

## 🔧 Environment Variables

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `base_url` | http://localhost:8000 | API base URL |
| `api_key` | stori_your_api_key_here | Your API key |
| `application_id` | 1 | MSME application ID |
| `gst_upload_id` | 1 | GST upload ID |
| `director_pan` | ABCDE1234F | Director PAN |
| `gstin` | 29ABCDE1234F1Z5 | Business GSTIN |

---

## 📊 Sample Data Included

### Director Banking Transaction
```json
{
  "date": "2025-01-15",
  "description": "Salary Credit - Company ABC",
  "amount": 150000,
  "type": "credit",
  "balance": 200000,
  "category": "salary"
}
```

### Business Banking Transaction
```json
{
  "date": "2025-01-05",
  "description": "Customer Payment - INV001",
  "amount": 50000,
  "type": "credit",
  "balance": 500000,
  "category": "revenue"
}
```

### GST Data
```json
{
  "gstin": "29ABCDE1234F1Z5",
  "total_revenue": 5000000,
  "total_tax_liability": 900000,
  "vendors": [...]
}
```

---

## 🎨 Features

✅ **Complete Examples** - All requests have sample JSON bodies
✅ **Environment Variables** - Easy to switch between environments
✅ **Auto-save IDs** - Response IDs saved automatically
✅ **Organized Folders** - Grouped by module
✅ **Detailed Descriptions** - Each request has clear description

---

## 📝 Response Examples

### Director Banking Analysis Response:
```json
{
  "success": true,
  "data": {
    "director_name": "Rajesh Kumar",
    "overall_score": 75,
    "risk_category": "low",
    "summary": {
      "monthly_income": 150000,
      "monthly_expense": 80000,
      "avg_balance": 200000,
      "income_stability": 0.85
    },
    "features": {
      "monthly_income": 150000,
      "spending_to_income": 53.33,
      "balance_volatility": 15.5,
      "estimated_emi": 25000,
      "upi_p2p_ratio": 0.25,
      // ... all 38 features
    }
  }
}
```

### GST Analysis Response:
```json
{
  "success": true,
  "data": {
    "compliance_score": 85,
    "risk_level": "low",
    "total_revenue_fy": 5000000,
    "gst_filing_regularity": 90.0,
    "vendor_verification_rate": 95.5,
    "outstanding_gst": 0
  }
}
```

### Business Banking Response:
```json
{
  "success": true,
  "data": {
    "cashflow_health_score": 80,
    "business_risk_category": "low",
    "summary": {
      "average_bank_balance": 500000,
      "monthly_inflow": 2000000,
      "monthly_outflow": 1800000,
      "inflow_outflow_ratio": 1.11
    }
  }
}
```

---

## 🔐 Authentication

All requests use **X-API-Key** header:
```
X-API-Key: {{api_key}}
```

Generate API key:
```bash
python manage.py generate_api_key admin "MSME API Key"
```

---

## 🎯 Testing Tips

1. **Start with Create Application** - Get application_id first
2. **Test Director Banking** - Returns all 38 features
3. **Test Business Banking** - Cash flow analysis
4. **Test GST Analysis** - Revenue & compliance
5. **Get Complete Result** - Final credit score

---

## 📞 Support

- **Documentation:** `MSME_JSON_API_GUIDE.md`
- **Setup Guide:** `MSME_QUICK_SETUP.md`
- **Complete Flow:** `MSME_COMPLETE_FLOW.md`

---

## 🎉 Ready to Use!

Import करो, API key update करो, और test करो! 🚀

Happy Testing! 🎊

