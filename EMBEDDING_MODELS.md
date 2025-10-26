# 🧠 MÔ HÌNH EMBEDDING TRONG DỰ ÁN VANNA

## 📊 TÓM TẮT

Dự án Vanna hỗ trợ **NHIỀU mô hình embedding khác nhau** tùy thuộc vào Vector Store và LLM provider bạn chọn. Dưới đây là chi tiết:

---

## 🎯 CÁC MÔ HÌNH EMBEDDING ĐƯỢC HỖ TRỢ

### **1️⃣ ChromaDB (Default) - `all-MiniLM-L6-v2`**

**File:** `src/vanna/chromadb/chromadb_vector.py`

```python
from chromadb.utils import embedding_functions

default_ef = embedding_functions.DefaultEmbeddingFunction()
```

**Mô hình:** `all-MiniLM-L6-v2` (sentence-transformers)
- **Provider:** Hugging Face
- **Kích thước:** 384 dimensions
- **Ưu điểm:** 
  - ✅ Chạy local, không cần API key
  - ✅ Nhanh và nhẹ (chỉ ~80MB)
  - ✅ Miễn phí 100%
  - ✅ Hỗ trợ đa ngôn ngữ tốt
- **Nhược điểm:**
  - ❌ Accuracy thấp hơn OpenAI embeddings
  - ❌ Cần tải model lần đầu (~79.3MB như bạn thấy trong output)

**Trong demo của bạn:**
```
/Users/kimtvh/.cache/chroma/onnx_models/all-MiniLM-L6-v2/onnx.tar.gz: 
100%|████| 79.3M/79.3M [00:46<00:00, 1.80MiB/s]
```
→ **Đây là mô hình bạn đã dùng!**

---

### **2️⃣ OpenAI Embeddings - `text-embedding-ada-002`**

**File:** `src/vanna/openai/openai_embeddings.py`

```python
def generate_embedding(self, data: str, **kwargs) -> list[float]:
    embedding = self.client.embeddings.create(
        model="text-embedding-ada-002",
        input=data,
    )
    return embedding.get("data")[0]["embedding"]
```

**Mô hình:** `text-embedding-ada-002`
- **Provider:** OpenAI
- **Kích thước:** 1536 dimensions
- **Ưu điểm:**
  - ✅ Accuracy cao nhất
  - ✅ Tối ưu cho tiếng Anh
  - ✅ Được train trên dữ liệu khổng lồ
- **Nhược điểm:**
  - ❌ Cần API key ($$$)
  - ❌ Phải gửi data lên cloud
  - ❌ Chi phí: $0.0001 / 1K tokens

**Cách sử dụng:**
```python
from vanna.openai import OpenAI_Embeddings, OpenAI_Chat

class MyVanna(OpenAI_Embeddings, OpenAI_Chat):
    def __init__(self, config=None):
        OpenAI_Embeddings.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

vn = MyVanna(config={'api_key': 'sk-...'})
```

---

### **3️⃣ Cohere Embeddings - `embed-multilingual-v3.0`**

**File:** `src/vanna/cohere/cohere_embeddings.py`

```python
def __init__(self, client=None, config=None):
    # Default embedding model
    self.model = "embed-multilingual-v3.0"

def generate_embedding(self, data: str, **kwargs) -> list[float]:
    embedding = self.client.embeddings.create(
        model=self.model,
        input=data,
        encoding_format="float",
    )
    return embedding.data[0].embedding
```

**Mô hình:** `embed-multilingual-v3.0`
- **Provider:** Cohere
- **Kích thước:** 1024 dimensions
- **Ưu điểm:**
  - ✅ Hỗ trợ 100+ ngôn ngữ (bao gồm tiếng Việt)
  - ✅ Accuracy cao cho multilingual
  - ✅ Giá rẻ hơn OpenAI
- **Nhược điểm:**
  - ❌ Cần API key
  - ❌ Phải gửi data lên cloud

---

### **4️⃣ Các Vector Store khác**

#### **Milvus:**
```python
# File: src/vanna/milvus/milvus_vector.py
from pymilvus import model

self.embedding_function = model.DefaultEmbeddingFunction()
```
→ Sử dụng `milvus_model.DefaultEmbeddingFunction()` (tương tự sentence-transformers)

#### **Oracle Vector:**
```python
# File: src/vanna/oracle/oracle_vector.py
from chromadb.utils import embedding_functions

default_ef = embedding_functions.DefaultEmbeddingFunction()
```
→ Cũng dùng `all-MiniLM-L6-v2`

#### **FAISS, Pinecone, Qdrant, Weaviate:**
→ Các vector stores này cho phép **tự custom embedding function**

