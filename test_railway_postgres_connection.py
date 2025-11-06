"""
Test PostgreSQL Connection trên Railway
Kiểm tra xem connection có hoạt động với Railway variables không
"""

import requests
import json

BASE_URL = "https://vanna-production.up.railway.app"
API_KEY = "L8WBBkJndxkbEJkMpCdOPmGc29HfWSTz"

def test_cache_stats():
    """Test cache stats endpoint để verify PostgreSQL connection"""
    print("=" * 70)
    print("🧪 Testing Railway PostgreSQL Connection")
    print("=" * 70)
    print()
    
    print("📊 Endpoint: /api/v0/cache_stats")
    print(f"🌐 URL: {BASE_URL}/api/v0/cache_stats")
    print()
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v0/cache_stats",
            headers={"X-API-Key": API_KEY},
            timeout=30
        )
        
        print(f"📥 Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            print("📊 Response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print()
            
            # Check for errors
            if "error" in data.get("stats", {}):
                error_msg = data["stats"]["error"]
                print(f"❌ ERROR FOUND: {error_msg}")
                print()
                
                if "connection pool exhausted" in error_msg:
                    print("🔴 PostgreSQL chưa được add hoặc chưa connect đúng!")
                    print()
                    print("Checklist:")
                    print("  1. ✅ PostgreSQL service đã được add chưa?")
                    print("  2. ✅ CACHE_BACKEND=postgres đã được set chưa?")
                    print("  3. ✅ Railway đã redeploy chưa?")
                    print("  4. ✅ Check logs: railway logs")
                    print()
                    return False
                else:
                    print(f"🔴 Unexpected error: {error_msg}")
                    return False
            else:
                total = data["stats"].get("total_entries", 0)
                print(f"✅ PostgreSQL Connection Working!")
                print(f"   Total cache entries: {total}")
                print()
                return True
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout!")
        print("   Server có thể đang restart hoặc không phản hồi")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        print("   Kiểm tra xem Railway deployment có đang chạy không")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_simple_cache():
    """Test generate_sql để xem có cache vào PostgreSQL không"""
    print("=" * 70)
    print("🧪 Testing Cache Functionality")
    print("=" * 70)
    print()
    
    question = "How many customers are there?"
    
    print(f"📝 Question: {question}")
    print()
    
    try:
        # Request 1: Should generate SQL via LLM
        print("🔄 Request 1: Generate SQL (should use LLM)...")
        response1 = requests.get(
            f"{BASE_URL}/api/v0/generate_sql",
            params={"question": question},
            headers={"X-API-Key": API_KEY},
            timeout=120
        )
        
        if response1.status_code != 200:
            print(f"❌ Request failed: {response1.status_code}")
            return False
        
        data1 = response1.json()
        cached1 = data1.get("cached", False)
        id1 = data1.get("id", "N/A")
        
        print(f"   ID: {id1}")
        print(f"   Cached: {cached1}")
        print(f"   SQL: {data1.get('text', 'N/A')[:100]}...")
        print()
        
        # Request 2: Should be cached
        print("🔄 Request 2: Same question (should use cache)...")
        response2 = requests.get(
            f"{BASE_URL}/api/v0/generate_sql",
            params={"question": question},
            headers={"X-API-Key": API_KEY},
            timeout=120
        )
        
        if response2.status_code != 200:
            print(f"❌ Request failed: {response2.status_code}")
            return False
        
        data2 = response2.json()
        cached2 = data2.get("cached", False)
        id2 = data2.get("id", "N/A")
        
        print(f"   ID: {id2}")
        print(f"   Cached: {cached2}")
        print()
        
        # Verify
        if id1 == id2:
            print("✅ Same ID - Cache logic working!")
        else:
            print(f"❌ Different IDs - Cache logic broken!")
            print(f"   ID1: {id1}")
            print(f"   ID2: {id2}")
            return False
        
        if cached2:
            print("✅ Cache working - Request 2 was cached!")
            return True
        else:
            print("⚠️  Cache not working - Request 2 should be cached but wasn't")
            print("   Check logs to see why cache isn't being used")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print()
    print("🚀 Railway PostgreSQL Connection Test")
    print("=" * 70)
    print()
    
    # Test 1: Cache stats (verify connection)
    stats_ok = test_cache_stats()
    print()
    
    if not stats_ok:
        print("=" * 70)
        print("🔴 FAILED: PostgreSQL connection not working")
        print("=" * 70)
        print()
        print("Next steps:")
        print("1. Add PostgreSQL database on Railway")
        print("2. Set CACHE_BACKEND=postgres in Main service")
        print("3. Wait for redeploy (~2 min)")
        print("4. Run this test again")
        print()
        return
    
    # Test 2: Cache functionality
    cache_ok = test_simple_cache()
    print()
    
    if cache_ok:
        print("=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print()
        print("PostgreSQL cache is working correctly! 🎉")
        print()
    else:
        print("=" * 70)
        print("⚠️  Cache connection OK but functionality needs debugging")
        print("=" * 70)
        print()
        print("Check Railway logs:")
        print("  railway logs --follow")
        print()


if __name__ == "__main__":
    main()
