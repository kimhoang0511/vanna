# 🚀 Quick Start - Deploy Flask VannaFlaskApp to Railway

## ✅ Đã hoàn thành:

### 1. **File chính:**
- ✅ `flask_main.py` - Flask app với VannaFlaskApp
- ✅ `Procfile` - Railway start command: `python flask_main.py`
- ✅ `railway.json` - Railway config
- ✅ `requirements.txt` - Đã cập nhật Flask dependencies

### 2. **Scripts tiện ích:**
- ✅ `test_railway_flask.sh` - Test local trước khi deploy
- ✅ `deploy_railway.sh` - Quick commit & push

### 3. **Documentation:**
- ✅ `RAILWAY_FLASK_DEPLOYMENT.md` - Hướng dẫn chi tiết

## 🎯 Deploy ngay lập tức:

### **Option 1: Dùng script tự động**

```bash
# Commit và push code
./deploy_railway.sh
```

### **Option 2: Manual**

```bash
# 1. Add và commit
git add .
git commit -m "Deploy Flask VannaFlaskApp to Railway"
git push origin vanna_dev

# 2. Truy cập Railway
# https://railway.app
```

## 🔧 Railway Setup (3 bước):

### **Bước 1: Create Project**
1. Login vào https://railway.app
2. **New Project** → **Deploy from GitHub repo**
3. Chọn: `kimhoang0511/vanna` branch `vanna_dev`

### **Bước 2: Environment Variables**

Thêm vào Railway Variables:

```bash
# Required
OPENAI_API_KEY=sk-proj-xxxxx
HUGGINGFACE_API_KEY=hf_xxxxx

# Database (nếu dùng Railway PostgreSQL)
DB_HOST=xxx.railway.app
DB_PORT=5432
DB_NAME=railway
DB_USER=postgres
DB_PASSWORD=xxxxx

# Config
DEBUG=False
ALLOW_LLM_TO_SEE_DATA=True
```

### **Bước 3: Deploy**

Railway tự động deploy! ✅

## 🌐 Access App:

Sau khi deploy:
- **Web UI**: `https://your-app.up.railway.app/`
- **API**: `https://your-app.up.railway.app/api/v0/`
- **Swagger**: Tự động có sẵn

## 📊 Tính năng:

✅ Web UI đầy đủ (VannaFlaskApp)
✅ REST API endpoints
✅ Swagger documentation
✅ WebSocket debug console
✅ Auto cache
✅ Generate SQL từ tiếng Việt
✅ Execute SQL
✅ Generate charts
✅ Training data management
✅ Follow-up questions
✅ Auto-fix SQL errors

## 🧪 Test Local trước khi deploy:

```bash
# 1. Tạo .env file
cp .env.example .env
# Sửa API keys trong .env

# 2. Test local
./test_railway_flask.sh
# hoặc
python flask_main.py

# 3. Truy cập
http://localhost:8000
```

## 📚 Docs:

- Chi tiết: `RAILWAY_FLASK_DEPLOYMENT.md`
- VannaFlaskApp Guide: `VANNAFLASKAPP_GUIDE.md`

---

**Bạn đã sẵn sàng deploy! 🚀**
