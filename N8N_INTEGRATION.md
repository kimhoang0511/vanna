# Hướng dẫn sử dụng Vietnamese Vanna API với n8n

## 📋 Tổng quan

API Server cho phép gọi các hàm của VietnameseVanna từ bên ngoài qua HTTP REST API.

**Use cases:**
- Tích hợp với n8n workflows
- Webhook từ external services
- Chatbot integration (Slack, Discord, Telegram)
- Custom web applications

---

## 🚀 Khởi động API Server

### 1. Cài đặt dependencies

```bash
pip install fastapi uvicorn pydantic
```

### 2. Chạy server

```bash
python api_server.py
```

Server sẽ chạy tại: `http://localhost:8000`

**Swagger UI (Documentation):** http://localhost:8000/docs  
**Health check:** http://localhost:8000/health

---

## 📡 API Endpoints

### 1. **POST /init** - Khởi tạo Vanna

**Body:**
```json
{
  "openai_api_key": "sk-proj-xxx...",
  "huggingface_api_key": "hf_xxx...",
  "model": "gpt-4o-mini",
  "dialect": "PostgreSQL",
  "temperature": 0.7,
  "n_results_sql": 5,
  "n_results_ddl": 3,
  "n_results_documentation": 7
}
```

**Response:**
```json
{
  "success": true,
  "message": "Vanna initialized successfully",
  "data": {
    "model": "gpt-4o-mini",
    "dialect": "PostgreSQL"
  }
}
```

---

### 2. **POST /connect/postgres** - Kết nối PostgreSQL

**Body:**
```json
{
  "host": "localhost",
  "port": 5432,
  "database": "mydb",
  "user": "postgres",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Connected to PostgreSQL successfully",
  "data": {
    "database": "mydb",
    "host": "localhost"
  }
}
```

---

### 3. **POST /train/ddl** - Train với DDL

**Body:**
```json
{
  "ddl": "CREATE TABLE public.sale (\n    id INTEGER PRIMARY KEY,\n    name TEXT,\n    date DATE,\n    sales MONEY\n);"
}
```

**Response:**
```json
{
  "success": true,
  "message": "DDL trained successfully",
  "data": {
    "training_id": "abc123-ddl"
  }
}
```

---

### 4. **POST /train/documentation** - Train với Documentation (tiếng Việt)

**Body:**
```json
{
  "documentation": "Bảng sale chứa dữ liệu bán hàng:\n- id: Mã giao dịch\n- name: Tên sản phẩm\n- sales: Doanh thu (dùng sales::numeric để tính toán)"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Documentation trained successfully",
  "data": {
    "training_id": "def456-doc"
  }
}
```

---

### 5. **POST /train/sql** - Train với SQL Examples

**Body:**
```json
{
  "question": "Tổng doanh thu là bao nhiêu?",
  "sql": "SELECT SUM(sales::numeric) as total_revenue FROM public.sale"
}
```

**Response:**
```json
{
  "success": true,
  "message": "SQL example trained successfully",
  "data": {
    "training_id": "ghi789-sql"
  }
}
```

---

### 6. **POST /generate_sql** - Generate SQL từ câu hỏi

**Body:**
```json
{
  "question": "Top 10 sản phẩm bán chạy nhất?",
  "allow_llm_to_see_data": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "SQL generated successfully",
  "data": {
    "sql": "SELECT name, COUNT(*) as total FROM public.sale GROUP BY name ORDER BY total DESC LIMIT 10",
    "question": "Top 10 sản phẩm bán chạy nhất?"
  }
}
```

---

### 7. **POST /execute_sql** - Execute SQL

**Body:**
```json
{
  "sql": "SELECT COUNT(*) as total FROM public.sale"
}
```

**Response:**
```json
{
  "success": true,
  "message": "SQL executed successfully",
  "data": {
    "sql": "SELECT COUNT(*) as total FROM public.sale",
    "rows": 1,
    "data": [
      {"total": 42}
    ]
  }
}
```

---

### 8. **POST /ask** - All-in-one (Generate + Execute)

