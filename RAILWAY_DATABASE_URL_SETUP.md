# Railway PostgreSQL Setup - Hướng Dẫn Chính Xác ✅

## 🎯 Cách Đúng Để Kết Nối PostgreSQL trên Railway

Railway sử dụng **Variable References** để kết nối giữa các services.

---

## 📋 Setup Steps (3 bước)

### Bước 1: Add PostgreSQL Database

1. Railway Dashboard → Project của bạn
2. Click **"+ New"** → **"Database"** → **"Add PostgreSQL"**
3. Đợi ~30 giây cho Railway provision
4. Verify: PostgreSQL service status = 🟢 Active

---

### Bước 2: Reference PostgreSQL trong Main Service

**QUAN TRỌNG:** Đây là bước mà nhiều người bỏ qua!

1. Click vào **Main Service** (Vanna app)
2. Tab **"Variables"**
3. Click **"New Variable"**
4. Điền:
   ```
   Name:  DATABASE_URL
   Value: ${{ Postgres.DATABASE_URL }}
   ```
   
   **Chú ý:** 
   - `Postgres` là tên của PostgreSQL service (có thể khác nếu bạn đổi tên)
   - Cú pháp: `${{ ServiceName.VariableName }}`
   - Railway sẽ tự động thay thế bằng connection string thật

5. Click **"Add"**

---

### Bước 3: Set CACHE_BACKEND

Trong **Main Service** → Tab **"Variables"**, thêm:

```
Name:  CACHE_BACKEND
Value: postgres
```

Click **"Add"** → Railway sẽ tự động redeploy (~2 phút)

---

## ✅ Verify Setup

### 1. Check Variables

Main Service → Tab "Variables" phải có:

```
DATABASE_URL = ${{ Postgres.DATABASE_URL }}  ← Railway reference
CACHE_BACKEND = postgres
```

### 2. Check Deployment Logs

Main Service → Tab "Deployments" → Click vào deployment mới nhất

Tìm các dòng này trong logs:

```
✅ Using DATABASE_URL for connection...
✅ Connecting to PostgreSQL: xxx.railway.internal:5432/railway...
✅ Database connected successfully!
✅ PostgreSQL cache initialized
```

**KHÔNG ĐƯỢC thấy:**
```
❌ connection refused
❌ connection pool exhausted
```

### 3. Test API

```bash
curl "https://vanna-production.up.railway.app/api/v0/cache_stats" \
  -H "X-API-Key: L8WBBkJndxkbEJkMpCdOPmGc29HfWSTz" | python3 -m json.tool
```

**Expected response:**
```json
{
  "type": "cache_stats",
  "stats": {
    "total_entries": 0,
    "oldest_entry": null,
    "newest_entry": null
  }
}
```

**KHÔNG phải:**
```json
{
  "stats": {
    "error": "connection refused",  ← Lỗi này = chưa setup đúng
    "total_entries": 0
  }
}
```

---

## 🔍 Troubleshooting

### Error: "connection refused"

**Nguyên nhân:** Thiếu variable reference hoặc PostgreSQL service chưa ready

**Fix:**
1. Verify PostgreSQL service status = 🟢 Active
2. Check Main service có `DATABASE_URL = ${{ Postgres.DATABASE_URL }}`
3. Redeploy Main service

---

### Error: "ENV names can not be blank"

**Nguyên nhân:** Dockerfile parse error (Railway bug)

**Fix:** Đã fix trong code mới nhất. Push lại:
```bash
git push origin vanna_dev
```

---

### PostgreSQL service name khác

Nếu PostgreSQL service không tên "Postgres":

1. Click vào PostgreSQL service
2. Tab "Settings" → Xem tên service ở đầu trang
3. Dùng tên đó trong reference:
   ```
   ${{ YourPostgresServiceName.DATABASE_URL }}
   ```

---

## 📊 Cách Hoạt Động

### Variable Reference Workflow

```
1. Bạn set: DATABASE_URL = ${{ Postgres.DATABASE_URL }}
   
2. Railway deployment:
   - Đọc Postgres service
   - Lấy DATABASE_URL từ Postgres
   - Thay thế vào Main service
   
3. App nhận được:
   DATABASE_URL = postgresql://postgres:pass@xxx.railway.internal:5432/railway
   
4. Code parse và connect:
   host = xxx.railway.internal
   port = 5432
   dbname = railway
   user = postgres
   password = pass
```

### DATABASE_URL Format

```
postgresql://[user]:[password]@[host]:[port]/[database]
```

Code tự động parse format này và extract:
- Host (internal domain)
- Port (5432)
- Database name
- User & Password

---

## 🎯 Complete Checklist

Làm theo thứ tự:

- [ ] 1. Add PostgreSQL service
- [ ] 2. PostgreSQL status = 🟢 Active
- [ ] 3. Main service → Add variable: `DATABASE_URL = ${{ Postgres.DATABASE_URL }}`
- [ ] 4. Main service → Add variable: `CACHE_BACKEND = postgres`
- [ ] 5. Đợi redeploy (~2 min)
- [ ] 6. Check logs: "PostgreSQL cache initialized"
- [ ] 7. Test API: cache_stats không có error
- [ ] 8. Run: `python3 test_railway_postgres_connection.py`

---

## 💡 Tips

### Tip 1: Check Variable Value
Nếu muốn xem Railway inject value gì:

Temporary add:
```python
print(f"DATABASE_URL = {os.getenv('DATABASE_URL')[:50]}...")
```

Check deployment logs.

### Tip 2: Manual Connection String
Nếu Reference không work, có thể dùng connection string thủ công:

1. PostgreSQL service → Tab "Connect"
2. Copy "Internal URL"
3. Set vào Main service:
   ```
   DATABASE_URL = postgresql://postgres:...@xxx.railway.internal:5432/railway
   ```

### Tip 3: External Database
Nếu muốn dùng external PostgreSQL (Supabase, Neon, etc.):

```
DATABASE_URL = postgresql://user:pass@external-host.com:5432/dbname
CACHE_BACKEND = postgres
```

Code support cả internal và external!

---

## 🚀 Quick Start (TL;DR)

```bash
# 1. Add PostgreSQL trên Railway UI
# 2. Main Service → Variables → Add:

DATABASE_URL = ${{ Postgres.DATABASE_URL }}
CACHE_BACKEND = postgres

# 3. Đợi redeploy
# 4. Test:

python3 test_railway_postgres_connection.py
```

---

## ❓ FAQ

**Q: Tại sao không dùng PGHOST, PGPORT riêng lẻ?**
A: Railway recommend dùng DATABASE_URL cho service-to-service connection. Đơn giản và reliable hơn.

**Q: Có cần set thêm PGHOST, PGPORT không?**
A: KHÔNG. Chỉ cần DATABASE_URL. Code sẽ tự parse.

**Q: Service name phải là "Postgres"?**
A: Không. Dùng tên thật của service. Check trong Settings tab.

**Q: Cache vẫn lỗi sau khi setup?**
A: Check logs để xem error. Có thể:
- PostgreSQL chưa ready (đợi thêm 1-2 phút)
- Reference variable sai tên service
- CACHE_BACKEND chưa được set

---

## 📞 Support

Nếu vẫn lỗi, share:
1. Screenshot Railway services (cả Main và PostgreSQL)
2. Screenshot Variables tab của Main service
3. Copy deployment logs (500 dòng cuối)

Happy coding! 🎉
