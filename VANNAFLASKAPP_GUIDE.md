# VannaFlaskApp - Hướng dẫn chi tiết

## 📖 Tổng quan

`VannaFlaskApp` là một class trong Vanna framework cho phép tạo **web UI tương tác** để làm việc với Vanna thông qua giao diện trực quan. Nó khác với API server hiện tại của bạn.

## 🔍 So sánh với Main.py hiện tại

### Main.py hiện tại (FastAPI)
```python
# main.py - Bạn đang dùng
app = FastAPI(title="Vietnamese Vanna API")
# → REST API endpoints (JSON input/output)
# → Không có UI, chỉ có API
# → Dùng cho n8n, Postman, curl, etc.
```

### VannaFlaskApp (Flask UI)
```python
# Cách dùng VannaFlaskApp
from vanna.flask import VannaFlaskApp

app = VannaFlaskApp(
    vn=vanna_instance,
    title="Vietnamese SQL Assistant",
    subtitle="Trợ lý SQL tiếng Việt"
)
app.run()
# → Web UI đầy đủ (HTML/CSS/JS)
# → Người dùng nhập câu hỏi trực tiếp trên web
# → Hiển thị kết quả dạng bảng, chart, SQL
```

## 🏗️ Kiến trúc VannaFlaskApp

```
VannaFlaskApp
    └─ extends VannaFlaskAPI
        └─ Endpoints API (/api/v0/*)
        └─ Web UI (/, /assets/*)
        └─ Authentication
        └─ Cache system
```

### 1. **VannaFlaskAPI** (Parent Class)
- Cung cấp REST API endpoints như main.py
- `/api/v0/generate_sql` - Generate SQL
- `/api/v0/run_sql` - Execute SQL
- `/api/v0/train` - Training
- `/api/v0/get_training_data` - Xem training data
- Có authentication, caching

### 2. **VannaFlaskApp** (Child Class)
- **Thêm Web UI** đầy đủ
- **Serve static assets** (CSS, JS, HTML)
- **Customizable UI** (logo, title, colors)
- **Interactive features**: charts, tables, export CSV

## 📋 Cách sử dụng VannaFlaskApp

### Ví dụ 1: Basic Setup
```python
from vanna.flask import VannaFlaskApp
from vietnamese_vanna import VietnameseVanna
from vanna.chromadb import ChromaDB_VectorStore
from vanna.openai import OpenAI_Chat

# Define your Vanna class
class MyVanna(VietnameseVanna, ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

# Initialize Vanna
vn = MyVanna(config={
    'model': 'gpt-4o-mini',
    'api_key': 'your-openai-key',
})

# Connect to database
vn.connect_to_postgres(
    host='localhost',
    dbname='mydb',
    user='postgres',
    password='password',
    port=5432
)

# Create Flask App with UI
app = VannaFlaskApp(vn)
app.run()  # Runs on http://localhost:8084
```

### Ví dụ 2: Customized UI
```python
app = VannaFlaskApp(
    vn=vn,
    # UI Customization
    logo="https://your-company.com/logo.png",
    title="Trợ lý SQL Tiếng Việt",
    subtitle="Hỏi câu hỏi bằng tiếng Việt, nhận SQL tự động",
    
    # Features Toggle
    show_training_data=True,      # Hiện training data
    suggested_questions=True,     # Hiện suggested questions
    sql=True,                     # Hiện SQL code
    table=True,                   # Hiện bảng kết quả
    csv_download=True,            # Cho phép download CSV
    chart=True,                   # Hiện charts
    redraw_chart=True,            # Cho phép vẽ lại chart
    auto_fix_sql=True,            # Tự động fix SQL errors
    followup_questions=True,      # Hiện followup questions
    summarization=True,           # Summarize kết quả
    
    # Advanced
    allow_llm_to_see_data=False,  # Bảo mật data
    debug=True,                   # Debug mode
)

app.run(host='0.0.0.0', port=8080)
```

### Ví dụ 3: With Authentication
```python
from vanna.flask import VannaFlaskApp
from vanna.flask.auth import AuthInterface

class MyAuth(AuthInterface):
    def is_logged_in(self, user):
        # Custom login logic
        return user is not None
    
    def login_handler(self, request):
        # Custom login handler
        pass

app = VannaFlaskApp(
    vn=vn,
    auth=MyAuth(),  # Custom authentication
    title="Secure SQL Portal"
)
app.run()
```

## 🎨 UI Features

### 1. Question Input
- Text box để nhập câu hỏi tiếng Việt
- Suggested questions (từ training data)
- Question history

### 2. SQL Display
- Syntax highlighting
- Edit SQL manually
- Auto-fix SQL errors

