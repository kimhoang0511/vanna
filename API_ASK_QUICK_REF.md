# ⚡ Quick Reference: /api/v0/ask

> One-liner examples cho API endpoint `/api/v0/ask`

## 🚀 Basic Usage

### GET Method (Simple)
```bash
curl "http://localhost:8000/api/v0/ask?question=Có bao nhiêu customers?"
```

### POST Method (Recommended)
```bash
curl -X POST http://localhost:8000/api/v0/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Top 10 customers"}'
```

---

## 📋 Common Questions

### Count total records
```bash
curl "http://localhost:8000/api/v0/ask?question=Tổng số khách hàng"
curl "http://localhost:8000/api/v0/ask?question=Có bao nhiêu đơn hàng?"
curl "http://localhost:8000/api/v0/ask?question=COUNT products"
```

### Top N queries
```bash
curl "http://localhost:8000/api/v0/ask?question=Top 10 customers by revenue"
curl "http://localhost:8000/api/v0/ask?question=Top 5 sản phẩm bán chạy nhất"
curl "http://localhost:8000/api/v0/ask?question=Top 20 orders by amount"
```

### Time-based queries
```bash
curl "http://localhost:8000/api/v0/ask?question=Doanh thu theo tháng năm 2024"
curl "http://localhost:8000/api/v0/ask?question=Đơn hàng trong tháng 10"
curl "http://localhost:8000/api/v0/ask?question=Revenue last week"
```

### Aggregations
```bash
curl "http://localhost:8000/api/v0/ask?question=Tổng doanh thu"
curl "http://localhost:8000/api/v0/ask?question=Average order value"
curl "http://localhost:8000/api/v0/ask?question=SUM sales by country"
```

---

## 🔧 With Parameters

### Allow LLM to see data
```bash
curl -X POST http://localhost:8000/api/v0/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Top products",
    "allow_llm_to_see_data": true
  }'
```

---

## 🎯 Response Handling

### Parse JSON with jq
```bash
# Get just the SQL
curl -s "http://localhost:8000/api/v0/ask?question=COUNT customers" | jq -r '.sql'

# Get just the data
curl -s "http://localhost:8000/api/v0/ask?question=COUNT customers" | jq '.data'

# Get row count
curl -s "http://localhost:8000/api/v0/ask?question=COUNT customers" | jq '.rows_count'

# Check success
curl -s "http://localhost:8000/api/v0/ask?question=COUNT customers" | jq '.success'
```

### Save to file
```bash
# Save full response
curl "http://localhost:8000/api/v0/ask?question=Top 10 customers" > response.json

# Save only data
curl -s "http://localhost:8000/api/v0/ask?question=Top 10 customers" | jq '.data' > data.json
```

---

## 🐍 Python Examples

### Basic request
```python
import requests

response = requests.get(
    "http://localhost:8000/api/v0/ask",
    params={"question": "Có bao nhiêu customers?"}
)
result = response.json()

if result['success']:
    print(f"SQL: {result['sql']}")
    print(f"Data: {result['data']}")
```

### POST request
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v0/ask",
    json={
        "question": "Top 10 by revenue",
        "allow_llm_to_see_data": False
    }
)
result = response.json()
```

### With error handling
```python
import requests

try:
    response = requests.post(
        "http://localhost:8000/api/v0/ask",
        json={"question": "Your question"},
        timeout=30
    )
    response.raise_for_status()
    result = response.json()
    
    if result['success']:
        print(f"✅ Got {result['rows_count']} rows")
        return result['data']
    else:
        print(f"❌ Error: {result['error']}")
        
except requests.exceptions.RequestException as e:
    print(f"❌ Request failed: {e}")
```

---

## 🌐 JavaScript/Node.js Examples

### Fetch API
```javascript
const response = await fetch(
  'http://localhost:8000/api/v0/ask?question=COUNT customers'
);
const result = await response.json();

if (result.success) {
  console.log('SQL:', result.sql);
  console.log('Data:', result.data);
}
```

### Axios
```javascript
const axios = require('axios');

const result = await axios.post('http://localhost:8000/api/v0/ask', {
  question: 'Top 10 customers',
  allow_llm_to_see_data: false
});

if (result.data.success) {
  console.log(result.data.data);
}
```

---

## 🔗 n8n Node Config

### HTTP Request Node
```json
{
  "method": "POST",
  "url": "http://localhost:8000/api/v0/ask",
  "authentication": "none",
  "sendBody": true,
  "bodyParameters": {
    "parameters": [
      {
        "name": "question",
        "value": "={{ $json.question }}"
      }
    ]
  }
}
```

### Access response in next node
```javascript
// Get SQL
{{ $json.sql }}

// Get data
{{ $json.data }}

// Get row count
{{ $json.rows_count }}

// Check success
{{ $json.success }}
```

---

## 📊 Compare với Old Endpoints

### Old Way (2 calls)
```bash
# Step 1
ID=$(curl -s "http://localhost:8000/api/v0/generate_sql?question=COUNT" | jq -r '.id')

# Step 2
curl "http://localhost:8000/api/v0/run_sql?id=$ID"
```

### New Way (1 call)
```bash
curl "http://localhost:8000/api/v0/ask?question=COUNT"
```

---

## 🧪 Testing

### Health check first
```bash
curl http://localhost:8000/health
```

### Test with simple question
```bash
curl "http://localhost:8000/api/v0/ask?question=SELECT 1"
```

### Test with Vietnamese
```bash
curl "http://localhost:8000/api/v0/ask?question=Có bao nhiêu?"
```

### Run test script
```bash
python test_ask_endpoint.py
```

---

## 🔐 Production Usage

### With API Key
```bash
curl "http://localhost:8000/api/v0/ask?question=COUNT" \
  -H "X-API-Key: your-secret-key"
```

### Railway/Production URL
```bash
curl "https://your-app.railway.app/api/v0/ask?question=COUNT"
```

---

## 💡 Tips

### Tip 1: URL Encode Questions
```bash
# If question has spaces/special chars
QUESTION="Top 10 customers có doanh thu > 100000"
ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$QUESTION'))")
curl "http://localhost:8000/api/v0/ask?question=$ENCODED"
```

### Tip 2: Save SQL for reuse
```bash
SQL=$(curl -s "http://localhost:8000/api/v0/ask?question=COUNT" | jq -r '.sql')
echo $SQL
```

### Tip 3: Format output
```bash
curl -s "http://localhost:8000/api/v0/ask?question=COUNT" | jq '.'
```

---

## 📚 More Info

- Full docs: [API_ASK_ENDPOINT.md](./API_ASK_ENDPOINT.md)
- Test script: [test_ask_endpoint.py](./test_ask_endpoint.py)
- Source code: [flask_main.py](./flask_main.py)

---

## ⚡ One-Liners Collection

```bash
# Production ready
alias vanna-ask='curl -s "http://localhost:8000/api/v0/ask?question="'

# Usage
vanna-ask "COUNT customers" | jq '.'
vanna-ask "Top 10 by revenue" | jq '.data'
vanna-ask "Tổng doanh thu" | jq '.sql'
```

---

**🚀 Copy & paste ready!**
