# 🔧 Workaround: Generate Chart trên Railway

## ❌ Vấn đề

API `/api/v0/generate_plotly_figure` trả về lỗi:
```json
{
  "error": "No df found",
  "type": "error"
}
```

## 🔍 Nguyên nhân

`VannaFlaskApp` có **2 cache systems**:

### 1. Custom Cache (PostgresCache) - HOẠT ĐỘNG TỐT ✅
```python
# flask_main.py line ~200
custom_cache = PostgresCache(connection_params=db_params)
app = VannaFlaskApp(vn=vn, cache=custom_cache, ...)
```
- Cache: `question` → `sql`
- Persistent qua restarts
- Dùng PostgreSQL

### 2. Internal Cache (trong VannaFlaskApp) - BỊ MẤT ❌
```python
# src/vanna/flask/__init__.py
class VannaFlaskAPI:
    def __init__(self, vn, cache=MemoryCache(), ...):
        self.cache = cache  # Đây là cache được pass vào
```

**Nhưng** trong code của `/api/v0/run_sql`:
```python
# Line ~500 trong __init__.py
df = vn.run_sql(sql=sql)
self.cache.set(id=id, field="df", value=df)  # Cache df vào internal cache
```

**Và** trong `/api/v0/generate_plotly_figure`:
```python
# Line ~650
def generate_plotly_figure(user: any, id: str, df, question, sql):
    # Decorator @self.requires_cache(["df", "question", "sql"])
    # Cần lấy df từ cache
```

**Vấn đề**: Railway restart container → Internal cache mất → "No df found"

## ✅ Giải pháp

### Solution 1: Sử dụng `/api/v0/ask` endpoint (RECOMMENDED)

Endpoint `/api/v0/ask` được thêm mới trong `flask_main.py`, nó:
- Generate SQL
- Run SQL
- Trả về cả data lẫn chart (nếu có)
- **KHÔNG phụ thuộc vào cache**

#### Cách sử dụng:

```bash
# Method 1: GET request
curl "https://vanna-production.up.railway.app/api/v0/ask?question=Top 10 khách hàng có doanh thu cao nhất"

# Method 2: POST request  
curl -X POST "https://vanna-production.up.railway.app/api/v0/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Top 10 khách hàng có doanh thu cao nhất"}'
```

#### Response:
```json
{
  "success": true,
  "question": "Top 10 khách hàng có doanh thu cao nhất",
  "sql": "SELECT customer_id, name, revenue FROM sales ORDER BY revenue DESC LIMIT 10",
  "data": [
    {"customer_id": 9, "name": "Hoang Van E", "revenue": "$4,200,000.00"},
    ...
  ],
  "rows_count": 10,
  "cache_id": "5e3889e577678d281a44222f93da0962"
}
```

#### Để có chart, cần implement thêm:

```python
# flask_main.py - Thêm vào endpoint /api/v0/ask
# Sau khi run SQL, thêm logic generate chart

if vn.should_generate_chart(df):
    plotly_code = vn.generate_plotly_code(
        question=question,
        sql=sql,
        df_metadata=f"df.dtypes:\n{df.dtypes}"
    )
    fig = vn.get_plotly_figure(plotly_code, df)
    
    return jsonify({
        "success": True,
        "question": question,
        "sql": sql,
        "data": data_json,
        "rows_count": rows_count,
        "cache_id": cache_id,
        "chart": fig.to_json()  # ← Thêm chart vào response
    })
```

### Solution 2: Fix VannaFlaskApp để dùng persistent cache

Sửa file `src/vanna/flask/__init__.py` để `internal cache` cũng dùng PostgresCache:

```python
# src/vanna/flask/__init__.py line ~143
def __init__(
    self,
    vn: VannaBase,
    cache: Cache = MemoryCache(),  # ← Đây là problem
    auth: AuthInterface = NoAuth(),
    debug=True,
    allow_llm_to_see_data=False,
    chart=True,
):
    # ...
    self.cache = cache  # ← Cache này phải là PostgresCache
```

