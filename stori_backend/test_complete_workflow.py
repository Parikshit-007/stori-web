"""
Complete Workflow Test - Account Aggregator to Credit Score
Tests the entire flow:
1. Bank Statement Analysis (JSON)
2. Credit Report Analysis (JSON)
3. Credit Score Calculation (GBM Model)
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/customer"
API_KEY = "stori_6CFocXsPyo4tJDxq8MkVE6Iy-aii0_7eN59VJvUlfmU"

HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def print_separator(title=""):
    print("\n" + "="*80)
    if title:
        print(f"  {title}")
        print("="*80)

def print_json(data, title="Response"):
    print(f"\n{title}:")
    print(json.dumps(data, indent=2, ensure_ascii=False))

def test_bank_statement_analysis():
    """Test 1: Analyze bank statement from Account Aggregator"""
    print_separator("TEST 1: BANK STATEMENT ANALYSIS (JSON)")
    
    url = f"{BASE_URL}/bank-statement/analyze-json/"
    
    # Example: Account Aggregator JSON
    payload = {
        "transactions": [
            {
                "date": "2024-01-15",
                "description": "SALARY CREDIT - TECH COMPANY",
                "debit": 0,
                "credit": 75000,
                "balance": 80000
            },
            {
                "date": "2024-01-16",
                "description": "UPI-SWIGGY-FOOD",
                "debit": 500,
                "credit": 0,
                "balance": 79500
            },
            {
                "date": "2024-01-17",
                "description": "NEFT-RENT PAYMENT",
                "debit": 20000,
                "credit": 0,
                "balance": 59500
            },
            {
                "date": "2024-01-20",
                "description": "ATM WITHDRAWAL",
                "debit": 5000,
                "credit": 0,
                "balance": 54500
            },
            {
                "date": "2024-01-25",
                "description": "UPI-AMAZON-SHOPPING",
                "debit": 3000,
                "credit": 0,
                "balance": 51500
            },
            {
                "date": "2024-02-15",
                "description": "SALARY CREDIT - TECH COMPANY",
                "debit": 0,
                "credit": 75000,
                "balance": 126500
            },
            {
                "date": "2024-02-16",
                "description": "CREDIT CARD BILL",
                "debit": 15000,
                "credit": 0,
                "balance": 111500
            }
        ],
        "account_info": {
            "account_number": "123456789012",
            "bank_name": "HDFC Bank",
            "ifsc": "HDFC0001234",
            "holder_name": "John Doe",
            "account_type": "SAVINGS"
        }
    }
    
    print(f"\n📤 Sending bank statement data...")
    print(f"   Transactions: {len(payload['transactions'])}")
    print(f"   Bank: {payload['account_info']['bank_name']}")
    
    try:
        response = requests.post(url, json=payload, headers=HEADERS)
        response.raise_for_status()
        
        result = response.json()
        print(f"\n✅ SUCCESS! Status: {result.get('status')}")
        
        # Extract banking features for credit scoring
        features = result.get('features', {})
        banking_features = {
            'avg_monthly_credits': features.get('avg_monthly_credits', 0),
            'avg_monthly_debits': features.get('avg_monthly_debits', 0),
            'avg_balance': features.get('avg_balance', 0),
            'monthly_income': features.get('salary_credits', {}).get('avg_salary', 0)
        }
        
        print(f"\n📊 Banking Features Extracted:")
        print(f"   • Average Monthly Credits: ₹{banking_features['avg_monthly_credits']:,.2f}")
        print(f"   • Average Monthly Debits: ₹{banking_features['avg_monthly_debits']:,.2f}")
        print(f"   • Average Balance: ₹{banking_features['avg_balance']:,.2f}")
        print(f"   • Monthly Income: ₹{banking_features['monthly_income']:,.2f}")
        
        return banking_features
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERROR: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def test_credit_report_analysis():
    """Test 2: Analyze credit report from Bureau"""
    print_separator("TEST 2: CREDIT REPORT ANALYSIS (JSON)")
    
    url = f"{BASE_URL}/credit-report/analyze-json/"
    
    # Example: Bureau JSON (CIBIL format)
    payload = {
        "score": 720,
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
                "account_open_date": "2020-06-15"
            },
            {
                "account_type": "credit_card",
                "bank": "ICICI Bank",
                "status": "active",
                "outstanding": 15000,
                "credit_limit": 150000,
                "dpd": 0,
                "account_open_date": "2019-03-20"
            },
            {
                "account_type": "personal_loan",
                "bank": "Axis Bank",
                "status": "active",
                "outstanding": 180000,
                "loan_amount": 200000,
                "dpd": 0,
                "account_open_date": "2023-01-10"
            },
            {
                "account_type": "home_loan",
                "bank": "SBI",
                "status": "active",
                "outstanding": 2500000,
                "loan_amount": 3000000,
                "dpd": 0,
                "account_open_date": "2021-08-01"
            }
        ],
        "enquiries": [
            {
                "bank": "Bajaj Finserv",
                "date": "2024-01-10",
                "type": "credit_card",
                "months_ago": 0
            },
            {
                "bank": "HDFC Bank",
                "date": "2023-11-15",
                "type": "personal_loan",
                "months_ago": 2
            }
        ],
        "delinquency_history": {
            "dpd_30": 0,
            "dpd_60": 0,
            "dpd_90": 0
        }
    }
    
    print(f"\n📤 Sending credit report data...")
    print(f"   Credit Score: {payload['score']}")
    print(f"   Bureau: {payload['bureau']}")
    print(f"   Active Accounts: {len(payload['accounts'])}")
    
    try:
        response = requests.post(url, json=payload, headers=HEADERS)
        response.raise_for_status()
        
        result = response.json()
        print(f"\n✅ SUCCESS! Status: {result.get('status')}")
        
        # Extract credit features for scoring
        features = result.get('features', {})
        credit_features = {
            'credit_score': payload['score'],
            'credit_accounts_active': features.get('active_accounts', 0),
            'credit_utilization_ratio': features.get('credit_utilization', {}).get('overall_utilization', 0),
            'dpd_30_count': payload.get('delinquency_history', {}).get('dpd_30', 0),
            'dpd_60_count': payload.get('delinquency_history', {}).get('dpd_60', 0),
            'dpd_90_count': payload.get('delinquency_history', {}).get('dpd_90', 0)
        }
        
        print(f"\n📊 Credit Features Extracted:")
        print(f"   • Credit Score: {credit_features['credit_score']}")
        print(f"   • Active Accounts: {credit_features['credit_accounts_active']}")
        print(f"   • Credit Utilization: {credit_features['credit_utilization_ratio']:.2%}")
        print(f"   • DPD History: 30d={credit_features['dpd_30_count']}, 60d={credit_features['dpd_60_count']}, 90d={credit_features['dpd_90_count']}")
        
        return credit_features
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERROR: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def test_credit_scoring(banking_features, credit_features):
    """Test 3: Calculate credit score using GBM model"""
    print_separator("TEST 3: CREDIT SCORE CALCULATION (GBM MODEL)")
    
    url = f"{BASE_URL}/credit-scoring/score/"
    
    # Combine all features
    payload = {
        # Demographics
        "age": 32,
        "employment_tenure_months": 48,
        "education_level": 4,  # Graduate
        "employment_type": 3,  # Salaried
        
        # Banking features (from Test 1)
        "monthly_income": banking_features['monthly_income'],
        "avg_monthly_credits": banking_features['avg_monthly_credits'],
        "avg_monthly_debits": banking_features['avg_monthly_debits'],
        "avg_balance": banking_features['avg_balance'],
        
        # Credit features (from Test 2)
        "credit_score": credit_features['credit_score'],
        "credit_accounts_active": credit_features['credit_accounts_active'],
        "credit_utilization_ratio": credit_features['credit_utilization_ratio'],
        "dpd_30_count": credit_features['dpd_30_count'],
        "dpd_60_count": credit_features['dpd_60_count'],
        "dpd_90_count": credit_features['dpd_90_count'],
        
        # Verification flags
        "pan_verified": 1,
        "aadhaar_verified": 1,
        "phone_verified": 1
    }
    
    print(f"\n📤 Sending combined features for scoring...")
    print(f"   Age: {payload['age']} years")
    print(f"   Monthly Income: ₹{payload['monthly_income']:,.2f}")
    print(f"   Credit Score: {payload['credit_score']}")
    print(f"   Active Credit Accounts: {payload['credit_accounts_active']}")
    
    try:
        response = requests.post(url, json=payload, headers=HEADERS)
        response.raise_for_status()
        
        result = response.json()
        print(f"\n✅ SUCCESS! Status: {result.get('status')}")
        
        # Display results
        data = result.get('data', {})
        print(f"\n🎯 FINAL CREDIT SCORE RESULTS:")
        print(f"   ┌─────────────────────────────────────────┐")
        print(f"   │  Credit Score: {data.get('credit_score', 0):.2f}/100          │")
        print(f"   │  Default Probability: {data.get('default_probability', 0):.4f}    │")
        print(f"   └─────────────────────────────────────────┘")
        
        risk_level = data.get('risk_category', 'Unknown')
        recommendation = data.get('recommendation', 'N/A')
        
        print(f"\n   Risk Level: {risk_level}")
        print(f"   Recommendation: {recommendation}")
        
        print(f"\n   📅 Scored At: {data.get('scored_at')}")
        print(f"   🔑 Request ID: {data.get('request_id')}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERROR: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def test_model_health():
    """Test 4: Check model health"""
    print_separator("TEST 4: MODEL HEALTH CHECK")
    
    url = f"{BASE_URL}/credit-scoring/health/"
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        result = response.json()
        print(f"\n✅ Model Status: {result.get('status')}")
        
        if result.get('model_loaded'):
            print(f"   • Model: Loaded ✓")
            print(f"   • Model Type: {result.get('model_info', {}).get('model_type')}")
            print(f"   • Features: {result.get('model_info', {}).get('n_features')}")
        else:
            print(f"   ⚠️  Model not loaded!")
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERROR: {e}")
        return None

def main():
    """Run complete workflow test"""
    print_separator("STORI NBFC - COMPLETE WORKFLOW TEST")
    print("\nThis test simulates the complete flow:")
    print("  Account Aggregator → Analysis → Credit Scoring")
    print("\n⏳ Starting tests...")
    
    # Test model health first
    health = test_model_health()
    if not health or not health.get('model_loaded'):
        print("\n⚠️  WARNING: Model not loaded! Credit scoring may fail.")
        print("   Please check model file at:")
        print("   C:\\Users\\ASUS\\OneDrive\\Desktop\\stori-nbfc\\credit_scoring_pipeline\\consumer\\consumer_model_artifacts\\consumer_credit_model.joblib")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Test 1: Bank Statement
    banking_features = test_bank_statement_analysis()
    if not banking_features:
        print("\n⚠️  Banking analysis failed! Cannot proceed.")
        return
    
    # Test 2: Credit Report
    credit_features = test_credit_report_analysis()
    if not credit_features:
        print("\n⚠️  Credit report analysis failed! Cannot proceed.")
        return
    
    # Test 3: Credit Scoring
    score_result = test_credit_scoring(banking_features, credit_features)
    if not score_result:
        print("\n⚠️  Credit scoring failed!")
        return
    
    # Final summary
    print_separator("🎉 WORKFLOW COMPLETE!")
    print("\n✅ All tests passed successfully!")
    print("\nYour complete NBFC system is working:")
    print("  ✓ Account Aggregator integration (JSON)")
    print("  ✓ Banking analysis")
    print("  ✓ Credit report analysis")
    print("  ✓ Credit scoring (GBM model)")
    print("\n🚀 System is ready for production!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


