# 🚂 Deploy Vietnamese Vanna API lên Railway.com

## 📋 Tổng quan

Hướng dẫn deploy dự án Vietnamese Vanna API lên Railway.com và kết nối với n8n.

**Railway.com** là platform cloud giúp deploy ứng dụng nhanh chóng, hỗ trợ:
- Auto-deploy từ GitHub
- PostgreSQL database built-in
- Free tier: $5 credit/tháng
- HTTPS tự động
- Environment variables management

---

## 🎯 Bước 1: Chuẩn bị Code

### 1.1. Kiểm tra các file cần thiết

Đảm bảo bạn có đầy đủ các file sau:

```
vanna/
├── api_server.py              # Main API server
├── vietnamese_vanna.py        # Custom Vanna class
├── bge_m3_embedding.py        # BGE-M3 embedding
├── requirements.txt           # Python dependencies
├── Procfile                   # Railway start command
├── railway.json              # Railway configuration
├── runtime.txt               # Python version
├── .env.example              # Environment variables template
└── .gitignore                # Git ignore file
```

### 1.2. Update `.gitignore`

Thêm vào `.gitignore`:

```gitignore
# Environment variables
.env

# ChromaDB
chroma.sqlite3
*.db

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environment
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
```

---

## 🔧 Bước 2: Push code lên GitHub

### 2.1. Tạo Git repository (nếu chưa có)

```bash
cd /Users/kimtvh/IdeaProjects/vanna
git init
git add .
git commit -m "Initial commit: Vietnamese Vanna API"
```

### 2.2. Tạo repository trên GitHub

1. Vào https://github.com/new
2. Repository name: `vanna-api` (hoặc tên bất kỳ)
3. Description: "Vietnamese-optimized SQL generation API using Vanna"
4. Public hoặc Private (tùy bạn)
5. **KHÔNG** check "Initialize with README" (vì đã có sẵn)
6. Click "Create repository"

### 2.3. Push lên GitHub

```bash
git remote add origin https://github.com/kimhoang0511/vanna-api.git
git branch -M main
git push -u origin main
```

---

## 🚀 Bước 3: Deploy lên Railway

### 3.1. Tạo account Railway

1. Vào https://railway.app
2. Click "Login" → Sign up with GitHub
3. Authorize Railway to access GitHub

### 3.2. Tạo New Project

1. Click "New Project"
2. Chọn "Deploy from GitHub repo"
3. Chọn repository `vanna-api` (hoặc tên bạn đặt)
4. Click "Deploy Now"

Railway sẽ tự động:
- Detect Python project
- Install dependencies từ `requirements.txt`
- Run command từ `Procfile`

### 3.3. Cấu hình Environment Variables

1. Trong Railway project, click vào tab "Variables"
2. Thêm các biến sau:

```env
# OpenAI API Key
OPENAI_API_KEY= "xxx"
# Hugging Face API Key
HUGGINGFACE_API_KEY="xxx"

# PostgreSQL Connection (Railway hoặc external)
DB_HOST=nozomi.proxy.rlwy.net
DB_PORT=26750
DB_NAME=railway
DB_USER=postgres
DB_PASSWORD=aLBazSQAKvyCNllyngDjoiTdMIjHLTDC

# API Configuration
API_KEY=your-secret-api-key-here-change-this
ENVIRONMENT=production
ALLOWED_ORIGINS=*

# Port (Railway tự set, không cần thêm)
# PORT=8000
```

**Lưu ý:**
- `PORT` sẽ được Railway tự động set
- `ALLOWED_ORIGINS` set thành `*` cho dev, production nên giới hạn domain
- `API_KEY` nên dùng password generator: https://passwordsgenerator.net/

### 3.4. Generate Domain

1. Trong Railway project, click tab "Settings"
2. Scroll xuống "Domains"
3. Click "Generate Domain"
4. Railway sẽ tạo URL kiểu: `https://vanna-api-production.up.railway.app`

**Hoặc dùng custom domain:**
1. Click "Custom Domain"
2. Nhập domain của bạn (ví dụ: `api.yourdomain.com`)
3. Cấu hình DNS records theo hướng dẫn

---

## 🧪 Bước 4: Test API trên Railway

### 4.1. Health Check

```bash
curl https://your-app.railway.app/health
```

Response:
```json
{
  "status": "healthy",
  "service": "Vietnamese Vanna API",
  "initialized": false,
  "environment": "production",
  "model": null
}
```

### 4.2. Initialize Vanna

```bash
curl -X POST https://your-app.railway.app/init \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key-here-change-this" \
  -d '{}'
```

**Lưu ý:** API keys đã được set trong environment variables nên không cần truyền trong request body.

Response:
```json
{
  "success": true,
  "message": "Vanna initialized successfully",
  "data": {
    "model": "gpt-4o-mini",
    "dialect": "PostgreSQL",
    "temperature": 0.7
  }
}
```

