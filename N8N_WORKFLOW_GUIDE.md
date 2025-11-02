# Hướng dẫn tích hợp n8n với Vanna RAG System

## Tổng quan

Hướng dẫn này giúp bạn tạo workflow n8n để tự động train RAG system với dữ liệu từ database của bạn. Workflow sẽ:

1. **Xóa dữ liệu training cũ** (quan trọng để tránh conflict)
2. **Train DDL** (Data Definition Language - cấu trúc bảng)
3. **Train Documentation** (tài liệu mô tả)
4. **Train SQL** (ví dụ SQL queries)

## Thông tin kết nối

```
API URL: https://vanna-production.up.railway.app
API Key: L8WBBkJndxkbEJkMpCdOPmGc29HfWSTz
```

## Workflow Architecture

```
┌─────────────────┐
│  Edit Fields    │  ← Chuẩn bị dữ liệu training
│     (Set)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Initialize     │  ← Khởi tạo Vanna
│   Vanna API     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Connect to     │  ← Kết nối PostgreSQL
│   PostgreSQL    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Clear Old      │  ← Xóa dữ liệu training cũ ⚠️
│  Training Data  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Train DDL      │  ← Training bước 1
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Train Docs     │  ← Training bước 2
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Train SQL      │  ← Training bước 3
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Success        │
│  Notification   │
└─────────────────┘
```

## Các bước thiết lập chi tiết

### Bước 1: Edit Fields (Set) - Chuẩn bị dữ liệu

**Node:** Edit Fields (Set)

**Purpose:** Định nghĩa 3 loại dữ liệu training

**Fields:**

```json
{
  "train_ddl": "CREATE TABLE customers (id INT PRIMARY KEY, name VARCHAR(100), email VARCHAR(100), country VARCHAR(50));",
  "train_documentation": "Bảng customers chứa thông tin khách hàng. Các trường quan trọng: id (mã khách hàng), name (tên), email (địa chỉ email), country (quốc gia).",
  "train_sql": "-- Tìm top 10 khách hàng\nSELECT name, email FROM customers ORDER BY id DESC LIMIT 10;"
}
```

**Configuration:**
- Include Other Fields: Yes
- Options: Keep Only Set Fields

### Bước 2: Initialize Vanna

**Node:** HTTP Request

**Method:** POST

**URL:** `https://vanna-production.up.railway.app/init`

**Headers:**
```json
{
  "X-API-Key": "L8WBBkJndxkbEJkMpCdOPmGc29HfWSTz",
  "Content-Type": "application/json"
}
```

**Body (JSON):**
```json
{
  "model": "gpt-4o-mini"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Vanna initialized successfully",
  "data": {
    "model": "gpt-4o-mini"
  }
}
```

### Bước 3: Connect to PostgreSQL

**Node:** HTTP Request

**Method:** POST

**URL:** `https://vanna-production.up.railway.app/connect/postgres`

**Headers:**
```json
{
  "X-API-Key": "L8WBBkJndxkbEJkMpCdOPmGc29HfWSTz",
  "Content-Type": "application/json"
}
```

**Body (JSON):**
```json
{
  "host": "nozomi.proxy.rlwy.net",
  "port": 26750,
  "dbname": "railway",
  "user": "postgres",
  "password": "YOUR_PASSWORD_HERE"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Connected to PostgreSQL successfully",
  "data": {
    "host": "nozomi.proxy.rlwy.net",
    "port": 26750,
    "dbname": "railway"
  }
}
```

### Bước 4: ⚠️ Clear Old Training Data (QUAN TRỌNG!)

**Node:** HTTP Request

**Method:** POST

**URL:** `https://vanna-production.up.railway.app/clear_training_data`

**Headers:**
```json
{
  "X-API-Key": "L8WBBkJndxkbEJkMpCdOPmGc29HfWSTz",
  "Content-Type": "application/json"
}
```

**Body:** Không cần body (empty)

**Response:**
```json
{
  "success": true,
  "message": "Training data cleared successfully. Removed 15 items. 0 items remaining.",
  "data": {
    "count_before": 15,
    "count_after": 0,
    "cleared": 15
  }
}
```

**Tại sao phải clear?**
- ✅ Tránh conflict giữa dữ liệu cũ và mới
- ✅ Đảm bảo RAG chỉ sử dụng dữ liệu mới nhất
- ✅ Tránh duplicate embeddings trong ChromaDB
- ✅ Giảm kích thước vector database

**Khi nào cần clear?**
- ✅ Khi database schema thay đổi
- ✅ Khi cập nhật documentation
- ✅ Khi thêm/sửa SQL examples
- ✅ Khi muốn retrain từ đầu

### Bước 5: Train DDL

**Node:** HTTP Request

**Method:** POST

**URL:** `https://vanna-production.up.railway.app/train/ddl`

