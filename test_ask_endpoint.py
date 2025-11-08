"""
Test script for /api/v0/ask endpoint
Tests both GET and POST methods
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
ASK_ENDPOINT = f"{BASE_URL}/api/v0/ask"

# Test cases
TEST_QUESTIONS = [
    "Có bao nhiêu khách hàng?",
    "Top 10 khách hàng có doanh thu cao nhất",
    "Doanh thu theo tháng trong năm 2024",
    "Tổng số đơn hàng trong tháng 10",
]


def test_get_method():
    """Test GET method with query parameters"""
    print("=" * 70)
    print("TEST 1: GET Method with query parameters")
    print("=" * 70)
    
    for question in TEST_QUESTIONS[:2]:  # Test first 2 questions
        print(f"\n📝 Question: {question}")
        
        try:
            response = requests.get(
                ASK_ENDPOINT,
                params={"question": question},
                timeout=30
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success: {data.get('success')}")
                print(f"SQL: {data.get('sql', 'N/A')[:100]}...")
                print(f"Rows: {data.get('rows_count', 0)}")
                
                # Show first 2 rows of data
                if data.get('data'):
                    print(f"Sample data: {json.dumps(data['data'][:2], indent=2, ensure_ascii=False)}")
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
        
        time.sleep(1)  # Avoid rate limiting


def test_post_method():
    """Test POST method with JSON body"""
    print("\n" + "=" * 70)
    print("TEST 2: POST Method with JSON body")
    print("=" * 70)
    
    for question in TEST_QUESTIONS[2:]:  # Test last 2 questions
        print(f"\n📝 Question: {question}")
        
        try:
            response = requests.post(
                ASK_ENDPOINT,
                headers={"Content-Type": "application/json"},
                json={
                    "question": question,
                    "allow_llm_to_see_data": False
                },
                timeout=30
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success: {data.get('success')}")
                print(f"SQL: {data.get('sql', 'N/A')[:100]}...")
                print(f"Rows: {data.get('rows_count', 0)}")
                print(f"Cache ID: {data.get('cache_id', 'N/A')}")
                
                # Show first 2 rows of data
                if data.get('data'):
                    print(f"Sample data: {json.dumps(data['data'][:2], indent=2, ensure_ascii=False)}")
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
        
        time.sleep(1)


def test_error_handling():
    """Test error handling"""
    print("\n" + "=" * 70)
    print("TEST 3: Error Handling")
    print("=" * 70)
    
    # Test 1: Missing question
    print("\n📝 Test: Missing question parameter")
    try:
        response = requests.get(ASK_ENDPOINT, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test 2: Empty question
    print("\n📝 Test: Empty question")
    try:
        response = requests.get(
            ASK_ENDPOINT,
            params={"question": ""},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")


def test_cache():
    """Test caching functionality"""
    print("\n" + "=" * 70)
    print("TEST 4: Cache Functionality")
    print("=" * 70)
    
    question = "Có bao nhiêu khách hàng?"
    
    # First call - should be cache MISS
    print(f"\n📝 First call (cache MISS): {question}")
    start_time = time.time()
    try:
        response1 = requests.get(
            ASK_ENDPOINT,
            params={"question": question},
            timeout=30
        )
        duration1 = time.time() - start_time
        
        if response1.status_code == 200:
            data1 = response1.json()
            print(f"✅ Success")
            print(f"Duration: {duration1:.2f}s")
            print(f"Cache ID: {data1.get('cache_id')}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    time.sleep(1)
    
    # Second call - should be cache HIT
    print(f"\n📝 Second call (cache HIT): {question}")
    start_time = time.time()
    try:
        response2 = requests.get(
            ASK_ENDPOINT,
            params={"question": question},
            timeout=30
        )
        duration2 = time.time() - start_time
        
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"✅ Success")
            print(f"Duration: {duration2:.2f}s")
            print(f"Cache ID: {data2.get('cache_id')}")
            
            # Compare durations
            if duration2 < duration1:
                speedup = (duration1 - duration2) / duration1 * 100
                print(f"🚀 Cache speedup: {speedup:.1f}% faster")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")


def test_with_allow_llm_to_see_data():
    """Test with allow_llm_to_see_data parameter"""
    print("\n" + "=" * 70)
    print("TEST 5: With allow_llm_to_see_data=true")
    print("=" * 70)
    
    question = "Top 5 sản phẩm bán chạy nhất"
    
    print(f"\n📝 Question: {question}")
    try:
        response = requests.post(
            ASK_ENDPOINT,
            headers={"Content-Type": "application/json"},
            json={
                "question": question,
                "allow_llm_to_see_data": True
            },
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data.get('success')}")
            print(f"SQL: {data.get('sql', 'N/A')}")
            print(f"Rows: {data.get('rows_count', 0)}")
            
            if data.get('data'):
                print(f"Data: {json.dumps(data['data'], indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")


def main():
    """Run all tests"""
    print("\n")
    print("🧪 Testing /api/v0/ask endpoint")
    print(f"Base URL: {BASE_URL}")
    print(f"Endpoint: {ASK_ENDPOINT}")
    print("\n")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running\n")
        else:
            print("⚠️  Server health check failed\n")
    except Exception as e:
        print(f"❌ Cannot connect to server: {str(e)}")
        print("Please make sure the server is running:")
        print("  python flask_main.py")
        return
    
    # Run tests
    try:
        test_get_method()
        test_post_method()
        test_error_handling()
        test_cache()
        test_with_allow_llm_to_see_data()
        
        print("\n" + "=" * 70)
        print("✅ All tests completed!")
        print("=" * 70)
        print()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
