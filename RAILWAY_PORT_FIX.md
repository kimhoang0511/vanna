# ⚠️ Railway Deployment Issue - PORT Configuration

## 🔴 Vấn đề:

App đang bị lỗi 502 vì:

```
PORT=8000  ❌ SAI!
```

## ✅ Giải pháp:

Railway **TỰ ĐỘNG** set `PORT` variable. Bạn KHÔNG NÊN override nó!

### Bước 1: Xóa PORT variable

1. Vào Railway Dashboard
2. Chọn service `vanna-production`
3. Click tab **"Variables"**
4. Tìm biến `PORT` 
5. Click **Delete** (icon thùng rác)
6. App sẽ tự động restart

### Bước 2: Verify

Railway sẽ tự động set PORT (ví dụ: 3000, 5000, etc.)

App code đã đúng:
```python
port = int(os.getenv("PORT", "8000"))  # Sẽ đọc từ Railway
```

## 📋 Environment Variables cần có:

### ✅ Required:
- `OPENAI_API_KEY` - ✅ Đã có
- `HUGGINGFACE_API_KEY` - ✅ Đã có
- `DB_HOST` - ✅ Đã có
- `DB_PORT` - ✅ Đã có
- `DB_NAME` - ✅ Đã có
- `DB_USER` - ✅ Đã có
- `DB_PASSWORD` - ✅ Đã có

### ⚙️ Config:
- `DEBUG=False` - ✅ Đã có
- `ALLOW_LLM_TO_SEE_DATA=True` - ✅ Đã có
- `VANNA_MODEL=gpt-4o-mini` - ✅ Đã có
- `VANNA_TEMPERATURE=0.7` - ✅ Đã có

### ❌ XÓA:
- `PORT=8000` - ❌ XÓA BIẾN NÀY! Railway sẽ tự set

### 🎨 Optional (OK):
- `VANNA_TITLE` - ✅ OK
- `VANNA_SUBTITLE` - ✅ OK
- `API_KEY` - ✅ OK
- `ENVIRONMENT` - ✅ OK
- `ALLOWED_ORIGINS` - ✅ OK

## 🧪 Test sau khi fix:

Sau khi xóa `PORT` và restart:

```bash
# Test health check
curl https://vanna-production.up.railway.app/health

# Test web UI
curl https://vanna-production.up.railway.app/

# Test API
curl https://vanna-production.up.railway.app/api/v0/get_config
```

Hoặc chạy:
```bash
python3 test_railway_deployment.py
```

## 📊 Railway Logs

Sau khi fix, check logs để verify:

```
✅ Vanna initialized successfully!
✅ Database connected successfully!
✅ Server is ready!
🌐 Web UI: http://0.0.0.0:XXXX  (XXXX = Railway's auto PORT)
```

---

**TL;DR: XÓA biến `PORT=8000` trong Railway Variables. Railway sẽ tự set PORT!**
