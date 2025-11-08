"""
Test script để verify fix cho connection pool exhausted bug
"""

import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

def test_connection_pool():
    """Test nhiều requests liên tiếp để kiểm tra connection pool"""
    
    base_url = os.getenv("API_URL", "http://localhost:8000")
    
    print("=" * 70)
    print("🧪 Testing PostgreSQL Cache Connection Pool")
    print("=" * 70)
    print()
    
    # Test 1: Check cache stats before
    print("📊 Checking cache stats before test...")
    try:
        response = requests.get(f"{base_url}/api/v0/cache_stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Cache Stats:")
            print(f"   - Total entries: {stats.get('stats', {}).get('total_entries', 0)}")
            pool = stats.get('stats', {}).get('connection_pool', {})
            if pool:
                print(f"   - Connection Pool:")
                print(f"     • Max: {pool.get('max_connections')}")
                print(f"     • Available: {pool.get('available')}")
                print(f"     • In use: {pool.get('in_use')}")
                print(f"     • Health: {pool.get('health')}")
        else:
            print(f"⚠️  Could not get cache stats: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Error: {e}")
    
    print()
    print("=" * 70)
    print("🚀 Running multiple API requests...")
    print("=" * 70)
    print()
    
    # Test 2: Gọi API nhiều lần liên tiếp
    num_requests = 20
    questions = [
        "Tổng doanh thu là bao nhiêu",
        "Top 10 khách hàng",
        "Danh sách sản phẩm",
        "Số lượng đơn hàng",
        "Doanh thu theo tháng"
    ]
    
    success_count = 0
    error_count = 0
    
    for i in range(num_requests):
        question = questions[i % len(questions)] + f" {i}"
        
        try:
            print(f"Request {i+1}/{num_requests}: {question[:40]}...", end=" ")
            
            response = requests.get(
                f"{base_url}/api/v0/generate_sql",
                params={"question": question},
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅")
                success_count += 1
            else:
                print(f"❌ Status: {response.status_code}")
                error_count += 1
                
        except Exception as e:
            print(f"❌ Error: {e}")
            error_count += 1
        
        # Small delay giữa các requests
        time.sleep(0.2)
    
    print()
    print("=" * 70)
    print("📊 Test Results")
    print("=" * 70)
    print(f"Total requests: {num_requests}")
    print(f"✅ Success: {success_count}")
    print(f"❌ Errors: {error_count}")
    
    if error_count == 0:
        print()
        print("🎉 ALL TESTS PASSED! Connection pool working correctly!")
    else:
        print()
        print("⚠️  Some requests failed. Check server logs for details.")
    
    # Test 3: Check cache stats after
    print()
    print("=" * 70)
    print("📊 Checking cache stats after test...")
    print("=" * 70)
    
    try:
        response = requests.get(f"{base_url}/api/v0/cache_stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Cache Stats:")
            print(f"   - Total entries: {stats.get('stats', {}).get('total_entries', 0)}")
            pool = stats.get('stats', {}).get('connection_pool', {})
            if pool:
                print(f"   - Connection Pool:")
                print(f"     • Max: {pool.get('max_connections')}")
                print(f"     • Available: {pool.get('available')}")
                print(f"     • In use: {pool.get('in_use')}")
                print(f"     • Health: {pool.get('health')}")
                
                if pool.get('health') == 'exhausted':
                    print()
                    print("⚠️  WARNING: Connection pool is exhausted!")
                    print("   This indicates the bug is NOT fixed yet.")
                elif pool.get('available', 0) > 0:
                    print()
                    print("✅ Connection pool is healthy!")
                    print("   Connections are being properly returned to pool.")
        else:
            print(f"⚠️  Could not get cache stats: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Error: {e}")
    
    print()
    print("=" * 70)


if __name__ == "__main__":
    print()
    print("⚠️  Make sure your Flask server is running first!")
    print("   python flask_main.py")
    print()
    input("Press Enter to start test...")
    print()
    
    test_connection_pool()