### 3. Results Display
- **Table**: Pandas DataFrame display
- **Chart**: Plotly charts (bar, line, pie, etc.)
- **CSV Export**: Download results
- **Summary**: AI-generated summary

### 4. Training Interface
- Add DDL
- Add documentation
- Add SQL examples
- View/remove training data

## 🔧 Configuration Options

```python
VannaFlaskApp(
    vn: VannaBase,                    # Your Vanna instance (REQUIRED)
    
    # Cache & Auth
    cache: Cache = MemoryCache(),     # Caching system
    auth: AuthInterface = NoAuth(),   # Authentication
    
    # UI Customization
    logo: str = "...",                # Logo URL
    title: str = "Welcome to Vanna",  # Page title
    subtitle: str = "...",            # Subtitle
    
    # Feature Toggles
    show_training_data: bool = True,
    suggested_questions: bool = True,
    sql: bool = True,
    table: bool = True,
    csv_download: bool = True,
    chart: bool = True,
    redraw_chart: bool = True,
    auto_fix_sql: bool = True,
    ask_results_correct: bool = True,
    followup_questions: bool = True,
    summarization: bool = True,
    function_generation: bool = True,
    
    # Advanced
    debug: bool = True,
    allow_llm_to_see_data: bool = False,
    
    # Custom Assets
    index_html_path: str = None,      # Custom HTML
    assets_folder: str = None,        # Custom assets
)
```

## 🚀 Khi nào dùng VannaFlaskApp?

### ✅ Dùng VannaFlaskApp khi:
1. **Cần web UI** cho end-users (non-technical users)
2. **Demo/prototype** nhanh chóng
3. **Internal tool** cho team data/analytics
4. **Training interface** để add/manage training data
5. **Interactive exploration** với charts, tables

### ❌ KHÔNG dùng VannaFlaskApp khi:
1. **Chỉ cần API** (như n8n integration) → Dùng FastAPI như main.py
2. **Custom frontend** (React, Vue, etc.) → Dùng VannaFlaskAPI
3. **Production at scale** → FastAPI + custom frontend
4. **Embedded trong app khác** → API only

## 🆚 FastAPI vs VannaFlaskApp

| Feature | FastAPI (main.py) | VannaFlaskApp |
|---------|-------------------|---------------|
| **REST API** | ✅ Custom endpoints | ✅ Built-in /api/v0/* |
| **Web UI** | ❌ No UI | ✅ Full UI included |
| **Performance** | ⚡ Very fast | 🐢 Slower (Flask) |
| **Async** | ✅ Native async | ❌ Sync only |
| **Customization** | 🎨 Full control | 🔧 Limited |
| **Production** | ✅ Best choice | ⚠️ OK for internal |
| **Setup** | 🛠️ Manual | ⚡ Instant |

## 💡 Kết hợp cả hai

Bạn có thể chạy **cả FastAPI và VannaFlaskApp** trên 2 ports khác nhau:

```python
# main.py (Production API for n8n)
# Port 8000: FastAPI REST API
uvicorn.run(app, host="0.0.0.0", port=8000)

# ui.py (Internal UI for team)
# Port 8084: VannaFlaskApp UI
from vanna.flask import VannaFlaskApp
ui_app = VannaFlaskApp(vn, title="Internal SQL Tool")
ui_app.run(host="0.0.0.0", port=8084)
```

## 📝 Tóm tắt

### Main.py (hiện tại) - FastAPI
- **Mục đích**: Production API cho n8n, external integrations
- **Port**: 8000 (hoặc Railway auto)
- **URL**: https://vanna-production.up.railway.app
- **Dùng cho**: n8n workflows, automation, custom frontend

### VannaFlaskApp (optional)
- **Mục đích**: Web UI cho internal users
- **Port**: 8084 (default)
- **URL**: http://localhost:8084
- **Dùng cho**: Interactive SQL exploration, training data management

## 🎯 Recommendation

**Với mục tiêu n8n integration của bạn:**
- ✅ **Giữ nguyên main.py (FastAPI)** - Đây là lựa chọn đúng!
- ✅ Railway deployment với FastAPI đã hoàn thành
- ✅ n8n sẽ connect vào FastAPI endpoints

**Nếu muốn thêm UI cho team:**
- Tạo file `ui.py` riêng với VannaFlaskApp
- Deploy riêng hoặc chạy local
- Dùng cho training, testing, exploration

---

## 🔗 Next Steps

Bạn đã có:
- ✅ FastAPI production API (main.py)
- ✅ Railway deployment (vanna-production.up.railway.app)
- ✅ All tests passing

**Tiếp theo: n8n Integration** 🎉

Tôi sẽ tạo hướng dẫn n8n workflow để connect với API của bạn!
