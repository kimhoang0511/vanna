#!/usr/bin/env python3
"""
Test cache behavior - Verify same question returns cached result
"""

import requests
import time

HOST = "vanna-production.up.railway.app"
BASE_URL = f"https://{HOST}"

def test_cache_behavior():
    """Test xem cache có hoạt động không"""
    
    print("=" * 70)
    print("🧪 Testing Cache Behavior")
    print("=" * 70)
    print()
    
    # Question để test (đơn giản để nhanh)
    question = "SELECT COUNT(*) FROM users"
    
    print(f"Question: {question}")
    print()
    
    # Request 1: Lần đầu (should call LLM)
    print("📝 Request 1: First time (should call LLM)...")
    start1 = time.time()
    
    try:
        response1 = requests.get(
            f"{BASE_URL}/api/v0/generate_sql",
            params={"question": question},
            timeout=120
        )
        elapsed1 = time.time() - start1
        
        if response1.status_code == 200:
            data1 = response1.json()
            sql1 = data1.get("text", "N/A")
            print(f"✅ Response 1: {elapsed1:.2f}s")
            print(f"   SQL: {sql1}")
        else:
            print(f"❌ Failed: {response1.status_code}")
            print(f"   {response1.text[:200]}")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    print()
    
    # Wait a bit
    time.sleep(2)
    
    # Request 2: Lần 2 với cùng question (should use cache)
    print("📝 Request 2: Same question (should use cache)...")
    start2 = time.time()
    
    try:
        response2 = requests.get(
            f"{BASE_URL}/api/v0/generate_sql",
            params={"question": question},
            timeout=120
        )
        elapsed2 = time.time() - start2
        
        if response2.status_code == 200:
            data2 = response2.json()
            sql2 = data2.get("text", "N/A")
            print(f"✅ Response 2: {elapsed2:.2f}s")
            print(f"   SQL: {sql2}")
        else:
            print(f"❌ Failed: {response2.status_code}")
            print(f"   {response2.text[:200]}")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    print()
    print("=" * 70)
    print("📊 Cache Analysis")
    print("=" * 70)
    
    # Compare
    if sql1 == sql2:
        print("✅ SQL responses are identical")
    else:
        print("⚠️  SQL responses are different")
        print(f"   SQL 1: {sql1}")
        print(f"   SQL 2: {sql2}")
    
    # Time comparison
    speedup = elapsed1 / elapsed2 if elapsed2 > 0 else 1
    
    print(f"\n⏱️  Time Comparison:")
    print(f"   Request 1: {elapsed1:.2f}s (LLM call)")
    print(f"   Request 2: {elapsed2:.2f}s")
    print(f"   Speedup: {speedup:.2f}x")
    
    if speedup > 2:
        print("\n✅ CACHE WORKING! Request 2 is significantly faster")
    elif speedup > 1.2:
        print("\n✅ Cache might be working (moderately faster)")
    else:
        print("\n❌ CACHE NOT WORKING! Request 2 took same time")
        print("   This means it's calling LLM again instead of using cache")
    
    print()

if __name__ == "__main__":
    test_cache_behavior()