**Body:**
```json
{
  "question": "Có bao nhiêu giao dịch trong tháng 10?",
  "allow_llm_to_see_data": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Question answered successfully",
  "data": {
    "question": "Có bao nhiêu giao dịch trong tháng 10?",
    "sql": "SELECT COUNT(*) FROM sale WHERE EXTRACT(MONTH FROM date) = 10",
    "rows": 1,
    "data": [
      {"count": 15}
    ]
  }
}
```

---

### 9. **GET /training_data** - Lấy training data

**Response:**
```json
{
  "success": true,
  "message": "Training data retrieved successfully",
  "data": {
    "count": 5,
    "data": [
      {
        "id": "abc-ddl",
        "training_data_type": "ddl",
        "content": "CREATE TABLE..."
      }
    ]
  }
}
```

---

## 🔧 Sử dụng với n8n

### Workflow Setup

#### Node 1: Initialize Vanna
- **Node Type:** HTTP Request
- **Method:** POST
- **URL:** `http://localhost:8000/init`
- **Body:**
```json
{
  "openai_api_key": "{{$env.OPENAI_API_KEY}}",
  "huggingface_api_key": "{{$env.HUGGINGFACE_API_KEY}}",
  "model": "gpt-4o-mini",
  "dialect": "PostgreSQL"
}
```

#### Node 2: Connect to Database
- **Node Type:** HTTP Request
- **Method:** POST
- **URL:** `http://localhost:8000/connect/postgres`
- **Body:**
```json
{
  "host": "localhost",
  "port": 5432,
  "database": "mydb",
  "user": "{{$env.DB_USER}}",
  "password": "{{$env.DB_PASSWORD}}"
}
```

#### Node 3: Train with Data (Optional)
- **Node Type:** HTTP Request
- **Method:** POST
- **URL:** `http://localhost:8000/train/documentation`
- **Body:**
```json
{
  "documentation": "Bảng sale chứa dữ liệu bán hàng..."
}
```

#### Node 4: Ask Question
- **Node Type:** HTTP Request
- **Method:** POST
- **URL:** `http://localhost:8000/ask`
- **Body:**
```json
{
  "question": "{{$json.question}}",
  "allow_llm_to_see_data": false
}
```

#### Node 5: Process Result
- **Node Type:** Code
- **JavaScript:**
```javascript
const response = $input.item.json;

if (response.success) {
  return {
    question: response.data.question,
    sql: response.data.sql,
    rows: response.data.rows,
    result: response.data.data
  };
} else {
  throw new Error(response.message);
}
```

---

## 📝 Example n8n Workflow JSON

```json
{
  "name": "Vietnamese Vanna SQL Generator",
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "position": [250, 300],
      "parameters": {
        "httpMethod": "POST",
        "path": "ask-sql",
        "responseMode": "responseNode"
      }
    },
    {
      "name": "Call Vanna API",
      "type": "n8n-nodes-base.httpRequest",
      "position": [450, 300],
      "parameters": {
        "method": "POST",
        "url": "http://localhost:8000/ask",
        "bodyParametersUi": {
          "parameter": [
            {
              "name": "question",
              "value": "={{$json.body.question}}"
            }
          ]
        },
        "options": {
          "timeout": 30000
        }
      }
    },
    {
      "name": "Return Response",
      "type": "n8n-nodes-base.respondToWebhook",
      "position": [650, 300],
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{$json}}"
      }
    }
  ],
  "connections": {
    "Webhook": {
      "main": [[{"node": "Call Vanna API", "type": "main", "index": 0}]]
    },
    "Call Vanna API": {
      "main": [[{"node": "Return Response", "type": "main", "index": 0}]]
    }
  }
}
```

---

## 🔐 Security Best Practices

### 1. Environment Variables

Đừng hardcode API keys. Dùng environment variables:

```bash
export OPENAI_API_KEY="sk-proj-xxx"
export HUGGINGFACE_API_KEY="hf_xxx"
export DB_PASSWORD="password123"
```

### 2. API Authentication (Production)

Thêm authentication vào API:

```python
from fastapi import Header, HTTPException

API_KEY = os.environ.get('API_KEY')

async def verify_token(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key

@app.post("/generate_sql", dependencies=[Depends(verify_token)])
async def generate_sql(request: GenerateSQLRequest):
    ...
```

### 3. CORS Configuration