**Headers:**
```json
{
  "X-API-Key": "L8WBBkJndxkbEJkMpCdOPmGc29HfWSTz",
  "Content-Type": "application/json"
}
```

**Body (JSON):**
```json
{
  "ddl": "{{ $node['Edit Fields (Set)'].json.train_ddl }}"
}
```

**Expression để lấy giá trị từ Edit Fields:**
```javascript
$node['Edit Fields (Set)'].json.train_ddl
```

**Response:**
```json
{
  "success": true,
  "message": "DDL trained successfully",
  "data": {
    "ddl": "CREATE TABLE customers..."
  }
}
```

### Bước 6: Train Documentation

**Node:** HTTP Request

**Method:** POST

**URL:** `https://vanna-production.up.railway.app/train/documentation`

**Headers:**
```json
{
  "X-API-Key": "L8WBBBkJndxkbEJkMpCdOPmGc29HfWSTz",
  "Content-Type": "application/json"
}
```

**Body (JSON):**
```json
{
  "documentation": "{{ $node['Edit Fields (Set)'].json.train_documentation }}"
}
```

**Expression:**
```javascript
$node['Edit Fields (Set)'].json.train_documentation
```

**Response:**
```json
{
  "success": true,
  "message": "Documentation trained successfully",
  "data": {
    "documentation": "Bảng customers chứa..."
  }
}
```

### Bước 7: Train SQL

**Node:** HTTP Request

**Method:** POST

**URL:** `https://vanna-production.up.railway.app/train/sql`

**Headers:**
```json
{
  "X-API-Key": "L8WBBkJndxkbEJkMpCdOPmGc29HfWSTz",
  "Content-Type": "application/json"
}
```

**Body (JSON):**
```json
{
  "question": "Tìm top 10 khách hàng",
  "sql": "{{ $node['Edit Fields (Set)'].json.train_sql }}"
}
```

**Expression:**
```javascript
$node['Edit Fields (Set)'].json.train_sql
```

**Response:**
```json
{
  "success": true,
  "message": "SQL trained successfully",
  "data": {
    "question": "Tìm top 10 khách hàng",
    "sql": "SELECT name, email FROM customers..."
  }
}
```

## Error Handling

### Thêm node "IF" sau mỗi HTTP Request

**Condition:** Check if response is successful

```javascript
{{ $json.success === true }}
```

**True branch:** Continue to next step

**False branch:** Send error notification

### Error Notification Node

**Node:** Send Email / Slack / Discord

**Message Template:**
```
⚠️ Vanna Training Failed!

Step: {{ $node['HTTP Request'].json.step }}
Error: {{ $node['HTTP Request'].json.message }}
Time: {{ $now }}

Please check the workflow and try again.
```

## Best Practices

### 1. Scheduling

**Trigger:** Cron

**Schedule:** 
- Daily: `0 2 * * *` (2 AM mỗi ngày)
- Weekly: `0 2 * * 0` (2 AM mỗi Chủ nhật)
- Monthly: `0 2 1 * *` (2 AM ngày 1 mỗi tháng)

### 2. Data Validation

Thêm node "Code" để validate dữ liệu trước khi train:

```javascript
// Validate DDL
if (!$node['Edit Fields (Set)'].json.train_ddl) {
  throw new Error('train_ddl is required');
}

// Validate Documentation
if (!$node['Edit Fields (Set)'].json.train_documentation) {
  throw new Error('train_documentation is required');
}

// Validate SQL
if (!$node['Edit Fields (Set)'].json.train_sql) {
  throw new Error('train_sql is required');
}

return [{
  json: {
    validated: true,
    message: 'All training data is valid'
  }
}];
```

### 3. Logging

Thêm node "Set" sau mỗi bước để log progress:

```json
{
  "step": "train_ddl",
  "status": "{{ $json.success }}",
  "timestamp": "{{ $now }}",
  "message": "{{ $json.message }}"
}
```

### 4. Retry Logic

**HTTP Request Settings:**
- Retry on Fail: Yes
- Max Tries: 3
- Wait Between Tries: 1000ms

## Complete Workflow JSON

