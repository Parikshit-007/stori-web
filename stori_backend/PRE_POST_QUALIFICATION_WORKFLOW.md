# Stori API - Pre-Qualification & Post-Qualification Workflow

## Overview

The credit assessment process is divided into **two stages**:

1. **Pre-Qualification** - Initial validation and eligibility checks
2. **Post-Qualification** - Detailed financial analysis and credit scoring

**⚠️ IMPORTANT:** Post-Qualification APIs should **ONLY** be called after ALL Pre-Qualification criteria are met.

---

## Consumer Loan Workflow

### 📋 Stage 1: Pre-Qualification (Mandatory First Steps)

#### Step 1: KYC Document OCR
**API:** `POST /api/customer/ocr/document-ocr/`

**Purpose:** Extract and validate customer identity documents

**Documents to Process:**
- **Aadhaar Front:** Extract Aadhaar number, name, DOB, gender
- **Aadhaar Back:** Extract complete address
- **PAN Card:** Extract PAN number, name, father's name, DOB

**Validation:**
- ✅ Documents are clear and readable
- ✅ All fields extracted successfully
- ✅ No missing critical data

---

#### Step 2: Aadhaar Validation (External API Integration Required)

**Purpose:** Verify Aadhaar authenticity with government repository

**Integration:** Use UIDAI's official API or authorized partners (e.g., Digio, Signzy, IDfy)

**Validation:**
- ✅ Aadhaar number is valid
- ✅ Aadhaar is active (not blocked/cancelled)
- ✅ Name and DOB match with government records

**Sample External APIs:**
- UIDAI eKYC API
- Digio Aadhaar Verification
- Signzy Aadhaar API
- IDfy Aadhaar Verification

---

#### Step 3: Name Match Validation

**Purpose:** Ensure name consistency across all documents

**Cross-Check:**
- Name on Aadhaar
- Name on PAN Card
- Name on Bank Account (from bank statement)

**Validation:**
- ✅ Names match (allow for minor variations like initials)
- ✅ No major discrepancies
- ⚠️ Flag if names are completely different

**Algorithm:**
```python
# Use fuzzy matching (e.g., Levenshtein distance)
# Accept if similarity > 85%
from fuzzywuzzy import fuzz

aadhaar_name = "RAHUL SHARMA"
pan_name = "RAHUL KUMAR SHARMA"
bank_name = "R SHARMA"

similarity = fuzz.token_sort_ratio(aadhaar_name, pan_name)
# If similarity > 85%, consider it a match
```

---

#### Step 4: Face Match (Selfie vs Aadhaar Photo)

**Purpose:** Prevent identity fraud by matching live selfie with document photo

**Process:**
1. Capture live selfie from customer
2. Extract face from Aadhaar card photo
3. Compare using facial recognition AI

**Integration:** Use face matching APIs:
- AWS Rekognition
- Azure Face API
- Google Cloud Vision API
- Custom ML model

**Validation:**
- ✅ Face match confidence > 90%
- ✅ Liveness check passed (not a photo of photo)
- ❌ Reject if confidence < 80%

---

#### Step 5: Basic Eligibility Check

**Purpose:** Check basic loan eligibility criteria

**Checks:**
1. **Age Verification:**
   - Extract DOB from Aadhaar
   - Calculate age
   - ✅ Age between 21-65 years
   - ❌ Reject if outside range

2. **Location/Pincode Check:**
   - Extract pincode from Aadhaar address
   - Check against serviceable pincodes database
   - ✅ Pincode is serviceable
   - ❌ Reject if not serviceable

3. **Duplicate Check:**
   - Check if Aadhaar/PAN already has active loan
   - ✅ No active loan
   - ❌ Reject if duplicate found

**Sample Code:**
```python
def check_basic_eligibility(aadhaar_data):
    from datetime import datetime
    
    # Age check
    dob = datetime.strptime(aadhaar_data['dob'], '%d/%m/%Y')
    age = (datetime.now() - dob).days / 365.25
    
    if age < 21 or age > 65:
        return False, "Age not in range (21-65)"
    
    # Pincode check
    pincode = extract_pincode(aadhaar_data['address'])
    if pincode not in SERVICEABLE_PINCODES:
        return False, "Pincode not serviceable"
    
    # Duplicate check
    if check_duplicate_customer(aadhaar_data['aadhaar_number']):
        return False, "Duplicate customer found"
    
    return True, "Eligible for post-qualification"
```

---

