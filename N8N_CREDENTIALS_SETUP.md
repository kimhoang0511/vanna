# 🔐 Hướng dẫn Setup Credentials trong n8n

## ❌ Lỗi hiện tại

```
Credentials not found
NodeOperationError: Credentials not found at ExecuteContext.getCredentials
```

**Nguyên nhân:** Bạn chọn "Generic Credential Type" → "Header Auth" nhưng chưa tạo credential.

## ✅ Giải pháp: 2 cách setup Authentication

### Cách 1: Không dùng Credentials (Đơn giản nhất) ⭐ RECOMMENDED

**Bước 1:** Trong node "Initialize Vanna", chọn:
- **Authentication:** `None` (thay vì Generic Credential Type)

**Bước 2:** Bật **Send Headers** toggle

**Bước 3:** Click **Add Parameter** → Chọn **Header Parameters**

**Bước 4:** Thêm header:
- **Name:** `X-API-Key`
- **Value:** `YOUR_API_KEY_HERE`

**Screenshot config:**
```
┌─────────────────────────────────────────┐
│ Authentication: None                    │
├─────────────────────────────────────────┤
│ Send Headers: ✓ ON                      │
├─────────────────────────────────────────┤
│ Header Parameters                       │
│   Name:  X-API-Key                      │
│   Value: YOUR_API_KEY_HERE              │
└─────────────────────────────────────────┘
```

### Cách 2: Tạo Credential Header Auth (Bảo mật hơn)

**Bước 1: Tạo Credential mới**

1. Click vào tab **Credentials** (góc trên bên trái n8n)
2. Click nút **+ Add Credential**
3. Search: `Header Auth`
4. Click **Header Auth**

**Bước 2: Điền thông tin**

- **Credential Name:** `Vanna API Key` (hoặc tên bạn muốn)
- **Name:** `X-API-Key`
- **Value:** `YOUR_API_KEY_HERE` (thay bằng API key thật của bạn)

**Bước 3: Save**

Click nút **Save** (màu đỏ góc trên)

**Bước 4: Quay lại node và chọn credential**

1. Vào node "Initialize Vanna"
2. **Authentication:** `Generic Credential Type`
3. **Generic Auth Type:** `Header Auth`
4. **Header Auth:** Click dropdown → Chọn `Vanna API Key` (credential vừa tạo)

## 🔧 Config cho tất cả nodes

**Áp dụng cho các nodes:**
- Initialize Vanna
- Connect PostgreSQL
- Clear Training Data
- Train DDL
- Train Documentation
- Train SQL

### Template cho mỗi node:

```json
{
  "url": "https://vanna-production.up.railway.app/[endpoint]",
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
      // Body parameters here
    ]
  }
}
```

## 📝 Chi tiết từng node

### 1. Initialize Vanna

**URL:** `https://vanna-production.up.railway.app/init`

**Method:** `POST`

**Headers:**
- Name: `X-API-Key`
- Value: `YOUR_API_KEY_HERE`

**Body:**
```json
{
  "model": "gpt-4o-mini"
}
```

**Send Body:** Yes

**Body Content Type:** JSON

**Body Parameters:**
- Name: `model`
- Value: `gpt-4o-mini`

### 2. Connect PostgreSQL

**URL:** `https://vanna-production.up.railway.app/connect/postgres`

**Method:** `POST`

**Headers:**
- Name: `X-API-Key`
- Value: `YOUR_API_KEY_HERE`

**Body Parameters:**
- `host`: `your_host_here`
- `port`: `26750`
- `dbname`: `railway`
- `user`: `postgres`
- `password`: `your_password_here`

### 3. Clear Training Data

**URL:** `https://vanna-production.up.railway.app/clear_training_data`

**Method:** `POST`

**Headers:**
- Name: `X-API-Key`
- Value: `YOUR_API_KEY_HERE`

**Body:** Không cần (empty)

**Send Body:** No

### 4. Train DDL

**URL:** `https://vanna-production.up.railway.app/train/ddl`

**Method:** `POST`

**Headers:**
- Name: `X-API-Key`
- Value: `YOUR_API_KEY_HERE`

**Body Parameters:**
- `ddl`: `={{ $node['Edit Fields (Set)'].json.train_ddl }}`

### 5. Train Documentation

**URL:** `https://vanna-production.up.railway.app/train/documentation`

**Method:** `POST`

**Headers:**
- Name: `X-API-Key`
- Value: `YOUR_API_KEY_HERE`

**Body Parameters:**
- `documentation`: `={{ $node['Edit Fields (Set)'].json.train_documentation }}`

### 6. Train SQL

**URL:** `https://vanna-production.up.railway.app/train/sql`

**Method:** `POST`

**Headers:**
- Name: `X-API-Key`
- Value: `YOUR_API_KEY_HERE`

**Body Parameters:**
- `question`: `Tìm top 10 khách hàng`
- `sql`: `={{ $node['Edit Fields (Set)'].json.train_sql }}`

## 🧪 Test Authentication

### Test bằng curl (để lấy API key đúng)

```bash
# Test với API key
curl -X POST https://vanna-production.up.railway.app/init \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4o-mini"}'
```

**Expected response (nếu API key đúng):**
```json
{
  "success": true,
  "message": "Vanna initialized successfully",
  "data": {
    "model": "gpt-4o-mini"
  }
}
```

