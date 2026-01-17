# API Documentation Web Interface

## Overview

A simple web-based interface for browsing Stori API documentation. The interface provides separate sections for Consumer and MSME credit scoring APIs with detailed information about endpoints, authentication, request/response formats, and usage examples.

## Features

- **Clean, Simple Design** - Easy to navigate documentation
- **Two Main Sections:**
  - Consumer Credit Scoring APIs
  - MSME Credit Scoring APIs
- **Detailed API Pages** - Each API has its own dedicated page with:
  - Authentication requirements
  - Sample JSON input
  - Sample JSON output
  - Field descriptions
  - Usage notes
  - Error codes

## URL Structure

### Main Documentation Page
```
https://mycfo.club/stori/api/documentation/
```

### Authentication Guide
```
https://mycfo.club/stori/api/documentation/authentication/
```

### Consumer APIs
```
/api/documentation/consumer/bank-statement/    - Bank Statement Analysis
/api/documentation/consumer/itr/               - ITR Analysis
/api/documentation/consumer/credit-report/     - Credit Report Analysis
/api/documentation/consumer/asset/             - Asset Analysis
/api/documentation/consumer/credit-score/      - Final Credit Score
```

### MSME APIs
```
/api/documentation/msme/gst/                   - GST Analysis
/api/documentation/msme/director-banking/      - Director Personal Banking
/api/documentation/msme/business-banking/      - Business Banking
/api/documentation/msme/credit-score/          - MSME Final Credit Score
```

## Local Development

### Access Locally
```
http://localhost:8000/api/documentation/
```

### Run Development Server
```bash
cd stori_backend
python manage.py runserver
```

Then visit: `http://localhost:8000/api/documentation/`

## How to Use

1. **Start at Main Page** - View overview of all available APIs
2. **Click on Any API** - Opens dedicated page with complete details
3. **Copy Sample JSON** - Use sample inputs to test APIs
4. **Follow Authentication Guide** - Learn how to add API keys to requests

## Navigation

- Each API page has a "Back to Documentation" link
- Authentication guide is accessible from main page and all API pages
- Clean URL structure for easy bookmarking

## Files Structure

```
stori_backend/
├── api_docs/
│   ├── static/
│   │   └── api_docs/
│   │       └── style.css              # Simple CSS styling
│   ├── templates/
│   │   └── api_docs/
│   │       ├── index.html             # Main documentation page
│   │       ├── authentication.html    # Authentication guide
│   │       ├── consumer/              # Consumer API pages
│   │       │   ├── bank_statement.html
│   │       │   ├── itr.html
│   │       │   ├── credit_report.html
│   │       │   ├── asset.html
│   │       │   └── credit_score.html
│   │       └── msme/                  # MSME API pages
│   │           ├── gst.html
│   │           ├── director_banking.html
│   │           ├── business_banking.html
│   │           └── credit_score.html
│   ├── views.py                       # View functions
│   └── urls.py                        # URL routing
```

## Features of Each API Page

### All API Pages Include:

1. **Overview** - What the API does
2. **Endpoint** - Complete URL with HTTP method
3. **Authentication** - Required headers
4. **Request Body** - Sample input JSON with all fields
5. **Request Parameters Table** - Field descriptions
6. **Response** - Sample output JSON
7. **Key Metrics** - Important features/fields explained
8. **Usage Notes** - Best practices and tips
9. **Error Codes** - Common errors and solutions (where applicable)

## Design Philosophy

- **Simple and Clean** - No fancy animations or complex UI
- **Easy to Read** - Clear typography and spacing
- **Code-Focused** - JSON samples are prominent and copyable
- **Technical** - Focused on developers, no marketing content
- **Fast Loading** - Minimal CSS, no JavaScript required

## Deployment

The documentation is automatically available when the Django app is running. No additional setup needed beyond adding `api_docs` to `INSTALLED_APPS` and including the URLs.

## Production URL

```
Production: https://mycfo.club/stori/api/documentation/
```

All API endpoints in the documentation use the production base URL for easy copy-paste.

---

*Last Updated: January 17, 2026*