### ✅ Pre-Qualification Criteria Checklist

Before proceeding to Post-Qualification, verify:

- [ ] Aadhaar OCR extraction successful
- [ ] PAN OCR extraction successful
- [ ] Aadhaar validated from government API
- [ ] Name matches across Aadhaar, PAN, and bank account
- [ ] Face verification passed (selfie matches Aadhaar photo)
- [ ] Age between 21-65 years
- [ ] Pincode is serviceable
- [ ] No duplicate customer

**→ If ALL checks pass, proceed to Post-Qualification**  
**→ If ANY check fails, REJECT application**

---

### 🎯 Stage 2: Post-Qualification (Detailed Financial Analysis)

**⚠️ Only proceed if Pre-Qualification is complete!**

#### Step 1: Bank Statement Analysis
**API:** `POST /api/customer/bank-statement/analyze-json/`

**Input:** Last 6-12 months bank transactions

**Output:** 38+ financial features including:
- Monthly income
- Income stability
- Spending patterns
- EMI obligations
- Bounce rate
- Average balance

---

#### Step 2: ITR Analysis (Optional but Recommended)
**API:** `POST /api/customer/itr/analyze-json/`

**Input:** Income Tax Return data (ITR-1, ITR-2, etc.)

**Output:**
- Annual income
- Tax compliance score
- Income source verification
- Cross-check with bank statement income

---

#### Step 3: Credit Report Analysis
**API:** `POST /api/customer/credit-report/analyze-json/`

**Input:** CIBIL/Experian credit report

**Output:**
- Credit score
- Total debt
- Current EMI obligations
- Days past due (DPD)
- Credit utilization
- Payment history

---

#### Step 4: Asset Analysis (Optional)
**API:** `POST /api/customer/asset/analyze-json/`

**Input:** Asset details (property, vehicles, investments)

**Output:**
- Total asset value
- Liquid assets
- Asset diversity score

---

#### Step 5: Final Credit Score
**API:** `POST /api/customer/credit-scoring/score/`

**Input:** Combined features from all previous analyses

**Output:**
- Final credit score (300-900)
- Risk tier (Prime, Near-Prime, Standard, Subprime)
- Approval recommendation
- Loan amount recommendation
- Interest rate recommendation
- FOIR analysis

---

## MSME Loan Workflow

### 📋 Stage 1: Pre-Qualification (Mandatory First Steps)

#### Step 1: Director KYC - Document OCR
**API:** `POST /api/customer/ocr/document-ocr/`

**Purpose:** Extract and validate director's identity documents

**Documents:**
- Director's Aadhaar (Front + Back)
- Director's PAN Card

**Validation:**
- ✅ All documents processed successfully
- ✅ Director details extracted

---

#### Step 2: Director Aadhaar Validation (External API)

**Purpose:** Verify director's Aadhaar with government repository

**Integration:** Use UIDAI API or authorized partners

**Validation:**
- ✅ Director's Aadhaar is valid
- ✅ Active and not blocked
- ✅ Details match government records

---

#### Step 3: GSTIN Verification (External API)

**Purpose:** Verify business GSTIN is valid and active

**Integration:** Use GST Portal API or authorized partners:
- GST Network API
- MasterGST API
- ClearTax GST API
- Signzy GSTIN Verification

**API Call:**
```
GET https://gst-api-provider.com/verify-gstin
Headers:
  - API-Key: your_api_key
Body:
  - gstin: 29ABCDE1234F1Z5
```

**Validation:**
- ✅ GSTIN is valid format (15 characters)
- ✅ GSTIN is active (not cancelled)
- ✅ Business name matches registration
- ✅ Business address matches
- ✅ Filing status is regular
- ✅ No major compliance issues

**Response Check:**
```json
{
  "gstin": "29ABCDE1234F1Z5",
  "status": "Active",
  "legal_name": "ABC TRADERS PRIVATE LIMITED",
  "trade_name": "ABC Traders",
  "registration_date": "2020-01-15",
  "taxpayer_type": "Regular",
  "business_address": "...",
  "filing_status": "Regular"
}
```

---

#### Step 4: Business Name & Address Match

**Purpose:** Ensure business information consistency

**Cross-Check:**
- Business name on GST registration
- Business name on bank account
- Business address on GST vs actual location

**Validation:**
- ✅ Names match (allow minor variations)
- ✅ Address pincode matches
- ✅ No major discrepancies

---

#### Step 5: Basic Business Eligibility

