# ⚡ Quick Fix - Railway PostgreSQL Connection Timeout

## 🚨 Vấn đề
App bị **"Attempting to connect to the database..."** mãi không kết nối được khi deploy lên Railway.

## 🎯 Nguyên nhân
1. ❌ Dùng Railway **internal hostname** (`postgres.railway.internal`) - chỉ hoạt động TRONG Railway network
2. ❌ Không có **connect_timeout** - app chờ mãi không timeout
3. ❌ Không có **sslmode** config

## ✅ Giải pháp

### Bước 1: Check config hiện tại
```bash
python check_railway_config.py
```

Nếu thấy `postgres.railway.internal` → Cần đổi sang PUBLIC hostname!

### Bước 2: Lấy Railway PUBLIC hostname

**Cách 1: Railway Dashboard**
1. Vào Railway dashboard
2. Click vào PostgreSQL service
3. Tab "Connect" → "TCP Proxy"
4. Copy hostname + port (ví dụ: `nozomi.proxy.rlwy.net:26750`)

**Cách 2: Railway CLI**
```bash
railway variables
# Tìm PGHOST và PGPORT
```

### Bước 3: Update .env file

```bash
# ❌ SAI (Internal hostname)
DATABASE_URL=postgresql://postgres:pass@postgres.railway.internal:5432/railway

# ✅ ĐÚNG (Public hostname)
DATABASE_URL=postgresql://postgres:pass@nozomi.proxy.rlwy.net:26750/railway

# Hoặc dùng individual vars:
DB_HOST=nozomi.proxy.rlwy.net  # ← Public hostname
DB_PORT=26750                   # ← Public port
DB_NAME=railway
DB_USER=postgres
DB_PASSWORD=your_password_here
```

### Bước 4: Code đã được fix

✅ `flask_main.py` - Added:
- `connect_timeout=30` - Timeout sau 30s thay vì chờ mãi
- `sslmode='prefer'` - Support SSL cho Railway
- Warning messages cho railway.internal hostname
- Better error messages

✅ `postgres_cache.py` - Added:
- Default timeout và SSL cho connection pool

### Bước 5: Test connection
```bash
# Test connection với các strategies khác nhau
python test_railway_connection.py
```

Expected output:
```
Strategy 6: Best practice (timeout + SSL)
Connecting to nozomi.proxy.rlwy.net:26750...
✅ SUCCESS! Connected in 2.34s
   PostgreSQL version: PostgreSQL 15.x...
   ✅ This strategy works!
```

### Bước 6: Run app
```bash
python flask_main.py
```

Expected output:
```
🔗 Connecting to PostgreSQL: nozomi.proxy.rlwy.net:26750/railway (timeout: 30s)...
✅ Database connected successfully!
✅ PostgreSQL cache initialized: nozomi.proxy.rlwy.net:26750/railway
```

## 📋 Checklist

- [ ] Run `python check_railway_config.py`
- [ ] Get PUBLIC hostname from Railway dashboard
- [ ] Update `.env` with PUBLIC hostname
- [ ] Verify no `.railway.internal` in config
- [ ] Run `python test_railway_connection.py`
- [ ] Connection should succeed in < 5 seconds
- [ ] Run `python flask_main.py`
- [ ] App should connect successfully
- [ ] Test API: `curl http://localhost:8000/api/v0/cache_stats`

## 🎯 Key Points

### ❌ Internal Hostname (WRONG)
```
postgres.railway.internal:5432
```
- ✅ Works: Inside Railway network only
- ❌ Fails: Local machine, external APIs

### ✅ Public Hostname (CORRECT)
```
nozomi.proxy.rlwy.net:26750
```
- ✅ Works: Everywhere (local, Railway, external)
- ✅ Access: TCP Proxy enabled

## 🐛 Troubleshooting

### Still hanging?
```bash
# Check if using internal hostname
python check_railway_config.py
```

### Timeout after 30s?
- ✅ Good! At least it times out now (not hanging forever)
- Check if hostname is correct
- Check if Railway service is running
- Check firewall/network

### Connection refused?
- Check host:port are correct
- Check Railway TCP Proxy is enabled
- Verify service is running

### Authentication failed?
- Check username/password
- Check they match Railway credentials

## 📝 Files Modified

1. ✅ `flask_main.py` - Added timeout + SSL + better errors
2. ✅ `postgres_cache.py` - Added default timeout + SSL
3. ✅ `check_railway_config.py` - New: Quick config checker
4. ✅ `test_railway_connection.py` - New: Connection tester
5. ✅ `RAILWAY_CONNECTION_ISSUE.md` - Full documentation

## 🚀 Deploy to Railway

After fixing locally:
```bash
git add .
git commit -m "Fix: Add connection timeout and SSL for Railway PostgreSQL"
git push
```

Railway will auto-deploy. Check logs:
```bash
railway logs
```

Should see:
```
✅ Database connected successfully!
✅ Server is ready!
```

## 💡 Pro Tip

Monitor connection in production:
```bash
# Check cache stats (includes pool health)
curl https://your-app.railway.app/api/v0/cache_stats

# Should show:
{
  "connection_pool": {
    "health": "healthy",
    "available": 10
  }
}
```

---

**Tóm lại: Đổi từ internal hostname sang public hostname + add timeout + SSL = FIXED! 🎉**
