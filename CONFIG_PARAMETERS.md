# Hướng dẫn Config MyVanna Parameters

## 1. Cấu trúc cơ bản

```python
from vanna.chromadb import ChromaDB_VectorStore
from vanna.openai import OpenAI_Chat

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

# Khởi tạo với config
vn = MyVanna(config={
    # Tham số ở đây
})
```

## 2. Các tham số ChromaDB_VectorStore

### 2.1. Embedding Function
```python
config = {
    'embedding_function': custom_embedding_function
}
```
- **Mô tả**: Function để tạo embeddings cho text
- **Mặc định**: `chromadb.utils.embedding_functions.DefaultEmbeddingFunction()` (all-MiniLM-L6-v2, 384 dims)
- **Custom**: Có thể dùng BGE-M3, OpenAI embeddings, v.v.

**Ví dụ:**
```python
from bge_m3_embedding import BGE_M3_EmbeddingFunction

bge_ef = BGE_M3_EmbeddingFunction(api_key="hf_xxx")
vn = MyVanna(config={'embedding_function': bge_ef})
```

### 2.2. ChromaDB Client Type
```python
config = {
    'client': 'persistent'  # hoặc 'in-memory'
}
```
- **Mặc định**: `'persistent'`
- **Tùy chọn**:
  - `'persistent'`: Lưu data vào disk (file `chroma.sqlite3`)
  - `'in-memory'`: Chỉ lưu trong RAM (mất khi restart)
  - Hoặc pass trực tiếp ChromaDB client object

### 2.3. Storage Path
```python
config = {
    'path': './my_chroma_db'
}
```
- **Mặc định**: `'.'` (thư mục hiện tại)
- **Mô tả**: Đường dẫn lưu ChromaDB data (khi dùng persistent client)

### 2.4. Number of Results (Retrieval)
```python
config = {
    'n_results': 10,              # Áp dụng cho tất cả
    'n_results_sql': 5,           # Chỉ SQL examples
    'n_results_ddl': 3,           # Chỉ DDL/schema
    'n_results_documentation': 7  # Chỉ documentation
}
```
- **Mặc định**: `10` cho tất cả
- **Mô tả**: Số lượng kết quả retrieve từ vector store khi generate SQL
- **Tip**: Tăng nếu có nhiều training data, giảm để tăng tốc độ

### 2.5. Collection Metadata
```python
config = {
    'collection_metadata': {'hnsw:space': 'cosine'}
}
```
- **Mặc định**: `None`
- **Mô tả**: Metadata cho ChromaDB collections (advanced)

## 3. Các tham số OpenAI_Chat

### 3.1. API Key
```python
config = {
    'api_key': 'sk-proj-xxx...'
}
```
- **Mặc định**: Đọc từ `OPENAI_API_KEY` environment variable
- **Bắt buộc**: Phải có API key (qua config hoặc env var)

### 3.2. Model Selection
```python
config = {
    'model': 'gpt-4o-mini'  # Sẽ được dùng trong generate_sql()
}
```
- **Tùy chọn phổ biến**:
  - `'gpt-3.5-turbo'`: Rẻ, nhanh, đủ dùng
  - `'gpt-4o-mini'`: ⭐ **Recommended** - Balance tốt
  - `'gpt-4o'`: Chất lượng cao nhất, đắt
  - `'gpt-4-turbo'`: Legacy GPT-4

**Lưu ý**: Tham số `model` trong config sẽ được override bởi `kwargs` trong các method như `generate_sql(model='gpt-4o')`

### 3.3. Temperature
```python
config = {
    'temperature': 0.7
}
```
- **Mặc định**: `0.7`
- **Phạm vi**: `0.0` - `2.0`
- **Mô tả**: Độ "sáng tạo" của LLM
  - `0.0`: Deterministic, luôn trả về kết quả giống nhau
  - `0.7`: Cân bằng (recommended)
  - `1.0+`: Random hơn, ít dùng cho SQL generation

### 3.4. Custom OpenAI Client
```python
from openai import OpenAI

custom_client = OpenAI(
    api_key="sk-xxx",
    base_url="https://api.openai.com/v1",
    timeout=60.0
)

vn = MyVanna(client=custom_client, config={...})
```
- **Dùng khi**: Cần custom base_url, timeout, hoặc dùng proxy

## 4. Các tham số VannaBase (Base Class)

### 4.1. Dialect
```python
config = {
    'dialect': 'PostgreSQL'  # hoặc 'MySQL', 'SQL Server', v.v.
}
```
- **Mặc định**: `'SQL'`
- **Mô tả**: Loại SQL database, giúp LLM generate syntax đúng

### 4.2. Language
```python
config = {
    'language': 'Vietnamese'
}
```
- **Mặc định**: `None` (English)
- **Mô tả**: Ngôn ngữ response từ LLM
- **Ví dụ**: `'Vietnamese'`, `'Spanish'`, `'French'`

