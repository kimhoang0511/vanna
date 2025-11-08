# 🚀 API Endpoint: /api/v0/ask

> All-in-one endpoint: Generate SQL và Execute trong một request

## 📋 Tổng quan

Endpoint `/api/v0/ask` kết hợp 2 bước:
1. **Generate SQL** từ câu hỏi (tiếng Việt hoặc tiếng Anh)
2. **Execute SQL** trên database và trả về kết quả

Tương tự n8n workflow `02_generate_and_run_sql.json` nhưng gọn hơn (1 request thay vì 2).

---

## 🔌 Endpoint Details

**URL:** `/api/v0/ask`

**Methods:** `GET` hoặc `POST`

**Content-Type:** `application/json` (for POST)

---

## 📤 Request

### Option 1: GET Method

**URL:** `GET /api/v0/ask?question=<câu hỏi>`

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `question` | string | ✅ Yes | - | Câu hỏi bằng tiếng Việt hoặc English |
| `allow_llm_to_see_data` | boolean | ❌ No | `false` | Cho phép LLM xem dữ liệu mẫu |

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v0/ask?question=Top 10 khách hàng có doanh thu cao nhất"
```

**With allow_llm_to_see_data:**
```bash
curl -X GET "http://localhost:8000/api/v0/ask?question=Tổng doanh thu&allow_llm_to_see_data=true"
```

---

### Option 2: POST Method

**URL:** `POST /api/v0/ask`

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "question": "Câu hỏi của bạn",
  "allow_llm_to_see_data": false
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v0/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Top 10 khách hàng có doanh thu cao nhất trong năm 2024",
    "allow_llm_to_see_data": false
  }'
```

---

## 📥 Response

### Success Response (200 OK)

```json
{
  "success": true,
  "question": "Top 10 khách hàng có doanh thu cao nhất trong năm 2024",
  "sql": "SELECT customer_name, SUM(total_amount) as revenue FROM orders WHERE YEAR(order_date) = 2024 GROUP BY customer_name ORDER BY revenue DESC LIMIT 10",
  "data": [
    {
      "customer_name": "ABC Corp",
      "revenue": 150000.50
    },
    {
      "customer_name": "XYZ Ltd",
      "revenue": 125000.00
    }
  ],
  "rows_count": 10,
  "cache_id": "abc123def456"
}
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | `true` nếu thành công |
| `question` | string | Câu hỏi gốc |
| `sql` | string | SQL query đã generate |
| `data` | array | Kết quả từ database (array of objects) |
| `rows_count` | integer | Số lượng rows trả về |
| `cache_id` | string | ID để load lại từ cache |

---

### Error Response (400/500/503)

**400 Bad Request - Missing question:**
```json
{
  "success": false,
  "error": "No question provided",
  "usage": {
    "GET": "?question=Your question here",
    "POST": "{\"question\": \"Your question here\"}"
  }
}
```

**500 Internal Server Error - SQL generation failed:**
```json
{
  "success": false,
  "error": "Failed to generate SQL",
  "question": "Your question"
}
```

**500 Internal Server Error - Invalid SQL:**
```json
{
  "success": false,
  "error": "Generated SQL is not valid",
  "question": "Your question",
  "sql": "SELECT ..."
}
```

**503 Service Unavailable - Database not connected:**
```json
{
  "success": false,
  "error": "Database not connected. Please connect to a database first.",
  "question": "Your question",
  "sql": "SELECT ...",
  "hint": "Use vn.connect_to_postgres() or similar method"
}
```

**500 Internal Server Error - Execution error:**
```json
{
  "success": false,
  "error": "column \"xyz\" does not exist",
  "question": "Your question",
  "sql": "SELECT xyz FROM ...",
  "error_type": "ProgrammingError"
}
```

---

## 🧪 Examples

### Example 1: Simple Question (GET)

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v0/ask?question=Có bao nhiêu khách hàng?"
```

**Response:**
```json
{
  "success": true,
  "question": "Có bao nhiêu khách hàng?",
  "sql": "SELECT COUNT(*) as total FROM customers",
  "data": [
    {"total": 1542}
  ],
  "rows_count": 1,
  "cache_id": "hash-abc123"
}
```

---

### Example 2: Complex Question (POST)

**Request:**
```bash
curl -X POST http://localhost:8000/api/v0/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Doanh thu theo tháng trong năm 2024, chỉ lấy tháng có doanh thu > 100000"
  }'
```

