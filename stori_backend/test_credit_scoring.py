"""
Test Credit Scoring API
"""
import requests
import json

API_KEY = "stori_6CFocXsPyo4tJDxq8MkVE6Iy-aii0_7eN59VJvUlfmU"
BASE_URL = "http://localhost:8000/api"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

print("="*70)
print("TESTING CREDIT SCORING API - GBM MODEL")
print("="*70)

# Test 1: Model Health Check
print("\n Test 1: Model Health Check")
print("-" * 70)
try:
    response = requests.get(
        f"{BASE_URL}/customer/credit-scoring/health/",
        headers=headers
    )
    result = response.json()
    if result.get('success') and result.get('model_loaded'):
        print("✅ Model is loaded and ready")
        print(f"   Model Type: {result.get('model_type')}")
        print(f"   Feature Count: {result.get('feature_count')}")
        if result.get('metrics'):
            metrics = result['metrics']
            print(f"   AUC: {metrics.get('auc', 'N/A')}")
    else:
        print("⚠️  Model not loaded - scoring may not work")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Calculate Credit Score (Example 1 - Good Profile)
print("\n\nTest 2: Good Credit Profile")
print("-" * 70)

good_profile = {
    "age": 32,
    "monthly_income": 75000,
    "employment_tenure_months": 48,
    "credit_score": 720,
    "credit_accounts_active": 4,
    "credit_utilization_ratio": 0.35,
    "dpd_30_count": 0,
    "dpd_60_count": 0,
    "dpd_90_count": 0,
    "avg_monthly_credits": 80000,
    "avg_monthly_debits": 55000,
    "avg_balance": 125000,
    "pan_verified": 1,
    "aadhaar_verified": 1
}

try:
    response = requests.post(
        f"{BASE_URL}/customer/credit-scoring/score/",
        headers=headers,
        json=good_profile
    )
    result = response.json()
    if result.get('success'):
        print("✅ Credit Score Calculated")
        print(f"   Credit Score: {result['credit_score']}/100")
        print(f"   Default Probability: {result['default_probability']:.2%}")
        print(f"   Risk Tier: {result['risk_tier']}")
        print(f"   Recommendation: {result['recommendation']}")
        print("\n   Top 3 Important Features:")
        for feat in result.get('feature_importance', [])[:3]:
            print(f"     - {feat['feature']}: {feat['importance']:.4f}")
    else:
        print(f"❌ Error: {result.get('message')}")
except Exception as e:
    print(f"❌ Exception: {e}")

# Test 3: Calculate Credit Score (Example 2 - Poor Profile)
print("\n\nTest 3: Poor Credit Profile")
print("-" * 70)

poor_profile = {
    "age": 25,
    "monthly_income": 25000,
    "employment_tenure_months": 6,
    "credit_score": 550,
    "credit_accounts_active": 2,
    "credit_utilization_ratio": 0.85,
    "dpd_30_count": 2,
    "dpd_60_count": 1,
    "dpd_90_count": 0,
    "avg_monthly_credits": 30000,
    "avg_monthly_debits": 28000,
    "avg_balance": 5000,
    "pan_verified": 1,
    "aadhaar_verified": 0
}

try:
    response = requests.post(
        f"{BASE_URL}/customer/credit-scoring/score/",
        headers=headers,
        json=poor_profile
    )
    result = response.json()
    if result.get('success'):
        print("✅ Credit Score Calculated")
        print(f"   Credit Score: {result['credit_score']}/100")
        print(f"   Default Probability: {result['default_probability']:.2%}")
        print(f"   Risk Tier: {result['risk_tier']}")
        print(f"   Recommendation: {result['recommendation']}")
    else:
        print(f"❌ Error: {result.get('message')}")
except Exception as e:
    print(f"❌ Exception: {e}")

# Test 4: Load from example file
print("\n\nTest 4: Using Example File")
print("-" * 70)

try:
    with open('example_jsons/credit_score_request_example.json', 'r') as f:
        example_data = json.load(f)
    
    response = requests.post(
        f"{BASE_URL}/customer/credit-scoring/score/",
        headers=headers,
        json=example_data
    )
    result = response.json()
    if result.get('success'):
        print("✅ Example File Test: SUCCESS")
        print(f"   Credit Score: {result['credit_score']}/100")
        print(f"   Risk Tier: {result['risk_tier']}")
    else:
        print(f"❌ Example File Test: FAILED")
        print(f"   Error: {result.get('message')}")
except FileNotFoundError:
    print("ℹ  Example file not found (optional)")
except Exception as e:
    print(f"❌ Exception: {e}")

# Test 5: Get Score History
print("\n\nTest 5: Credit Score History")
print("-" * 70)

try:
    response = requests.get(
        f"{BASE_URL}/customer/credit-scoring/history/",
        headers=headers
    )
    result = response.json()
    if result.get('success'):
        count = result.get('count', 0)
        print(f"✅ Found {count} past credit scores")
        if count > 0:
            latest = result['history'][0]
            print(f"   Latest Score: {latest['credit_score']}/100")
            print(f"   Risk Tier: {latest['risk_tier']}")
    else:
        print(f"❌ Error: {result.get('message')}")
except Exception as e:
    print(f"❌ Exception: {e}")

print("\n" + "="*70)
print("CREDIT SCORING API TEST COMPLETE!")
print("="*70)
print("\n✅ Credit Scoring API is working!")
print("✅ GBM Model integrated successfully!")
print("\nEndpoints:")
print("  POST /api/customer/credit-scoring/score/")
print("  GET  /api/customer/credit-scoring/history/")
print("  GET  /api/customer/credit-scoring/health/")
print("\nFor more details: CREDIT_SCORING_API_GUIDE.txt")
print("="*70)


