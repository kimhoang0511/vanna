# 🎨 Customize n8n Workflows

> Hướng dẫn customize workflows cho use case của bạn

## 📋 Table of Contents

1. [Thay đổi câu hỏi](#thay-đổi-câu-hỏi)
2. [Thay đổi URL endpoints](#thay-đổi-url-endpoints)
3. [Thêm Authentication](#thêm-authentication)
4. [Customize Training Data](#customize-training-data)
5. [Thay đổi Schedule](#thay-đổi-schedule)
6. [Custom Email Templates](#custom-email-templates)
7. [Error Handling](#error-handling)
8. [Logging & Monitoring](#logging--monitoring)

---

## 1. Thay đổi câu hỏi

### Workflow 01 & 02: Static Questions

**Mở node "Set Question":**

```javascript
// Original
{
  "question": "Top 10 khách hàng có doanh thu cao nhất"
}

// Your custom question
{
  "question": "Doanh thu theo tháng trong năm 2024"
}
```

### Workflow 04: Dynamic Questions (Webhook)

Không cần thay đổi! Workflow tự động lấy `question` từ request body:

```bash
curl -X POST http://n8n-url/webhook/vanna-chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Câu hỏi của bạn"}'
```

### Workflow 05: Multiple Questions (Report)

**Mở node "Set Report Config" → Field `report_questions`:**

```json
[
  "Tổng doanh thu hôm qua",
  "Top 10 sản phẩm bán chạy nhất",
  "Số lượng đơn hàng mới"
]
```

**Thêm/bớt câu hỏi:**

```json
[
  "Question 1",
  "Question 2",
  "Question 3",
  "Question 4",  // ← Thêm mới
  "Question 5"   // ← Thêm mới
]
```

---

## 2. Thay đổi URL endpoints

### Development → Production

**Tìm tất cả HTTP Request nodes:**

1. Mở workflow
2. Tìm nodes có icon 🌐 (HTTP Request)
3. Click vào từng node
4. Thay đổi URL field

**Example:**

```javascript
// Development
http://localhost:8000/api/v0/generate_sql

// Production (Railway)
https://vanna-production.railway.app/api/v0/generate_sql

// Production (Custom domain)
https://api.yourdomain.com/api/v0/generate_sql
```

### Batch Replace (n8n Desktop)

**Nếu có nhiều workflows:**

1. Export workflow as JSON
2. Open trong text editor
3. Find & Replace:
   ```
   Find: http://localhost:8000
   Replace: https://your-production-url.com
   ```
4. Save và import lại vào n8n

---

## 3. Thêm Authentication

### Option 1: API Key Header

**Mở HTTP Request node → Options → Header Parameters:**

```json
{
  "name": "X-API-Key",
  "value": "your-secret-api-key-here"
}
```

### Option 2: Bearer Token

**Authentication → Generic Credential Type:**

1. Click **"Authentication"** dropdown
2. Chọn **"Generic Credential Type"**
3. Chọn **"Header Auth"**
4. Create credential:
   - Name: `Authorization`
   - Value: `Bearer your-token-here`

### Option 3: Basic Auth

**Authentication → Basic Auth:**

1. Click **"Authentication"** → **"Basic Auth"**
2. Enter:
   - User: `your-username`
   - Password: `your-password`

### Best Practice: Use Credentials

**Thay vì hardcode API key:**

1. n8n sidebar → **"Credentials"**
2. Click **"Add Credential"**
3. Search "Header Auth"
4. Create credential:
   - **Credential Name:** Vanna API Key
   - **Name:** X-API-Key
   - **Value:** your-secret-key
5. Trong HTTP Request node:
   - Authentication → Header Auth
   - Select credential: "Vanna API Key"

**Ưu điểm:**
- ✅ Reuse across workflows
- ✅ Dễ update (1 chỗ)
- ✅ Bảo mật hơn

---

## 4. Customize Training Data

### Workflow 03: Full Training

**Mở node "Set Training Data":**

#### 4.1. DDL (Database Schema)

```javascript
{
  "train_ddl": "CREATE TABLE your_table (\n    id SERIAL PRIMARY KEY,\n    column1 VARCHAR(100),\n    column2 INTEGER\n);"
}
```

**Tips:**
- Include ALL tables trong database
- Include foreign keys và indexes
- Use `\n` cho line breaks trong JSON string

#### 4.2. Documentation (Tiếng Việt)

```javascript
{
  "train_documentation": "# Bảng your_table\n\n- id: Mã duy nhất\n- column1: Mô tả chi tiết\n- column2: Số lượng\n\n## Business Rules\n- Rule 1: ...\n- Rule 2: ..."
}
```

**Tips:**
- Viết bằng tiếng Việt
- Explain business logic
- Mention data types và constraints
- Include relationships giữa tables

#### 4.3. SQL Examples

```javascript
{
  "train_sql_question_1": "Câu hỏi mẫu 1",
  "train_sql_1": "SELECT ...",
  
  "train_sql_question_2": "Câu hỏi mẫu 2",
  "train_sql_2": "SELECT ...",
  
  // Thêm nhiều examples hơn
  "train_sql_question_4": "Câu hỏi mới",
  "train_sql_4": "SELECT ..."
}
```

**Nếu có nhiều SQL examples:**

1. Add fields mới trong "Set Training Data"
2. Duplicate node "Train SQL Example 3"
3. Rename → "Train SQL Example 4"
4. Update JSON body:
   ```json
   {
     "question": "{{ $('Set Training Data').item.json.train_sql_question_4 }}",
     "sql": "{{ $('Set Training Data').item.json.train_sql_4 }}"
   }
   ```
5. Connect từ "Train Documentation" → "Train SQL Example 4"
6. Connect từ "Train SQL Example 4" → "Verify Training Data"

---

## 5. Thay đổi Schedule

### Workflow 05: Daily Report

**Mở node "Schedule Trigger":**

#### 5.1. Using Cron Expression

**Current:** `0 9 * * *` (9 AM daily)

**Common schedules:**

| Schedule | Cron | Description |
|----------|------|-------------|
| Mỗi giờ | `0 * * * *` | Top of every hour |
| 9 AM hàng ngày | `0 9 * * *` | 9:00 AM every day |
| 9 AM + 5 PM | `0 9,17 * * *` | Twice daily |
| Thứ 2 hàng tuần | `0 9 * * 1` | Monday 9 AM |
| Cuối tháng | `0 9 L * *` | Last day of month |
| Mỗi 6 giờ | `0 */6 * * *` | Every 6 hours |

#### 5.2. Using Interval

**Click "Add Rule" → "Interval":**

```
Run every: 6 hours
```

#### 5.3. Using Fixed Time

**Click "Add Rule" → "Specific Time":**

```
Hour: 9
Minute: 0
```

### Test Schedule without waiting

**Temporary change schedule để test:**

1. Change cron to: `*/5 * * * *` (every 5 minutes)
2. Activate workflow
3. Wait 5 minutes → Check execution
4. If OK → Change back to production schedule

---

## 6. Custom Email Templates

### Workflow 05: Email Report

**Mở node "Format Email":**

#### 6.1. Change Email Template

```javascript
// Current: HTML table format
// Custom: Simple text format

let emailBody = `Báo cáo Doanh số ${date}\n\n`;

items.forEach((item, index) => {
  const question = ...;
  const data = ...;
  
  emailBody += `=== ${question} ===\n`;
  emailBody += `SQL: ${sqlResponse.text}\n`;
  emailBody += `Kết quả: ${JSON.stringify(data, null, 2)}\n\n`;
});

return {
  json: {
    to: config.email_to,
    subject: config.email_subject,
    text: emailBody  // ← Plain text instead of HTML
  }
};
```

#### 6.2. Add Charts/Images

**Using QuickChart API:**

```javascript
// Generate chart URL
const chartData = data.map(row => row.total);
const chartLabels = data.map(row => row.name);

const chartUrl = `https://quickchart.io/chart?c={
  type:'bar',
  data:{
    labels:${JSON.stringify(chartLabels)},
    datasets:[{
      label:'Revenue',
      data:${JSON.stringify(chartData)}
    }]
  }
}`;

// Add to email HTML
emailBody += `<img src="${chartUrl}" alt="Chart">`;
```

#### 6.3. Multiple Recipients

```javascript
// Single recipient
to: "manager@company.com"

// Multiple recipients (comma-separated)
to: "manager@company.com,analyst@company.com,ceo@company.com"
```

#### 6.4. CC/BCC

**Mở node "Send Email" → Options:**

```
CC: "backup@company.com"
BCC: "archive@company.com"
```

---

## 7. Error Handling

### Add Try-Catch Logic

**Mở node "Format Results" (Code node):**

```javascript
try {
  const response = $input.first().json;
  
  if (response.type === 'df') {
    const data = JSON.parse(response.df);
    return { json: { success: true, data } };
  } else {
    throw new Error('Unexpected response type');
  }
} catch (error) {
  return {
    json: {
      success: false,
      error: error.message,
      stack: error.stack
    }
  };
}
```

### Add Error Workflow

**Create separate "Error Workflow":**

1. Create new workflow: "Error Handler"
2. Webhook trigger: `/error-notification`
3. Format error message
4. Send to Slack/Email

**Link to main workflow:**

1. Main workflow → Settings → Error Workflow
2. Select "Error Handler"
3. When error → Automatically call error workflow

### Retry Logic

**HTTP Request node → Options → Retry On Fail:**

```
Max Tries: 3
Wait Between Tries: 2000ms
Backoff: Exponential
```

---

## 8. Logging & Monitoring

### Add Logging Node

**After important nodes, add Code node:**

```javascript
// Log to console
const input = $input.first().json;

console.log('='.repeat(50));
console.log('Node:', '{{ $node["Previous Node"].name }}');
console.log('Timestamp:', new Date().toISOString());
console.log('Data:', JSON.stringify(input, null, 2));
console.log('='.repeat(50));

return $input.all(); // Pass through
```

### Save Logs to Database

**Add Postgres node after Code node:**

```sql
INSERT INTO workflow_logs (
  workflow_name,
  node_name,
  timestamp,
  data,
  success
) VALUES (
  '{{ $workflow.name }}',
  '{{ $node.name }}',
  NOW(),
  '{{ JSON.stringify($json) }}',
  {{ $json.success ?? true }}
);
```

### Monitor Executions

**n8n UI → Executions tab:**

- View all workflow executions
- Filter by status (success/error)
- View execution time
- Inspect node outputs

### Webhook Monitoring

**Add logging webhook:**

```javascript
// After successful execution
await $http.post('https://your-monitoring-service.com/log', {
  workflow: $workflow.name,
  status: 'success',
  duration: $execution.duration,
  timestamp: new Date()
});
```

---

## 🎯 Common Customizations

### Custom 1: Add Data Validation

**Before Generate SQL:**

```javascript
// Validate question length
const question = $json.question;

if (question.length < 5) {
  throw new Error('Question too short (min 5 characters)');
}

if (question.length > 500) {
  throw new Error('Question too long (max 500 characters)');
}

// Check forbidden keywords
const forbidden = ['DROP', 'DELETE', 'TRUNCATE'];
if (forbidden.some(word => question.toUpperCase().includes(word))) {
  throw new Error('Forbidden keyword detected');
}

return { json: { question } };
```

### Custom 2: Add Caching

**Check cache before calling API:**

```javascript
// Generate cache key
const crypto = require('crypto');
const cacheKey = crypto.createHash('md5').update($json.question).digest('hex');

// Check Redis/File cache
const cached = await getCachedSQL(cacheKey);

if (cached) {
  console.log('Cache HIT');
  return { json: { sql: cached, from_cache: true } };
}

// If not cached, continue to Generate SQL node
```

### Custom 3: Add Rate Limiting

**Before HTTP Request:**

```javascript
// Check request count in last minute
const requestCount = await getRequestCount($workflow.user);

if (requestCount > 10) {
  throw new Error('Rate limit exceeded (10 requests per minute)');
}

// Increment counter
await incrementRequestCount($workflow.user);

return $input.all();
```

---

## 📦 Export/Import Customized Workflows

### Export

1. Open workflow
2. Click **"..."** menu (top right)
3. Click **"Download"**
4. Save as `custom_workflow_name.json`

### Import

1. Workflows tab
2. Click **"+"** → **"Import from File"**
3. Select your custom JSON file

### Share với team

1. Export workflow
2. Commit to Git repository
3. Team members import từ Git

---

## 💡 Advanced Tips

### Tip 1: Use Environment Variables

**Instead of hardcoding URLs:**

```javascript
// In Code node
const API_URL = $env.VANNA_API_URL || 'http://localhost:8000';
const API_KEY = $env.VANNA_API_KEY;

// Set in n8n:
// Settings → Environments → Add Variable
```

### Tip 2: Modular Workflows

**Split complex workflows:**

1. Main workflow calls sub-workflows
2. Use "Execute Workflow" node
3. Reuse logic across workflows

### Tip 3: Version Control

**Track workflow changes:**

1. Export workflows regularly
2. Commit to Git
3. Use branches for experiments
4. Tag releases

---

**🎨 Happy Customizing!**

Có questions? Check:
- n8n Community: https://community.n8n.io
- n8n Docs: https://docs.n8n.io
- This repo's issues page
