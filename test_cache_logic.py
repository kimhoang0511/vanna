#!/usr/bin/env python3
"""
Test cache logic locally without needing full server
"""

from vanna_cache_fix import QuestionHashCache, PersistentQuestionCache
import hashlib

def calculate_question_hash(question):
    """Calculate hash như trong QuestionHashCache"""
    question_normalized = question.lower().strip()
    hash_object = hashlib.md5(question_normalized.encode())
    return hash_object.hexdigest()

def test_memory_cache():
    """Test in-memory cache"""
    print("\n" + "=" * 70)
    print("🧪 TEST 1: QuestionHashCache (In-Memory)")
    print("=" * 70)
    
    cache = QuestionHashCache()
    question = "How many users?"
    cache_id = cache.generate_id(question=question)
    expected_id = calculate_question_hash(question)
    
    print(f"\nQuestion: {question}")
    print(f"Generated ID: {cache_id}")
    print(f"Expected ID:  {expected_id}")
    
    if cache_id == expected_id:
        print("✅ ID generation works correctly!")
    else:
        print("❌ ID generation mismatch!")
        return False
    
    # Test set/get
    cache.set(cache_id, "question", question)
    cache.set(cache_id, "sql", "SELECT COUNT(*) FROM users;")
    
    retrieved_question = cache.get(cache_id, "question")
    retrieved_sql = cache.get(cache_id, "sql")
    
    print(f"\nStored question: {question}")
    print(f"Retrieved question: {retrieved_question}")
    print(f"Retrieved SQL: {retrieved_sql}")
    
    if retrieved_question == question and retrieved_sql == "SELECT COUNT(*) FROM users;":
        print("✅ Cache set/get works correctly!")
        return True
    else:
        print("❌ Cache set/get failed!")
        return False

def test_persistent_cache():
    """Test persistent cache"""
    print("\n" + "=" * 70)
    print("🧪 TEST 2: PersistentQuestionCache (File-based)")
    print("=" * 70)
    
    import os
    test_file = "test_persistent_cache.json"
    
    # Clean up old test file
    if os.path.exists(test_file):
        os.remove(test_file)
    
    # Test 1: Save to cache
    print("\n📝 Step 1: Save to cache...")
    cache1 = PersistentQuestionCache(cache_file=test_file)
    
    question = "Top 10 customers"
    cache_id = cache1.generate_id(question=question)
    
    cache1.set(cache_id, "question", question)
    cache1.set(cache_id, "sql", "SELECT * FROM customers ORDER BY revenue DESC LIMIT 10;")
    
    print(f"✅ Saved: {question} -> {cache_id}")
    print(f"   File exists: {os.path.exists(test_file)}")
    
    # Test 2: Load from cache (new instance)
    print("\n📖 Step 2: Load from cache (new instance)...")
    cache2 = PersistentQuestionCache(cache_file=test_file)
    
    retrieved_question = cache2.get(cache_id, "question")
    retrieved_sql = cache2.get(cache_id, "sql")
    
    print(f"Retrieved question: {retrieved_question}")
    print(f"Retrieved SQL: {retrieved_sql}")
    
    # Clean up
    if os.path.exists(test_file):
        os.remove(test_file)
    
    if retrieved_question == question and retrieved_sql:
        print("\n✅ Persistent cache works! Data survives across instances!")
        return True
    else:
        print("\n❌ Persistent cache failed!")
        return False

def test_load_question_logic():
    """Test the load_question endpoint logic"""
    print("\n" + "=" * 70)
    print("🧪 TEST 3: Load Question Endpoint Logic")
    print("=" * 70)
    
    cache = QuestionHashCache()
    
    # Simulate generate_sql: save to cache
    question = "How many users?"
    cache_id = cache.generate_id(question=question)
    sql = "SELECT COUNT(*) FROM users;"
    
    print(f"\n📝 Step 1: Generate SQL (save to cache)")
    print(f"   Question: {question}")
    print(f"   SQL: {sql}")
    print(f"   Cache ID: {cache_id}")
    
    cache.set(cache_id, "question", question)
    cache.set(cache_id, "sql", sql)
    
    # Simulate load_question: retrieve from cache
    print(f"\n📖 Step 2: Load from cache by ID")
    cached_question = cache.get(cache_id, "question")
    cached_sql = cache.get(cache_id, "sql")
    
    print(f"   Cached Question: {cached_question}")
    print(f"   Cached SQL: {cached_sql}")
    
    if cached_question and cached_sql:
        print("\n✅ Load question logic works!")
        
        # This is what the endpoint should return
        response = {
            "type": "question_cache",
            "id": cache_id,
            "question": cached_question,
            "sql": cached_sql
        }
        print(f"\n📤 Expected response:")
        import json
        print(json.dumps(response, indent=2))
        return True
    else:
        print("\n❌ Load question logic failed!")
        print(f"   cached_question = {cached_question}")
        print(f"   cached_sql = {cached_sql}")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("=" * 70)
    print("🔬 CACHE LOGIC VERIFICATION")
    print("=" * 70)
    
    results = {}
    
    try:
        results["Memory Cache"] = test_memory_cache()
    except Exception as e:
        print(f"❌ Memory cache test failed: {e}")
        results["Memory Cache"] = False
    
    try:
        results["Persistent Cache"] = test_persistent_cache()
    except Exception as e:
        print(f"❌ Persistent cache test failed: {e}")
        results["Persistent Cache"] = False
    
    try:
        results["Load Question Logic"] = test_load_question_logic()
    except Exception as e:
        print(f"❌ Load question logic test failed: {e}")
        results["Load Question Logic"] = False
    
    # Summary
    print("\n")
    print("=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print("=" * 70)
    print(f"Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Cache logic is correct!")
    else:
        print(f"\n❌ {total - passed} test(s) failed!")
    
    print("=" * 70)
    print()

if __name__ == "__main__":
    main()
