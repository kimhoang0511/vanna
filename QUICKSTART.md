# 🚀 Quick Start Guide - Deploy lên Railway

## Bước 1: Commit & Push lên GitHub

```bash
cd /Users/kimtvh/IdeaProjects/vanna

# Add all files
git add .

# Commit
git commit -m "Add Railway deployment files and API server"

# Push to GitHub
git push origin vanna_dev
```

## Bước 2: Deploy lên Railway

### 2.1. Tạo Account
1. Vào https://railway.app
2. Click "Login" → Sign in with GitHub
3. Authorize Railway

### 2.2. Create New Project
1. Click "New Project"
2. Chọn "Deploy from GitHub repo"
3. Chọn repository: **kimhoang0511/vanna**
4. Chọn branch: **vanna_dev**
5. Click "Deploy Now"

### 2.3. Thêm Environment Variables

Trong Railway project → Tab "Variables" → Click "Raw Editor" → Paste:

```env
OPENAI_API_KEY="xxx"
HUGGINGFACE_API_KEY="xxx"
DB_HOST=nozomi.proxy.rlwy.net
DB_PORT=26750
DB_NAME=railway
DB_USER=postgres
DB_PASSWORD=aLBazSQAKvyCNllyngDjoiTdMIjHLTDC
API_KEY=vanna-secret-2024-change-this-in-production
ENVIRONMENT=production
ALLOWED_ORIGINS=*
```

Click "Add" để save.

### 2.4. Generate Domain
1. Tab "Settings" → Scroll xuống "Domains"
2. Click "Generate Domain"
3. Copy URL (ví dụ: `https://vanna-production.up.railway.app`)

## Bước 3: Test API

```bash
# Replace with your Railway URL
export RAILWAY_URL="https://vanna-production.up.railway.app"

# Test health
curl $RAILWAY_URL/health

# Initialize Vanna
curl -X POST $RAILWAY_URL/init \
  -H "Content-Type: application/json" \
  -H "X-API-Key: vanna-secret-2024-change-this-in-production"

# Connect to database
curl -X POST $RAILWAY_URL/connect/postgres \
  -H "Content-Type: application/json" \
  -H "X-API-Key: vanna-secret-2024-change-this-in-production"

# Test Vietnamese question
curl -X POST $RAILWAY_URL/ask \
  -H "Content-Type: application/json" \
  -H "X-API-Key: vanna-secret-2024-change-this-in-production" \
  -d '{"question": "Có bao nhiêu giao dịch?"}'
```

## Bước 4: Kết nối với n8n

### Option A: n8n Cloud
1. Vào https://n8n.cloud → Sign up
2. Tạo new workflow
3. Add nodes theo hướng dẫn trong `N8N_INTEGRATION.md`

### Option B: n8n Self-hosted
```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

### n8n Workflow - Quick Setup

**Node 1: Webhook**
- Path: `ask-sql`
- Method: POST

**Node 2: HTTP Request**
- URL: `https://vanna-production.up.railway.app/ask`
- Method: POST
- Authentication:
  - Type: Header Auth
  - Name: `X-API-Key`
  - Value: `vanna-secret-2024-change-this-in-production`
- Body:
  ```json
  {
    "question": "={{$json.body.question}}"
  }
  ```

**Node 3: Respond to Webhook**
- Response: `={{$json}}`

Test webhook:
```bash
curl -X POST https://your-n8n.app/webhook/ask-sql \
  -H "Content-Type: application/json" \
  -d '{"question": "Tổng doanh thu?"}'
```

## Troubleshooting

### ❌ Build fails
- Check Railway logs: Tab "Deployments" → Click deployment → "View Logs"
- Common issue: Missing dependencies in `requirements.txt`

### ❌ API returns 400
- Vanna not initialized → Call `/init` first
- Database not connected → Call `/connect/postgres` first

### ❌ CORS error
- Add your domain to `ALLOWED_ORIGINS`:
  ```env
  ALLOWED_ORIGINS=https://your-n8n.app,https://yourdomain.com
  ```

### ❌ 403 Forbidden
- Check `X-API-Key` header matches `API_KEY` env variable

## Next Steps

1. ✅ Deploy to Railway
2. ✅ Test API endpoints
3. ✅ Create n8n workflow
4. 📖 Read full docs:
   - [API_README.md](API_README.md) - API usage
   - [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) - Detailed deployment guide
   - [N8N_INTEGRATION.md](N8N_INTEGRATION.md) - n8n workflows

## Support

- GitHub Issues: https://github.com/kimhoang0511/vanna/issues
- Railway Docs: https://docs.railway.app
- n8n Docs: https://docs.n8n.io

---

**🎉 Chúc bạn deploy thành công!**
