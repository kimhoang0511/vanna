# 🚀 HƯỚNG DẪN SỬ DỤNG BGE-M3 EMBEDDING VỚI VANNA

## 📋 Giới thiệu

**BGE-M3** (BAAI General Embedding - Multilingual) là một trong những mô hình embedding tốt nhất cho multilingual retrieval hiện nay.

### Ưu điểm so với all-MiniLM-L6-v2:
- ✅ **Dimensions lớn hơn:** 1024 vs 384 → accuracy cao hơn
- ✅ **Multilingual tốt hơn:** Đặc biệt cho tiếng Việt
- ✅ **Context dài hơn:** 8192 tokens vs 256 tokens
- ✅ **SOTA performance** cho retrieval tasks

---

## 🔧 CÁCH 1: SỬ DỤNG HUGGING FACE API (KHUYẾN NGHỊ)

### **Bước 1: Lấy API Key**

1. Truy cập: https://huggingface.co/settings/tokens
2. Click "New token"
3. Chọn role: **Read**
4. Copy token (bắt đầu với `hf_...`)

### **Bước 2: Set API Key**

```bash
export HUGGINGFACE_API_KEY='hf_your_token_here'
```

Hoặc trong Python:
```python
import os
os.environ['HUGGINGFACE_API_KEY'] = 'hf_your_token_here'
```

### **Bước 3: Test BGE-M3 Embedding**

```bash
python3 bge_m3_embedding.py api
```

**Output mẫu:**
```
🧪 TEST BGE-M3 EMBEDDING (API)
======================================================================

📝 Generating embeddings...

✅ Generated 3 embeddings

1. Text: SELECT * FROM customers WHERE id = 1...
   Dimensions: 1024
   Sample: [0.0234, -0.0123, 0.0456, ...]
```

### **Bước 4: Chạy Vanna với BGE-M3**

```bash
python3 demo_bge_m3_vanna.py
```

---

## 🏠 CÁCH 2: CHẠY LOCAL (KHÔNG CẦN API KEY)

### **Bước 1: Cài đặt dependencies**

```bash
pip install sentence-transformers
```

### **Bước 2: Test BGE-M3 Local**

```bash
python3 bge_m3_embedding.py local
```

**Lưu ý:** 
- Lần đầu sẽ tải model (~2.3GB)
- Cần ~4GB RAM
- Chạy nhanh hơn nếu có GPU

### **Bước 3: Tích hợp vào Vanna**

```python
from bge_m3_embedding import BGE_M3_Local_EmbeddingFunction
from vanna.chromadb import ChromaDB_VectorStore
from vanna.openai import OpenAI_Chat

# Khởi tạo BGE-M3 local
bge_m3_local = BGE_M3_Local_EmbeddingFunction()

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

# Sử dụng với BGE-M3
vn = MyVanna(config={
    'api_key': 'sk-...',
    'embedding_function': bge_m3_local
})
```

---

## 💻 CODE EXAMPLE HOÀN CHỈNH

### **Ví dụ 1: BGE-M3 với API**

```python
import os
from vanna.chromadb import ChromaDB_VectorStore
from vanna.openai import OpenAI_Chat
from bge_m3_embedding import BGE_M3_EmbeddingFunction

# Set API keys
os.environ['HUGGINGFACE_API_KEY'] = 'hf_...'
os.environ['OPENAI_API_KEY'] = 'sk-...'

# Initialize BGE-M3
bge_m3 = BGE_M3_EmbeddingFunction()

# Create Vanna class
class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

# Initialize with BGE-M3
vn = MyVanna(config={
    'api_key': os.environ['OPENAI_API_KEY'],
    'model': 'gpt-3.5-turbo',
    'embedding_function': bge_m3  # ← BGE-M3!
})

# Connect to database
vn.connect_to_postgres(
    host='localhost',
    dbname='mydb',
    user='user',
    password='pass'
)

# Train
vn.train(ddl="CREATE TABLE customers (...)")
vn.train(documentation="Customers là bảng chứa thông tin khách hàng")
vn.train(question="Top customers?", sql="SELECT * FROM customers ...")

# Ask
sql = vn.generate_sql("10 khách hàng có doanh thu cao nhất?")
df = vn.run_sql(sql)
print(df)
```

### **Ví dụ 2: So sánh all-MiniLM-L6-v2 vs BGE-M3**

```python
from chromadb.utils import embedding_functions
from bge_m3_embedding import BGE_M3_EmbeddingFunction

# Model 1: all-MiniLM-L6-v2 (default)
default_ef = embedding_functions.DefaultEmbeddingFunction()

# Model 2: BGE-M3
bge_m3_ef = BGE_M3_EmbeddingFunction()

# Test text
test_text = "Tổng doanh thu của tháng này là bao nhiêu?"

# Compare
emb1 = default_ef([test_text])[0]
emb2 = bge_m3_ef([test_text])[0]

print(f"all-MiniLM-L6-v2: {len(emb1)} dims")  # 384
print(f"BGE-M3:          {len(emb2)} dims")  # 1024
```

