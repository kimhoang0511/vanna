"""
Quick Check: Railway Database Configuration
Kiểm tra nhanh config DATABASE_URL có đúng không
"""

import os
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

print("=" * 70)
print("🔍 Railway Database Configuration Check")
print("=" * 70)
print()

# Check DATABASE_URL
database_url = os.getenv("DATABASE_URL")

if database_url:
    print("✅ DATABASE_URL found")
    print()
    
    # Parse URL
    parsed = urlparse(database_url)
    
    host = parsed.hostname
    port = parsed.port or 5432
    dbname = parsed.path[1:] if parsed.path else 'railway'
    user = parsed.username
    
    print(f"📊 Connection Details:")
    print(f"   Host:     {host}")
    print(f"   Port:     {port}")
    print(f"   Database: {dbname}")
    print(f"   User:     {user}")
    print(f"   Password: {'SET' if parsed.password else 'NOT SET'}")
    print()
    
    # Check hostname type
    if host and 'railway.internal' in host:
        print("❌ PROBLEM FOUND!")
        print("=" * 70)
        print()
        print("🚨 You are using Railway INTERNAL hostname:")
        print(f"   {host}")
        print()
        print("This hostname ONLY works from within Railway network!")
        print()
        print("✅ SOLUTION:")
        print("1. Go to Railway dashboard")
        print("2. Select your PostgreSQL service")
        print("3. Click 'Connect' tab")
        print("4. Look for 'TCP Proxy' section")
        print("5. Copy the PUBLIC hostname (e.g., nozomi.proxy.rlwy.net)")
        print("6. Copy the PUBLIC port (e.g., 26750)")
        print()
        print("Update your .env file:")
        print()
        print("# Option 1: Update DATABASE_URL")
        print(f"DATABASE_URL=postgresql://{user}:<password>@<public-host>:<public-port>/{dbname}")
        print()
        print("# Option 2: Use individual variables")
        print("DB_HOST=<public-host>     # e.g., nozomi.proxy.rlwy.net")
        print("DB_PORT=<public-port>     # e.g., 26750")
        print(f"DB_NAME={dbname}")
        print(f"DB_USER={user}")
        print("DB_PASSWORD=<password>")
        print()
        
    elif host and 'proxy.rlwy.net' in host:
        print("✅ LOOKS GOOD!")
        print("=" * 70)
        print()
        print("You are using Railway PUBLIC hostname (TCP Proxy):")
        print(f"   {host}:{port}")
        print()
        print("This should work from:")
        print("  ✅ Your local machine")
        print("  ✅ Railway deployment")
        print("  ✅ External APIs")
        print()
        print("If connection still fails, check:")
        print("  1. Railway PostgreSQL service is running")
        print("  2. Credentials (user/password) are correct")
        print("  3. Database name is correct")
        print()
        
    else:
        print("ℹ️  Using custom hostname:")
        print(f"   {host}:{port}")
        print()
        print("Make sure this hostname is accessible from your network.")
        print()

else:
    print("⚠️  DATABASE_URL not found")
    print()
    print("Checking individual environment variables...")
    print()
    
    db_host = os.getenv('PGHOST') or os.getenv('DB_HOST')
    db_port = os.getenv('PGPORT') or os.getenv('DB_PORT')
    db_name = os.getenv('PGDATABASE') or os.getenv('DB_NAME')
    db_user = os.getenv('PGUSER') or os.getenv('DB_USER')
    db_password = os.getenv('PGPASSWORD') or os.getenv('DB_PASSWORD')
    
    print(f"DB_HOST: {db_host if db_host else '❌ NOT SET'}")
    print(f"DB_PORT: {db_port if db_port else '❌ NOT SET'}")
    print(f"DB_NAME: {db_name if db_name else '❌ NOT SET'}")
    print(f"DB_USER: {db_user if db_user else '❌ NOT SET'}")
    print(f"DB_PASSWORD: {'SET' if db_password else '❌ NOT SET'}")
    print()
    
    if db_host and 'railway.internal' in db_host:
        print("❌ PROBLEM: Using Railway internal hostname!")
        print("   Change to PUBLIC hostname from Railway dashboard.")
        print()

print("=" * 70)
print()
print("💡 Quick Test:")
print("   python test_railway_connection.py")
print()
print("=" * 70)
