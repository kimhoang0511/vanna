# 🧪 Test Chart API - Kết quả & Phân tích

## 📊 Thông tin Test

- **API URL**: https://vanna-production.up.railway.app
- **Test Date**: 2025-11-12
- **Test File**: `test_chart_api_sales_summary.py`
- **Question**: "Tổng hợp doanh số bán hàng"

## ✅ Kết quả Test

### Test Summary
- **Tests Run**: 4
- **Tests Passed**: 1 (25%)
- **Tests Failed**: 3 (75%)

### Chi tiết từng bước

#### ✅ Step 1: Generate SQL - PASSED
```sql
SELECT 
    customer_id,
    name,
    SUM(revenue) AS total_revenue
FROM sales
GROUP BY 
    customer_id, name
ORDER BY 
    total_revenue DESC;
```
- Query ID: `8e61ae65edd1f99f844f6691c2465350`
- Status: **SUCCESS** ✅

#### ✅ Step 2: Run SQL - PASSED (với retry)
```json
{
  "type": "df",
  "rows": 10,
  "should_generate_chart": true,
  "sample_data": [
    {"customer_id": 9, "name": "Hoang Van E", "total_revenue": "$4,200,000.00"},
    {"customer_id": 17, "name": "Vo Van M", "total_revenue": "$4,100,000.00"},
    {"customer_id": 6, "name": "Tran Thi B", "total_revenue": "$3,500,000.00"}
  ]
}
```
- Status: **SUCCESS** ✅
- Note: Có 1 lần connection error nhưng retry thành công

#### ❌ Step 3: Generate Chart - FAILED
```json
{
  "type": "error",
  "error": "No df found"
}
```
- Status: **FAILED** ❌
- Retry: FAILED (cũng lỗi)

## 🔍 Nguyên nhân Lỗi

### Vấn đề chính: **MemoryCache không persistent trên Railway**

#### Luồng API hiện tại:
```
Step 1: Generate SQL
  ↓
  Cache: {id: sql} ← Lưu vào MemoryCache
  
Step 2: Run SQL  
  ↓
  Cache: {id: sql, df} ← Lưu thêm DataFrame
  
Step 3: Generate Chart
  ↓
  Cache.get(id, "df") ← ❌ KHÔNG TÌM THẤY!
```

#### Tại sao cache bị mất?

1. **Railway restarts containers** thường xuyên (ephemeral storage)
2. **MemoryCache** chỉ tồn tại trong memory process
3. **Mất cache khi**:
   - Server restart
   - Scale up/down
   - Deploy mới
   - Process crash

#### Evidence từ logs:
```
🔍 DEBUG INFO:
   This error means the DataFrame is not in cache.
   Possible causes:
   1. Cache expired (session timeout)
   2. Different session/cookie  
   3. Server restarted  ← CHÍNH XÁC!
```

## 💡 Giải pháp đề xuất

### ✅ Solution 1: Sử dụng PostgreSQL Cache (RECOMMENDED)

Thay vì `MemoryCache`, dùng `PostgresCache` để cache persistent:

```python
# flask_main.py
from vanna.flask import VannaFlaskApp
from postgres_cache import PostgresCache  # File có sẵn trong repo

# Initialize PostgreSQL cache
postgres_cache = PostgresCache(
    host=os.getenv('DB_HOST'),
    port=int(os.getenv('DB_PORT', 5432)),
    dbname=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)

# Use PostgresCache instead of default MemoryCache
app = VannaFlaskApp(
    vn=vn,
    cache=postgres_cache,  # ← Thay đổi này
    allow_llm_to_see_data=True,
    chart=True
)
```

**Ưu điểm**:
- ✅ Cache persistent qua restarts
- ✅ Share cache giữa nhiều instances
- ✅ Không mất data khi scale
- ✅ File `postgres_cache.py` đã có sẵn trong repo

### ✅ Solution 2: Combined Approach

```python
# Workflow mới: không cần cache df
@app.route("/api/v0/generate_chart_direct", methods=["POST"])
def generate_chart_direct():
    """Generate chart trực tiếp từ question, không qua cache"""
    question = request.json.get('question')
    
    # Step 1: Generate SQL
    sql = vn.generate_sql(question)
    
    # Step 2: Run SQL
    df = vn.run_sql(sql)
    
    # Step 3: Generate chart ngay
    if vn.should_generate_chart(df):
        plotly_code = vn.generate_plotly_code(
            question=question,
            sql=sql,
            df_metadata=f"df.dtypes:\n{df.dtypes}"
        )
        fig = vn.get_plotly_figure(plotly_code, df)
        
        return jsonify({
            "success": True,
            "sql": sql,
            "data": df.to_dict(orient='records'),
            "chart": fig.to_json()
        })
    
    return jsonify({
        "success": True,
        "sql": sql,
        "data": df.to_dict(orient='records'),
        "chart": None
    })
```

**Ưu điểm**:
- ✅ Không phụ thuộc cache
- ✅ Chạy 1 request duy nhất
- ✅ Đơn giản hơn
- ❌ Không tái sử dụng được kết quả

### ✅ Solution 3: Redis Cache (Nâng cao)

```python
from vanna.flask import Cache
import redis
import json

class RedisCache(Cache):
    def __init__(self, redis_url):
        self.redis = redis.from_url(redis_url)
    
    def generate_id(self, *args, **kwargs):
        return str(uuid.uuid4())
    
    def set(self, id, field, value):
        key = f"vanna:{id}:{field}"
        # Serialize DataFrame nếu cần
        if isinstance(value, pd.DataFrame):
            value = value.to_json()
        self.redis.setex(key, 3600, json.dumps(value))  # TTL 1 hour
    
    def get(self, id, field):
        key = f"vanna:{id}:{field}"
        value = self.redis.get(key)
        if value:
            return json.loads(value)
        return None
```

## 📋 Action Items

### Immediate (Ngay lập tức)
- [ ] Thay MemoryCache → PostgresCache trong `flask_main.py`
- [ ] Test lại với PostgresCache
- [ ] Verify cache persistence qua restarts

### Short-term (Ngắn hạn)
- [ ] Thêm endpoint `/api/v0/generate_chart_direct` cho use case đơn giản
- [ ] Document cách sử dụng 2 approaches
- [ ] Add health check cho cache

### Long-term (Dài hạn)  
- [ ] Consider Redis nếu cần scale horizontal
- [ ] Add cache TTL configuration
- [ ] Monitor cache hit/miss rates

## 🎯 Kết luận

### Hiện trạng
- ✅ SQL Generation: **Hoạt động tốt**
- ✅ SQL Execution: **Hoạt động tốt**  
- ❌ Chart Generation: **Bị block bởi cache issue**

### Root Cause
**MemoryCache không phù hợp cho production environment như Railway** vì:
- Containers restart thường xuyên
- Cache bị mất giữa các requests
- Không scale được

### Recommended Fix
**Chuyển sang PostgresCache** (file đã có sẵn):
```bash
# Chỉ cần sửa 1 dòng trong flask_main.py
cache = PostgresCache(...)  # Thay vì MemoryCache()
```

### Expected Result sau fix
```
✅ Step 1: Generate SQL - PASSED
✅ Step 2: Run SQL - PASSED  
✅ Step 3: Generate Chart - PASSED  ← Sẽ pass sau khi fix
✅ Step 4: Save Chart - PASSED
```

---

**Next Steps**: Implement PostgresCache và retest 🚀
