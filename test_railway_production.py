"""
Test script cho Vietnamese Vanna API trên Railway Production
URL: https://vanna-production.up.railway.app

Usage:
    export API_KEY="your-api-key"
    python test_railway_production.py
"""

import requests
import json
import time
import sys
import os

# Railway Production URL
BASE_URL = "https://vanna-production.up.railway.app"
API_KEY = os.getenv("API_KEY", "YOUR_API_KEY_HERE")  # Fallback for testing

def print_test(name):
    print(f"\n{'='*70}")
    print(f"TEST: {name}")
    print('='*70)

def print_response(response):
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        return data
    except:
        print(f"Response: {response.text}")
        return None

def test_health():
    """Test health check endpoint"""
    print_test("1. Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        data = print_response(response)
        
        if response.status_code == 200 and data:
            print(f"✅ Service: {data.get('service')}")
            print(f"✅ Status: {data.get('status')}")
            print(f"✅ Environment: {data.get('environment')}")
            print(f"✅ Initialized: {data.get('initialized')}")
            return True
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_root():
    """Test root endpoint"""
    print_test("2. Root Endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        data = print_response(response)
        
        if response.status_code == 200 and data:
            print(f"✅ Service: {data.get('service')}")
            print(f"✅ Version: {data.get('version')}")
            print(f"✅ Docs: {BASE_URL}{data.get('docs')}")
            return True
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_init():
    """Initialize Vanna"""
    print_test("3. Initialize Vanna")
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    # Empty body - will use env variables
    data = {}
    
    try:
        response = requests.post(
            f"{BASE_URL}/init",
            json=data,
            headers=headers,
            timeout=30
        )
        
        result = print_response(response)
        
        if response.status_code == 200 and result and result.get('success'):
            print(f"✅ Model: {result['data'].get('model')}")
            print(f"✅ Dialect: {result['data'].get('dialect')}")
            return True
        else:
            print(f"❌ Failed to initialize")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_connect():
    """Test connecting to PostgreSQL database"""
    print_test("4. Connect to PostgreSQL")
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    db_config = {
        "host": "nozomi.proxy.rlwy.net",
        "port": 26750,
        "database": "railway",
        "user": "postgres",
        "password": "aLBazSQAKvyCNllyngDjoiTdMIjHLTDC"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/connect/postgres", json=db_config, headers=headers, timeout=120)
        result = print_response(response)
        
        if response.status_code == 200 and result and result.get('success'):
            print("✅ Connected to PostgreSQL")
            return True
        else:
            print("❌ Connection failed")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_generate_sql():
    """Generate SQL from Vietnamese questions"""
    print_test("5. Generate SQL (Vietnamese)") 
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    question = "Có bao nhiêu giao dịch?"
    
    data = {
        "question": question,
        "allow_llm_to_see_data": False
    }
    
    print(f"❓ Question: {question}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/generate_sql",
            json=data,
            headers=headers,
            timeout=60
        )
        
        result = print_response(response)
        
        if response.status_code == 200 and result and result.get('success'):
            sql = result['data'].get('sql', '')
            print(f"\n✅ Generated SQL: {sql}")
            return True
        else:
            print(f"❌ Failed to generate SQL")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    print("=" * 70)
    print("🚂 VIETNAMESE VANNA API - RAILWAY PRODUCTION TEST")
    print("=" * 70)
    print(f"🌐 Base URL: {BASE_URL}")
    print(f"🔐 API Key: {API_KEY[:10]}...")
    print(f"📝 Docs: {BASE_URL}/docs")
    print("=" * 70)
    
    # Check if server is reachable
    print("\n⏳ Checking server availability...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Server is reachable")
        else:
            print(f"⚠️  Server returned status: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot reach server: {str(e)}")
        print("\nPlease check Railway deployment")
        sys.exit(1)
    
    results = {}
    
    # Run tests
    results['root'] = test_root()
    results['health'] = test_health()
    
    if not results['health']:
        print("\n❌ Health check failed")
        sys.exit(1)
    
    results['init'] = test_init()
    
    if results['init']:
        results['connect'] = test_connect()
        
        if results['connect']:
            # Wait a bit
            print("\n⏳ Waiting 3 seconds...")
            time.sleep(3)
            
            results['generate_sql'] = test_generate_sql()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "=" * 70)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 70)
    
    if passed == total:
        print("\n🎉 All tests passed! Railway deployment is working!")
        print(f"\n🌐 Your API: {BASE_URL}")
        print(f"📝 Docs: {BASE_URL}/docs")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
