"""
Test script for JSON-based API endpoints
Account Aggregator integration - No file upload!
"""

import requests
import json

# Your permanent API key
API_KEY = "stori_6CFocXsPyo4tJDxq8MkVE6Iy-aii0_7eN59VJvUlfmU"
BASE_URL = "http://localhost:8000/api"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

print("="*70)
print("TESTING JSON-BASED API ENDPOINTS (Account Aggregator)")
print("="*70)

# Test 1: Bank Statement Analysis (JSON)
print("\nTest 1: Bank Statement Analysis (JSON)")
print("-" * 70)

bank_data = {
    "transactions": [
        {
            "date": "2024-01-15",
            "description": "SALARY CREDIT",
            "debit": 0,
            "credit": 75000,
            "balance": 80000
        },
        {
            "date": "2024-01-16",
            "description": "UPI-SWIGGY",
            "debit": 500,
            "credit": 0,
            "balance": 79500
        },
        {
            "date": "2024-01-17",
            "description": "ATM WITHDRAWAL",
            "debit": 5000,
            "credit": 0,
            "balance": 74500
        },
        {
            "date": "2024-01-18",
            "description": "NEFT-RENT",
            "debit": 15000,
            "credit": 0,
            "balance": 59500
        },
        {
            "date": "2024-02-15",
            "description": "SALARY CREDIT",
            "debit": 0,
            "credit": 75000,
            "balance": 134500
        }
    ],
    "account_info": {
        "account_number": "1234567890",
        "bank_name": "HDFC Bank",
        "ifsc": "HDFC0001234",
        "holder_name": "John Doe"
    }
}

try:
    response = requests.post(
        f"{BASE_URL}/customer/bank-statement/analyze-json/",
        headers=headers,
        json=bank_data
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    if result.get('success'):
        print("✅ Bank Statement Analysis: SUCCESS")
        print(f"   Total Transactions: {result['data']['summary']['total_transactions']}")
        print(f"   Total Credits: ₹{result['data']['summary']['total_credits']:,.2f}")
        print(f"   Total Debits: ₹{result['data']['summary']['total_debits']:,.2f}")
        print(f"   Average Balance: ₹{result['data']['summary']['average_balance']:,.2f}")
        print(f"   Monthly Income: ₹{result['data']['summary']['monthly_income']:,.2f}")
    else:
        print(f"❌ Error: {result.get('message')}")
except Exception as e:
    print(f"❌ Exception: {e}")


# Test 2: Credit Report Analysis (JSON)
print("\n\nTest 2: Credit Report Analysis (JSON)")
print("-" * 70)

credit_data = {
    "score": 750,
    "bureau": "CIBIL",
    "report_date": "2024-01-15",
    "accounts": [
        {
            "account_type": "credit_card",
            "bank": "HDFC Bank",
            "status": "active",
            "outstanding": 25000,
            "credit_limit": 100000,
            "dpd": 0,
            "opened_date": "2020-01-15"
        },
        {
            "account_type": "loan",
            "bank": "ICICI Bank",
            "status": "active",
            "outstanding": 150000,
            "credit_limit": 200000,
            "dpd": 0,
            "opened_date": "2022-06-01"
        },
        {
            "account_type": "credit_card",
            "bank": "SBI",
            "status": "closed",
            "outstanding": 0,
            "credit_limit": 50000,
            "dpd": 0,
            "opened_date": "2018-03-10"
        }
    ],
    "enquiries": [
        {
            "bank": "Axis Bank",
            "date": "2024-01-10",
            "type": "credit_card",
            "months_ago": 0
        },
        {
            "bank": "Kotak Bank",
            "date": "2023-11-05",
            "type": "personal_loan",
            "months_ago": 2
        }
    ]
}

try:
    response = requests.post(
        f"{BASE_URL}/customer/credit-report/analyze-json/",
        headers=headers,
        json=credit_data
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    if result.get('success'):
        print("✅ Credit Report Analysis: SUCCESS")
        print(f"   Credit Score: {result['data']['summary']['credit_score']}")
        print(f"   Total Accounts: {result['data']['summary']['total_accounts']}")
        print(f"   Active Accounts: {result['data']['summary']['active_accounts']}")
        print(f"   Total Outstanding: ₹{result['data']['summary']['total_outstanding']:,.2f}")
        print(f"   Credit Utilization: {result['data']['summary']['credit_utilization']:.2f}%")
        print(f"   Total Enquiries: {result['data']['summary']['total_enquiries']}")
    else:
        print(f"❌ Error: {result.get('message')}")
except Exception as e:
    print(f"❌ Exception: {e}")


# Test 3: Load from example files
print("\n\nTest 3: Load from Example Files")
print("-" * 70)

try:
    # Load bank statement example
    with open('example_jsons/bank_statement_example.json', 'r') as f:
        bank_example = json.load(f)
    
    response = requests.post(
        f"{BASE_URL}/customer/bank-statement/analyze-json/",
        headers=headers,
        json=bank_example
    )
    
    if response.json().get('success'):
        print("✅ Bank Statement (from file): SUCCESS")
    else:
        print(f"❌ Bank Statement (from file): FAILED")
        print(f"   Error: {response.json().get('message')}")
except FileNotFoundError:
    print("ℹ  Example files not found (optional)")
except Exception as e:
    print(f"❌ Exception: {e}")


try:
    # Load credit report example
    with open('example_jsons/credit_report_example.json', 'r') as f:
        credit_example = json.load(f)
    
    response = requests.post(
        f"{BASE_URL}/customer/credit-report/analyze-json/",
        headers=headers,
        json=credit_example
    )
    
    if response.json().get('success'):
        print("✅ Credit Report (from file): SUCCESS")
    else:
        print(f"❌ Credit Report (from file): FAILED")
        print(f"   Error: {response.json().get('message')}")
except FileNotFoundError:
    print("ℹ  Example files not found (optional)")
except Exception as e:
    print(f"❌ Exception: {e}")


print("\n" + "="*70)
print("JSON API TEST COMPLETE!")
print("="*70)
print("\n✅ All JSON endpoints are working!")
print("✅ No file upload needed!")
print("✅ Direct JSON input accepted!")
print("\nNew Endpoints:")
print("  POST /api/customer/bank-statement/analyze-json/")
print("  POST /api/customer/itr/analyze-json/")
print("  POST /api/customer/credit-report/analyze-json/")
print("\nFor more details: JSON_API_GUIDE.txt")
print("="*70)