### 4.3. Connect to PostgreSQL

```bash
curl -X POST https://your-app.railway.app/connect/postgres \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key-here-change-this" \
  -d '{}'
```

Response:
```json
{
  "success": true,
  "message": "Connected to PostgreSQL successfully",
  "data": {
    "database": "railway",
    "host": "nozomi.proxy.rlwy.net",
    "port": 26750
  }
}
```

### 4.4. Test Generate SQL (Vietnamese)

```bash
curl -X POST https://your-app.railway.app/generate_sql \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key-here-change-this" \
  -d '{
    "question": "Có bao nhiêu giao dịch?",
    "allow_llm_to_see_data": false
  }'
```

Response:
```json
{
  "success": true,
  "message": "SQL generated successfully",
  "data": {
    "sql": "SELECT COUNT(*) FROM sale",
    "question": "Có bao nhiêu giao dịch?"
  }
}
```

---

## 🔗 Bước 5: Kết nối với n8n

### 5.1. Setup n8n Cloud hoặc Self-hosted

**Option A: n8n Cloud (dễ nhất)**
1. Vào https://n8n.io
2. Sign up for free account
3. Tạo new workflow

**Option B: Self-hosted**
```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

### 5.2. Tạo n8n Workflow

#### Node 1: Webhook Trigger

1. Add node → Trigger → Webhook
2. Configuration:
   - **HTTP Method:** POST
   - **Path:** `ask-sql`
   - **Response Mode:** When Last Node Finishes

#### Node 2: Initialize Vanna (Execute Once)

1. Add node → HTTP Request
2. Configuration:
   - **Method:** POST
   - **URL:** `https://your-app.railway.app/init`
   - **Authentication:** Generic Credential Type
     - **Generic Auth Type:** Header Auth
     - **Name:** `X-API-Key`
     - **Value:** `your-secret-api-key-here-change-this`
   - **Body Content Type:** JSON
   - **Specify Body:** Using JSON
   - **JSON:** `{}`

**Note:** Chỉ cần chạy node này 1 lần. Sau đó có thể disable hoặc xóa.

#### Node 3: Connect to Database (Execute Once)

1. Add node → HTTP Request
2. Configuration:
   - **Method:** POST
   - **URL:** `https://your-app.railway.app/connect/postgres`
   - **Authentication:** Same as Node 2
   - **JSON:** `{}`

**Note:** Chỉ cần chạy node này 1 lần sau khi initialize.

#### Node 4: Ask Question (Main Logic)

1. Add node → HTTP Request
2. Configuration:
   - **Method:** POST
   - **URL:** `https://your-app.railway.app/ask`
   - **Authentication:** Same as Node 2
   - **JSON:**
   ```json
   {
     "question": "={{$json.body.question}}",
     "allow_llm_to_see_data": false
   }
   ```

#### Node 5: Format Response

1. Add node → Code
2. Configuration:
   - **Language:** JavaScript
   - **Code:**
   ```javascript
   const response = $input.item.json;
   
   if (response.success) {
     return {
       success: true,
       question: response.data.question,
       sql: response.data.sql,
       rows: response.data.rows,
       data: response.data.data
     };
   } else {
     throw new Error(response.message);
   }
   ```

#### Node 6: Return Response

1. Add node → Respond to Webhook
2. Configuration:
   - **Respond With:** JSON
   - **Response Body:** `={{$json}}`

### 5.3. Test n8n Workflow

**Activate workflow** → Copy webhook URL (ví dụ: `https://your-n8n.app/webhook/ask-sql`)

Test với curl:

```bash
curl -X POST https://your-n8n.app/webhook/ask-sql \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Tổng doanh thu là bao nhiêu?"
  }'
```

Response:
```json
{
  "success": true,
  "question": "Tổng doanh thu là bao nhiêu?",
  "sql": "SELECT SUM(sales::numeric) FROM sale",
  "rows": 1,
  "data": [
    {"sum": "163000.00"}
  ]
}
```

---

## 📊 Bước 6: Monitor & Logs

### 6.1. Railway Logs

1. Trong Railway project, click tab "Deployments"
2. Click vào deployment hiện tại
3. Click "View Logs"

Bạn sẽ thấy logs như:
```
🚀 Vietnamese Vanna API Server
📝 Documentation: http://localhost:8000/docs
🔍 Health check: http://localhost:8000/health
🌐 Port: 8000
🔐 API Key: Enabled
```

### 6.2. Railway Metrics

1. Tab "Metrics" để xem:
   - CPU usage
   - Memory usage
   - Network traffic
   - Request count

### 6.3. Add Custom Logging

Update `api_server.py` để add logging:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.post("/generate_sql", response_model=SuccessResponse)
async def generate_sql(request: GenerateSQLRequest):
    logger.info(f"Generate SQL request: {request.question}")
    # ... existing code
