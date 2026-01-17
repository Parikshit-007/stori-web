# KYC Document OCR API Setup

## Overview
KYC Document OCR API endpoint for extracting structured data from PAN and Aadhaar documents using PaddleOCR.

## Endpoint
**POST** `/api/kyc/document-ocr/`

## Authentication
Uses existing X-API-Key header authentication (same as other APIs).

## Installation Requirements

Install the following Python packages:

```bash
pip install paddlepaddle paddleocr opencv-python numpy
```

For CPU-only systems:
```bash
pip install paddlepaddle-cpu paddleocr opencv-python numpy
```

## Request Format

**Content-Type:** `multipart/form-data`

**Headers:**
```
X-API-Key: <your-api-key>
```

**Form Data:**
- `document_type`: One of `PAN`, `AADHAAR_FRONT`, `AADHAAR_BACK`, `OTHER`
- `document_image`: Image file (jpg/png/jpeg)

## Response Format

### Success Response (200 OK)
```json
{
    "success": true,
    "message": "Document processed successfully",
    "data": {
        // PAN fields
        "pan_number": "ABCDE1234F",
        "dob": "01/01/1990",
        "name": "JOHN DOE",
        
        // OR Aadhaar Front fields
        "aadhaar_number": "1234 5678 9012",
        "gender": "MALE",
        "dob": "01/01/1990",
        "yob": "1990",
        "name": "JOHN DOE",
        
        // OR Aadhaar Back fields
        "address": "123 Main Street\nCity, State\nPIN: 123456"
    },
    "metadata": {
        "document_type": "PAN",
        "ocr_text_length": 150,
        "processed_at": "2026-01-16T10:30:00Z"
    }
}
```

### Error Response (400/500)
```json
{
    "success": false,
    "message": "Error description"
}
```

## Example Usage

### cURL
```bash
curl -X POST \
  http://localhost:8000/api/kyc/document-ocr/ \
  -H "X-API-Key: stori_xxxxxxxxxxxxx" \
  -F "document_type=PAN" \
  -F "document_image=@/path/to/pan_card.jpg"
```

### Python
```python
import requests

url = "http://localhost:8000/api/kyc/document-ocr/"
headers = {"X-API-Key": "stori_xxxxxxxxxxxxx"}

files = {
    "document_image": open("pan_card.jpg", "rb")
}
data = {
    "document_type": "PAN"
}

response = requests.post(url, headers=headers, files=files, data=data)
print(response.json())
```

## Features

1. **OpenCV Preprocessing:**
   - Grayscale conversion
   - Denoising (bilateral filter)
   - Adaptive thresholding
   - Optional resizing for large images

2. **PaddleOCR Integration:**
   - Singleton pattern (initialized once, reused)
   - English language support
   - GPU/CPU compatible

3. **Field Extraction:**
   - **PAN:** pan_number, dob, name
   - **Aadhaar Front:** aadhaar_number, gender, dob/yob, name
   - **Aadhaar Back:** address (multiline)

4. **Regex-based Extraction:**
   - PAN: `[A-Z]{5}[0-9]{4}[A-Z]`
   - Aadhaar: `\d{4}\s?\d{4}\s?\d{4}`
   - DOB: `\d{2}/\d{2}/\d{4}`

## Files Created

1. `apps/customer/ocr_analysis/kyc_ocr_views.py` - Main OCR view and extraction logic
2. Updated `apps/customer/ocr_analysis/urls.py` - Added document-ocr route
3. Updated `config/urls.py` - Added /api/kyc/ route

## Notes

- PaddleOCR is initialized once on first request (singleton pattern)
- Image preprocessing improves OCR accuracy
- Field extraction uses regex patterns optimized for Indian documents
- Works for both consumer and MSME use cases

