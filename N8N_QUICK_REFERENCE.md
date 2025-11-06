# n8n Workflow Quick Reference

## 🎯 Mục đích
Tự động train Vanna RAG system với dữ liệu từ database PostgreSQL

## 📋 Checklist Setup

### 1. Thông tin cần thiết
- [ ] API URL: `https://vanna-production.up.railway.app`
- [ ] API Key: `YOUR_API_KEY_HERE`
- [ ] PostgreSQL credentials (host, port, dbname, user, password)
- [ ] Training data (DDL, documentation, SQL examples)

### 2. Các bước workflow
```
1. Edit Fields (Set)       → Chuẩn bị dữ liệu
2. Initialize Vanna        → POST /init
3. Connect PostgreSQL      → POST /connect/postgres
4. Clear Training Data ⚠️  → POST /clear_training_data
5. Train DDL               → POST /train/ddl
6. Train Documentation     → POST /train/documentation
7. Train SQL               → POST /train/sql
```

## 🔧 Endpoints Reference

| Endpoint | Method | Purpose | Body Required |
|----------|--------|---------|---------------|
| `/init` | POST | Khởi tạo Vanna | `{"model": "gpt-4o-mini"}` |
| `/connect/postgres` | POST | Kết nối DB | `{host, port, dbname, user, password}` |
| `/clear_training_data` | POST | **Xóa dữ liệu cũ** | Không cần |
| `/train/ddl` | POST | Train DDL | `{"ddl": "CREATE TABLE..."}` |
| `/train/documentation` | POST | Train docs | `{"documentation": "..."}` |
| `/train/sql` | POST | Train SQL | `{"question": "...", "sql": "..."}` |
| `/training_data` | GET | Xem data | Không cần |

## 🔑 Authentication Header

**Tất cả requests phải có header:**
```json
{
  "X-API-Key": "YOUR_API_KEY_HERE",
  "Content-Type": "application/json"
}
```

## 📝 Edit Fields (Set) Example

```json
{
  "train_ddl": "CREATE TABLE customers (id INT PRIMARY KEY, name VARCHAR(100), email VARCHAR(100), country VARCHAR(50));",
  "train_documentation": "Bảng customers chứa thông tin khách hàng. Các trường quan trọng: id (mã khách hàng), name (tên), email (địa chỉ email), country (quốc gia).",
  "train_sql": "-- Tìm top 10 khách hàng\nSELECT name, email FROM customers ORDER BY id DESC LIMIT 10;"
}
```

## ⚠️ Critical: Clear Training Data

**Tại sao phải clear trước khi train?**
- ✅ Tránh conflict giữa dữ liệu cũ và mới
- ✅ Đảm bảo RAG chỉ dùng dữ liệu mới nhất
- ✅ Tránh duplicate embeddings
- ✅ Giảm kích thước vector database

**Response example:**
```json
{
  "success": true,
  "message": "Training data cleared successfully. Removed 15 items. 0 items remaining.",
  "data": {
    "count_before": 15,
    "count_after": 0,
    "cleared": 15
  }
}
```

## 🔄 n8n Expression Reference

Lấy giá trị từ Edit Fields (Set) node:

```javascript
// DDL
{{ $node['Edit Fields (Set)'].json.train_ddl }}

// Documentation
{{ $node['Edit Fields (Set)'].json.train_documentation }}

// SQL
{{ $node['Edit Fields (Set)'].json.train_sql }}
```

## ✅ Success Response Format

Tất cả endpoints trả về format:
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { ... }
}
```

## ❌ Error Response Format

```json
{
  "detail": "Error message here"
}
```

## 🧪 Test Commands

### Test Clear Endpoint
```bash
curl -X POST https://vanna-production.up.railway.app/clear_training_data \
  -H "X-API-Key: YOUR_API_KEY_HERE"
```

### Test Get Training Data
```bash
curl -X GET https://vanna-production.up.railway.app/training_data \
  -H "X-API-Key: YOUR_API_KEY_HERE"
```

### Test Train DDL
```bash
curl -X POST https://vanna-production.up.railway.app/train/ddl \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{"ddl": "CREATE TABLE test (id INT);"}'
```

## 📊 Monitoring

### Check workflow status
1. n8n Executions tab → View execution details
2. Check each node's output
3. Verify `success: true` in responses

### Verify training completed
```bash
# Should return count = 3 (or more)
curl -X GET https://vanna-production.up.railway.app/training_data \
  -H "X-API-Key: YOUR_API_KEY_HERE"
```

## ⚙️ Recommended Settings

### HTTP Request Node Settings
- **Retry on Fail:** Yes
- **Max Tries:** 3
- **Wait Between Tries:** 1000ms
- **Timeout:** 30000ms (30 seconds)

### Workflow Settings
- **Error Workflow:** Enable error notifications
- **Execution Order:** Sequential (not parallel)
- **Save Execution Progress:** Yes

## 📅 Scheduling

### Cron Expressions
```
Daily (2 AM):    0 2 * * *
Weekly (Sunday): 0 2 * * 0
Monthly (Day 1): 0 2 1 * *
```

## 🔍 Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| 401 Unauthorized | Check API Key trong header |
| 500 Server Error | Check Railway logs, verify server running |
| Training data không clear | Call `/clear_training_data` nhiều lần |
| Timeout | Tăng timeout trong HTTP Request settings |

## 📚 Full Documentation

Chi tiết đầy đủ: `N8N_WORKFLOW_GUIDE.md`

## 🚀 Quick Start

1. Import workflow JSON từ `N8N_WORKFLOW_GUIDE.md`
2. Update PostgreSQL credentials
3. Update training data trong Edit Fields node
4. Click **Execute Workflow**
5. Verify trong `/training_data` endpoint

## ✨ Success Criteria

- [ ] All nodes show green checkmark
- [ ] `/clear_training_data` returns `count_after: 0`
- [ ] Each train endpoint returns `success: true`
- [ ] `/training_data` shows 3+ items
- [ ] Test SQL generation với câu hỏi mới

---

**API Documentation:** https://vanna-production.up.railway.app/docs
**Health Check:** https://vanna-production.up.railway.app/health
