# 🚀 HƯỚNG DẪN CHẠY DỰ ÁN VANNA

## 📌 Tổng quan
Vanna là framework Python cho phép **hỏi database bằng ngôn ngữ tự nhiên** và tự động sinh SQL.

---

## 🔧 CÁC CÁCH CHẠY DỰ ÁN

### **Cách 1: Chạy Demo Đơn Giản (Không cần API key)**

File demo này sử dụng Mock LLM để minh họa workflow:

```bash
cd /Users/kimtvh/IdeaProjects/vanna
python3 demo_simple.py
```

**Kết quả:** Hiển thị toàn bộ workflow từ train → ask → generate SQL

---

### **Cách 2: Chạy Demo Thực Tế với OpenAI**

#### Bước 1: Cài đặt dependencies
```bash
pip install 'vanna[openai,chromadb]'
```

#### Bước 2: Set API key
```bash
export OPENAI_API_KEY='sk-your-api-key-here'
```

Hoặc trong Python:
```python
import os
os.environ['OPENAI_API_KEY'] = 'sk-...'
```

#### Bước 3: Chạy demo
```bash
python3 demo_real.py
```

**Kết quả:** 
- Kết nối tới SQLite database
- Train với DDL, documentation, SQL examples
- Hỏi 3 câu hỏi và nhận SQL + kết quả thực tế

---

### **Cách 3: Chạy Tests**

#### Cài đặt dev dependencies:
```bash
pip install -e '.[all]' tox pre-commit
```

#### Chạy test suite:
```bash
# Chạy tất cả tests
tox -e py310

# Hoặc trên macOS
tox -e mac

# Chạy tests cụ thể
pytest tests/test_vanna.py -v

# Chạy một test function
pytest tests/test_vanna.py::test_vn_openai -v
```

---

### **Cách 4: Chạy trong Jupyter Notebook**

#### Cài đặt Jupyter:
```bash
pip install jupyter notebook
```

#### Tạo notebook mới:
```python
# Cell 1: Install và import
!pip install 'vanna[openai,chromadb]'

from vanna.chromadb import ChromaDB_VectorStore
from vanna.openai import OpenAI_Chat

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

# Cell 2: Khởi tạo
import os
vn = MyVanna(config={
    'api_key': os.environ['OPENAI_API_KEY'],
    'model': 'gpt-3.5-turbo'
})

# Cell 3: Connect DB
vn.connect_to_sqlite('https://vanna.ai/Chinook.sqlite')

# Cell 4: Train
df_ddl = vn.run_sql("SELECT type, sql FROM sqlite_master WHERE sql is not null")
for ddl in df_ddl['sql'].to_list():
    vn.train(ddl=ddl)

# Cell 5: Ask
sql = vn.generate_sql("What are the top 10 customers by sales?")
df = vn.run_sql(sql)
print(df)
```

---

## 🎯 WORKFLOW CƠ BẢN

### **1. Train (Huấn luyện)**

```python
# Train với DDL (database schema)
vn.train(ddl="""
    CREATE TABLE customers (
        id INT PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100)
    )
""")

# Train với Documentation
vn.train(documentation="Customers table chứa thông tin khách hàng...")

# Train với SQL examples
vn.train(
    question="Who are the top customers?",
    sql="SELECT * FROM customers ORDER BY total_sales DESC LIMIT 10"
)

# Train từ JSON file
vn.train(json_file='training_data/sample-imdb/questions.json')
```

### **2. Ask (Hỏi đáp)**

```python
# Cách 1: Chỉ generate SQL
sql = vn.generate_sql("What are the top 10 products by revenue?")
print(sql)

# Cách 2: Generate SQL và chạy
df = vn.run_sql(sql)
print(df)

# Cách 3: Sử dụng ask() - tự động chạy và tạo chart
sql, df, fig, followup_questions = vn.ask(
    question="Show me sales by month",
    print_results=True
)
```

### **3. Visualize (Trực quan hóa)**

```python
# Generate Plotly code
plotly_code = vn.generate_plotly_code(
    question="Show sales trend",
    sql=sql,
    df=df
)

# Get figure
fig = vn.get_plotly_figure(plotly_code, df)
fig.show()  # Hiển thị chart
```

---

## 💡 CÁC USE CASE THỰC TẾ

### **Use Case 1: PostgreSQL + OpenAI + ChromaDB**

```python
from vanna.chromadb import ChromaDB_VectorStore
from vanna.openai import OpenAI_Chat

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

vn = MyVanna(config={'api_key': 'sk-...', 'model': 'gpt-4'})

# Connect to PostgreSQL
vn.connect_to_postgres(
    host='localhost',
    dbname='mydb',
    user='myuser',
    password='mypassword',
    port=5432
)

# Train và sử dụng
# ... (như ví dụ trên)
```