### 4.3. Max Tokens
```python
config = {
    'max_tokens': 14000
}
```
- **Mặc định**: `14000`
- **Mô tả**: Giới hạn context length cho LLM prompt

## 5. Ví dụ Config đầy đủ

### 5.1. Config cơ bản (Production-ready)
```python
from vanna.chromadb import ChromaDB_VectorStore
from vanna.openai import OpenAI_Chat
from bge_m3_embedding import BGE_M3_EmbeddingFunction
import os

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

# Custom BGE-M3 embedding
bge_ef = BGE_M3_EmbeddingFunction(
    api_key=os.environ['HUGGINGFACE_API_KEY']
)

vn = MyVanna(config={
    # OpenAI
    'api_key': os.environ['OPENAI_API_KEY'],
    'model': 'gpt-4o-mini',
    'temperature': 0.7,
    
    # ChromaDB
    'embedding_function': bge_ef,
    'client': 'persistent',
    'path': './chroma_db',
    
    # Retrieval
    'n_results_sql': 5,
    'n_results_ddl': 3,
    'n_results_documentation': 7,
    
    # Base
    'dialect': 'PostgreSQL',
    'language': 'Vietnamese',
    'max_tokens': 14000
})
```

### 5.2. Config cho Testing (In-memory)
```python
vn = MyVanna(config={
    'api_key': os.environ['OPENAI_API_KEY'],
    'model': 'gpt-3.5-turbo',
    'client': 'in-memory',  # ← Không lưu disk
    'temperature': 0.0,      # ← Deterministic
    'n_results': 5           # ← Ít training data
})
```

### 5.3. Config với Custom OpenAI Endpoint
```python
from openai import OpenAI

# Custom client cho Azure OpenAI hoặc proxy
custom_client = OpenAI(
    api_key="xxx",
    base_url="https://your-azure-endpoint.openai.azure.com/",
    timeout=120.0
)

vn = MyVanna(
    client=custom_client,
    config={
        'embedding_function': bge_ef,
        'dialect': 'SQL Server',
        'temperature': 0.5
    }
)
```

## 6. Override tham số runtime

Nhiều tham số có thể override khi gọi methods:

```python
# Config với gpt-4o-mini mặc định
vn = MyVanna(config={'model': 'gpt-4o-mini'})

# Nhưng có thể dùng GPT-4 cho câu hỏi phức tạp
sql = vn.generate_sql(
    question="Complex question",
    model='gpt-4o'  # ← Override
)
```

## 7. Best Practices

### 7.1. Môi trường Development
```python
config = {
    'client': 'in-memory',
    'model': 'gpt-3.5-turbo',
    'temperature': 0.0,
    'n_results': 5
}
```

### 7.2. Môi trường Production
```python
config = {
    'api_key': os.environ['OPENAI_API_KEY'],
    'model': 'gpt-4o-mini',
    'temperature': 0.7,
    'embedding_function': bge_m3_ef,
    'client': 'persistent',
    'path': '/var/lib/vanna/chroma_db',
    'n_results_sql': 10,
    'n_results_ddl': 5,
    'n_results_documentation': 10,
    'dialect': 'PostgreSQL',
    'language': 'Vietnamese'
}
```

### 7.3. Tiếng Việt tối ưu
```python
config = {
    'model': 'gpt-4o-mini',        # ← Hiểu tiếng Việt tốt
    'embedding_function': bge_ef,   # ← BGE-M3 multilingual
    'language': 'Vietnamese',       # ← Response bằng tiếng Việt
    'dialect': 'PostgreSQL'
}
```

## 8. Troubleshooting

### Lỗi: "Embedding dimension mismatch"
**Nguyên nhân**: Đổi embedding function sau khi đã train
**Giải pháp**: Xóa ChromaDB và train lại
```bash
rm -f chroma.sqlite3
rm -rf chroma_db/
```

### Lỗi: "API key not found"
**Giải pháp**:
```python
config = {
    'api_key': 'sk-proj-xxx'  # ← Pass trực tiếp
}
# Hoặc
export OPENAI_API_KEY="sk-proj-xxx"
```

### Lỗi: Rate limit exceeded
**Giải pháp**: Giảm `n_results` hoặc dùng OpenAI client với retry logic
```python
from openai import OpenAI

client = OpenAI(
    api_key="xxx",
    max_retries=3,
    timeout=60.0
)
vn = MyVanna(client=client, config={...})
```

## 9. Tham khảo thêm

- **ChromaDB Docs**: https://docs.trychroma.com/
- **OpenAI API Docs**: https://platform.openai.com/docs/api-reference
- **Vanna Docs**: https://vanna.ai/docs/
- **BGE-M3 Model**: https://huggingface.co/BAAI/bge-m3
