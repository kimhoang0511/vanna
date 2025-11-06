# 🔧 Node HTTP Request: Generate SQL

## Tổng quan

Node này gọi endpoint `/generate_sql` để chuyển đổi câu hỏi tiếng Việt (hoặc tiếng Anh) thành SQL query.

## 📋 Config Node

### Basic Settings

**Node Name:** `Generate SQL`

**Method:** `POST`

**URL:** `https://vanna-production.up.railway.app/generate_sql`

### Authentication

**Option 1: No Authentication (Recommended)**
- **Authentication:** `None`
- **Send Headers:** `✓ ON`
- **Header Parameters:**
  - Name: `X-API-Key`
  - Value: `YOUR_API_KEY_HERE`

**Option 2: Using Credentials**
- **Authentication:** `Generic Credential Type`
- **Generic Auth Type:** `Header Auth`
- **Header Auth:** Select your saved credential

### Request Body

**Send Body:** `✓ ON`

**Body Content Type:** `JSON`

**Specify Body:** `Using Fields Below`

**Body Parameters:**

| Name | Value | Description |
|------|-------|-------------|
| `question` | Text or Expression | Câu hỏi tiếng Việt/Anh |
| `allow_llm_to_see_data` | `false` | (Optional) Cho phép LLM xem dữ liệu mẫu |

## 📝 Examples

### Example 1: Câu hỏi tĩnh (Static Question)

**Body Parameters:**
```json
{
  "question": "Top 10 khách hàng có doanh thu cao nhất trong năm 2024",
  "allow_llm_to_see_data": false
}
```

**Config trong n8n:**
- Name: `question`
- Value: `Top 10 khách hàng có doanh thu cao nhất trong năm 2024`

- Name: `allow_llm_to_see_data`
- Value: `false`

### Example 2: Lấy từ node trước (From Previous Node)

**Giả sử có node "Edit Fields" với field `user_question`:**

**Body Parameters:**
- Name: `question`
- Value: `={{ $node['Edit Fields'].json.user_question }}`

- Name: `allow_llm_to_see_data`
- Value: `false`

### Example 3: Từ Webhook Input

**Nếu nhận question từ webhook:**

**Body Parameters:**
- Name: `question`
- Value: `={{ $json.question }}`

- Name: `allow_llm_to_see_data`
- Value: `={{ $json.allow_llm_to_see_data ?? false }}`

## 📤 Response Format

### Success Response

```json
{
  "success": true,
  "message": "SQL generated successfully",
  "data": {
    "sql": "SELECT customer_id, customer_name, SUM(total_amount) as revenue FROM sales WHERE YEAR(sale_date) = 2024 GROUP BY customer_id, customer_name ORDER BY revenue DESC LIMIT 10;",
    "question": "Top 10 khách hàng có doanh thu cao nhất trong năm 2024"
  }
}
```

### Error Response

```json
{
  "detail": "Failed to generate SQL: [error message]"
}
```

## 🔗 Complete Node Configuration JSON

```json
{
  "parameters": {
    "url": "https://vanna-production.up.railway.app/generate_sql",
    "authentication": "none",
    "sendHeaders": true,
    "headerParameters": {
      "parameters": [
        {
          "name": "X-API-Key",
          "value": "YOUR_API_KEY_HERE"
        }
      ]
    },
    "sendBody": true,
    "bodyParameters": {
      "parameters": [
        {
          "name": "question",
          "value": "Top 10 khách hàng có doanh thu cao nhất trong năm 2024"
        },
        {
          "name": "allow_llm_to_see_data",
          "value": false
        }
      ]
    },
    "options": {
      "retry": {
        "maxTries": 3,
        "waitBetweenTries": 1000
      }
    }
  },
  "name": "Generate SQL",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4.2,
  "position": [850, 300]
}
```

## 🎯 Use Cases

### Use Case 1: Simple Workflow (Generate Only)

```
┌─────────────────┐
│  Manual Trigger │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Edit Fields    │  question = "Tổng doanh thu tháng 10?"
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Generate SQL   │  ← THIS NODE
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Show Result    │  Display SQL
└─────────────────┘
```

### Use Case 2: Full Workflow (Generate + Execute)

```
┌─────────────────┐
│  Webhook        │  Nhận question từ external app
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Generate SQL   │  ← THIS NODE
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Execute SQL    │  POST /execute_sql
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Send Results   │  Email/Slack/API
└─────────────────┘
```

### Use Case 3: With Chart Generation

