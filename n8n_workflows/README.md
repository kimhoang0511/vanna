# 📦 n8n Workflow Collection for Vanna AI

> Pre-built n8n workflows để sử dụng Vanna AI SQL generation API

## 📋 Danh sách Workflows

| Workflow | Mô tả | Use Case |
|----------|-------|----------|
| `01_simple_generate_sql.json` | Generate SQL đơn giản | Test và debug |
| `02_generate_and_run_sql.json` | Generate + Execute SQL | Hỏi đáp SQL cơ bản |
| `03_train_vanna_complete.json` | Train Vanna với data | Setup và training |
| `04_webhook_chatbot.json` | Webhook chatbot API | Integration với apps |
| `05_scheduled_report.json` | Báo cáo tự động hàng ngày | Automation & reporting |

---

## 🚀 Cách sử dụng

### Bước 1: Import vào n8n

1. Mở n8n UI (thường là `http://localhost:5678`)
2. Click **"Workflows"** ở sidebar
3. Click nút **"Import from File"** hoặc **"Add workflow"** → **"Import"**
4. Chọn file JSON từ thư mục `n8n_workflows/`
5. Click **"Import"**

### Bước 2: Cấu hình

**Thay đổi URL endpoints:**

Tất cả workflows đều sử dụng `http://localhost:8000` mặc định.

Nếu bạn deploy lên Railway hoặc server khác, cần thay đổi URL trong các HTTP Request nodes:

```
http://localhost:8000  →  https://your-app.railway.app
```

**Cách thay đổi nhanh:**
1. Mở workflow
2. Click vào từng **HTTP Request node**
3. Thay đổi field **URL**
4. Save workflow

### Bước 3: Activate

1. Click nút **"Active"** toggle ở góc trên phải
2. Workflow sẽ bắt đầu hoạt động (đối với webhooks và schedules)

---

## 📝 Chi tiết từng Workflow

### 01 - Simple Generate SQL

**Mục đích:** Test generate SQL từ câu hỏi

**Nodes:**
- ✅ Manual Trigger
- ✅ Set Question
- ✅ Generate SQL
- ✅ Format Output

**Cách dùng:**
1. Import workflow
2. Mở node "Set Question"
3. Thay đổi câu hỏi trong field `question`
4. Click **"Execute Workflow"**
5. Xem kết quả ở node "Format Output"

**Output:**
```json
{
  "success": true,
  "cache_id": "abc123",
  "sql": "SELECT ...",
  "type": "sql"
}
```

---

### 02 - Generate and Run SQL

**Mục đích:** Generate SQL và execute ngay

**Nodes:**
- ✅ Manual Trigger
- ✅ Set Question
- ✅ Generate SQL (GET /api/v0/generate_sql)
- ✅ Run SQL (GET /api/v0/run_sql)
- ✅ Format Results

**Cách dùng:**
1. Import workflow
2. Đảm bảo Vanna đã kết nối database
3. Thay đổi câu hỏi trong "Set Question"
4. Execute workflow
5. Xem data trong "Format Results"

**Output:**
```json
{
  "success": true,
  "question": "...",
  "sql": "SELECT ...",
  "rows_count": 10,
  "data": [...]
}
```

**⚠️ Lưu ý:** Workflow này cần database đã được connect.

---

### 03 - Train Vanna (Complete)

**Mục đích:** Train Vanna với DDL, Documentation, và SQL examples

**Flow:**
```
Manual Trigger
    ↓
Set Training Data (DDL, docs, SQL examples)
    ↓
Clear Training Data (⚠️ Xóa data cũ)
    ↓
Train DDL
    ↓
Train Documentation
    ↓
Train SQL Example 1, 2, 3 (parallel)
    ↓
Verify Training Data
    ↓
Training Summary
```

**Cách dùng:**
1. Import workflow
2. Mở node **"Set Training Data"**
3. Thay đổi training data:
   - `train_ddl`: DDL của bảng
   - `train_documentation`: Mô tả bằng tiếng Việt
   - `train_sql_question_X`: Câu hỏi mẫu
   - `train_sql_X`: SQL tương ứng
4. Execute workflow
5. Kiểm tra summary ở cuối

**Output:**
```json
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

**⚠️ Quan trọng:** Node "Clear Training Data" sẽ **XÓA TẤT CẢ** training data cũ.

---

### 04 - Webhook Chatbot

**Mục đích:** API endpoint cho chatbot hoặc external apps

**Webhook URL:** `http://your-n8n-url/webhook/vanna-chat`

**Request:**
```bash
curl -X POST http://localhost:5678/webhook/vanna-chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Top 10 customers"}'
```

**Response:**
```json
{
  "success": true,
  "question": "Top 10 customers",
  "sql": "SELECT ...",
  "data": [...],
  "rows_count": 10,
  "summary": "Tìm thấy 10 kết quả.\n\n1. ..."
}
```

**Flow:**
```
Webhook Trigger (POST /vanna-chat)
    ↓
Validate Input (check question not empty)
    ├─ Valid → Generate SQL → Run SQL → Format → Respond
    └─ Invalid → Return Error 400
```

**Use cases:**
- Slack bot integration
- Telegram bot
- Custom web app
- Mobile app backend

**⚠️ Production tips:**
- Add authentication (API key header)
- Add rate limiting
- Log all requests

---

### 05 - Scheduled Report (Daily)

