# Quick Reference - API Documentation URLs

## 🌐 Main Documentation

```
Production: https://mycfo.club/stori/api/documentation/
Local:      http://localhost:8000/api/documentation/
```

---

## 🔐 Authentication

```
URL: /api/documentation/authentication/

Required Headers:
X-API-Key: your_api_key_here
Content-Type: application/json
```

---

## 👤 Consumer APIs

### 1. Bank Statement Analysis
```
URL:      /api/documentation/consumer/bank-statement/
Endpoint: POST /api/customer/bank-statement/analyze-json/
Output:   38+ financial features
```

### 2. ITR Analysis
```
URL:      /api/documentation/consumer/itr/
Endpoint: POST /api/customer/itr/analyze-json/
Output:   Income validation features
```

### 3. Credit Report Analysis
```
URL:      /api/documentation/consumer/credit-report/
Endpoint: POST /api/customer/credit-report/analyze-json/
Output:   Credit history features
```

### 4. Asset Analysis
```
URL:      /api/documentation/consumer/asset/
Endpoint: POST /api/customer/asset/analyze-json/
Output:   Asset portfolio features
```

### 5. Final Credit Score
```
URL:      /api/documentation/consumer/credit-score/
Endpoint: POST /api/customer/credit-scoring/score/
Output:   Credit score (300-900) + recommendation
```

### 6. KYC Document OCR
```
URL:      /api/documentation/consumer/kyc-ocr/
Endpoint: POST /api/customer/ocr/document-ocr/
Output:   Extracted PAN/Aadhaar data (name, DOB, address, etc.)
Type:     Multipart/form-data (file upload)
```

---

## 🏢 MSME APIs

### 1. GST Analysis
```
URL:      /api/documentation/msme/gst/
Endpoint: POST /api/msme/gst/uploads/
Output:   Compliance score + revenue analysis
```

### 2. Director Personal Banking
```
URL:      /api/documentation/msme/director-banking/
Endpoint: POST /api/msme/director-banking/analyze-json/
Output:   Director's financial health (38 features)
```

### 3. Business Banking
```
URL:      /api/documentation/msme/business-banking/
Endpoint: POST /api/msme/business-banking/analyze-json/
Output:   Cash flow health + DSCR inputs
```

### 4. MSME Final Credit Score
```
URL:      /api/documentation/msme/credit-score/
Endpoint: POST /api/msme/applications/quick_score/
Output:   Business credit score + DSCR analysis
```

---

## 📋 Quick Access

### For Clients/Developers:
1. Visit main page: `/api/documentation/`
2. Click any API name
3. Copy sample JSON
4. Test immediately

### For Testing:
```bash
# Start server
python manage.py runserver

# Visit
http://localhost:8000/api/documentation/
```

---

## 🎯 What Each Page Has

- ✅ Overview
- ✅ Complete endpoint URL
- ✅ Authentication headers
- ✅ Sample input JSON
- ✅ Parameters table
- ✅ Sample output JSON
- ✅ Key metrics explained
- ✅ Usage notes
- ✅ Error codes

---

## 📁 File Locations

```
stori_backend/
├── api_docs/
│   ├── views.py           # All page views
│   ├── urls.py            # URL routing
│   ├── static/api_docs/
│   │   └── style.css      # Styling
│   └── templates/api_docs/
│       ├── index.html     # Main page
│       ├── authentication.html
│       ├── consumer/      # 5 consumer pages
│       └── msme/          # 4 MSME pages
```

---

## 🚀 Integration Flow

### Consumer:
```
1. Bank Statement → Get features
2. ITR → Get features
3. Credit Report → Get features
4. (Optional) Assets → Get features
5. Final Score → Combine all → Get decision
```

### MSME:
```
1. GST → Get data
2. Director Banking → Get data
3. Business Banking → Get data
4. Final Score → Combine all → Get DSCR + decision
```

---

## ✅ Status

**COMPLETE** - All pages created and ready to use!

Access now: `https://mycfo.club/stori/api/documentation/`

