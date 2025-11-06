# ✅ Railway Deployment Checklist

## 📦 Code đã sẵn sàng!

✅ Code đã được push lên GitHub: `vanna_dev` branch
✅ Commit: `Deploy Flask VannaFlaskApp to Railway - Full setup with Web UI`

## 🚀 Deploy trên Railway.com (5 phút)

### **Bước 1: Login & Create Project** (1 phút)

1. Truy cập: https://railway.app
2. Login với GitHub account
3. Click: **"New Project"**
4. Chọn: **"Deploy from GitHub repo"**
5. Chọn repository: **`kimhoang0511/vanna`**
6. Chọn branch: **`vanna_dev`**

✅ Railway sẽ tự động detect `railway.json` và `Procfile`

---

### **Bước 2: Add Environment Variables** (3 phút)

Click vào service → **Variables** tab → Add từng biến:

#### 🔑 **Required (BẮT BUỘC):**

```
OPENAI_API_KEY
```
Giá trị: `sk-proj-xxxxxxxxxxxxx` (lấy từ OpenAI dashboard)

```
HUGGINGFACE_API_KEY
```
Giá trị: `hf_xxxxxxxxxxxxx` (lấy từ HuggingFace settings)

#### 🗄️ **Database (nếu đã có PostgreSQL):**

```
DB_HOST
```
Giá trị: `your-db.railway.app`

```
DB_PORT
```
Giá trị: `5432`

```
DB_NAME
```
Giá trị: `railway` hoặc tên database của bạn

```
DB_USER
```
Giá trị: `postgres`

```
DB_PASSWORD
```
Giá trị: password từ Railway PostgreSQL

#### ⚙️ **Configuration:**

```
DEBUG
```
Giá trị: `False`

```
ALLOW_LLM_TO_SEE_DATA
```
Giá trị: `True`

#### 🎨 **UI Customization (Optional):**

```
VANNA_TITLE
```
Giá trị: `Vietnamese Vanna SQL Assistant`

```
VANNA_SUBTITLE
```
Giá trị: `AI-powered SQL generation với hỗ trợ tiếng Việt 🇻🇳`

---

### **Bước 3: Add PostgreSQL Database** (Optional - 1 phút)

Nếu chưa có database:

1. Trong Railway project, click: **"New"** → **"Database"** → **"Add PostgreSQL"**
2. Railway tự động tạo và set các variables:
   - `PGHOST`
   - `PGPORT`
   - `PGDATABASE`
   - `PGUSER`
   - `PGPASSWORD`
3. Copy các giá trị này vào `DB_*` variables ở Bước 2

---

### **Bước 4: Deploy!** (Tự động)

✅ Railway sẽ tự động:
1. Detect Python project
2. Install dependencies từ `requirements.txt`
3. Run command: `python flask_main.py`
4. Expose service với public URL

---

### **Bước 5: Get Your URL** (10 giây)

1. Trong Railway service, click tab: **"Settings"**
2. Tìm section: **"Domains"**
3. Click: **"Generate Domain"**
4. Copy URL dạng: `https://your-app-name.up.railway.app`

---

## 🎯 Verify Deployment

### 1. Check Logs

Click vào service → **"Deployments"** tab → Latest deployment → **"View Logs"**

Tìm các dòng:
```
✅ Vanna initialized successfully!
✅ Database connected successfully!
✅ Server is ready!
🌐 Web UI: http://0.0.0.0:8000
```

### 2. Test Web UI

Truy cập: `https://your-app-name.up.railway.app/`

Bạn sẽ thấy:
- Web interface của VannaFlaskApp
- Có thể hỏi câu hỏi bằng tiếng Việt
- Xem training data
- Generate charts

### 3. Test API

```bash
# Generate SQL
curl "https://your-app-name.up.railway.app/api/v0/generate_sql?question=Top 10 khách hàng"

# Get training data
curl "https://your-app-name.up.railway.app/api/v0/get_training_data"
```

---

## 🐛 Troubleshooting

### ❌ Build Failed

**Check:**
- Logs có error gì không?
- `requirements.txt` syntax đúng chưa?
- Python version compatible?

**Fix:** Trigger rebuild bằng cách push dummy commit

---

### ❌ Cannot connect to database

**Check:**
- DB_* environment variables đúng chưa?
- PostgreSQL service có running không?

**Fix:** Verify và update DB variables

---

### ❌ API Key errors

**Check:**
- Environment variables đã set chưa?
- API keys còn valid không?
- OpenAI account có credits không?

**Fix:** 
- Restart service sau khi update variables
- Verify API keys trên OpenAI/HuggingFace dashboard

---

## 📊 Railway Free Tier

- ✅ 500 hours/month execution time
- ✅ $5 monthly credit
- ✅ Unlimited projects
- ✅ 1GB RAM per service
- ✅ Shared CPU

**Upgrade nếu cần:**
- Hobby plan: $5/month + usage
- Pro plan: $20/month + usage

---

## 🎉 Success!

Sau khi deploy thành công:

✅ Web UI: `https://your-app-name.up.railway.app/`
✅ API: `https://your-app-name.up.railway.app/api/v0/`
✅ Swagger docs: Tự động có sẵn
✅ WebSocket debug: Available nếu DEBUG=True

---

## 📚 Next Steps

1. **Upload training data:**
   - Qua Web UI hoặc
   - POST to `/api/v0/train`

2. **Test với câu hỏi tiếng Việt:**
   ```
   "Top 10 khách hàng có doanh thu cao nhất"
   "Tổng số đơn hàng trong tháng 10"
   "Sản phẩm bán chạy nhất"
   ```

3. **Monitor usage:**
   - Railway dashboard
   - OpenAI usage dashboard

4. **Share với team:**
   - Copy URL và share
   - Hoặc setup custom domain

---

## 🆘 Cần hỗ trợ?

- 📖 Docs chi tiết: `RAILWAY_FLASK_DEPLOYMENT.md`
- 🌐 Railway Status: https://status.railway.app
- 💬 Railway Discord: https://discord.gg/railway
- 🐛 Issues: https://github.com/kimhoang0511/vanna/issues

---

**Happy Deploying! 🚀**

Railway URL của bạn: `_______________________________________`
(Ghi lại để dễ nhớ)
