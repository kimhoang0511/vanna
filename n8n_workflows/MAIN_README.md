# 📦 n8n Workflows Collection for Vanna AI

> 5 pre-built n8n workflows để tích hợp Vanna AI SQL generation vào automation workflows

[![n8n](https://img.shields.io/badge/n8n-workflows-FF6D5A?logo=n8n)](https://n8n.io)
[![Vanna AI](https://img.shields.io/badge/Vanna-AI-blue)](https://vanna.ai)
[![JSON](https://img.shields.io/badge/format-JSON-orange)](.)

## 🎯 Tổng quan

Package này bao gồm **5 workflows n8n** ready-to-import để sử dụng Vanna AI:

1. **Simple Generate SQL** - Test SQL generation nhanh
2. **Generate & Run SQL** - Query database với natural language
3. **Train Vanna Complete** - Setup và train Vanna với data
4. **Webhook Chatbot** - API endpoint cho chatbot/apps
5. **Scheduled Report** - Email báo cáo tự động hàng ngày

## 📂 Cấu trúc

```
n8n_workflows/
│
├── 📘 Documentation (4 files)
│   ├── INDEX.md           ← Bắt đầu từ đây!
│   ├── README.md          ← Full documentation  
│   ├── QUICK_START.md     ← Quick start guide
│   └── CUSTOMIZE.md       ← Customization guide
│
├── 🔧 Workflows (5 files)
│   ├── 01_simple_generate_sql.json
│   ├── 02_generate_and_run_sql.json
│   ├── 03_train_vanna_complete.json
│   ├── 04_webhook_chatbot.json
│   └── 05_scheduled_report.json
│
└── 📋 This file
    └── SUMMARY.md
```

## 🚀 Quick Start

### Bước 1: Download workflows

```bash
# Clone repo (nếu chưa có)
git clone https://github.com/yourusername/vanna.git
cd vanna/n8n_workflows

# Hoặc download trực tiếp từ GitHub
```

### Bước 2: Start n8n

```bash
# Cài n8n (nếu chưa có)
npm install -g n8n

# Start n8n
n8n start

# Mở browser: http://localhost:5678
```

### Bước 3: Import workflow

1. Trong n8n UI, click **"Workflows"**
2. Click **"+"** → **"Import from File"**
3. Chọn file JSON (ví dụ: `01_simple_generate_sql.json`)
4. Click **"Import"**
5. Execute workflow! ✅

## 📖 Documentation

| File | Mô tả | Khi nào đọc |
|------|-------|-------------|
| **[INDEX.md](./INDEX.md)** | Overview, cheat sheet, quick links | Bắt đầu |
| **[README.md](./README.md)** | Chi tiết từng workflow | Sau khi import |
| **[QUICK_START.md](./QUICK_START.md)** | Import & test trong 5 phút | Bắt đầu nhanh |
| **[CUSTOMIZE.md](./CUSTOMIZE.md)** | Customize workflows | Khi customize |

### 🎓 Đề xuất đọc theo thứ tự:

1. **INDEX.md** - Hiểu tổng quan
2. **QUICK_START.md** - Import & test ngay
3. **README.md** - Đọc chi tiết khi cần
4. **CUSTOMIZE.md** - Khi muốn customize

## 🔧 Workflows Overview

### 1. Simple Generate SQL
**File:** `01_simple_generate_sql.json`

```
Input:  "Top 10 customers có doanh thu cao nhất"
Output: SELECT name, SUM(revenue) FROM ...
```

**Use cases:**
- ✅ Test SQL generation
- ✅ Debug prompts
- ✅ Quick SQL generation

---

### 2. Generate and Run SQL
**File:** `02_generate_and_run_sql.json`

```
Input:  "Có bao nhiêu customers?"
Output: {"count": 42}
```

**Use cases:**
- ✅ Ad-hoc queries
- ✅ Data exploration
- ✅ Business questions

---

### 3. Train Vanna Complete
**File:** `03_train_vanna_complete.json`

```
Trains with:
- DDL (schema)
- Documentation (Vietnamese)
- SQL examples (Q&A pairs)
```

**Use cases:**
- ✅ Initial setup
- ✅ Update schema
- ✅ Add training data

---

### 4. Webhook Chatbot
**File:** `04_webhook_chatbot.json`

```bash
POST /webhook/vanna-chat
Body: {"question": "..."}
Response: {"sql": "...", "data": [...]}
```

**Use cases:**
- ✅ Slack/Telegram bot
- ✅ Web app integration
- ✅ Mobile app backend
- ✅ API for external services

---

### 5. Scheduled Report
**File:** `05_scheduled_report.json`

```
Schedule: Daily at 9 AM
Action:   Generate SQL for multiple questions
Output:   HTML email report
```

**Use cases:**
- ✅ Daily/weekly reports
- ✅ Management dashboards
- ✅ Automated analytics

## 📊 Feature Matrix

| Feature | 01 | 02 | 03 | 04 | 05 |
|---------|:--:|:--:|:--:|:--:|:--:|
| Generate SQL | ✅ | ✅ | ❌ | ✅ | ✅ |
| Run SQL | ❌ | ✅ | ❌ | ✅ | ✅ |
| Train Vanna | ❌ | ❌ | ✅ | ❌ | ❌ |
| API Endpoint | ❌ | ❌ | ❌ | ✅ | ❌ |
| Email Report | ❌ | ❌ | ❌ | ❌ | ✅ |
| Error Handling | ✅ | ✅ | ✅ | ✅ | ✅ |
| Retry Logic | ✅ | ✅ | ✅ | ✅ | ✅ |

## ⚙️ Requirements

### Software
- ✅ **n8n** (v0.200.0+)
- ✅ **Vanna API** running (localhost:8000 or Railway)
- ✅ **Database** connected (for workflows 02, 04, 05)
- ✅ **Node.js** 16+ (for n8n)

### Configuration
- ✅ Vanna API URL
- ✅ Database credentials (optional)
- ✅ Email credentials (for workflow 05)
- ✅ API Key (optional, for production)

## 🧪 Testing

### Local Development

```bash
# Terminal 1: Start Vanna API
cd /path/to/vanna
python flask_main.py

# Terminal 2: Start n8n
npx n8n

# Browser: Import và test workflows
http://localhost:5678
```

### Test Sequence

1. ✅ Import workflow 01 → Test SQL generation
2. ✅ Import workflow 03 → Train Vanna
3. ✅ Import workflow 02 → Test with database
4. ✅ Import workflow 04 → Test webhook
5. ✅ Import workflow 05 → Test email (optional)

## 🎨 Customization

### Thay đổi API URL

**Development:**
```
http://localhost:8000
```

**Production (Railway):**
```
https://your-app.railway.app
```

**Cách thay đổi:**
1. Mở workflow
2. Click HTTP Request node
3. Update URL field
4. Save

### Thêm Authentication

**Mở HTTP Request node → Options → Header Parameters:**

```json
{
  "name": "X-API-Key",
  "value": "your-api-key-here"
}
```

### Customize Training Data (Workflow 03)

**Mở node "Set Training Data":**
- `train_ddl`: Update với schema của bạn
- `train_documentation`: Viết documentation tiếng Việt
- `train_sql_X`: Add SQL examples

**Chi tiết:** Xem [CUSTOMIZE.md](./CUSTOMIZE.md)

## 📋 Use Case Examples

### Use Case 1: Business Analytics Dashboard

**Workflow:** 02 (Generate & Run SQL)

**Questions:**
- "Doanh thu theo tháng năm 2024"
- "Top 10 sản phẩm bán chạy"
- "Customer churn rate tháng này"

**Integration:** Export data → Visualization tool

---

### Use Case 2: Slack Bot

**Workflow:** 04 (Webhook Chatbot)

**Flow:**
```
User asks in Slack
  ↓
Slack webhook → n8n
  ↓
n8n → Vanna API
  ↓
SQL → Database
  ↓
Results → Slack
```

---

### Use Case 3: Daily Sales Report

**Workflow:** 05 (Scheduled Report)

**Schedule:** Every day 9 AM

**Content:**
- Total revenue yesterday
- Top products
- New orders count

**Recipients:** Management team

## 🔍 Troubleshooting

### Issue: Cannot import workflow

**Cause:** Corrupted JSON

**Fix:**
- Verify JSON format
- Re-download file
- Check n8n version

---

### Issue: "Cannot connect to localhost:8000"

**Cause:** Vanna API not running

**Fix:**
```bash
cd /path/to/vanna
python flask_main.py
```

---

### Issue: Webhook returns 404

**Cause:** Workflow not activated

**Fix:**
1. Open workflow
2. Click **"Active"** toggle
3. Test again

---

### Issue: No SQL generated

**Cause:** Vanna not trained

**Fix:**
1. Import workflow 03
2. Update training data
3. Execute workflow

**Xem thêm:** [README.md - Troubleshooting](./README.md#troubleshooting)

## 📊 Stats

- **Total Files:** 10
- **Total Workflows:** 5
- **Total Nodes:** ~45
- **Documentation Pages:** 4
- **Lines of JSON:** ~1000+
- **Setup Time:** 10-30 minutes

## 🤝 Contributing

Contributions welcome! 🎉

**Ideas:**
- Add more workflows
- Improve error handling
- Add more use cases
- Better documentation
- Bug fixes

**Process:**
1. Fork repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit Pull Request

## 📝 License

MIT License - Use freely!

## 🙏 Credits

- **Vanna AI:** https://vanna.ai
- **n8n:** https://n8n.io
- **OpenAI:** GPT-4o-mini
- **BGE-M3:** Embedding model

## 📞 Support

| Channel | Link |
|---------|------|
| **Documentation** | [INDEX.md](./INDEX.md) |
| **Quick Start** | [QUICK_START.md](./QUICK_START.md) |
| **n8n Community** | https://community.n8n.io |
| **GitHub Issues** | [Issues page](../../issues) |

## ⭐ Show Your Support

Nếu project này hữu ích, hãy give a star! ⭐

## 🗺️ Roadmap

- [ ] More workflows (6-10)
- [ ] Video tutorials
- [ ] Advanced error handling
- [ ] Integration examples (Slack, Discord, etc.)
- [ ] Multi-language support
- [ ] Cloud deployment guides

## 📈 Version History

- **v1.0** (Nov 2025) - Initial release
  - 5 workflows
  - Full documentation
  - Production-ready

---

## 🚀 Get Started Now!

```bash
1. cd n8n_workflows/
2. Read INDEX.md or QUICK_START.md
3. Import 01_simple_generate_sql.json
4. Execute workflow
5. Done! 🎉
```

**Documentation:** [INDEX.md](./INDEX.md) | [QUICK_START.md](./QUICK_START.md) | [README.md](./README.md)

---

**Made with ❤️ for the n8n + Vanna AI community**

🇻🇳 **Vietnamese support built-in!**