**Response:**
```json
{
  "success": true,
  "question": "Doanh thu theo tháng trong năm 2024, chỉ lấy tháng có doanh thu > 100000",
  "sql": "SELECT EXTRACT(MONTH FROM order_date) as month, SUM(total_amount::numeric) as revenue FROM orders WHERE EXTRACT(YEAR FROM order_date) = 2024 GROUP BY month HAVING SUM(total_amount::numeric) > 100000 ORDER BY month",
  "data": [
    {"month": 1, "revenue": 125000.50},
    {"month": 3, "revenue": 150000.00},
    {"month": 5, "revenue": 180000.75}
  ],
  "rows_count": 3,
  "cache_id": "hash-def456"
}
```

---

### Example 3: With allow_llm_to_see_data

**Request:**
```bash
curl -X POST http://localhost:8000/api/v0/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Top 5 sản phẩm",
    "allow_llm_to_see_data": true
  }'
```

**Response:**
```json
{
  "success": true,
  "question": "Top 5 sản phẩm",
  "sql": "SELECT product_name, COUNT(*) as total_orders FROM order_items GROUP BY product_name ORDER BY total_orders DESC LIMIT 5",
  "data": [
    {"product_name": "iPhone 15", "total_orders": 450},
    {"product_name": "MacBook Pro", "total_orders": 320}
  ],
  "rows_count": 5,
  "cache_id": "hash-ghi789"
}
```

---

## 🔄 Comparison với `/generate_sql` + `/run_sql`

### Old Way (2 requests):

```bash
# Step 1: Generate SQL
curl -X GET "http://localhost:8000/api/v0/generate_sql?question=Top 10 customers"

# Response:
{
  "type": "sql",
  "id": "abc123",
  "text": "SELECT ..."
}

# Step 2: Run SQL
curl -X GET "http://localhost:8000/api/v0/run_sql?id=abc123"

# Response:
{
  "type": "df",
  "id": "abc123",
  "df": "[{...}]",
  "should_generate_chart": true
}
```

### New Way (1 request):

```bash
# All-in-one
curl -X GET "http://localhost:8000/api/v0/ask?question=Top 10 customers"

# Response:
{
  "success": true,
  "question": "...",
  "sql": "SELECT ...",
  "data": [{...}],
  "rows_count": 10,
  "cache_id": "abc123"
}
```

**Ưu điểm:**
- ✅ Gọn hơn (1 request thay vì 2)
- ✅ Response format nhất quán (JSON)
- ✅ Error handling tốt hơn
- ✅ Có `success` flag rõ ràng
- ✅ Trả về data trực tiếp (không cần parse `df`)

---

## 🎯 Use Cases

### Use Case 1: Chatbot Integration

```javascript
// Slack bot example
async function handleQuestion(question) {
  const response = await fetch('http://api.example.com/api/v0/ask', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({question})
  });
  
  const result = await response.json();
  
  if (result.success) {
    return formatResultsForSlack(result.data);
  } else {
    return `Error: ${result.error}`;
  }
}
```

---

### Use Case 2: Dashboard Data Source

```javascript
// React component
const DashboardMetrics = () => {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    fetch('/api/v0/ask?question=Tổng doanh thu hôm nay')
      .then(res => res.json())
      .then(result => {
        if (result.success) {
          setData(result.data);
        }
      });
  }, []);
  
  return <MetricCard data={data} />;
};
```

---

### Use Case 3: n8n Workflow (Simplified)

**Old workflow (2 nodes):**
```
HTTP Request 1: /generate_sql
    ↓
HTTP Request 2: /run_sql
```

**New workflow (1 node):**
```
HTTP Request: /ask
```

---

## ⚙️ Configuration

### Prerequisites

**Để endpoint hoạt động, cần:**

1. ✅ **Vanna đã được train:**
   ```bash
   # Train với DDL, documentation, SQL examples
   curl -X POST http://localhost:8000/api/v0/train -d '{"ddl": "..."}'
   ```

2. ✅ **Database đã được connect:**
   ```python
   # In flask_main.py, function connect_to_database() sẽ tự động connect
   # Hoặc dùng environment variables:
   export DATABASE_URL="postgresql://user:pass@host:5432/dbname"
   ```

3. ✅ **Server đang chạy:**
   ```bash
   python flask_main.py
   ```

---

## 🔐 Security (Production)

### Add API Key Authentication

