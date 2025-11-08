"""
Test Railway PostgreSQL Connection
Kiểm tra kết nối với Railway DB với nhiều scenarios
"""

import os
import psycopg2
from dotenv import load_dotenv
from urllib.parse import urlparse
import time

load_dotenv()

print("=" * 70)
print("🧪 Testing Railway PostgreSQL Connection")
print("=" * 70)
print()

# Test 1: Parse DATABASE_URL
print("TEST 1: Parse DATABASE_URL")
print("-" * 70)

database_url = os.getenv("DATABASE_URL")
if database_url:
    print(f"✅ DATABASE_URL found")
    print(f"   URL: {database_url[:50]}...")
    
    parsed = urlparse(database_url)
    db_params = {
        'host': parsed.hostname,
        'port': parsed.port or 5432,
        'dbname': parsed.path[1:] if parsed.path else 'railway',
        'user': parsed.username,
        'password': '***' if parsed.password else None
    }
    
    print(f"\n📊 Parsed parameters:")
    print(f"   Host: {db_params['host']}")
    print(f"   Port: {db_params['port']}")
    print(f"   Database: {db_params['dbname']}")
    print(f"   User: {db_params['user']}")
    print(f"   Password: {'SET' if db_params['password'] != 'None' else 'NOT SET'}")
    
    # Check if using Railway internal hostname
    if 'railway.internal' in db_params['host']:
        print(f"\n⚠️  WARNING: Using Railway internal hostname: {db_params['host']}")
        print(f"   This ONLY works from within Railway network!")
        print(f"   For external access, use PUBLIC hostname from Railway dashboard")
else:
    print("❌ DATABASE_URL not found")
    print("   Checking individual env vars...")
    
    db_params = {
        'host': os.getenv('PGHOST') or os.getenv('DB_HOST'),
        'port': int(os.getenv('PGPORT') or os.getenv('DB_PORT') or 5432),
        'dbname': os.getenv('PGDATABASE') or os.getenv('DB_NAME'),
        'user': os.getenv('PGUSER') or os.getenv('DB_USER'),
        'password': os.getenv('PGPASSWORD') or os.getenv('DB_PASSWORD')
    }
    
    print(f"\n📊 Environment variables:")
    print(f"   Host: {db_params['host']}")
    print(f"   Port: {db_params['port']}")
    print(f"   Database: {db_params['dbname']}")
    print(f"   User: {db_params['user']}")
    print(f"   Password: {'SET' if db_params['password'] else 'NOT SET'}")

print()

# Test 2: Connection attempts with different strategies
print("TEST 2: Connection Attempts")
print("-" * 70)

strategies = [
    {
        "name": "Default (no timeout, no SSL)",
        "params": {}
    },
    {
        "name": "With connect_timeout=10",
        "params": {"connect_timeout": 10}
    },
    {
        "name": "With connect_timeout=30",
        "params": {"connect_timeout": 30}
    },
    {
        "name": "With sslmode=require",
        "params": {"sslmode": "require"}
    },
    {
        "name": "With sslmode=prefer",
        "params": {"sslmode": "prefer"}
    },
    {
        "name": "Best practice (timeout + SSL)",
        "params": {"connect_timeout": 30, "sslmode": "prefer"}
    }
]

for i, strategy in enumerate(strategies, 1):
    print(f"\nStrategy {i}: {strategy['name']}")
    print(f"Parameters: {strategy['params']}")
    
    start_time = time.time()
    
    try:
        # Prepare connection params
        conn_params = {
            'host': db_params['host'],
            'port': db_params['port'],
            'dbname': db_params['dbname'],
            'user': db_params['user'],
            'password': parsed.password if database_url else db_params['password']
        }
        
        # Add strategy params
        conn_params.update(strategy['params'])
        
        print(f"Connecting to {conn_params['host']}:{conn_params['port']}...")
        
        # Try to connect
        conn = psycopg2.connect(**conn_params)
        
        elapsed = time.time() - start_time
        print(f"✅ SUCCESS! Connected in {elapsed:.2f}s")
        
        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"   PostgreSQL version: {version[:60]}...")
        
        cursor.close()
        conn.close()
        
        print(f"   ✅ This strategy works!")
        break  # Stop after first success
        
    except psycopg2.OperationalError as e:
        elapsed = time.time() - start_time
        print(f"❌ FAILED after {elapsed:.2f}s")
        print(f"   Error: {str(e)[:100]}...")
        
        # Check for common issues
        if "timeout" in str(e).lower():
            print(f"   💡 Hint: Connection timeout - may need longer timeout or network issue")
        elif "refused" in str(e).lower():
            print(f"   💡 Hint: Connection refused - check host/port or firewall")
        elif "authentication" in str(e).lower():
            print(f"   💡 Hint: Authentication failed - check username/password")
        elif "ssl" in str(e).lower():
            print(f"   💡 Hint: SSL issue - try different sslmode")
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ UNEXPECTED ERROR after {elapsed:.2f}s")
        print(f"   Error: {str(e)}")

print()
print("=" * 70)
print("📋 Summary & Recommendations")
print("=" * 70)

if 'railway.internal' in db_params['host']:
    print("""
⚠️  CRITICAL: Railway Internal Hostname Detected!

The hostname '{host}' is ONLY accessible from within Railway network.
This means:
  ✅ Will work when deployed on Railway
  ❌ Will NOT work from your local machine
  ❌ Will NOT work from external APIs

🔧 SOLUTION:
1. Go to Railway dashboard
2. Find your PostgreSQL service
3. Look for "Public Networking" or "TCP Proxy"
4. Use the PUBLIC hostname (e.g., nozomi.proxy.rlwy.net:26750)
5. Update your .env file with PUBLIC hostname

Example .env:
  DB_HOST=nozomi.proxy.rlwy.net  ← PUBLIC hostname
  DB_PORT=26750                   ← PUBLIC port
  DB_NAME=railway
  DB_USER=postgres
  DB_PASSWORD=your_password
""".format(host=db_params['host']))

else:
    print("""
📡 Using external hostname - should work from anywhere!

If connection still fails:
1. Check firewall settings
2. Verify credentials are correct
3. Try with connect_timeout=30
4. Try with sslmode=prefer
5. Check Railway service is running

Recommended connection params:
  connect_timeout=30
  sslmode=prefer
""")

print()
print("=" * 70)