```

---

## 🔐 Bước 7: Security Best Practices

### 7.1. Environment Variables

✅ **DO:**
- Store API keys in Railway environment variables
- Use strong API_KEY (32+ characters, random)
- Rotate API keys định kỳ

❌ **DON'T:**
- Commit API keys vào Git
- Share API keys qua Slack/Email
- Use default/weak API keys

### 7.2. CORS Configuration

**Development:**
```env
ALLOWED_ORIGINS=*
```

**Production:**
```env
ALLOWED_ORIGINS=https://your-n8n.app,https://yourdomain.com
```

### 7.3. Rate Limiting (Optional)

Install:
```bash
pip install slowapi
```

Add to `api_server.py`:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/generate_sql")
@limiter.limit("10/minute")
async def generate_sql(request: Request, ...):
    # ... existing code
```

---

## 🚨 Troubleshooting

### Issue 1: Railway build fails

**Error:** `Could not find a version that satisfies the requirement ...`

**Solution:** Check `requirements.txt`, remove version constraints:
```
# Before
chromadb==0.4.18

# After
chromadb>=0.4.18
```

### Issue 2: Out of memory

**Error:** `Killed` in logs

**Solution:** 
1. Railway Settings → Resources → Increase memory
2. Optimize embedding model (reduce batch size)

### Issue 3: API timeout

**Error:** `504 Gateway Timeout`

**Solution:**
1. Railway Settings → Deployment → Increase timeout to 60s
2. Add caching for common queries

### Issue 4: CORS error from n8n

**Error:** `Access-Control-Allow-Origin` error

**Solution:** Add n8n domain to `ALLOWED_ORIGINS`:
```env
ALLOWED_ORIGINS=https://your-n8n.app,*
```

### Issue 5: ChromaDB persistence

**Problem:** Training data lost after restart

**Solution:** Use Railway Volumes:
1. Railway Settings → Volumes → Add Volume
2. Mount path: `/app/chroma_db`
3. Update `api_server.py`:
   ```python
   config = {
       'chroma_db_impl': 'duckdb+parquet',
       'persist_directory': '/app/chroma_db'
   }
   ```

---

## 💰 Cost Estimation

### Railway Free Tier
- **$5 credit/month** (automatically applied)
- ~500 hours of execution time
- Good for: Development, testing, low-traffic apps

### Railway Pro Plan ($20/month)
- Unlimited execution time
- Higher resources
- Priority support
- Good for: Production apps

### Additional costs
- **OpenAI API:** ~$0.002 per 1K tokens (GPT-4o-mini)
- **Hugging Face:** Free for inference API
- **PostgreSQL:** Railway included (or use external)

**Example calculation:**
- 1000 SQL generations/month
- Average 500 tokens per request
- Cost: 1000 × 500 / 1000 × $0.002 = **$1/month**

---

## 🎓 Next Steps

### 1. Add Training Endpoints
Create n8n workflows to auto-train when:
- New table created → Train DDL
- Documentation updated → Train documentation
- Good query found → Train SQL example

### 2. Add Monitoring
- Set up Railway alerts (email/Slack)
- Track API usage metrics
- Monitor OpenAI costs

### 3. Improve Performance
- Add Redis caching for common queries
- Batch processing for multiple questions
- Load balancing with multiple instances

### 4. Add Features
- SQL validation before execution
- Query history & analytics
- User authentication & authorization
- Multi-database support

---

## 📚 Related Files

- `api_server.py` - Main API server code
- `N8N_INTEGRATION.md` - n8n integration guide
- `requirements.txt` - Python dependencies
- `Procfile` - Railway start command
- `.env.example` - Environment variables template

---

## 🆘 Support

### Railway
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway
- Status: https://status.railway.app

### Vietnamese Vanna API
- GitHub: https://github.com/kimhoang0511/vanna
- Issues: https://github.com/kimhoang0511/vanna/issues

---

## ✅ Deployment Checklist

- [ ] Push code to GitHub
- [ ] Create Railway project
- [ ] Add environment variables
- [ ] Generate domain
- [ ] Test health endpoint
- [ ] Initialize Vanna
- [ ] Connect to database
- [ ] Test SQL generation
- [ ] Create n8n workflow
- [ ] Test end-to-end
- [ ] Set up monitoring
- [ ] Configure CORS for production
- [ ] Rotate API keys
- [ ] Document custom domain (if any)
- [ ] Add team members (if any)

---

## 🎉 Done!

Bạn đã successfully deploy Vietnamese Vanna API lên Railway và kết nối với n8n!

**API URL:** `https://your-app.railway.app`  
**n8n Webhook:** `https://your-n8n.app/webhook/ask-sql`

Try it:
```bash
curl -X POST https://your-n8n.app/webhook/ask-sql \
  -H "Content-Type: application/json" \
  -d '{"question": "Có bao nhiêu giao dịch hôm nay?"}'
```
