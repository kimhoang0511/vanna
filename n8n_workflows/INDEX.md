# 📦 n8n Workflows for Vanna AI - Complete Package

## 📂 Files Overview

```
n8n_workflows/
│
├── 📘 Documentation
│   ├── README.md              ← Hướng dẫn đầy đủ (bắt đầu từ đây!)
│   ├── QUICK_START.md         ← Quick start guide (3 steps)
│   ├── CUSTOMIZE.md           ← Customize workflows
│   └── INDEX.md               ← File này
│
└── 🔧 Workflows (JSON)
    ├── 01_simple_generate_sql.json
    ├── 02_generate_and_run_sql.json
    ├── 03_train_vanna_complete.json
    ├── 04_webhook_chatbot.json
    └── 05_scheduled_report.json
```

---

## 🚀 Quick Links

| File | Description | When to use |
|------|-------------|-------------|
| [README.md](./README.md) | **Đọc đầu tiên!** Full documentation | Tìm hiểu chi tiết |
| [QUICK_START.md](./QUICK_START.md) | Import & test trong 3 bước | Bắt đầu nhanh |
| [CUSTOMIZE.md](./CUSTOMIZE.md) | Customize cho use case của bạn | Sau khi test OK |

---

## 🔧 Workflows Cheat Sheet

### 1️⃣ Simple Generate SQL
**File:** `01_simple_generate_sql.json`

**What:** Chuyển câu hỏi → SQL

**Flow:** 
```
Manual → Set Question → Generate SQL → Format
```

**Use when:** 
- ✅ Test SQL generation
- ✅ Debug prompt issues
- ✅ Quick SQL generation

**Customize:**
- Thay đổi question trong node "Set Question"

---

### 2️⃣ Generate and Run SQL
**File:** `02_generate_and_run_sql.json`

**What:** Chuyển câu hỏi → SQL → Execute → Data

**Flow:**
```
Manual → Set Question → Generate SQL → Run SQL → Format Results
```

**Use when:**
- ✅ Query database với natural language
- ✅ Ad-hoc data analysis
- ✅ Test full pipeline

**Customize:**
- Thay đổi question
- Add data validation
- Format output khác

---

### 3️⃣ Train Vanna Complete
**File:** `03_train_vanna_complete.json`

**What:** Train Vanna với DDL + Docs + SQL examples

**Flow:**
```
Manual → Set Training Data → Clear Old Data → 
Train DDL → Train Docs → Train SQL (x3) → 
Verify → Summary
```

**Use when:**
- ✅ First time setup
- ✅ Update schema
- ✅ Add new training data

**Customize:**
- Update DDL với schema mới
- Add thêm SQL examples
- Update documentation

---

### 4️⃣ Webhook Chatbot
**File:** `04_webhook_chatbot.json`

**What:** API endpoint cho chatbot/apps

**Flow:**
```
Webhook (POST /vanna-chat) → Validate → 
Generate SQL → Run SQL → Format → Respond JSON
```

**Use when:**
- ✅ Slack/Telegram bot
- ✅ Web app integration
- ✅ Mobile app backend
- ✅ API for external services

**Customize:**
- Add authentication
- Add rate limiting
- Custom response format

**Test:**
```bash
curl -X POST http://localhost:5678/webhook/vanna-chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Top 10 customers"}'
```

---

### 5️⃣ Scheduled Report
**File:** `05_scheduled_report.json`

**What:** Email báo cáo tự động hàng ngày

**Flow:**
```
Schedule (9 AM daily) → Set Config → 
Split Questions → Generate SQL → Run SQL (loop) →
Aggregate → Format HTML Email → Send Email
```

**Use when:**
- ✅ Daily/weekly reports
- ✅ Management dashboards
- ✅ Automated analytics

**Customize:**
- Change schedule (cron)
- Update questions list
- Custom email template
- Add charts/images

---

## 📊 Workflow Comparison Matrix