---

## 🔧 CUSTOM EMBEDDING MODEL

Bạn có thể thay đổi embedding model khi khởi tạo:

### **Cách 1: Với ChromaDB - Dùng Sentence Transformers**

```python
from chromadb.utils import embedding_functions
from vanna.chromadb import ChromaDB_VectorStore
from vanna.openai import OpenAI_Chat

# Chọn model khác
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"  # Tốt hơn cho tiếng Việt
)

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

vn = MyVanna(config={
    'api_key': 'sk-...',
    'embedding_function': sentence_transformer_ef  # Custom embedding
})
```

### **Cách 2: Với ChromaDB - Dùng OpenAI Embeddings**

```python
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key="sk-...",
    model_name="text-embedding-ada-002"
)

vn = MyVanna(config={
    'api_key': 'sk-...',
    'embedding_function': openai_ef
})
```

### **Cách 3: Với ChromaDB - Dùng Cohere Embeddings**

```python
cohere_ef = embedding_functions.CohereEmbeddingFunction(
    api_key="cohere-api-key",
    model_name="embed-multilingual-v3.0"
)

vn = MyVanna(config={
    'api_key': 'sk-...',
    'embedding_function': cohere_ef
})
```

---

## 🎯 KHUYẾN NGHỊ THEO USE CASE

### **1. Cho môi trường Production / Accuracy cao:**
```
✅ OpenAI text-embedding-ada-002
   → Accuracy tốt nhất, tiếng Anh tốt
   
✅ Cohere embed-multilingual-v3.0
   → Hỗ trợ tiếng Việt tốt, giá rẻ hơn
```

### **2. Cho Development / Testing / Local:**
```
✅ ChromaDB DefaultEmbeddingFunction (all-MiniLM-L6-v2)
   → Miễn phí, chạy local, không cần API key
```

### **3. Cho multilingual (tiếng Việt):**
```
✅ paraphrase-multilingual-MiniLM-L12-v2 (local)
✅ Cohere embed-multilingual-v3.0 (cloud)
```

### **4. Cho scale lớn / chi phí thấp:**
```
✅ Sentence Transformers (local)
   → Chạy trên GPU/CPU của bạn, không tốn API calls
```

---

## 📝 SO SÁNH CÁC MÔ HÌNH

| Model | Provider | Dimensions | API Key | Cost | Multilingual | Accuracy |
|-------|----------|------------|---------|------|--------------|----------|
| **all-MiniLM-L6-v2** | HuggingFace | 384 | ❌ Không | ✅ Free | ⭐⭐⭐ | ⭐⭐⭐ |
| **text-embedding-ada-002** | OpenAI | 1536 | ✅ Có | 💰 $0.0001/1K | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **embed-multilingual-v3.0** | Cohere | 1024 | ✅ Có | 💰 Rẻ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **paraphrase-multilingual-MiniLM-L12-v2** | HuggingFace | 384 | ❌ Không | ✅ Free | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 🧪 KIỂM TRA MODEL ĐANG DÙNG

Chạy code này để xem model embedding hiện tại:

```python
from vanna.chromadb import ChromaDB_VectorStore
from vanna.openai import OpenAI_Chat

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

vn = MyVanna(config={'api_key': 'sk-...'})

# In ra embedding function
print(f"Embedding Function: {vn.embedding_function}")
print(f"Model Name: {getattr(vn.embedding_function, '_model_name', 'Unknown')}")

# Test embedding
test_embedding = vn.generate_embedding("test")
print(f"Embedding Dimensions: {len(test_embedding)}")
```

**Output mẫu:**
```
Embedding Function: <chromadb.utils.embedding_functions.ONNXMiniLM_L6_V2 object>
Model Name: all-MiniLM-L6-v2
Embedding Dimensions: 384
```

---

## 🔍 KẾT LUẬN

**Trong demo của bạn vừa chạy:**
- ✅ Dùng **ChromaDB** làm Vector Store
- ✅ Dùng **all-MiniLM-L6-v2** làm Embedding Model (default của ChromaDB)
- ✅ Dùng **OpenAI GPT-3.5-turbo** để generate SQL
- ✅ Model được tải tự động lần đầu: `79.3MB`

**Để improve accuracy với tiếng Việt, bạn có thể:**
1. Đổi sang `paraphrase-multilingual-MiniLM-L12-v2` (free, local)
2. Hoặc dùng `Cohere embed-multilingual-v3.0` (paid, cloud, accuracy cao hơn)

Bạn muốn tôi tạo demo với embedding model khác không? 🚀
