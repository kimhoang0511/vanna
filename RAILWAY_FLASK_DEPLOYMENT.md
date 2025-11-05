# Railway Deployment Guide - Flask VannaFlaskApp

Hướng dẫn deploy `flask_main.py` (VannaFlaskApp) lên Railway.com

## 📋 Prerequisites

- Tài khoản Railway.com (đăng ký miễn phí tại https://railway.app)
- GitHub repository đã được push code
- API keys: OpenAI và Hugging Face

## 🚀 Bước 1: Chuẩn bị Repository

### Files đã được cấu hình:

✅ **Procfile**
```
web: python flask_main.py
```

✅ **railway.json**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python flask_main.py"
  }
}
```

✅ **requirements.txt**
- Đã thay FastAPI → Flask
- Thêm flask-cors, flask-sock, flasgger
- Giữ nguyên các dependencies khác

✅ **runtime.txt**
```
python-3.11.6
```

### Commit và push code:

```bash
git add .
git commit -m "Deploy VannaFlaskApp to Railway"
git push origin vanna_dev
```

## 🌐 Bước 2: Deploy trên Railway

### A. Tạo Project mới

1. Đăng nhập vào https://railway.app
2. Click **"New Project"**
3. Chọn **"Deploy from GitHub repo"**
4. Chọn repository: `kimhoang0511/vanna`
5. Chọn branch: `vanna_dev`

### B. Cấu hình Environment Variables

Trong Railway dashboard, vào **Variables** tab và thêm:

#### **Required Variables:**

```bash
# OpenAI API Key (BẮT BUỘC)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx

# Hugging Face API Key (BẮT BUỘC)
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxx

# Database Connection
DB_HOST=your-db-host.railway.app
DB_PORT=5432
DB_NAME=railway
DB_USER=postgres
DB_PASSWORD=your-db-password

# Server Configuration
PORT=8000
DEBUG=False
ALLOW_LLM_TO_SEE_DATA=True

# Vanna Configuration
VANNA_MODEL=gpt-4o-mini
VANNA_TEMPERATURE=0.7
VANNA_N_RESULTS_SQL=5
VANNA_N_RESULTS_DDL=3
VANNA_N_RESULTS_DOCUMENTATION=7

# UI Customization (Optional)
VANNA_TITLE=Vietnamese Vanna SQL Assistant
VANNA_SUBTITLE=AI-powered SQL generation với hỗ trợ tiếng Việt 🇻🇳
```

#### **Railway Auto Variables:**
Railway tự động cung cấp:
- `PORT` - Port để bind (nếu không set thì dùng 8000)
- `RAILWAY_ENVIRONMENT` - environment name

### C. Setup PostgreSQL Database (Optional)

Nếu chưa có database:

1. Trong Railway project, click **"New"** → **"Database"** → **"Add PostgreSQL"**
2. Railway sẽ tự động tạo và cung cấp connection variables:
   - `PGHOST`
   - `PGPORT`
   - `PGDATABASE`
   - `PGUSER`
   - `PGPASSWORD`
3. Copy các giá trị này vào `DB_*` variables ở trên

### D. Deploy

Railway sẽ tự động:
1. ✅ Build từ `requirements.txt`
2. ✅ Chạy `python flask_main.py`
3. ✅ Expose service với domain công khai

## 🔍 Bước 3: Verify Deployment

### Check Deployment Logs

Trong Railway dashboard, xem **Deployments** tab:

```
🔧 Initializing BGE-M3 Embedding Function...
🔧 Initializing Vanna with Vietnamese support...
✅ Vanna initialized successfully!
🔗 Connecting to PostgreSQL: xxx.railway.app:5432/railway...
✅ Database connected successfully!
🌐 Starting Flask server...
✅ Server is ready!
🌐 Web UI:          http://0.0.0.0:8000
📝 API Endpoints:   http://0.0.0.0:8000/api/v0/
```

### Access URLs

Railway sẽ cung cấp URL dạng:
```
https://your-app-name.up.railway.app
```

**Endpoints:**
- Web UI: `https://your-app-name.up.railway.app/`
- API: `https://your-app-name.up.railway.app/api/v0/`
- Swagger: `https://your-app-name.up.railway.app/api/v0/` (tự động)

