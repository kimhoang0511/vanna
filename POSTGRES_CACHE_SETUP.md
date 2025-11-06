# PostgreSQL Cache Setup cho Railway

## 📊 Tổng quan

Thay vì dùng file cache (`vanna_cache.json`) có thể bị mất khi restart, chúng ta dùng **PostgreSQL** để lưu cache:

✅ **Persistent**: Không bị mất khi restart/deploy  
✅ **Shared**: Nhiều instances có thể share cache  
✅ **Scalable**: Database có thể scale độc lập  
✅ **Queryable**: Dễ query và debug

## 🚀 Setup trên Railway

### Bước 1: Thêm PostgreSQL Database

1. Mở Railway project: https://railway.app
2. Click **"+ New"** → **"Database"** → **"PostgreSQL"**
3. Database sẽ tự động được tạo và connect

### Bước 2: Config Environment Variables

Railway tự động set các biến môi trường PostgreSQL:
- `PGHOST` / `DB_HOST`
- `PGPORT` / `DB_PORT`
- `PGDATABASE` / `DB_NAME`
- `PGUSER` / `DB_USER`
- `PGPASSWORD` / `DB_PASSWORD`

Thêm biến để enable PostgreSQL cache:

```bash
CACHE_BACKEND=postgres
```

**Cách thêm:**
1. Mở Service → **Variables** tab
2. Add: `CACHE_BACKEND` = `postgres`
3. Save

### Bước 3: Deploy

Code đã sẵn sàng! Chỉ cần:

```bash
git push origin vanna_dev
```

Railway sẽ tự động:
1. Deploy code mới
2. Connect tới PostgreSQL
3. Tạo table `vanna_cache` 
4. Bắt đầu cache vào database

## 📋 Cache Table Structure

```sql
CREATE TABLE vanna_cache (
    id VARCHAR(255) PRIMARY KEY,           -- Hash của câu hỏi
    data JSONB NOT NULL,                   -- {question, sql, ...}
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## 🔍 Query Cache

Kết nối PostgreSQL trên Railway và chạy:

```sql
-- Xem tất cả cache
SELECT id, data->>'question' as question, created_at 
FROM vanna_cache 
ORDER BY created_at DESC;

-- Đếm số lượng cache
SELECT COUNT(*) FROM vanna_cache;

-- Xem cache của 1 question cụ thể
SELECT * FROM vanna_cache 
WHERE data->>'question' LIKE '%customer%';

-- Clear cache (nếu cần)
DELETE FROM vanna_cache;
```

## 🧪 Test Endpoints

### 1. Generate SQL (sẽ cache vào PostgreSQL)
```bash
curl "https://vanna-production.up.railway.app/api/v0/generate_sql?question=Top%2010%20customers" \
  -H "X-API-Key: YOUR_API_KEY"
```

### 2. Get Cache Stats
```bash
curl "https://vanna-production.up.railway.app/api/v0/cache_stats" \
  -H "X-API-Key: YOUR_API_KEY"
```

Response:
```json
{
  "type": "cache_stats",
  "stats": {
    "total_entries": 25,
    "oldest_entry": "2025-11-06 10:00:00",
    "newest_entry": "2025-11-06 15:30:00",
    "sample_questions": [
      "Top 10 customers",
      "How many users?",
      ...
    ]
  }
}
```

### 3. Load Cached Question
```bash
curl "https://vanna-production.up.railway.app/api/v0/get_cached_question?id=e06588e348c119268765713b5834b30a" \
  -H "X-API-Key: YOUR_API_KEY"
```

## 🔄 Fallback Strategy

Code tự động fallback nếu PostgreSQL không available:

```
PostgreSQL Cache (try)
  ↓
  ✅ Success → Use PostgreSQL
  ↓
  ❌ Failed → Fallback to File Cache
```

## 📊 So sánh File Cache vs PostgreSQL Cache

| Feature | File Cache | PostgreSQL Cache |
|---------|-----------|------------------|
| **Persistent** | ⚠️ Mất khi container restart | ✅ Luôn persistent |
| **Multi-instance** | ❌ Mỗi instance riêng cache | ✅ Share giữa instances |
| **Scalable** | ❌ Giới hạn bởi disk | ✅ Scale with database |
| **Queryable** | ❌ Phải đọc file | ✅ SQL queries |
| **Setup** | ✅ Đơn giản (không cần DB) | ⚠️ Cần PostgreSQL |

## 🎯 Khuyến nghị

- **Development**: Dùng File Cache
- **Production**: Dùng PostgreSQL Cache
- **Railway**: Dùng PostgreSQL Cache (đã có PostgreSQL sẵn)

## 🐛 Troubleshooting

### Cache không hoạt động?

1. Check environment variable:
```bash
railway variables
```

Phải có: `CACHE_BACKEND=postgres`

2. Check logs:
```bash
railway logs
```

Tìm: `✅ PostgreSQL cache initialized`

3. Check database connection:
```bash
railway run psql $DATABASE_URL -c "SELECT COUNT(*) FROM vanna_cache;"
```

### Clear cache

```bash
railway run psql $DATABASE_URL -c "DELETE FROM vanna_cache;"
```

hoặc qua API:
```bash
curl -X POST "https://vanna-production.up.railway.app/api/v0/clear_cache" \
  -H "X-API-Key: YOUR_API_KEY"
```
