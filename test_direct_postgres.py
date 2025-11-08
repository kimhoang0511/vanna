"""
Test PostgreSQL Connection với DATABASE_URL từ Railway
"""
import psycopg2
from urllib.parse import urlparse

# DATABASE_URL from Railway
DATABASE_URL = "postgresql://postgres:aLBazSQAKvyCNllyngDjoiTdMIjHLTDC@postgres.railway.internal:5432/railway"

print("=" * 70)
print("🧪 Testing PostgreSQL Connection")
print("=" * 70)
print()

# Parse URL
print("📊 Parsing DATABASE_URL...")
parsed = urlparse(DATABASE_URL)

db_params = {
    'host': parsed.hostname,
    'port': parsed.port or 5432,
    'dbname': parsed.path[1:],  # Remove leading /
    'user': parsed.username,
    'password': parsed.password
}

print(f"Host:     {db_params['host']}")
print(f"Port:     {db_params['port']}")
print(f"Database: {db_params['dbname']}")
print(f"User:     {db_params['user']}")
print(f"Password: {'*' * len(db_params['password'])}")
print()

# Test connection
print("🔗 Testing connection...")
print()

try:
    conn = psycopg2.connect(**db_params)
    print("✅ Connection successful!")
    print()
    
    # Test query
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"📊 PostgreSQL version:")
    print(f"   {version[:80]}...")
    print()
    
    # Check if vanna_cache table exists
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'vanna_cache'
        );
    """)
    table_exists = cursor.fetchone()[0]
    
    if table_exists:
        print("✅ Table 'vanna_cache' exists!")
        
        # Count entries
        cursor.execute("SELECT COUNT(*) FROM vanna_cache;")
        count = cursor.fetchone()[0]
        print(f"   Total entries: {count}")
        print()
    else:
        print("⚠️  Table 'vanna_cache' does not exist yet")
        print("   (Will be created on first use)")
        print()
    
    cursor.close()
    conn.close()
    
    print("=" * 70)
    print("✅ ALL TESTS PASSED!")
    print("=" * 70)
    print()
    print("PostgreSQL connection is working! 🎉")
    print()
    print("Next steps:")
    print("1. Make sure Railway Main service has these variables:")
    print("   DATABASE_URL = ${{ Postgres.DATABASE_URL }}")
    print("   CACHE_BACKEND = postgres")
    print()
    print("2. Redeploy if needed")
    print()
    print("3. Test API:")
    print("   curl https://vanna-production.up.railway.app/api/v0/cache_stats \\")
    print("     -H 'X-API-Key: L8WBBkJndxkbEJkMpCdOPmGc29HfWSTz'")
    print()
    
except psycopg2.OperationalError as e:
    print(f"❌ Connection failed: {e}")
    print()
    print("Possible causes:")
    print("1. Host 'postgres.railway.internal' only accessible FROM Railway")
    print("   (Cannot connect from local machine)")
    print()
    print("2. If running locally, this is EXPECTED!")
    print()
    print("Solution:")
    print("- This connection string works on Railway deployment")
    print("- Set it in Railway Main service variables")
    print("- Railway will handle internal networking")
    print()
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    print()