| Feature | 01 | 02 | 03 | 04 | 05 |
|---------|----|----|----|----|---- |
| **Trigger** | Manual | Manual | Manual | Webhook | Schedule |
| **Generate SQL** | ✅ | ✅ | ❌ | ✅ | ✅ |
| **Run SQL** | ❌ | ✅ | ❌ | ✅ | ✅ |
| **Train Vanna** | ❌ | ❌ | ✅ | ❌ | ❌ |
| **API Response** | ❌ | ❌ | ❌ | ✅ | ❌ |
| **Email** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Loop/Batch** | ❌ | ❌ | ✅ | ❌ | ✅ |
| **Complexity** | Low | Low | High | Medium | High |
| **Setup Time** | 1 min | 2 min | 5 min | 3 min | 10 min |

---

## 🎯 Use Case → Workflow

| Use Case | Recommended Workflow | Notes |
|----------|---------------------|-------|
| Test SQL generation | 01 | Nhanh nhất |
| Query database | 02 | Cần database connected |
| Initial setup | 03 | Chạy 1 lần |
| Chatbot integration | 04 | Cần activate webhook |
| Daily reports | 05 | Configure email |
| Custom app | 04 (modify) | Customize response format |
| Batch processing | 05 (modify) | Remove email, add export |
| Analytics dashboard | 02 + 04 | Combine both |

---

## ⚙️ Configuration Checklist

### Before Import
- [ ] n8n đang chạy (`npx n8n` hoặc `n8n start`)
- [ ] Vanna API server đang chạy (`python flask_main.py`)
- [ ] Database đã connected (cho workflow 02, 04, 05)
- [ ] Vanna đã được train (workflow 03)

### After Import
- [ ] Update API URLs (nếu không dùng localhost)
- [ ] Add authentication (nếu cần)
- [ ] Test manual workflows (01, 02, 03)
- [ ] Activate webhooks (04)
- [ ] Configure email (05)
- [ ] Set schedule (05)

### Production Ready
- [ ] Update URLs to production
- [ ] Add API key authentication
- [ ] Configure error handling
- [ ] Add logging/monitoring
- [ ] Test all workflows
- [ ] Document customizations

---

## 🔄 Typical Workflow Order

### First Time Setup

```
1. Import 03_train_vanna_complete.json
   ↓
2. Edit training data
   ↓
3. Execute → Vanna trained ✅
   ↓
4. Import 01_simple_generate_sql.json
   ↓
5. Test SQL generation ✅
   ↓
6. Import 02_generate_and_run_sql.json
   ↓
7. Test with database ✅
   ↓
8. Import 04_webhook_chatbot.json
   ↓
9. Activate → Test API ✅
   ↓
10. Import 05_scheduled_report.json
    ↓
11. Configure email → Activate ✅
```

### Daily Usage

```
Development:
  → Test new questions với 01
  → Query data với 02

Production:
  → Apps call 04 (webhook)
  → Daily reports tự động (05)
  
Update Training:
  → Run 03 when schema changes
```

---

## 📖 Documentation Guide

### Start Here
1. **[README.md](./README.md)** - Full documentation
   - Import guide
   - Detailed explanation của từng workflow
   - Troubleshooting
   - API configuration

### Quick Start
2. **[QUICK_START.md](./QUICK_START.md)** - 3 steps to start
   - Import trong 3 bước
   - Test workflows
   - Common issues
   - Tips & tricks

### Customization
3. **[CUSTOMIZE.md](./CUSTOMIZE.md)** - Make it yours
   - Change questions
   - Update URLs
   - Add authentication
   - Custom templates
   - Error handling
   - Logging

---

## 🧪 Testing Sequence

### Development Environment

```bash
# Terminal 1: Start Vanna
cd /path/to/vanna
python flask_main.py

# Terminal 2: Start n8n
npx n8n
```

**Test order:**

