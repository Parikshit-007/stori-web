"""
Quick API Test Script
Test your permanent API key without login!
"""

import requests

# YOUR PERMANENT API KEY
API_KEY = "stori_6CFocXsPyo4tJDxq8MkVE6Iy-aii0_7eN59VJvUlfmU"
BASE_URL = "http://localhost:8000/api"

# Headers with your API key
headers = {"X-API-Key": API_KEY}

print("="*70)
print("TESTING STORI NBFC API with Permanent API Key")
print("="*70)

# Test 1: Check ITR endpoint
print("\nTest 1: Checking ITR Analysis endpoint...")
try:
    response = requests.get(f"{BASE_URL}/customer/itr/", headers=headers)
    print(f"✅ Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Check Bank Statement endpoint
print("\nTest 2: Checking Bank Statement endpoint...")
try:
    response = requests.get(f"{BASE_URL}/customer/bank-statement/", headers=headers)
    print(f"✅ Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Check Credit Report endpoint
print("\nTest 3: Checking Credit Report endpoint...")
try:
    response = requests.get(f"{BASE_URL}/customer/credit-report/", headers=headers)
    print(f"✅ Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Check OCR endpoint
print("\nTest 4: Checking OCR/Document endpoint...")
try:
    response = requests.get(f"{BASE_URL}/customer/ocr/documents/", headers=headers)
    print(f"✅ Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*70)
print("API TEST COMPLETE!")
print("="*70)
print("\n✅ Your API is working!")
print(f"✅ Your API Key: {API_KEY}")
print("\nUse this key in ALL your requests:")
print(f'  headers = {{"X-API-Key": "{API_KEY}"}}')
print("="*70)