### **Use Case 2: Snowflake + OpenAI**

```python
vn.connect_to_snowflake(
    account='your-account',
    username='your-username',
    password='your-password',
    database='your-database',
    schema='your-schema'
)
```

### **Use Case 3: Local LLM với Ollama**

```bash
# Cài đặt
pip install 'vanna[ollama,chromadb]'

# Start Ollama
ollama serve
ollama pull llama2
```

```python
from vanna.ollama import Ollama
from vanna.chromadb import ChromaDB_VectorStore

class MyVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)

vn = MyVanna(config={'model': 'llama2'})
# Không cần API key!
```

### **Use Case 4: Deploy Web App với Streamlit**

```bash
pip install vanna[openai,chromadb]
pip install streamlit

# Clone streamlit template
git clone https://github.com/vanna-ai/vanna-streamlit.git
cd vanna-streamlit

# Sửa config trong app.py
# Chạy app
streamlit run app.py
```

---

## 📊 CẤU TRÚC TRAINING DATA

Xem ví dụ trong `training_data/`:

**Format JSON:**
```json
[
  {
    "question": "what are 5 most grossing movies?",
    "answer": "SELECT series_title, gross FROM movies ORDER BY gross DESC LIMIT 5;"
  },
  {
    "question": "which director has the most movies?",
    "answer": "SELECT director, count(*) FROM movies GROUP BY director ORDER BY count(*) DESC LIMIT 1;"
  }
]
```

**Load training data:**
```python
import json

with open('training_data/sample-imdb/questions.json', 'r') as f:
    data = json.load(f)
    
for item in data:
    vn.train(question=item['question'], sql=item['answer'])
```

---

## 🔍 DEBUG & TROUBLESHOOTING

### Xem training data hiện có:
```python
df = vn.get_training_data()
print(df)
```

### Xóa training data:
```python
# Xóa theo ID
vn.remove_training_data(id='abc123')

# Xóa tất cả
for _, row in df.iterrows():
    vn.remove_training_data(row['id'])
```

### Xem prompt được gửi tới LLM:
```python
# Vanna tự động log
vn.generate_sql("Your question")
# Output sẽ show "SQL Prompt" và "LLM Response"
```

### Kiểm tra connection:
```python
# Test query
df = vn.run_sql("SELECT 1")
print(df)
```

---

## ⚡ PERFORMANCE TIPS

1. **Train đủ dữ liệu:** Ít nhất 10-20 ví dụ SQL cho mỗi loại câu hỏi
2. **Sử dụng documentation:** Giải thích business logic và thuật ngữ
3. **Fine-tune n_results:** Điều chỉnh số lượng training data được retrieve
   ```python
   vn = MyVanna(config={
       'api_key': 'sk-...',
       'n_results': 10,  # Default là 10
       'n_results_sql': 5,  # Số SQL examples
       'n_results_ddl': 3,  # Số DDL statements
   })
   ```
4. **Auto-train:** Tự động lưu các query thành công
   ```python
   sql, df, fig, _ = vn.ask(question="...", auto_train=True)
   ```

---

## 📚 TÀI LIỆU THAM KHẢO

- **Documentation:** https://vanna.ai/docs/
- **GitHub:** https://github.com/vanna-ai/vanna
- **Discord:** https://discord.gg/qUZYKHremx
- **Examples:** https://vanna.ai/docs/app/

---

## ❓ CÂU HỎI THƯỜNG GẶP

**Q: Vanna gửi data của tôi lên đâu không?**
A: Không! Chỉ metadata (DDL, documentation, SQL examples) được lưu trong vector DB. Dữ liệu thực trong bảng KHÔNG được gửi tới LLM.

**Q: Tôi có thể dùng free không?**
A: Có! Dùng Ollama (local LLM) + ChromaDB (local vector DB) hoàn toàn free.

**Q: Vanna hỗ trợ tiếng Việt không?**
A: Có! Set config:
```python
vn = MyVanna(config={'language': 'Vietnamese'})
```

**Q: Làm sao improve accuracy?**
A: Train nhiều hơn! Càng nhiều DDL, documentation và SQL examples → càng chính xác.

---

## 🎉 KẾT LUẬN

Vanna giúp bạn:
- ✅ Hỏi database bằng ngôn ngữ tự nhiên
- ✅ Tự động sinh SQL chính xác
- ✅ Tạo visualizations
- ✅ Không cần developer để viết query
- ✅ Dễ deploy và tích hợp

**Bắt đầu ngay với:**
```bash
python3 demo_simple.py  # Mock demo
python3 demo_real.py    # Real demo (cần API key)
```