```json
{
  "name": "Vanna RAG Training Workflow",
  "nodes": [
    {
      "parameters": {
        "values": {
          "string": [
            {
              "name": "train_ddl",
              "value": "CREATE TABLE customers (id INT PRIMARY KEY, name VARCHAR(100), email VARCHAR(100), country VARCHAR(50));"
            },
            {
              "name": "train_documentation",
              "value": "Bảng customers chứa thông tin khách hàng. Các trường quan trọng: id (mã khách hàng), name (tên), email (địa chỉ email), country (quốc gia)."
            },
            {
              "name": "train_sql",
              "value": "-- Tìm top 10 khách hàng\nSELECT name, email FROM customers ORDER BY id DESC LIMIT 10;"
            }
          ]
        },
        "options": {}
      },
      "name": "Edit Fields (Set)",
      "type": "n8n-nodes-base.set",
      "typeVersion": 1,
      "position": [250, 300]
    },
    {
      "parameters": {
        "url": "https://vanna-production.up.railway.app/init",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "X-API-Key",
              "value": "L8WBBkJndxkbEJkMpCdOPmGc29HfWSTz"
            }
          ]
        },
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "model",
              "value": "gpt-4o-mini"
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
      "name": "Initialize Vanna",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 3,
      "position": [450, 300]
    },
    {
      "parameters": {
        "url": "https://vanna-production.up.railway.app/connect/postgres",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "X-API-Key",
              "value": "L8WBBkJndxkbEJkMpCdOPmGc29HfWSTz"
            }
          ]
        },
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "host",
              "value": "nozomi.proxy.rlwy.net"
            },
            {
              "name": "port",
              "value": "26750"
            },
            {
              "name": "dbname",
              "value": "railway"
            },
            {
              "name": "user",
              "value": "postgres"
            },
            {
              "name": "password",
              "value": "YOUR_PASSWORD_HERE"
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
      "name": "Connect PostgreSQL",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 3,
      "position": [650, 300]
    },
    {
      "parameters": {
        "url": "https://vanna-production.up.railway.app/clear_training_data",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "X-API-Key",
              "value": "L8WBBkJndxkbEJkMpCdOPmGc29HfWSTz"
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
      "name": "Clear Training Data",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 3,
      "position": [850, 300]
    },
    {
      "parameters": {
        "url": "https://vanna-production.up.railway.app/train/ddl",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "X-API-Key",
              "value": "L8WBBkJndxkbEJkMpCdOPmGc29HfWSTz"
            }
          ]
        },
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "ddl",
              "value": "={{ $node['Edit Fields (Set)'].json.train_ddl }}"
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
      "name": "Train DDL",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 3,
      "position": [1050, 300]
    },
    {
      "parameters": {
        "url": "https://vanna-production.up.railway.app/train/documentation",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "X-API-Key",
              "value": "L8WBBkJndxkbEJkMpCdOPmGc29HfWSTz"
            }
          ]
        },
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "documentation",
              "value": "={{ $node['Edit Fields (Set)'].json.train_documentation }}"
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
      "name": "Train Documentation",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 3,
      "position": [1250, 300]
    },
    {
      "parameters": {
        "url": "https://vanna-production.up.railway.app/train/sql",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "X-API-Key",
              "value": "L8WBBkJndxkbEJkMpCdOPmGc29HfWSTz"
            }
          ]
        },
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "question",
              "value": "Tìm top 10 khách hàng"
            },
            {
              "name": "sql",
              "value": "={{ $node['Edit Fields (Set)'].json.train_sql }}"
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
      "name": "Train SQL",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 3,
      "position": [1450, 300]
    }
  ],
  "connections": {
    "Edit Fields (Set)": {
      "main": [[{"node": "Initialize Vanna", "type": "main", "index": 0}]]
    },
    "Initialize Vanna": {
      "main": [[{"node": "Connect PostgreSQL", "type": "main", "index": 0}]]
    },
    "Connect PostgreSQL": {
      "main": [[{"node": "Clear Training Data", "type": "main", "index": 0}]]
    },
    "Clear Training Data": {
      "main": [[{"node": "Train DDL", "type": "main", "index": 0}]]
    },
    "Train DDL": {
      "main": [[{"node": "Train Documentation", "type": "main", "index": 0}]]
    },
    "Train Documentation": {
      "main": [[{"node": "Train SQL", "type": "main", "index": 0}]]
    }
  }
}
```

## Testing Workflow

### 1. Test từng bước riêng lẻ

Trước khi chạy full workflow, test từng endpoint bằng curl:

```bash
# Test Clear Training Data
curl -X POST https://vanna-production.up.railway.app/clear_training_data \
  -H "X-API-Key: L8WBBkJndxkbEJkMpCdOPmGc29HfWSTz" \
  -H "Content-Type: application/json"

# Test Train DDL
curl -X POST https://vanna-production.up.railway.app/train/ddl \
  -H "X-API-Key: L8WBBkJndxkbEJkMpCdOPmGc29HfWSTz" \
  -H "Content-Type: application/json" \
  -d '{"ddl": "CREATE TABLE test (id INT);"}'
```

### 2. Test workflow trong n8n

1. Click **Execute Workflow** button
2. Xem kết quả từng node
3. Kiểm tra status code = 200
4. Kiểm tra `success: true` trong response

### 3. Verify training data

Sau khi workflow hoàn thành, kiểm tra:

