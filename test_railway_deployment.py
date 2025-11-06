#!/usr/bin/env python3
"""
Test script để kiểm tra Railway deployment
"""

import requests
import json
import time
from typing import Dict, Any

# Railway deployment info
HOST = "vanna-production.up.railway.app"
BASE_URL = f"https://{HOST}"
API_KEY = "L8WBBkJndxkbEJkMpCdOPmGc29HfWSTz"

# Headers with API key
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def print_test(name: str, result: bool, message: str = ""):
    """Print test result"""
    status = "✅" if result else "❌"
    print(f"{status} {name}")
    if message:
        print(f"   {message}")
    print()

def test_root():
    """Test root endpoint"""
    print("=" * 70)
    print("Testing Root Endpoint")
    print("=" * 70)
    
    try:
        response = requests.get(BASE_URL, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        success = response.status_code == 200
        print_test("Root Endpoint", success, response.text[:200])
        return success
    except Exception as e:
        print_test("Root Endpoint", False, f"Error: {str(e)}")
        return False

def test_web_ui():
    """Test if web UI is accessible"""
    print("=" * 70)
    print("Testing Web UI")
    print("=" * 70)
    
    try:
        response = requests.get(BASE_URL, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            # Check if HTML content
            is_html = 'html' in response.text.lower()
            print_test("Web UI", is_html, "HTML page loaded")
            return is_html
        else:
            print_test("Web UI", False, f"Status {response.status_code}")
            return False
    except Exception as e:
        print_test("Web UI", False, f"Error: {str(e)}")
        return False

def test_api_config():
    """Test API config endpoint"""
    print("=" * 70)
    print("Testing API Config Endpoint")
    print("=" * 70)
    
    try:
        url = f"{BASE_URL}/api/v0/get_config"
        response = requests.get(url, headers=HEADERS, timeout=30)
        
        print(f"URL: {url}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        success = response.status_code == 200
        if success:
            data = response.json()
            print(f"Config: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        print_test("API Config", success)
        return success
    except Exception as e:
        print_test("API Config", False, f"Error: {str(e)}")
        return False

def test_generate_questions():
    """Test generate questions endpoint"""
    print("=" * 70)
    print("Testing Generate Questions")
    print("=" * 70)
    
    try:
        url = f"{BASE_URL}/api/v0/generate_questions"
        response = requests.get(url, headers=HEADERS, timeout=30)
        
        print(f"URL: {url}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        success = response.status_code == 200
        if success:
            data = response.json()
            print(f"Questions: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        print_test("Generate Questions", success)
        return success
    except Exception as e:
        print_test("Generate Questions", False, f"Error: {str(e)}")
        return False

def test_training_data():
    """Test get training data endpoint"""
    print("=" * 70)
    print("Testing Get Training Data")
    print("=" * 70)
    
    try:
        url = f"{BASE_URL}/api/v0/get_training_data"
        response = requests.get(url, headers=HEADERS, timeout=30)
        
        print(f"URL: {url}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        success = response.status_code == 200
        if success:
            data = response.json()
            print(f"Training Data: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
        
        print_test("Get Training Data", success)
        return success
    except Exception as e:
        print_test("Get Training Data", False, f"Error: {str(e)}")
        return False

def test_generate_sql():
    """Test generate SQL endpoint"""
    print("=" * 70)
    print("Testing Generate SQL")
    print("=" * 70)
    
    try:
        url = f"{BASE_URL}/api/v0/generate_sql"
        params = {"question": "Top 5 khách hàng có doanh thu cao nhất"}
        
        response = requests.get(url, params=params, headers=HEADERS, timeout=60)
        
        print(f"URL: {url}")
        print(f"Question: {params['question']}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        success = response.status_code == 200
        if success:
            data = response.json()
            print(f"SQL: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        print_test("Generate SQL", success)
        return success
    except Exception as e:
        print_test("Generate SQL", False, f"Error: {str(e)}")
        return False

def main():
    """Main test runner"""
    print("\n")
    print("=" * 70)
    print("🧪 Railway Deployment Test")
    print("=" * 70)
    print(f"Host: {HOST}")
    print(f"Base URL: {BASE_URL}")
    print(f"API Key: {API_KEY[:20]}...")
    print("=" * 70)
    print("\n")
    
    results = {}
    
    # Run tests
    results["Root"] = test_root()
    time.sleep(1)
    
    results["Web UI"] = test_web_ui()
    time.sleep(1)
    
    results["API Config"] = test_api_config()
    time.sleep(1)
    
    results["Training Data"] = test_training_data()
    time.sleep(1)
    
    results["Generate Questions"] = test_generate_questions()
    time.sleep(1)
    
    results["Generate SQL"] = test_generate_sql()
    
    # Summary
    print("\n")
    print("=" * 70)
    print("📊 Test Summary")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test}")
    
    print("=" * 70)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check logs above.")
    
    print("=" * 70)
    print("\n")

if __name__ == "__main__":
    main()
