# 🚀 Quick Start - Import n8n Workflows

## 📦 Files đã tạo

```
n8n_workflows/
├── README.md                         ← Hướng dẫn đầy đủ
├── QUICK_START.md                    ← File này
├── 01_simple_generate_sql.json       ← Test SQL generation
├── 02_generate_and_run_sql.json      ← Generate + Execute
├── 03_train_vanna_complete.json      ← Train Vanna
├── 04_webhook_chatbot.json           ← Webhook API
└── 05_scheduled_report.json          ← Daily report
```

---

## ⚡ Import trong 3 bước

### Bước 1: Mở n8n
```bash
# Nếu chưa cài n8n
npm install -g n8n

# Start n8n
n8n start

# Mở browser: http://localhost:5678
```

### Bước 2: Import Workflow

1. Click **"Workflows"** ở sidebar trái
2. Click nút **"+"** → **"Import from File"**
3. Chọn file JSON (ví dụ: `01_simple_generate_sql.json`)
4. Click **"Import"**
5. Workflow sẽ xuất hiện

### Bước 3: Test

1. Click **"Execute Workflow"** (hoặc Ctrl+Enter)
2. Xem kết quả ở các nodes
3. Done! 🎉

---

## 🎯 Workflow nào dùng trước?

### Lần đầu setup → Workflow 03
**File:** `03_train_vanna_complete.json`

**Tại sao:** Train Vanna với DDL + Documentation + SQL examples

**Cách dùng:**
1. Import workflow
2. Edit node "Set Training Data" với data của bạn
3. Execute → Vanna sẽ được train

### Test basic → Workflow 01
**File:** `01_simple_generate_sql.json`

**Tại sao:** Test generate SQL nhanh

**Cách dùng:**
1. Import workflow
2. Edit câu hỏi trong node "Set Question"
3. Execute → Xem SQL generated

### Hỏi đáp SQL → Workflow 02
**File:** `02_generate_and_run_sql.json`

**Tại sao:** Generate + Execute SQL trong 1 lần

**Cách dùng:**
1. Import workflow
2. Đảm bảo Vanna đã connect database
3. Edit câu hỏi
4. Execute → Xem data

### API cho app → Workflow 04
**File:** `04_webhook_chatbot.json`

**Tại sao:** Webhook API để integrate với apps

**Cách dùng:**
1. Import workflow
2. Activate workflow
3. Gọi webhook:
```bash
curl -X POST http://localhost:5678/webhook/vanna-chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Top 10 customers"}'
```

### Báo cáo tự động → Workflow 05
**File:** `05_scheduled_report.json`

**Tại sao:** Email report hàng ngày

**Cách dùng:**
1. Import workflow
2. Configure email settings
3. Activate workflow → Tự động chạy mỗi ngày 9 AM

---

## 🔧 Config nhanh

### Thay đổi API URL

**Tất cả workflows mặc định dùng:** `http://localhost:8000`

**Nếu dùng Railway hoặc server khác:**

1. Mở workflow
2. Click vào HTTP Request node
3. Thay URL:
```
http://localhost:8000  →  https://your-app.railway.app
```
4. Save

### Thêm Authentication

**Nếu API cần API Key:**

1. Mở HTTP Request node
2. Scroll xuống **Options**
3. Add **Header Parameters**:
   - Name: `X-API-Key`
   - Value: `your-api-key`

---

## 🧪 Test ngay

### Test 1: Generate SQL (Workflow 01)

```bash
# 1. Import 01_simple_generate_sql.json
# 2. Execute workflow
# 3. Xem output:
{
  "success": true,
  "sql": "SELECT ...",
  "cache_id": "abc123"
}
```

### Test 2: Train Vanna (Workflow 03)

```bash
# 1. Import 03_train_vanna_complete.json
# 2. Edit training data trong node "Set Training Data"
# 3. Execute workflow
# 4. Xem summary:
{
  "success": true,
  "total_items": 5,
  "breakdown": {
    "ddl": 1,
    "documentation": 1,
    "sql": 3
  }
}
```

### Test 3: Webhook (Workflow 04)

```bash
# 1. Import 04_webhook_chatbot.json
# 2. Click "Active" toggle để activate
# 3. Copy webhook URL từ Webhook node
# 4. Test với curl:

curl -X POST http://localhost:5678/webhook/vanna-chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Có bao nhiêu customers?"}'

# Response:
{
  "success": true,
  "question": "Có bao nhiêu customers?",
  "sql": "SELECT COUNT(*) FROM customers",
  "data": [{"count": 42}],
  "summary": "count: 42"
}
```

---

## ❓ Common Issues

### Issue: "Cannot GET /api/v0/generate_sql"

**Fix:** Vanna server chưa chạy

```bash
# Start Vanna server
cd /path/to/vanna
python flask_main.py
```

### Issue: "Webhook not found"

**Fix:** Workflow chưa được activate

1. Mở workflow
2. Click toggle **"Active"** ở góc trên phải
3. Refresh và thử lại

### Issue: "Training data not found"

**Fix:** Chưa train Vanna

1. Import và run workflow 03 (Train Vanna)
2. Verify với endpoint: `GET /api/v0/get_training_data`

---

## 📊 Workflow Comparison

| Workflow | Trigger | Output | Use Case |
|----------|---------|--------|----------|
| 01 | Manual | SQL string | Test & debug |
| 02 | Manual | SQL + Data | Query database |
| 03 | Manual | Training summary | Initial setup |
| 04 | Webhook | JSON API response | App integration |
| 05 | Schedule | Email report | Automation |

---

## 🎓 Next Steps

1. ✅ Import workflows
2. ✅ Test với workflow 01
3. ✅ Train với workflow 03
4. ✅ Setup webhook với workflow 04
5. ✅ Configure daily report với workflow 05

**Sau đó:**
- Customize workflows cho use case của bạn
- Add error handling
- Add logging
- Deploy n8n lên cloud (nếu cần)

---

## 📖 Resources

| Resource | Link |
|----------|------|
| Full README | `README.md` |
| n8n Docs | https://docs.n8n.io |
| Vanna API Docs | `../API_README.md` |
| n8n Integration Guide | `../N8N_INTEGRATION.md` |

---

## 💡 Tips

### Tip 1: Duplicate workflows
- Không sợ làm hỏng workflows gốc
- Right-click workflow → Duplicate
- Edit và test ở bản copy

### Tip 2: Debug với Execute Node
- Click vào node bất kỳ
- Click "Execute Node" (chỉ chạy node đó)
- Xem output nhanh

### Tip 3: Pin data để test
- Right-click node → "Pin data"
- Giữ output cố định để test downstream nodes
- Không cần chạy lại upstream nodes

### Tip 4: Use Sticky Notes
- Drag "Sticky Note" từ toolbar
- Add ghi chú, documentation trong workflow
- Giúp team hiểu workflow dễ hơn

---

**🎉 Ready to go! Import và test ngay thôi!**

Có vấn đề? Check `README.md` hoặc n8n community forum.