Trong production, giới hạn origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],  # ← Chỉ định domain
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
```

---

## 🐳 Deploy với Docker

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "api_server.py"]
```

### requirements.txt

```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
psycopg2-binary==2.9.9
pandas==2.1.3
chromadb==0.4.18
openai==1.3.7
huggingface-hub==0.19.4
numpy==1.26.2
```

### Build & Run

```bash
docker build -t vanna-api .
docker run -p 8000:8000 \
  -e OPENAI_API_KEY="sk-xxx" \
  -e HUGGINGFACE_API_KEY="hf_xxx" \
  vanna-api
```

---

## 🧪 Testing với cURL

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Initialize
```bash
curl -X POST http://localhost:8000/init \
  -H "Content-Type: application/json" \
  -d '{
    "openai_api_key": "sk-xxx",
    "huggingface_api_key": "hf_xxx",
    "model": "gpt-4o-mini"
  }'
```

### 3. Train Documentation
```bash
curl -X POST http://localhost:8000/train/documentation \
  -H "Content-Type: application/json" \
  -d '{
    "documentation": "Bảng sale chứa dữ liệu bán hàng"
  }'
```

### 4. Generate SQL
```bash
curl -X POST http://localhost:8000/generate_sql \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Tổng doanh thu là bao nhiêu?",
    "allow_llm_to_see_data": false
  }'
```

### 5. Ask Question (All-in-one)
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Top 5 sản phẩm bán chạy?"
  }'
```

---

## 📊 Monitoring & Logging

### Add logging to API

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.post("/generate_sql")
async def generate_sql(request: GenerateSQLRequest):
    logger.info(f"Generate SQL request: {request.question}")
    try:
        sql = vn_instance.generate_sql(request.question)
        logger.info(f"Generated SQL: {sql}")
        return SuccessResponse(...)
    except Exception as e:
        logger.error(f"Error generating SQL: {str(e)}")
        raise
```

---

## 🔄 Complete n8n Workflow Example

### Chatbot Integration (Telegram/Slack)

```
1. Trigger: Telegram/Slack Message
   ↓
2. HTTP Request: POST /ask
   Body: {"question": "{{$json.message}}"}
   ↓
3. Function: Format Response
   Code: 
   const data = $json.data;
   return {
     text: `SQL: ${data.sql}\n\nResults:\n${JSON.stringify(data.data, null, 2)}`
   };
   ↓
4. Telegram/Slack: Send Reply
```

### Scheduled Reports

```
1. Cron: Every Monday 9am
   ↓
2. HTTP Request: POST /ask
   Body: {"question": "Tổng doanh thu tuần trước?"}
   ↓
3. Email: Send Report
   Subject: "Weekly Sales Report"
   Body: "{{$json.data}}"
```

---

## 🎯 Best Practices

1. **Initialize once** - Gọi `/init` một lần khi start workflow
2. **Reuse connection** - Không connect lại database mỗi request
3. **Cache training data** - Train data persistent trong ChromaDB
4. **Error handling** - Always check `success` field trong response
5. **Timeout** - Set reasonable timeout (30-60s) cho LLM calls
6. **Rate limiting** - Implement rate limiting trong production

---

## 📖 Related Files

- `api_server.py` - API server code
- `vietnamese_vanna.py` - Vietnamese-optimized Vanna class
- `bge_m3_embedding.py` - BGE-M3 embedding function
- `PROMPT_CONSTRUCTION.md` - Prompt engineering guide

---

## 💡 Tips

- Dùng `/ask` endpoint cho use cases đơn giản (1 request = SQL + results)
- Dùng `/generate_sql` + `/execute_sql` riêng để có control tốt hơn
- Train trước với DDL và documentation để có kết quả tốt nhất
- Set `allow_llm_to_see_data=true` nếu cần intermediate SQL

---

## 🐛 Troubleshooting

### Error: "Vanna not initialized"
**Solution:** Call `/init` endpoint first

### Error: "Connection failed"
**Solution:** Check database credentials và network

### Error: "Rate limit exceeded"
**Solution:** Add delay between requests hoặc upgrade OpenAI plan

### Slow response
**Solution:** 
- Reduce `n_results_*` parameters
- Use faster model (gpt-3.5-turbo)
- Cache common queries