### Test API

```bash
# Generate SQL
curl "https://your-app-name.up.railway.app/api/v0/generate_sql?question=Top 10 khách hàng"

# Get training data
curl "https://your-app-name.up.railway.app/api/v0/get_training_data"

# Health check (nếu có)
curl "https://your-app-name.up.railway.app/health"
```

## 🎯 Bước 4: Quản lý và Monitoring

### View Logs

```bash
# Trong Railway dashboard, click vào service
# → Chọn tab "Deployments"
# → Click vào deployment hiện tại
# → Xem "Logs" để theo dõi realtime
```

### Metrics

Railway cung cấp:
- CPU usage
- Memory usage
- Network traffic
- Request count

### Restart Service

```bash
# Trong Railway dashboard:
# → Click vào service
# → Click "..." menu
# → Chọn "Restart"
```

## 🔧 Troubleshooting

### Issue 1: Module not found

**Lỗi:** `ModuleNotFoundError: No module named 'vanna'`

**Giải pháp:**
- Kiểm tra `requirements.txt` đã có `vanna==0.7.9`
- Trigger rebuild: push commit mới hoặc restart deployment

### Issue 2: Database connection failed

**Lỗi:** `⚠️ Warning: Could not connect to database`

**Giải pháp:**
- Kiểm tra DB_* environment variables
- Verify PostgreSQL service đang running
- Check network/firewall settings

### Issue 3: Port binding error

**Lỗi:** `Address already in use`

**Giải pháp:**
- Railway tự động set PORT variable
- Đảm bảo `flask_main.py` đọc từ `os.getenv("PORT", "8000")`

### Issue 4: API Keys not working

**Lỗi:** `ValueError: OPENAI_API_KEY not found`

**Giải pháp:**
- Verify environment variables trong Railway dashboard
- Restart service sau khi thêm/sửa variables
- Check API key còn valid và có credits

## 📊 Performance Tips

### 1. Enable Production Mode

```bash
DEBUG=False
```

### 2. Optimize ChromaDB

ChromaDB sẽ tạo persistent storage trong Railway:
- Data sẽ được lưu giữa các deploys
- Nếu cần clear cache: xóa và redeploy

### 3. Monitor Resource Usage

- Railway free tier: 500 hours/month, $5 credit
- Production tier: unlimited hours, pay-as-you-go
- Monitor usage trong dashboard

### 4. Custom Domain (Optional)

```bash
# Trong Railway dashboard:
# → Settings
# → Domains
# → Add custom domain
# → Follow DNS setup instructions
```

## 🔐 Security Best Practices

1. **Never commit API keys** - Always use environment variables
2. **Use strong DB passwords** - Railway auto-generates secure passwords
3. **Enable CORS properly** - Configure allowed origins
4. **Monitor API usage** - Check OpenAI/HF usage regularly
5. **Set rate limits** - Consider implementing rate limiting

## 📚 Additional Resources

- Railway Docs: https://docs.railway.app
- Vanna Docs: https://vanna.ai/docs
- Flask Docs: https://flask.palletsprojects.com

## 🆘 Support

Nếu gặp vấn đề:
1. Check Railway logs: `Deployments → Latest deployment → Logs`
2. Check Railway status: https://status.railway.app
3. Railway Discord: https://discord.gg/railway
4. GitHub Issues: https://github.com/kimhoang0511/vanna/issues

## 📝 Next Steps

Sau khi deploy thành công:

1. ✅ Test Web UI
2. ✅ Upload training data qua UI hoặc API
3. ✅ Test câu hỏi tiếng Việt
4. ✅ Monitor performance
5. ✅ Share URL với team

---

**Happy Deploying! 🚀**
