"""
Script kiểm tra embedding model đang được sử dụng trong Vanna
"""

from vanna.chromadb import ChromaDB_VectorStore
from vanna.openai import OpenAI_Chat
import os

# Set API key
os.environ['OPENAI_API_KEY'] = 'xxx'

print("=" * 70)
print("🔍 KIỂM TRA EMBEDDING MODEL")
print("=" * 70)

# Tạo class
class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

print("\n📊 Khởi tạo Vanna với ChromaDB (default)...")
vn = MyVanna(config={'api_key': os.environ['OPENAI_API_KEY']})

print("\n" + "=" * 70)
print("📋 THÔNG TIN EMBEDDING FUNCTION")
print("=" * 70)

# Lấy thông tin embedding function
ef = vn.embedding_function
print(f"\n✅ Embedding Function Type: {type(ef).__name__}")
print(f"   Module: {type(ef).__module__}")

# Kiểm tra model name
if hasattr(ef, '_model_name'):
    print(f"   Model Name: {ef._model_name}")
elif hasattr(ef, 'model_name'):
    print(f"   Model Name: {ef.model_name}")
else:
    print("   Model Name: all-MiniLM-L6-v2 (ChromaDB default)")

# Test generate embedding
print("\n" + "=" * 70)
print("🧪 TEST EMBEDDING GENERATION")
print("=" * 70)

test_texts = [
    "SELECT * FROM customers WHERE id = 1",
    "CREATE TABLE users (id INT, name VARCHAR(100))",
    "Tổng doanh thu của tháng này là bao nhiêu?"
]

for i, text in enumerate(test_texts, 1):
    print(f"\n📝 Test {i}: {text[:50]}...")
    try:
        embedding = vn.generate_embedding(text)
        print(f"   ✅ Embedding dimensions: {len(embedding)}")
        print(f"   ✅ Sample values: [{embedding[0]:.4f}, {embedding[1]:.4f}, {embedding[2]:.4f}, ...]")
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "=" * 70)
print("📊 TÓM TẮT")
print("=" * 70)

print("""
🎯 Embedding Model hiện tại:
   • Model: all-MiniLM-L6-v2 (sentence-transformers)
   • Provider: Hugging Face
   • Vector dimensions: 384
   • Cost: FREE (chạy local)
   • Multilingual: Có hỗ trợ (tốt cho tiếng Việt)

💡 Để đổi embedding model khác:
   1. OpenAI text-embedding-ada-002 (1536 dims, $$$, accuracy cao nhất)
   2. Cohere embed-multilingual-v3.0 (1024 dims, $$, tốt cho multilingual)
   3. paraphrase-multilingual-MiniLM-L12-v2 (384 dims, FREE, tốt cho Việt)

📚 Xem chi tiết trong file: EMBEDDING_MODELS.md
""")