```
┌─────────────────┐
│  Schedule       │  Cron: daily at 9am
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Generate SQL   │  ← THIS NODE
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Generate Chart │  POST /generate_chart with SQL
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Save to Drive  │  Upload chart image
└─────────────────┘
```

## 🔄 Accessing Generated SQL in Next Node

**Method 1: Direct access**
```javascript
{{ $json.data.sql }}
```

**Method 2: From named node**
```javascript
{{ $node['Generate SQL'].json.data.sql }}
```

**Method 3: With error handling**
```javascript
{{ $json.success ? $json.data.sql : 'SQL generation failed' }}
```

## 🧪 Testing

### Test với curl

```bash
curl -X POST https://vanna-production.up.railway.app/generate_sql \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Top 10 khách hàng có doanh thu cao nhất trong năm 2024",
    "allow_llm_to_see_data": false
  }'
```

### Expected Response

```json
{
  "success": true,
  "message": "SQL generated successfully",
  "data": {
    "sql": "SELECT customer_name, SUM(revenue) FROM customers JOIN sales ON customers.id = sales.customer_id WHERE YEAR(sale_date) = 2024 GROUP BY customer_name ORDER BY SUM(revenue) DESC LIMIT 10;",
    "question": "Top 10 khách hàng có doanh thu cao nhất trong năm 2024"
  }
}
```

## 🎨 Node Variations

### Variation 1: Với Multiple Questions (Loop)

```
┌─────────────────┐
│  Edit Fields    │  questions = ["Q1", "Q2", "Q3"]
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Split in Batch │  Iterate over questions
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Generate SQL   │  question = {{ $json.question }}
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Collect All    │  Aggregate results
└─────────────────┘
```

### Variation 2: With Validation

```
┌─────────────────┐
│  Generate SQL   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  IF Node        │  Check if success = true
└────┬────────┬───┘
     │        │
   TRUE     FALSE
     │        │
     ▼        ▼
┌─────────┐ ┌──────────┐
│ Execute │ │  Error   │
│  SQL    │ │  Handler │
└─────────┘ └──────────┘
```

### Variation 3: With Caching

```
┌─────────────────┐
│  Check Cache    │  Redis/Memory lookup
└────┬────────┬───┘
     │        │
   MISS      HIT
     │        │
     ▼        ▼
┌─────────┐ ┌──────────┐
│Generate │ │ Return   │
│  SQL    │ │  Cached  │
└────┬────┘ └──────────┘
     │
     ▼
┌─────────────────┐
│  Save to Cache  │
└─────────────────┘
```

## ⚙️ Advanced Settings

### Timeout

**Connection Timeout:** `30000` ms (30 seconds)

**Response Timeout:** `60000` ms (60 seconds)

*Generate SQL có thể mất thời gian nếu query phức tạp*

### Retry Logic

**Retry on Fail:** `✓ ON`

**Max Tries:** `3`

**Wait Between Tries:** `2000` ms

**Backoff:** Exponential

### Error Handling

**Continue on Fail:** `☐ OFF`

*Nên dừng workflow nếu SQL generation fail*

### Response Format

**Response Format:** `Auto-detect`

**Full Response:** `☐ OFF`

*Chỉ cần body, không cần headers*

## 📊 Monitoring & Logging

### Log SQL Generated

**Add Code Node after Generate SQL:**

```javascript
const sql = $input.first().json.data.sql;
const question = $input.first().json.data.question;

console.log('='.repeat(70));
console.log('Question:', question);
console.log('Generated SQL:', sql);
console.log('='.repeat(70));

return $input.all();
```

### Save to Database

**Add Postgres Node after Generate SQL:**

```sql
INSERT INTO sql_generation_log (
  question,
  generated_sql,
  timestamp,
  success
) VALUES (
  '{{ $json.data.question }}',
  '{{ $json.data.sql }}',
  NOW(),
  {{ $json.success }}
);
```

### Send Notification on Error

**Add IF Node → Send Email:**

```javascript
// Condition
{{ $json.success === false }}

// Email body
Subject: SQL Generation Failed
Body: Failed to generate SQL for question: {{ $json.data.question }}
Error: {{ $json.message }}
```

## 🔍 Troubleshooting

### Issue 1: "Vanna not initialized"

**Error:**
```json
{
  "detail": "Vanna not initialized. Call /init endpoint first."
}
```

**Fix:** Thêm node "Initialize Vanna" trước node này

### Issue 2: "Invalid question"

**Error:**
```json
{
  "detail": "Failed to generate SQL: Question is empty"
}
```

**Fix:** Kiểm tra expression `{{ $json.question }}` có giá trị

