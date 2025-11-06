# 🚀 Quick Config: Generate SQL Node

## ⚡ Minimal Config (Copy & Paste)

```
Node Type: HTTP Request
Name: Generate SQL
Method: POST
URL: https://vanna-production.up.railway.app/generate_sql

Authentication: None
Send Headers: ✓ ON

Header Parameters:
  Name: X-API-Key
  Value: YOUR_API_KEY_HERE

Send Body: ✓ ON
Body Content Type: JSON

Body Parameters:
  Name: question
  Value: [Your question here]
  
  Name: allow_llm_to_see_data
  Value: false
```

## 📝 3 Examples

### 1. Static Question
```json
{
  "question": "Top 10 sản phẩm bán chạy nhất",
  "allow_llm_to_see_data": false
}
```

### 2. From Previous Node
```
question: ={{ $node['Edit Fields'].json.user_question }}
allow_llm_to_see_data: false
```

### 3. From Webhook
```
question: ={{ $json.question }}
allow_llm_to_see_data: ={{ $json.allow_llm ?? false }}
```

## 📤 Response

```json
{
  "success": true,
  "message": "SQL generated successfully",
  "data": {
    "sql": "SELECT ... FROM ... WHERE ...",
    "question": "..."
  }
}
```

## 🔗 Get SQL in Next Node

```javascript
{{ $json.data.sql }}
```

## 🧪 Test with curl

```bash
curl -X POST https://vanna-production.up.railway.app/generate_sql \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{"question": "Tổng doanh thu tháng 10?", "allow_llm_to_see_data": false}'
```

## 🎯 Common Workflows

**Simple:**
```
Manual Trigger → Edit Fields → Generate SQL → Display
```

**Execute:**
```
Generate SQL → Execute SQL → Send Results
```

**With Chart:**
```
Generate SQL → Generate Chart → Save Image
```

## ⚙️ Settings

- Timeout: 30-60 seconds
- Retry: 3 times
- Wait: 1-2 seconds between retries

---

Full guide: `N8N_GENERATE_SQL_NODE.md`