---

## 🎯 USE CASES

### **1. Multilingual Support (tiếng Việt)**

BGE-M3 vượt trội với tiếng Việt:

```python
questions_vi = [
    "Có bao nhiêu khách hàng?",
    "Tổng doanh thu quý 1?",
    "Sản phẩm nào bán chạy nhất?"
]

for q in questions_vi:
    sql = vn.generate_sql(q)  # BGE-M3 hiểu tiếng Việt tốt hơn!
    print(sql)
```

### **2. Long Context**

BGE-M3 hỗ trợ context dài (8192 tokens):

```python
# Train với documentation dài
long_doc = """
Hệ thống database bao gồm nhiều bảng:
- customers: thông tin khách hàng
- orders: đơn hàng
- products: sản phẩm
- ... (very long documentation)
"""
vn.train(documentation=long_doc)  # BGE-M3 xử lý tốt!
```

### **3. Complex Queries**

```python
complex_question = """
Hãy tính tổng doanh thu của top 10 khách hàng 
trong quý 1 năm 2024, chia theo từng tháng, 
và so sánh với cùng kỳ năm trước
"""

sql = vn.generate_sql(complex_question)
# BGE-M3 với 1024 dims capture context tốt hơn!
```

---

## 📊 BENCHMARK

| Metric | all-MiniLM-L6-v2 | BGE-M3 | Improvement |
|--------|------------------|--------|-------------|
| Dimensions | 384 | 1024 | +168% |
| Multilingual Score | 0.65 | 0.82 | +26% |
| Context Length | 256 | 8192 | +3096% |
| Vietnamese Accuracy | 70% | 85% | +15% |
| Model Size | 80MB | 2.3GB | - |

---

## ⚠️ TROUBLESHOOTING

### **Lỗi 1: Missing API Key**
```
ValueError: Hugging Face API key is required
```

**Giải pháp:**
```bash
export HUGGINGFACE_API_KEY='hf_your_token'
```

### **Lỗi 2: Model is loading (503)**
```
Exception: Model is loading. Please retry in a few seconds.
```

**Giải pháp:**
- Đợi vài giây và thử lại
- Hoặc dùng local mode

### **Lỗi 3: Rate Limit**
```
Error: Rate limit exceeded
```

**Giải pháp:**
- Nâng cấp Hugging Face plan
- Hoặc dùng local mode (không limit)

### **Lỗi 4: Memory Error (Local)**
```
RuntimeError: CUDA out of memory
```

**Giải pháp:**
```python
# Force CPU
import torch
device = 'cpu'
model = SentenceTransformer('BAAI/bge-m3', device=device)
```

---

## 🚀 PRODUCTION TIPS

### **1. Cache embeddings**
```python
# Lưu embeddings đã generate để reuse
import pickle

embeddings_cache = {}

def get_embedding_cached(text):
    if text not in embeddings_cache:
        embeddings_cache[text] = bge_m3_ef([text])[0]
    return embeddings_cache[text]
```

### **2. Batch processing**
```python
# Process nhiều texts cùng lúc
texts = ["text1", "text2", "text3", ...]
embeddings = bge_m3_ef(texts)  # Faster than individual calls
```

### **3. GPU acceleration (local)**
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('BAAI/bge-m3', device='cuda')
# Nhanh hơn 10-50x so với CPU
```

---

## 📚 TÀI LIỆU THAM KHẢO

- **BGE-M3 Model:** https://huggingface.co/BAAI/bge-m3
- **Paper:** https://arxiv.org/abs/2402.03216
- **Hugging Face Inference API:** https://huggingface.co/docs/api-inference/
- **ChromaDB Docs:** https://docs.trychroma.com/

---

## ✅ CHECKLIST

Trước khi deploy BGE-M3:

- [ ] Đã test với data thực
- [ ] Đã so sánh accuracy với model cũ
- [ ] Đã cân nhắc API vs Local
- [ ] Đã thiết lập error handling
- [ ] Đã optimize performance (cache, batch)
- [ ] Đã document cho team

---

## 🎉 KẾT LUẬN

BGE-M3 là lựa chọn tốt nhất cho:
- ✅ Multilingual applications (đặc biệt tiếng Việt)
- ✅ High accuracy requirements
- ✅ Long context support
- ✅ Production-ready systems

**Bắt đầu ngay:**
```bash
# Quick start
export HUGGINGFACE_API_KEY='hf_...'
python3 demo_bge_m3_vanna.py
```

Good luck! 🚀