### Issue 3: Generated SQL không chính xác

**Cause:** Thiếu training data hoặc training data không đầy đủ

**Fix:**
1. Train thêm DDL (schema)
2. Train thêm documentation
3. Train thêm SQL examples tương tự

### Issue 4: Timeout

**Error:** Request timeout after 30s

**Fix:**
1. Tăng timeout lên 60s
2. Check Railway server status
3. Simplify question nếu quá phức tạp

## 💡 Best Practices

### 1. Input Validation

**Validate question trước khi gọi API:**

```javascript
// Code Node before Generate SQL
const question = $json.question;

if (!question || question.trim().length === 0) {
  throw new Error('Question cannot be empty');
}

if (question.length > 500) {
  throw new Error('Question too long (max 500 characters)');
}

return [{ json: { question: question.trim() } }];
```

### 2. Cache Results

**Cache để tránh regenerate SQL giống nhau:**

```javascript
// Generate cache key
const cacheKey = `sql_${require('crypto').createHash('md5').update($json.question).digest('hex')}`;

// Check cache first
// If not in cache, call Generate SQL
// Save to cache after
```

### 3. Log All Requests

**Track tất cả SQL generation requests:**

```javascript
{
  "timestamp": "{{ $now }}",
  "question": "{{ $json.data.question }}",
  "sql": "{{ $json.data.sql }}",
  "success": {{ $json.success }},
  "user": "{{ $workflow.user }}"
}
```

### 4. Rate Limiting

**Tránh spam API:**

```javascript
// Check request count in last minute
// If > 10 requests, wait or skip
```

## 🎯 Complete Example Workflow

```json
{
  "name": "SQL Generation Workflow",
  "nodes": [
    {
      "parameters": {},
      "name": "Manual Trigger",
      "type": "n8n-nodes-base.manualTrigger",
      "position": [250, 300]
    },
    {
      "parameters": {
        "values": {
          "string": [
            {
              "name": "question",
              "value": "Top 10 khách hàng có doanh thu cao nhất trong năm 2024"
            }
          ]
        }
      },
      "name": "Edit Fields",
      "type": "n8n-nodes-base.set",
      "position": [450, 300]
    },
    {
      "parameters": {
        "url": "https://vanna-production.up.railway.app/generate_sql",
        "authentication": "none",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "X-API-Key",
              "value": "YOUR_API_KEY_HERE"
            }
          ]
        },
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "question",
              "value": "={{ $json.question }}"
            },
            {
              "name": "allow_llm_to_see_data",
              "value": false
            }
          ]
        },
        "options": {
          "retry": {
            "maxTries": 3
          }
        }
      },
      "name": "Generate SQL",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [650, 300]
    },
    {
      "parameters": {
        "jsCode": "const sql = $input.first().json.data.sql;\nconst question = $input.first().json.data.question;\n\nconsole.log('Generated SQL:', sql);\n\nreturn [{ json: { question, sql } }];"
      },
      "name": "Log Result",
      "type": "n8n-nodes-base.code",
      "position": [850, 300]
    }
  ],
  "connections": {
    "Manual Trigger": {
      "main": [[{"node": "Edit Fields", "type": "main", "index": 0}]]
    },
    "Edit Fields": {
      "main": [[{"node": "Generate SQL", "type": "main", "index": 0}]]
    },
    "Generate SQL": {
      "main": [[{"node": "Log Result", "type": "main", "index": 0}]]
    }
  }
}
```

## 📚 Related Endpoints

Các endpoints khác bạn có thể dùng tiếp:

- **POST /execute_sql** - Execute SQL đã generate
- **POST /ask** - All-in-one (generate + execute)
- **POST /generate_chart** - Tạo chart từ SQL
- **GET /training_data** - Xem training data

## 🎓 Summary

**Node Generate SQL cho phép:**
- ✅ Chuyển câu hỏi tiếng Việt → SQL
- ✅ Sử dụng RAG (Retrieval Augmented Generation)
- ✅ Tự động tham khảo training data
- ✅ Hỗ trợ retry và error handling
- ✅ Dễ dàng integrate vào workflow

**Config cơ bản:**
1. Method: POST
2. URL: /generate_sql
3. Header: X-API-Key
4. Body: question + allow_llm_to_see_data
5. Response: SQL string

**Next steps:**
1. Generate SQL ← YOU ARE HERE
2. Execute SQL với node khác
3. Hoặc dùng /ask để làm cả 2 bước

---

**Happy SQL Generation! 🚀**
