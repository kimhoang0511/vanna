"""
Ví dụ config MyVanna cho các use case khác nhau
"""

import os
from vanna.chromadb import ChromaDB_VectorStore
from vanna.openai import OpenAI_Chat
from bge_m3_embedding import BGE_M3_EmbeddingFunction


class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    """Custom Vanna class kết hợp ChromaDB + OpenAI"""
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)


# ============================================================================
# 1. CONFIG CƠ BẢN - Cho người mới bắt đầu
# ============================================================================
def config_basic():
    """Config đơn giản nhất, sử dụng defaults"""
    vn = MyVanna(config={
        'api_key': os.environ['OPENAI_API_KEY']
    })
    return vn


# ============================================================================
# 2. CONFIG PRODUCTION - Đầy đủ tham số
# ============================================================================
def config_production():
    """Config production-ready với BGE-M3 + GPT-4o-mini"""
    
    # Custom embedding function
    bge_ef = BGE_M3_EmbeddingFunction(
        api_key=os.environ.get('HUGGINGFACE_API_KEY')
    )
    
    vn = MyVanna(config={
        # ===== OpenAI Settings =====
        'api_key': os.environ['OPENAI_API_KEY'],
        'model': 'gpt-4o-mini',          # Balance cost vs quality
        'temperature': 0.7,               # Creativity level
        
        # ===== ChromaDB Settings =====
        'embedding_function': bge_ef,     # BGE-M3 for multilingual
        'client': 'persistent',           # Save to disk
        'path': './chroma_db_production', # Storage path
        
        # ===== Retrieval Settings =====
        'n_results_sql': 10,              # Top-10 similar SQL examples
        'n_results_ddl': 5,               # Top-5 table schemas
        'n_results_documentation': 10,    # Top-10 docs
        
        # ===== Base Settings =====
        'dialect': 'PostgreSQL',          # SQL dialect
        'language': 'Vietnamese',         # Response language
        'max_tokens': 14000               # Context limit
    })
    
    return vn


# ============================================================================
# 3. CONFIG TESTING - In-memory, không lưu disk
# ============================================================================
def config_testing():
    """Config cho testing, không lưu data"""
    vn = MyVanna(config={
        'api_key': os.environ['OPENAI_API_KEY'],
        'model': 'gpt-3.5-turbo',  # Cheap & fast
        'client': 'in-memory',     # ← Không lưu disk
        'temperature': 0.0,        # ← Deterministic
        'n_results': 5             # ← Ít data
    })
    return vn


# ============================================================================
# 4. CONFIG TIẾNG VIỆT - Tối ưu cho Vietnamese
# ============================================================================
def config_vietnamese():
    """Config tối ưu cho câu hỏi tiếng Việt"""
    
    # BGE-M3 hỗ trợ multilingual tốt
    bge_ef = BGE_M3_EmbeddingFunction(
        api_key=os.environ['HUGGINGFACE_API_KEY']
    )
    
    vn = MyVanna(config={
        'api_key': os.environ['OPENAI_API_KEY'],
        'model': 'gpt-4o-mini',        # ← Hiểu tiếng Việt tốt
        'embedding_function': bge_ef,   # ← BGE-M3 multilingual
        'language': 'Vietnamese',       # ← Response tiếng Việt
        'dialect': 'PostgreSQL',
        'temperature': 0.7,
        'n_results_sql': 7,
        'n_results_documentation': 10
    })
    
    return vn


# ============================================================================
# 5. CONFIG HIGH-ACCURACY - Dùng GPT-4 cho độ chính xác cao
# ============================================================================
def config_high_accuracy():
    """Config cho độ chính xác cao nhất (đắt hơn)"""
    
    bge_ef = BGE_M3_EmbeddingFunction(
        api_key=os.environ['HUGGINGFACE_API_KEY']
    )
    
    vn = MyVanna(config={
        'api_key': os.environ['OPENAI_API_KEY'],
        'model': 'gpt-4o',             # ← GPT-4 latest
        'temperature': 0.3,             # ← Ít random hơn
        'embedding_function': bge_ef,
        'n_results_sql': 15,            # ← Retrieve nhiều examples
        'n_results_ddl': 10,
        'n_results_documentation': 15,
        'dialect': 'PostgreSQL'
    })
    
    return vn