**Purpose:** Check minimum business requirements

**Checks:**

1. **Business Age:**
   - Extract registration date from GSTIN verification
   - Calculate business age
   - ✅ Business operational for minimum 1 year
   - ❌ Reject if less than 1 year

2. **Turnover Check:**
   - Get annual turnover from GST data
   - ✅ Meets minimum turnover threshold (e.g., ₹10 lakhs)
   - ❌ Reject if below threshold

3. **Location Serviceability:**
   - Check business location pincode
   - ✅ Location is serviceable
   - ❌ Reject if not serviceable

4. **Business Type:**
   - Check if business type is eligible for loan
   - ✅ Eligible business category
   - ❌ Reject if restricted category (e.g., gambling, liquor)

**Sample Code:**
```python
def check_msme_eligibility(gstin_data, business_data):
    from datetime import datetime
    
    # Business age check
    reg_date = datetime.strptime(gstin_data['registration_date'], '%Y-%m-%d')
    business_age = (datetime.now() - reg_date).days / 365.25
    
    if business_age < 1:
        return False, "Business operational for less than 1 year"
    
    # Turnover check
    if business_data['annual_turnover'] < 1000000:  # 10 lakhs
        return False, "Annual turnover below minimum threshold"
    
    # Location check
    pincode = extract_pincode(business_data['address'])
    if pincode not in SERVICEABLE_BUSINESS_LOCATIONS:
        return False, "Business location not serviceable"
    
    # Business type check
    if business_data['business_type'] in RESTRICTED_CATEGORIES:
        return False, "Business type not eligible for loan"
    
    return True, "Eligible for post-qualification"
```

---

### ✅ MSME Pre-Qualification Criteria Checklist

Before proceeding to Post-Qualification, verify:

- [ ] Director's Aadhaar and PAN extracted and validated
- [ ] Director's Aadhaar verified from government API
- [ ] GSTIN verified and active from GST portal
- [ ] Business name matches across documents
- [ ] Business operational for minimum 1 year
- [ ] Annual turnover meets minimum threshold
- [ ] Business location is serviceable
- [ ] Business type is eligible
- [ ] No major GST compliance issues

**→ If ALL checks pass, proceed to Post-Qualification**  
**→ If ANY check fails, REJECT application**

---

### 🎯 Stage 2: Post-Qualification (Business Financial Analysis)

**⚠️ Only proceed if Pre-Qualification is complete!**

#### Step 1: GST Returns Analysis
**API:** `POST /api/msme/gst/uploads/`

**Input:** GST returns data (GSTR-1, GSTR-3B for 12 months)

**Output:**
- Compliance score
- Revenue trends (MoM, QoQ growth)
- Filing regularity
- Vendor verification
- Tax compliance

---

#### Step 2: Director Personal Banking
**API:** `POST /api/msme/director-banking/analyze-json/`

**Input:** Director's personal bank statement (6-12 months)

**Output:**
- Director's financial health (38 features)
- Personal income stability
- Personal EMI obligations
- Savings pattern

---

#### Step 3: Business Banking Analysis
**API:** `POST /api/msme/business-banking/analyze-json/`

**Input:** Business current account transactions (12 months)

**Output:**
- Cash flow health score
- Inflow/outflow ratio
- Average bank balance
- Working capital adequacy
- Bounce rate

---

#### Step 4: Final MSME Credit Score
**API:** `POST /api/msme/applications/quick_score/`

**Input:** Combined data from GST, Director Banking, Business Banking

**Output:**
- Final business credit score (300-900)
- Risk tier
- DSCR (Debt Service Coverage Ratio)
- Approval recommendation
- Recommended loan amount
- Interest rate
- Conditions

---

## Implementation Workflow

### Consumer Loan - Complete Flow

