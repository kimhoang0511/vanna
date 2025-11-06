#!/usr/bin/env python3
"""
Chi tiết test cache behavior với nhiều cách verify
"""

import requests
import time
import hashlib

HOST = "vanna-production.up.railway.app"
BASE_URL = f"https://{HOST}"
API_KEY = "L8WBBkJndxkbEJkMpCdOPmGc29HfWSTz"

HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def calculate_question_hash(question):
    """Calculate hash như trong QuestionHashCache"""
    question_normalized = question.lower().strip()
    hash_object = hashlib.md5(question_normalized.encode())
    return hash_object.hexdigest()

def test_method_1_timing():
    """Method 1: So sánh thời gian response"""
    print("\n" + "=" * 70)
    print("📊 METHOD 1: Timing Comparison")
    print("=" * 70)
    
    # Use unique question with timestamp to avoid pre-existing cache
    import random
    question = f"SELECT COUNT(*) FROM customers WHERE id > {random.randint(1, 1000)}"
    
    print(f"\nQuestion: {question}")
    print(f"Expected Cache ID: {calculate_question_hash(question)}")
    print()
    
    times = []
    responses = []
    cached_flags = []
    
    for i in range(3):
        print(f"Request {i+1}/3...")
        start = time.time()
        
        try:
            response = requests.get(
                f"{BASE_URL}/api/v0/generate_sql",
                params={"question": question},
                headers=HEADERS,
                timeout=120
            )
            elapsed = time.time() - start
            times.append(elapsed)
            
            if response.status_code == 200:
                data = response.json()
                sql = data.get("text", data.get("sql", "N/A"))
                response_id = data.get("id", "N/A")
                cached = data.get("cached", False)
                cached_flags.append(cached)
                responses.append({
                    "sql": sql,
                    "id": response_id,
                    "time": elapsed,
                    "cached": cached
                })
                cache_status = "CACHED" if cached else "LLM"
                print(f"  ✅ Time: {elapsed:.2f}s | ID: {response_id} | {cache_status}")
            else:
                print(f"  ❌ Failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False
        
        time.sleep(1)
    
    # Analysis
    print("\n" + "-" * 70)
    print("📈 Analysis:")
    print(f"  Request 1: {times[0]:.2f}s (cached={cached_flags[0]})")
    print(f"  Request 2: {times[1]:.2f}s (cached={cached_flags[1]})")
    print(f"  Request 3: {times[2]:.2f}s (cached={cached_flags[2]})")
    
    # Check if requests 2 & 3 are marked as cached OR significantly faster
    if (cached_flags[1] and cached_flags[2]) or (times[1] < times[0] * 0.5 and times[2] < times[0] * 0.5):
        print("\n✅ CACHE WORKING: Requests 2-3 are cached or much faster!")
        return True
    else:
        print("\n❌ CACHE NOT WORKING: Requests not properly cached")
        return False

def test_method_2_response_id():
    """Method 2: Kiểm tra response ID (should be same for same question)"""
    print("\n" + "=" * 70)
    print("🔑 METHOD 2: Response ID Comparison")
    print("=" * 70)
    
    question = "Top 10 customers"
    expected_id = calculate_question_hash(question)
    
    print(f"\nQuestion: {question}")
    print(f"Expected Cache ID: {expected_id}")
    print()
    
    ids = []
    
    for i in range(3):
        print(f"Request {i+1}/3...")
        
        try:
            response = requests.get(
                f"{BASE_URL}/api/v0/generate_sql",
                params={"question": question},
                headers=HEADERS,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                response_id = data.get("id", "N/A")
                ids.append(response_id)
                print(f"  ID: {response_id}")
            else:
                print(f"  ❌ Failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False
        
        time.sleep(1)
    
    # Analysis
    print("\n" + "-" * 70)
    print("📈 Analysis:")
    
    if len(set(ids)) == 1:
        print(f"  ✅ All 3 requests have SAME ID: {ids[0]}")
        if ids[0] == expected_id:
            print(f"  ✅ ID matches expected hash: {expected_id}")
        else:
            print(f"  ⚠️  ID different from expected: {expected_id}")
        print("\n✅ CACHE WORKING: Same question = Same ID!")
        return True
    else:
        print(f"  ❌ IDs are DIFFERENT: {set(ids)}")
        print("\n❌ CACHE NOT WORKING: Same question but different IDs")
        return False

def test_method_3_sql_consistency():
    """Method 3: Kiểm tra SQL output (should be identical)"""
    print("\n" + "=" * 70)
    print("📝 METHOD 3: SQL Output Consistency")
    print("=" * 70)
    
    question = "SELECT * FROM users WHERE active = true"
    
    print(f"\nQuestion: {question}")
    print()
    
    sqls = []
    
    for i in range(3):
        print(f"Request {i+1}/3...")
        
        try:
            response = requests.get(
                f"{BASE_URL}/api/v0/generate_sql",
                params={"question": question},
                headers=HEADERS,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                sql = data.get("text", data.get("sql", "N/A"))
                sqls.append(sql)
                print(f"  SQL: {sql[:80]}...")
            else:
                print(f"  ❌ Failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False
        
        time.sleep(1)
    
    # Analysis
    print("\n" + "-" * 70)
    print("📈 Analysis:")
    
    if len(set(sqls)) == 1:
        print(f"  ✅ All 3 requests return IDENTICAL SQL")
        print(f"  SQL: {sqls[0]}")
        print("\n✅ CACHE WORKING: Cached SQL is being reused!")
        return True
    else:
        print(f"  ❌ SQL outputs are DIFFERENT:")
        for i, sql in enumerate(sqls, 1):
            print(f"    {i}. {sql}")
        print("\n⚠️  Different SQL each time (LLM might generate variations)")
        print("   This could mean cache is NOT working OR LLM is non-deterministic")
        return False

def test_method_4_load_question():
    """Method 4: Test load_question endpoint (trực tiếp lấy từ cache)"""
    print("\n" + "=" * 70)
    print("💾 METHOD 4: Load Question from Cache")
    print("=" * 70)
    
    question = "How many users?"
    
    # Step 1: Generate SQL (should cache it)
    print(f"\nStep 1: Generate SQL for: {question}")
    
    try:
        response1 = requests.get(
            f"{BASE_URL}/api/v0/generate_sql",
            params={"question": question},
            headers=HEADERS,
            timeout=120
        )
        
        if response1.status_code != 200:
            print(f"❌ Failed to generate SQL: {response1.status_code}")
            return False
        
        data1 = response1.json()
        sql1 = data1.get("text", data1.get("sql", "N/A"))
        cache_id = data1.get("id", "N/A")
        
        print(f"  ✅ SQL Generated: {sql1}")
        print(f"  Cache ID: {cache_id}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    time.sleep(2)
    
    # Step 2: Load từ cache với ID
    print(f"\nStep 2: Load from cache with ID: {cache_id}")
    
    try:
        response2 = requests.get(
            f"{BASE_URL}/api/v0/load_question",
            params={"id": cache_id},
            headers=HEADERS,
            timeout=30
        )
        
        if response2.status_code == 200:
            data2 = response2.json()
            cached_sql = data2.get("sql", "N/A")
            cached_question = data2.get("question", "N/A")
            
            print(f"  ✅ Loaded from cache!")
            print(f"  Question: {cached_question}")
            print(f"  SQL: {cached_sql}")
            
            if cached_sql == sql1:
                print("\n✅ CACHE WORKING: Loaded SQL matches original!")
                return True
            else:
                print("\n❌ SQL mismatch!")
                return False
        else:
            print(f"❌ Failed to load: {response2.status_code}")
            print(f"   {response2.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_method_5_different_questions():
    """Method 5: Verify different questions get different cache IDs"""
    print("\n" + "=" * 70)
    print("🔀 METHOD 5: Different Questions Test")
    print("=" * 70)
    
    questions = [
        "SELECT COUNT(*) FROM users",
        "SELECT COUNT(*) FROM orders",
        "SELECT COUNT(*) FROM products"
    ]
    
    print("\nTesting 3 different questions...\n")
    
    ids = []
    
    for i, question in enumerate(questions, 1):
        expected_id = calculate_question_hash(question)
        print(f"{i}. Question: {question}")
        print(f"   Expected ID: {expected_id}")
        
        try:
            response = requests.get(
                f"{BASE_URL}/api/v0/generate_sql",
                params={"question": question},
                headers=HEADERS,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                response_id = data.get("id", "N/A")
                ids.append(response_id)
                print(f"   Response ID: {response_id}")
                
                if response_id == expected_id:
                    print(f"   ✅ ID matches expected hash")
                else:
                    print(f"   ⚠️  ID different from expected")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
        time.sleep(1)
    
    # Analysis
    print("-" * 70)
    print("📈 Analysis:")
    
    if len(set(ids)) == len(questions):
        print(f"  ✅ All {len(questions)} questions have DIFFERENT IDs")
        print("\n✅ CACHE WORKING: Different questions = Different cache keys!")
        return True
    else:
        print(f"  ❌ Some IDs are duplicated: {ids}")
        print("\n❌ CACHE ISSUE: Different questions should have different IDs")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("=" * 70)
    print("🧪 COMPREHENSIVE CACHE TEST SUITE")
    print("=" * 70)
    print(f"Host: {HOST}")
    print("=" * 70)
    
    results = {}
    
    # Run all test methods
    print("\n🎯 Running 5 different test methods...\n")
    
    try:
        results["Method 1: Timing"] = test_method_1_timing()
    except Exception as e:
        print(f"❌ Method 1 failed: {e}")
        results["Method 1: Timing"] = False
    
    try:
        results["Method 2: Response ID"] = test_method_2_response_id()
    except Exception as e:
        print(f"❌ Method 2 failed: {e}")
        results["Method 2: Response ID"] = False
    
    try:
        results["Method 3: SQL Consistency"] = test_method_3_sql_consistency()
    except Exception as e:
        print(f"❌ Method 3 failed: {e}")
        results["Method 3: SQL Consistency"] = False
    
    try:
        results["Method 4: Load Cache"] = test_method_4_load_question()
    except Exception as e:
        print(f"❌ Method 4 failed: {e}")
        results["Method 4: Load Cache"] = False
    
    try:
        results["Method 5: Different Questions"] = test_method_5_different_questions()
    except Exception as e:
        print(f"❌ Method 5 failed: {e}")
        results["Method 5: Different Questions"] = False
    
    # Final summary
    print("\n")
    print("=" * 70)
    print("📊 FINAL SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for method, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {method}")
    
    print("=" * 70)
    print(f"Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Cache is working perfectly!")
    elif passed >= total * 0.6:
        print(f"\n✅ {passed}/{total} tests passed. Cache is mostly working.")
    else:
        print(f"\n❌ Only {passed}/{total} tests passed. Cache may not be working correctly.")
    
    print("=" * 70)
    print()

if __name__ == "__main__":
    main()