1. ✅ Import 01 → Execute → Verify SQL generated
2. ✅ Import 03 → Execute → Verify training successful
3. ✅ Import 02 → Execute → Verify data returned
4. ✅ Import 04 → Activate → Test với curl
5. ✅ Import 05 → Change schedule to 1 minute → Test email

### Production Environment

```bash
# Deploy Vanna to Railway
# Deploy n8n to cloud (optional)

# Update all URLs in workflows
# Add authentication
# Test all workflows again
# Monitor executions
```

---

## 💡 Pro Tips

### Tip 1: Start Simple
- Import workflow 01 trước
- Test basic functionality
- Sau đó mới import advanced workflows

### Tip 2: Duplicate Before Edit
- Right-click workflow → Duplicate
- Edit bản copy
- Giữ original làm backup

### Tip 3: Use Sticky Notes
- Add notes trong workflow
- Document customizations
- Help team understand flow

### Tip 4: Version Control
- Export workflows thường xuyên
- Commit to Git
- Tag releases
- Document changes

### Tip 5: Monitor Executions
- n8n UI → Executions tab
- Check failed executions
- Debug từng node
- Fix issues

---

## 🆘 Quick Help

### Issue → Solution

| Problem | Solution | Where |
|---------|----------|-------|
| Cannot import | Check JSON format | - |
| Cannot execute | Check Vanna server running | Terminal |
| No SQL generated | Run training (workflow 03) | - |
| No data returned | Check database connected | Vanna logs |
| Webhook 404 | Activate workflow | n8n UI |
| Email not sent | Configure Gmail OAuth | Node settings |
| Slow execution | Check timeout settings | HTTP Request options |
| Cache issues | Clear browser cache | Browser |

### Get Help

1. **Check documentation** (README.md)
2. **Check logs** (n8n executions + Vanna server)
3. **Test with curl** (webhook endpoints)
4. **n8n Community** (https://community.n8n.io)
5. **GitHub Issues** (this repo)

---

## 📦 Package Contents

```
Total: 8 files

Documentation:
  ✅ INDEX.md          (this file)
  ✅ README.md         (full guide)
  ✅ QUICK_START.md    (quick guide)
  ✅ CUSTOMIZE.md      (customization guide)

Workflows:
  ✅ 01_simple_generate_sql.json
  ✅ 02_generate_and_run_sql.json
  ✅ 03_train_vanna_complete.json
  ✅ 04_webhook_chatbot.json
  ✅ 05_scheduled_report.json
```

---

## 🎓 Learning Path

### Beginner
1. Read QUICK_START.md
2. Import workflow 01
3. Test với manual trigger
4. Understand flow

### Intermediate
1. Import workflow 03 (training)
2. Import workflow 02 (with database)
3. Customize questions
4. Add error handling

### Advanced
1. Import workflow 04 (webhook)
2. Integrate với apps
3. Import workflow 05 (scheduled)
4. Customize everything
5. Add monitoring
6. Deploy to production

---

## 📊 Stats

- **Total Workflows:** 5
- **Total Nodes:** ~45
- **Lines of Code (JSON):** ~1000
- **Documentation Pages:** 4
- **Setup Time:** 10-30 minutes
- **Maintenance:** Low

---

## 🚀 Next Steps

### After Import

1. ✅ **Test** all workflows locally
2. ✅ **Customize** cho use case của bạn
3. ✅ **Document** changes
4. ✅ **Deploy** to production
5. ✅ **Monitor** executions
6. ✅ **Iterate** and improve

### Contribute

Found a bug? Have an improvement?

1. Fork repository
2. Make changes
3. Test thoroughly
4. Submit Pull Request

---

## 📞 Support

- 📖 **Documentation:** Start with [README.md](./README.md)
- 💬 **n8n Community:** https://community.n8n.io
- 🐛 **Issues:** GitHub Issues
- 📧 **Email:** (your contact)

---

**🎉 You're all set! Start with README.md or QUICK_START.md**

Happy automating! 🚀