```bash
curl -X GET https://vanna-production.up.railway.app/training_data \
  -H "X-API-Key: L8WBBkJndxkbEJkMpCdOPmGc29HfWSTz"
```

Expected response:
```json
{
  "success": true,
  "message": "Training data retrieved successfully",
  "data": {
    "count": 3,
    "data": [
      {"id": "...", "training_data_type": "ddl", ...},
      {"id": "...", "training_data_type": "documentation", ...},
      {"id": "...", "training_data_type": "sql", ...}
    ]
  }
}
```

## Advanced: Multiple Training Data Sources

Nếu bạn có nhiều bảng và muốn train cùng lúc:

### Option 1: Loop Node

```
Edit Fields (Set) → Split In Batches → Train DDL → Loop → Train Documentation → ...
```

### Option 2: Multiple Parallel Nodes

```
Edit Fields (Set) 
    ├→ Train DDL Table 1
    ├→ Train DDL Table 2
    └→ Train DDL Table 3
           ↓
    Merge → Train Documentation
```

### Option 3: Dynamic Training from Database

1. **Postgres Node** - Query để lấy schema:
```sql
SELECT 
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;
```

2. **Code Node** - Generate DDL statements:
```javascript
const items = $input.all();
const tables = {};

// Group columns by table
items.forEach(item => {
  const tableName = item.json.table_name;
  if (!tables[tableName]) {
    tables[tableName] = [];
  }
  tables[tableName].push({
    name: item.json.column_name,
    type: item.json.data_type
  });
});

// Generate DDL for each table
const ddlStatements = Object.entries(tables).map(([tableName, columns]) => {
  const columnDefs = columns.map(col => `${col.name} ${col.type}`).join(', ');
  return `CREATE TABLE ${tableName} (${columnDefs});`;
});

return ddlStatements.map(ddl => ({ json: { ddl } }));
```

3. **Split In Batches** → **Train DDL** (loop for each table)

## Monitoring & Alerts

### Success Notification

**Node:** Send Email/Slack

**Trigger:** After last training step succeeds

**Message:**
```
✅ Vanna Training Completed Successfully!

Statistics:
- DDL trained: {{ $node['Train DDL'].json.success }}
- Docs trained: {{ $node['Train Documentation'].json.success }}
- SQL trained: {{ $node['Train SQL'].json.success }}
- Total time: {{ $workflow.duration }}ms
- Timestamp: {{ $now.format('YYYY-MM-DD HH:mm:ss') }}

You can now use the trained model for SQL generation!
```

### Failure Alert

**Node:** Send Email/Slack

**Trigger:** If any step fails (use IF node)

**Message:**
```
❌ Vanna Training Failed!

Failed Step: {{ $node['HTTP Request'].json.step }}
Error Message: {{ $json.error }}
Status Code: {{ $json.code }}
Timestamp: {{ $now.format('YYYY-MM-DD HH:mm:ss') }}

Please check the workflow execution and logs.
```

## Troubleshooting

### Issue 1: "Authentication failed"

**Problem:** API key không đúng hoặc thiếu header

**Solution:**
- Kiểm tra header `X-API-Key` có đúng không
- Verify API key: `L8WBBkJndxkbEJkMpCdOPmGc29HfWSTz`

### Issue 2: "Training data not cleared"

**Problem:** Clear endpoint không hoạt động

**Solution:**
- Check response từ `/clear_training_data`
- Verify `count_after` = 0
- Nếu vẫn còn data, gọi endpoint nhiều lần

### Issue 3: "Connection timeout"

**Problem:** Railway server không response

**Solution:**
- Check Railway deployment status
- Verify server đang chạy: `https://vanna-production.up.railway.app/health`
- Tăng timeout trong HTTP Request settings

### Issue 4: "Invalid DDL format"

**Problem:** DDL statement không hợp lệ

**Solution:**
- Validate DDL trước khi train
- Remove comments (`--`, `/* */`)
- Use single line format hoặc proper multiline với `\n`

## Next Steps

Sau khi setup workflow thành công:

1. **Test với dữ liệu thật** từ database của bạn
2. **Schedule workflow** để tự động update training data
3. **Monitor logs** để đảm bảo training thành công
4. **Test SQL generation** với câu hỏi mới
5. **Tune parameters** (model, temperature, etc.) nếu cần

## Resources

- **API Documentation:** https://vanna-production.up.railway.app/docs
- **Health Check:** https://vanna-production.up.railway.app/health
- **Training Data:** https://vanna-production.up.railway.app/training_data
- **n8n Documentation:** https://docs.n8n.io/

## Support

Nếu có vấn đề, check:
1. Railway logs: https://railway.app/project/[your-project]
2. n8n execution logs
3. API response messages

---

**Version:** 1.0
**Last Updated:** 2024
**Author:** Vietnamese Vanna Team
