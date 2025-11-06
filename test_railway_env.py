"""
Test Railway Environment Variables
Kiểm tra xem Railway đang set những biến gì
"""

import requests
import json

BASE_URL = "https://vanna-production.up.railway.app"
API_KEY = "L8WBBkJndxkbEJkMpCdOPmGc29HfWSTz"

def test_env_debug():
    """Call một endpoint để xem environment variables"""
    print("=" * 70)
    print("🔍 Testing Railway Environment Variables")
    print("=" * 70)
    print()
    
    # Test health check hoặc cache_stats
    print("📊 Testing /api/v0/cache_stats...")
    print()
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v0/cache_stats",
            headers={"X-API-Key": API_KEY},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            print("Response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print()
            
            if "error" in data.get("stats", {}):
                error = data["stats"]["error"]
                print(f"❌ ERROR: {error}")
                print()
                
                # Analyze error
                if "connection refused" in error.lower():
                    print("🔴 PostgreSQL service không thể connect")
                    print()
                    print("Có thể do:")
                    print("1. PostgreSQL service chưa được add")
                    print("2. PostgreSQL service đang khởi động (chưa ready)")
                    print("3. Main service chưa được reference tới PostgreSQL")
                    print("4. Network policy blocking connection")
                    print()
                    
                elif "pool exhausted" in error.lower():
                    print("🔴 Connection pool exhausted")
                    print()
                    print("Nghĩa là code đang cố connect nhưng không có database")
                    print()
                    
            else:
                print("✅ PostgreSQL connection working!")
                print()
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            print()
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout - server không phản hồi")
        print()
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        print()
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print()


def check_logs_instructions():
    """In hướng dẫn check Railway logs"""
    print("=" * 70)
    print("🔍 KIỂM TRA RAILWAY LOGS")
    print("=" * 70)
    print()
    print("Railway logs sẽ cho biết environment variables đang được set:")
    print()
    print("1. Mở Railway Dashboard")
    print("2. Click vào Main Service")
    print("3. Tab 'Deployments' → Click vào deployment mới nhất")
    print("4. Scroll logs và tìm dòng:")
    print()
    print("   🔗 Connecting to PostgreSQL: <host>:<port>/<dbname>...")
    print()
    print("5. Host phải là:")
    print("   ✅ xxx.railway.internal (internal domain)")
    print("   hoặc")
    print("   ✅ xxx.railway.app (public domain)")
    print()
    print("   KHÔNG PHẢI:")
    print("   ❌ localhost")
    print("   ❌ vanna.railway.internal (có thể sai tên)")
    print()
    print("6. Nếu thấy lỗi connection, copy TOÀN BỘ error message")
    print()
    print("=" * 70)
    print()


def check_service_reference():
    """Hướng dẫn check service reference"""
    print("=" * 70)
    print("🔗 KIỂM TRA SERVICE REFERENCE")
    print("=" * 70)
    print()
    print("Cách 1: Check Variables")
    print("-" * 70)
    print("1. Railway Dashboard → Main Service → Tab 'Variables'")
    print("2. Tìm các biến bắt đầu với PG:")
    print()
    print("   Phải có ít nhất 5 biến:")
    print("   ✅ PGHOST")
    print("   ✅ PGPORT")
    print("   ✅ PGDATABASE")
    print("   ✅ PGUSER")
    print("   ✅ PGPASSWORD")
    print()
    print("   Hoặc:")
    print("   ✅ RAILWAY_PRIVATE_DOMAIN")
    print()
    print("   Nếu KHÔNG CÓ → Main service chưa reference PostgreSQL")
    print()
    
    print("Cách 2: Add Reference Manually")
    print("-" * 70)
    print("1. Main Service → Tab 'Settings'")
    print("2. Scroll down → 'Service Variables'")
    print("3. Click 'New Reference'")
    print("4. Chọn PostgreSQL service")
    print("5. Click 'Add Reference'")
    print("6. Đợi redeploy (~2 min)")
    print()
    print("=" * 70)
    print()


def alternative_solution():
    """Giải pháp thay thế"""
    print("=" * 70)
    print("💡 GIẢI PHÁP THAY THẾ")
    print("=" * 70)
    print()
    print("Nếu PostgreSQL quá phức tạp, có thể:")
    print()
    print("Option 1: Dùng File Cache (Đơn giản nhất)")
    print("-" * 70)
    print("1. Main Service → Variables")
    print("2. Xóa hoặc đổi CACHE_BACKEND thành: file")
    print("3. App sẽ dùng vanna_cache.json")
    print("4. Cache vẫn hoạt động nhưng mất khi restart")
    print()
    
    print("Option 2: Dùng External PostgreSQL")
    print("-" * 70)
    print("1. Tạo PostgreSQL ở nơi khác (Supabase, Neon, etc)")
    print("2. Set các biến DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD")
    print("3. Set CACHE_BACKEND=postgres")
    print("4. Code sẽ connect tới external DB")
    print()
    
    print("Option 3: Debug với Railway Support")
    print("-" * 70)
    print("1. Railway Dashboard → Help (?) icon")
    print("2. Open support ticket")
    print("3. Mô tả: 'Cannot connect to PostgreSQL service from main service'")
    print("4. Share deployment logs")
    print()
    print("=" * 70)
    print()


def main():
    print()
    print("🚀 Railway PostgreSQL Connection Debugger")
    print("=" * 70)
    print()
    
    # Test 1: API call to see error
    test_env_debug()
    
    # Instructions
    check_logs_instructions()
    check_service_reference()
    alternative_solution()
    
    print("=" * 70)
    print("📋 CHECKLIST - Làm tuần tự")
    print("=" * 70)
    print()
    print("□ 1. Verify PostgreSQL service tồn tại và status = Active")
    print("□ 2. Check Main service có PG* variables không")
    print("□ 3. Nếu không có → Add Service Reference")
    print("□ 4. Check Railway logs xem host đang connect tới đâu")
    print("□ 5. Copy error message từ logs và share với tôi")
    print()
    print("Hoặc:")
    print("□ Tạm thời dùng file cache (đơn giản hơn)")
    print()
    print("=" * 70)
    print()
    print("Sau khi check xong, hãy share với tôi:")
    print("1. Screenshot Railway services (Main + PostgreSQL)")
    print("2. Copy error từ Railway logs")
    print("3. List của PG* variables trong Main service")
    print()


if __name__ == "__main__":
    main()