**Mục đích:** Gửi email báo cáo tự động hàng ngày

**Schedule:** Mỗi ngày lúc 9:00 AM (cron: `0 9 * * *`)

**Flow:**
```
Schedule Trigger (9 AM daily)
    ↓
Set Report Config (questions, email settings)
    ↓
Split Questions (iterate)
    ↓
For each question:
    - Generate SQL
    - Run SQL
    ↓
Aggregate Results
    ↓
Format Email (HTML with tables)
    ↓
Send Email
```

**Cách dùng:**
1. Import workflow
2. Mở node **"Set Report Config"**:
   - `report_questions`: Array của câu hỏi (JSON string)
   - `email_to`: Email người nhận
   - `email_subject`: Tiêu đề email
3. Configure node **"Send Email"**:
   - Option 1: Sử dụng Gmail node (cần OAuth)
   - Option 2: Thay bằng SMTP node
4. Activate workflow

**Thay đổi schedule:**

Mở node "Schedule Trigger" → Edit cron expression:

| Schedule | Cron |
|----------|------|
| Mỗi giờ | `0 * * * *` |
| Mỗi ngày 9 AM | `0 9 * * *` |
| Thứ 2 hàng tuần 9 AM | `0 9 * * 1` |
| Ngày 1 hàng tháng | `0 9 1 * *` |

**Email output:**
- HTML formatted
- Tables với borders
- SQL queries
- Summary statistics

**⚠️ Lưu ý:** 
- Node "Send Email" mặc định **disabled**
- Cần configure Gmail OAuth hoặc thay bằng SMTP

---

## ⚙️ Configuration Guide

### API URL Configuration

**Localhost (Development):**
```
http://localhost:8000/api/v0/generate_sql
http://localhost:8000/api/v0/run_sql
http://localhost:8000/api/v0/train
```

**Railway (Production):**
```
https://your-app.railway.app/api/v0/generate_sql
https://your-app.railway.app/api/v0/run_sql
https://your-app.railway.app/api/v0/train
```

### Authentication

Nếu API có authentication (X-API-Key header):

1. Mở HTTP Request node
2. Scroll xuống **"Options"**
3. Click **"Add Option"** → **"Header Parameters"**
4. Add header:
   - Name: `X-API-Key`
   - Value: `your-api-key-here`

### Timeout Settings

Tất cả HTTP Request nodes đã set timeout = 30s.

Để thay đổi:
1. Mở HTTP Request node
2. Scroll xuống **"Options"**
3. Set **"Timeout"** (milliseconds)

### Error Handling

Workflows đã có retry logic:
- Max tries: 3
- Wait between tries: 1000ms (1s)

Để thay đổi:
1. Mở HTTP Request node
2. Options → Retry On Fail
3. Configure settings

---

## 🧪 Testing Workflows

### Test Locally

**Bước 1:** Start Vanna API server
```bash
cd /path/to/vanna
python flask_main.py
```

**Bước 2:** Start n8n
```bash
npx n8n
```

**Bước 3:** Import và test workflow

### Test với Production URL

1. Thay đổi URL trong all HTTP Request nodes
2. Test với Manual Trigger workflows trước
3. Khi OK → Test Webhook và Schedule workflows

---

## 🔍 Troubleshooting

### Issue 1: "Cannot connect to localhost:8000"

**Giải pháp:**
- Check Vanna server đang chạy: `curl http://localhost:8000/health`
- Nếu server on Railway → thay URL trong workflows

### Issue 2: "Webhook không hoạt động"

**Giải pháp:**
- Check n8n đang chạy
- Verify webhook URL: `http://localhost:5678/webhook/vanna-chat`
- Check webhook trong n8n UI có "Active" không

### Issue 3: "SQL generation failed"

**Giải pháp:**
- Check Vanna đã được train chưa (run workflow 03)
- Check API logs
- Test với simple question trước

### Issue 4: "Email không gửi được"

**Giải pháp:**
- Node "Send Email" mặc định disabled
- Configure Gmail OAuth credentials
- Hoặc thay bằng SMTP node

---

## 📚 Resources

- **n8n Documentation:** https://docs.n8n.io
- **Vanna Documentation:** https://vanna.ai/docs
- **API Documentation:** `../API_README.md`
- **n8n Integration Guide:** `../N8N_INTEGRATION.md`

---

## 🤝 Contributing

Muốn thêm workflows mới?

1. Tạo workflow trong n8n UI
2. Export as JSON
3. Add vào thư mục này
4. Update README
5. Create Pull Request

---

## 📝 Workflow Template Structure

```json
{
  "name": "Workflow Name",
  "nodes": [
    {
      "parameters": {...},
      "id": "unique-id",
      "name": "Node Name",
      "type": "n8n-nodes-base.nodeType",
      "position": [x, y]
    }
  ],
  "connections": {...},
  "active": false
}
```

---

## ✅ Checklist Import

- [ ] Downloaded all JSON files
- [ ] Imported into n8n
- [ ] Updated API URLs (if needed)
- [ ] Configured authentication (if needed)
- [ ] Tested Manual Trigger workflows
- [ ] Tested Webhook workflows
- [ ] Configured email settings (for workflow 05)
- [ ] Activated webhooks and schedules

---

**🎉 Happy Automating with Vanna + n8n!**

Nếu có vấn đề, check:
1. n8n logs
2. Vanna API logs
3. Network/firewall settings
4. This README troubleshooting section