```python
# STAGE 1: PRE-QUALIFICATION
def pre_qualification_consumer(customer_data):
    # Step 1: KYC OCR
    aadhaar_data = call_kyc_ocr_api(customer_data['aadhaar_image'], 'AADHAAR_FRONT')
    pan_data = call_kyc_ocr_api(customer_data['pan_image'], 'PAN')
    
    # Step 2: Aadhaar Validation
    aadhaar_valid = validate_aadhaar_external(aadhaar_data['aadhaar_number'])
    if not aadhaar_valid:
        return "REJECTED: Aadhaar validation failed"
    
    # Step 3: Name Match
    name_match = verify_name_match(aadhaar_data['name'], pan_data['name'])
    if not name_match:
        return "REJECTED: Name mismatch"
    
    # Step 4: Face Match
    face_match = verify_face_match(customer_data['selfie'], aadhaar_data)
    if not face_match:
        return "REJECTED: Face verification failed"
    
    # Step 5: Basic Eligibility
    eligible, message = check_basic_eligibility(aadhaar_data)
    if not eligible:
        return f"REJECTED: {message}"
    
    return "PRE-QUALIFIED: Proceed to post-qualification"

# STAGE 2: POST-QUALIFICATION
def post_qualification_consumer(customer_data):
    # Only call if pre-qualification passed
    
    # Step 1: Bank Statement
    bank_features = call_bank_statement_api(customer_data['bank_statement'])
    
    # Step 2: ITR
    itr_features = call_itr_api(customer_data['itr_data'])
    
    # Step 3: Credit Report
    credit_features = call_credit_report_api(customer_data['credit_report'])
    
    # Step 4: Assets (optional)
    asset_features = call_asset_api(customer_data['assets']) if 'assets' in customer_data else {}
    
    # Step 5: Final Score
    final_score = call_credit_scoring_api({
        'bank_statement_features': bank_features,
        'itr_features': itr_features,
        'credit_report_features': credit_features,
        'asset_features': asset_features,
        'loan_amount': customer_data['loan_amount'],
        'loan_tenure_months': customer_data['tenure']
    })
    
    return final_score
```

### MSME Loan - Complete Flow

```python
# STAGE 1: PRE-QUALIFICATION
def pre_qualification_msme(business_data):
    # Step 1: Director KYC
    director_aadhaar = call_kyc_ocr_api(business_data['director_aadhaar'], 'AADHAAR_FRONT')
    director_pan = call_kyc_ocr_api(business_data['director_pan'], 'PAN')
    
    # Step 2: Director Aadhaar Validation
    aadhaar_valid = validate_aadhaar_external(director_aadhaar['aadhaar_number'])
    if not aadhaar_valid:
        return "REJECTED: Director Aadhaar validation failed"
    
    # Step 3: GSTIN Verification
    gstin_data = verify_gstin_external(business_data['gstin'])
    if gstin_data['status'] != 'Active':
        return "REJECTED: GSTIN not active"
    
    # Step 4: Business Name Match
    name_match = verify_business_name_match(gstin_data['legal_name'], business_data['business_name'])
    if not name_match:
        return "REJECTED: Business name mismatch"
    
    # Step 5: Business Eligibility
    eligible, message = check_msme_eligibility(gstin_data, business_data)
    if not eligible:
        return f"REJECTED: {message}"
    
    return "PRE-QUALIFIED: Proceed to post-qualification"

# STAGE 2: POST-QUALIFICATION
def post_qualification_msme(business_data):
    # Only call if pre-qualification passed
    
    # Step 1: GST Analysis
    gst_analysis = call_gst_analysis_api(business_data['gst_returns'])
    
    # Step 2: Director Banking
    director_banking = call_director_banking_api(business_data['director_bank_statement'])
    
    # Step 3: Business Banking
    business_banking = call_business_banking_api(business_data['business_bank_statement'])
    
    # Step 4: Final MSME Score
    final_score = call_msme_scoring_api({
        'gst_data': gst_analysis,
        'director_data': director_banking,
        'bank_data': business_banking,
        'loan_amount': business_data['loan_amount'],
        'loan_tenure_months': business_data['tenure']
    })
    
    return final_score
```

---

## External APIs Required

### For Pre-Qualification:

1. **Aadhaar Verification API**
   - UIDAI eKYC
   - Digio
   - Signzy
   - IDfy

2. **Face Matching API**
   - AWS Rekognition
   - Azure Face API
   - Google Cloud Vision
   - Custom ML model

3. **GSTIN Verification API**
   - GST Network API
   - MasterGST
   - ClearTax
   - Signzy

---

## Summary

| Stage | Purpose | APIs Used | Decision Point |
|-------|---------|-----------|----------------|
| **Pre-Qualification** | Identity validation, basic eligibility | KYC OCR + External validation APIs | PASS/REJECT |
| **Post-Qualification** | Financial analysis, credit scoring | Stori Analysis APIs | Credit Score + Loan Decision |

**Key Rule:** Never call Post-Qualification APIs without completing Pre-Qualification checks!

---

**Last Updated:** January 17, 2026  
**Status:** Complete Workflow Documentation