# ============================================================================
# 6. CONFIG COST-OPTIMIZED - Tiết kiệm chi phí
# ============================================================================
def config_cost_optimized():
    """Config tiết kiệm chi phí nhất"""
    vn = MyVanna(config={
        'api_key': os.environ['OPENAI_API_KEY'],
        'model': 'gpt-3.5-turbo',  # ← Rẻ nhất
        'temperature': 0.5,
        'n_results': 5,             # ← Ít retrieval = ít tokens
        'dialect': 'PostgreSQL'
    })
    return vn


# ============================================================================
# 7. CONFIG CUSTOM EMBEDDING - Dùng OpenAI embeddings
# ============================================================================
def config_openai_embeddings():
    """Dùng OpenAI embeddings thay vì BGE-M3"""
    from chromadb.utils import embedding_functions
    
    # OpenAI embedding function
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.environ['OPENAI_API_KEY'],
        model_name="text-embedding-3-small"  # hoặc text-embedding-ada-002
    )
    
    vn = MyVanna(config={
        'api_key': os.environ['OPENAI_API_KEY'],
        'model': 'gpt-4o-mini',
        'embedding_function': openai_ef,  # ← OpenAI embeddings
        'dialect': 'PostgreSQL'
    })
    
    return vn


# ============================================================================
# 8. CONFIG AZURE OPENAI - Dùng Azure endpoint
# ============================================================================
def config_azure_openai():
    """Config cho Azure OpenAI Service"""
    from openai import AzureOpenAI
    
    # Custom Azure client
    azure_client = AzureOpenAI(
        api_key=os.environ['AZURE_OPENAI_API_KEY'],
        api_version="2024-02-15-preview",
        azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT']
    )
    
    vn = MyVanna(
        client=azure_client,
        config={
            'temperature': 0.7,
            'dialect': 'SQL Server'  # Azure thường dùng SQL Server
        }
    )
    
    return vn


# ============================================================================
# 9. CONFIG MULTIPLE DATABASES - Nhiều database
# ============================================================================
def config_multi_database():
    """Config riêng cho từng database"""
    
    # Config cho PostgreSQL
    vn_postgres = MyVanna(config={
        'api_key': os.environ['OPENAI_API_KEY'],
        'model': 'gpt-4o-mini',
        'dialect': 'PostgreSQL',
        'path': './chroma_db_postgres'
    })
    
    # Config cho MySQL
    vn_mysql = MyVanna(config={
        'api_key': os.environ['OPENAI_API_KEY'],
        'model': 'gpt-4o-mini',
        'dialect': 'MySQL',
        'path': './chroma_db_mysql'
    })
    
    return vn_postgres, vn_mysql


# ============================================================================
# 10. CONFIG DEVELOPMENT - Cho local development
# ============================================================================
def config_development():
    """Config cho development/debugging"""
    vn = MyVanna(config={
        'api_key': os.environ.get('OPENAI_API_KEY', 'sk-test'),
        'model': 'gpt-3.5-turbo',
        'client': 'in-memory',
        'temperature': 0.0,     # ← Deterministic cho debugging
        'n_results': 3,
        'dialect': 'PostgreSQL'
    })
    return vn


# ============================================================================
# 11. Ví dụ sử dụng
# ============================================================================
if __name__ == '__main__':
    print("=" * 70)
    print("VÍ DỤ CONFIG MYVANNA")
    print("=" * 70)
    
    # Chọn config phù hợp
    print("\n1. Basic Config:")
    vn1 = config_basic()
    print(f"   ✅ Model: {vn1.config.get('model', 'default')}")
    
    print("\n2. Production Config (Vietnamese):")
    vn2 = config_vietnamese()
    print(f"   ✅ Model: gpt-4o-mini")
    print(f"   ✅ Embedding: BGE-M3 (1024 dims)")
    print(f"   ✅ Language: Vietnamese")
    
    print("\n3. Testing Config (In-memory):")
    vn3 = config_testing()
    print(f"   ✅ Client: in-memory")
    print(f"   ✅ Temperature: 0.0")
    
    print("\n" + "=" * 70)
    print("Chọn config phù hợp với use case của bạn!")
    print("=" * 70)