**Modify endpoint:**
```python
@app.flask_app.route("/api/v0/ask", methods=["GET", "POST"])
def ask_question():
    from flask import request, jsonify
    
    # Check API key
    api_key = request.headers.get('X-API-Key')
    if api_key != os.getenv('API_KEY'):
        return jsonify({"error": "Unauthorized"}), 401
    
    # ... rest of code
```

**Usage:**
```bash
curl -X GET "http://localhost:8000/api/v0/ask?question=..." \
  -H "X-API-Key: your-secret-key"
```

---

### Rate Limiting

**Use Flask-Limiter:**
```python
from flask_limiter import Limiter

limiter = Limiter(app.flask_app, key_func=lambda: request.remote_addr)

@app.flask_app.route("/api/v0/ask", methods=["GET", "POST"])
@limiter.limit("10 per minute")  # Max 10 requests per minute
def ask_question():
    # ... code
```

---

## 📊 Monitoring

### Log all requests

**Already implemented in code:**
```python
print(f"🔍 Question: {question}")
print(f"✅ Generated SQL: {sql[:100]}...")
print(f"⚙️  Executing SQL...")
print(f"✅ Query returned {rows_count} rows")
```

### Save to database

**Add logging to Postgres:**
```python
# After successful execution
db.execute("""
    INSERT INTO api_logs (endpoint, question, sql, rows_count, timestamp)
    VALUES (%s, %s, %s, %s, NOW())
""", ('/api/v0/ask', question, sql, rows_count))
```

---

## 🐛 Troubleshooting

### Issue 1: "Failed to generate SQL"

**Causes:**
- Training data không đủ
- Question không rõ ràng
- LLM timeout

**Fix:**
```bash
# Train thêm data
curl -X POST http://localhost:8000/api/v0/train -d '{
  "documentation": "..."
}'

# Thử lại với question rõ ràng hơn
```

---

### Issue 2: "Database not connected"

**Causes:**
- `connect_to_database()` failed
- Environment variables sai

**Fix:**
```bash
# Check DATABASE_URL
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"

# Restart server
python flask_main.py
```

---

### Issue 3: SQL execution error

**Causes:**
- SQL syntax sai
- Table/column không tồn tại
- Permission issues

**Fix:**
```bash
# Check generated SQL
# Response sẽ có field "sql" để debug

# Train với DDL mới
curl -X POST http://localhost:8000/api/v0/train -d '{
  "ddl": "CREATE TABLE ..."
}'
```

---

## ✅ Testing

### Manual Test

```bash
# Test 1: Simple question
curl "http://localhost:8000/api/v0/ask?question=COUNT customers"

# Test 2: Complex question
curl -X POST http://localhost:8000/api/v0/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Top 10 by revenue"}'

# Test 3: Error handling
curl "http://localhost:8000/api/v0/ask?question="

# Test 4: Vietnamese
curl "http://localhost:8000/api/v0/ask?question=Tổng số đơn hàng"
```

---

### Automated Test (pytest)

```python
def test_ask_endpoint_success():
    response = client.get('/api/v0/ask?question=COUNT customers')
    data = response.get_json()
    
    assert response.status_code == 200
    assert data['success'] == True
    assert 'sql' in data
    assert 'data' in data
    assert data['rows_count'] >= 0

def test_ask_endpoint_no_question():
    response = client.get('/api/v0/ask')
    data = response.get_json()
    
    assert response.status_code == 400
    assert data['success'] == False
    assert 'error' in data
```

---

## 📚 Related Documentation

- [API_README.md](../API_README.md) - Full API documentation
- [N8N_INTEGRATION.md](../N8N_INTEGRATION.md) - n8n integration guide
- [flask_main.py](../flask_main.py) - Source code

---

## 🎉 Summary

**Endpoint:** `/api/v0/ask`

**Purpose:** Generate SQL + Execute trong 1 request

**Input:** Question (string)

**Output:** 
```json
{
  "success": true,
  "sql": "...",
  "data": [...],
  "rows_count": 10
}
```

**Use when:**
- ✅ Chatbot integration
- ✅ API for web/mobile apps
- ✅ Quick data queries
- ✅ Dashboard data source

**Advantages:**
- ✅ Simpler than 2 separate calls
- ✅ Consistent JSON response
- ✅ Built-in error handling
- ✅ Caching support

---

**🚀 Ready to use! Test it now:**

```bash
curl "http://localhost:8000/api/v0/ask?question=Your question here"
```