**Fix đã áp dụng trong flask_main.py**:
```python
# flask_main.py line ~200
custom_cache = PostgresCache(connection_params=db_params)

app = VannaFlaskApp(
    vn=vn,
    cache=custom_cache,  # ← Pass PostgresCache thay vì MemoryCache
    ...
)
```

**NHƯNG** vẫn có issue vì PostgresCache có thể không implement đủ methods để cache DataFrame.

### Solution 3: Custom API endpoint để generate chart trực tiếp

Tạo endpoint mới không phụ thuộc cache:

```python
@app.flask_app.route("/api/v0/generate_chart_direct", methods=["POST"])
def generate_chart_direct():
    """
    Generate chart directly without relying on cache
    
    POST body:
    {
        "question": "Your question",
        "sql": "Optional: pre-generated SQL",
        "chart_instructions": "Optional: custom chart instructions"
    }
    """
    data = request.get_json()
    question = data.get('question')
    sql = data.get('sql')
    chart_instructions = data.get('chart_instructions')
    
    # Generate SQL if not provided
    if not sql:
        sql = vn.generate_sql(question)
    
    # Run SQL
    df = vn.run_sql(sql)
    
    # Generate chart
    if vn.should_generate_chart(df):
        if chart_instructions:
            question_with_instructions = f"{question}. {chart_instructions}"
        else:
            question_with_instructions = question
        
        plotly_code = vn.generate_plotly_code(
            question=question_with_instructions,
            sql=sql,
            df_metadata=f"df.dtypes:\n{df.dtypes}"
        )
        
        fig = vn.get_plotly_figure(plotly_code, df)
        
        return jsonify({
            "success": True,
            "question": question,
            "sql": sql,
            "data": df.to_dict(orient='records'),
            "chart": fig.to_json()
        })
    
    return jsonify({
        "success": False,
        "error": "Data not suitable for chart"
    })
```

## 📝 Test Script

```python
import requests
import json

BASE_URL = "https://vanna-production.up.railway.app"

# Test với endpoint /api/v0/ask
response = requests.get(f"{BASE_URL}/api/v0/ask", params={
    'question': 'Top 10 khách hàng có doanh thu cao nhất'
})

data = response.json()

if data['success']:
    print(f"✅ Question: {data['question']}")
    print(f"✅ SQL: {data['sql']}")
    print(f"✅ Rows: {data['rows_count']}")
    print(f"✅ Data: {json.dumps(data['data'][:3], indent=2)}")
    
    # Nếu cần chart, gọi thêm endpoint khác (sau khi implement)
    # hoặc generate chart ở client side với data
```

## 🎯 Recommended Action

**NGAY BÂY GIỜ**: Sử dụng endpoint `/api/v0/ask` thay vì workflow 3 bước.

**SAU ĐÓ**: Implement Solution 3 (endpoint `/api/v0/generate_chart_direct`) trong `flask_main.py` để có workflow hoàn chỉnh không phụ thuộc cache.

## 📊 So sánh Workflows

| Workflow | Steps | Cache Dependency | Status |
|----------|-------|------------------|--------|
| **Old (3 steps)** | generate_sql → run_sql → generate_plotly_figure | ❌ High (df in cache) | BROKEN on Railway |
| **New (/api/v0/ask)** | 1 request | ✅ Low (only for caching SQL) | WORKS |
| **Future (direct)** | 1 request with chart | ✅ None | WILL WORK |

## 💡 TL;DR

**Problem**: `/api/v0/generate_plotly_figure` cần `df` từ cache, nhưng cache bị mất trên Railway.

**Quick Fix**: Dùng `/api/v0/ask` endpoint thay vì workflow 3 bước.

**Permanent Fix**: Implement `/api/v0/generate_chart_direct` endpoint không phụ thuộc cache.