**Error response (nếu API key sai):**
```json
{
  "detail": "Invalid API key"
}
```

## 📸 Screenshots guide

### Cách 1: No Authentication (Recommended)

```
┌─────────────────────────────────────────────────────────────┐
│ HTTP Request Node: Initialize Vanna                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Method: POST                                                │
│ URL: https://vanna-production.up.railway.app/init          │
│                                                             │
│ Authentication: None ◄── CHỌN "None"                        │
│                                                             │
│ Send Query Parameters: ☐ OFF                               │
│ Send Headers: ☑ ON ◄── BẬT ĐÂY                             │
│                                                             │
│ Specify Headers: Using Fields Below                        │
│                                                             │
│ Header Parameters:                                          │
│   ┌─────────────────────────────────────┐                  │
│   │ Name:  X-API-Key                    │                  │
│   │ Value: YOUR_API_KEY_HERE            │                  │
│   └─────────────────────────────────────┘                  │
│                                                             │
│ Send Body: ☑ ON                                             │
│ Body Content Type: JSON                                     │
│ Specify Body: Using Fields Below                           │
│                                                             │
│ Body Parameters:                                            │
│   ┌─────────────────────────────────────┐                  │
│   │ Name:  model                        │                  │
│   │ Value: gpt-4o-mini                  │                  │
│   └─────────────────────────────────────┘                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Cách 2: Using Credentials

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Create Credential                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Go to: Credentials tab → + Add Credential → Header Auth    │
│                                                             │
│ ┌───────────────────────────────────────────────────────┐  │
│ │ Credential Name: Vanna API Key                        │  │
│ │                                                       │  │
│ │ Name:  X-API-Key                                      │  │
│ │ Value: YOUR_API_KEY_HERE                              │  │
│ │                                                       │  │
│ │                                    [Save] ◄── CLICK   │  │
│ └───────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Step 2: Use Credential in Node                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ HTTP Request Node: Initialize Vanna                         │
│                                                             │
│ Method: POST                                                │
│ URL: https://vanna-production.up.railway.app/init          │
│                                                             │
│ Authentication: Generic Credential Type                     │
│ Generic Auth Type: Header Auth                              │
│ Header Auth: [Select Credential ▼] ◄── CHỌN "Vanna API Key"│
│                                                             │
│ Send Body: ☑ ON                                             │
│ Body Parameters:                                            │
│   Name:  model                                              │
│   Value: gpt-4o-mini                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## ⚠️ Common Errors

### Error 1: "Credentials not found"
**Cause:** Chọn credential nhưng chưa tạo

**Fix:** 
- Option A: Đổi Authentication thành "None" và dùng Header Parameters
- Option B: Tạo credential trước

### Error 2: "Invalid API key"
**Cause:** API key sai

**Fix:** 
- Check API key trong Railway environment variables
- Hoặc check file `.env` local

### Error 3: "401 Unauthorized"
**Cause:** Header name sai hoặc thiếu

**Fix:** 
- Đảm bảo header name là `X-API-Key` (chính xác, case-sensitive)
- Không phải `X-Api-Key` hay `x-api-key`

## 🎯 Checklist

Để đảm bảo setup đúng:

- [ ] **Method:** POST (tất cả endpoints trừ /training_data)
- [ ] **URL:** Đầy đủ và chính xác
- [ ] **Authentication:** Chọn "None" hoặc setup credential đúng
- [ ] **Send Headers:** Bật (nếu dùng Authentication = None)
- [ ] **Header name:** `X-API-Key` (chính xác)
- [ ] **Header value:** API key hợp lệ
- [ ] **Send Body:** Bật (trừ clear_training_data)
- [ ] **Body Content Type:** JSON
- [ ] **Body Parameters:** Điền đúng theo từng endpoint

## 🚀 Quick Fix cho lỗi của bạn

**Làm theo các bước này:**

1. **Vào node "Initialize Vanna"**

2. **Thay đổi Authentication:**
   - Từ: `Generic Credential Type` → `Header Auth`
   - Sang: `None`

3. **Bật Send Headers:**
   - Toggle **Send Headers** = ON

4. **Click "Add Parameter":**
   - Chọn: `Header Parameters`

5. **Thêm header:**
   - Click nút **+** (Add Parameter)
   - **Name:** `X-API-Key`
   - **Value:** Paste API key của bạn

6. **Click "Execute Node" để test**

7. **Nếu thành công, copy config này sang các nodes khác**

## 📞 Get API Key

Nếu bạn không biết API key:

```bash
# Check Railway environment variables
railway variables

# Or check local .env
cat .env | grep API_KEY
```

Hoặc liên hệ admin để lấy API key.

## ✅ Expected Success

Sau khi setup đúng, bạn sẽ thấy:

```json
{
  "success": true,
  "message": "Vanna initialized successfully",
  "data": {
    "model": "gpt-4o-mini",
    "dialect": "PostgreSQL",
    "temperature": 0.7
  }
}
```

Node sẽ có **checkmark xanh** ✅ thay vì lỗi đỏ ❌

---

**Tóm lại:** Dùng **Cách 1** (Authentication = None + Header Parameters) là đơn giản và nhanh nhất! 🚀
