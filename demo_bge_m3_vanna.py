"""
Demo: Sử dụng BGE-M3 Embedding với Vanna + ChromaDB
- LLM: GPT-4o-mini (OpenAI)
- Embedding: BAAI/bge-m3 (1024 dims, Hugging Face)
- Vector Store: ChromaDB
- Database: PostgreSQL
- Prompt: Tối ưu cho tiếng Việt documentation
"""

import os
from vietnamese_vanna import VietnameseVanna
from bge_m3_embedding import BGE_M3_EmbeddingFunction

# Set API keys
os.environ['OPENAI_API_KEY'] = 'xxx'

print("=" * 70)
print("🚀 VANNA + BGE-M3 EMBEDDING DEMO")
print("=" * 70)

# Bước 1: Kiểm tra Hugging Face API key
hf_api_key = os.getenv('HUGGINGFACE_API_KEY')

if not hf_api_key:
    print("\n⚠️  CHƯA CÓ HUGGING FACE API KEY")
    print("\n📋 Hướng dẫn lấy API key:")
    print("1. Truy cập: https://huggingface.co/settings/tokens")
    print("2. Click 'New token' → Chọn 'Read' role")
    print("3. Copy token và set:")
    print("   export HUGGINGFACE_API_KEY='hf_your_token_here'")
    print("\n💡 Hoặc dùng local mode (không cần API key):")
    print("   pip install sentence-transformers")
    print("   python demo_bge_m3_vanna.py local")
    exit(1)

print(f"\n✅ Found Hugging Face API key: {hf_api_key[:10]}...")

# Bước 2: Khởi tạo BGE-M3 Embedding Function
print("\n🔧 Initializing BGE-M3 Embedding Function...")
try:
    bge_m3_ef = BGE_M3_EmbeddingFunction(api_key=hf_api_key)
    print("✅ BGE-M3 initialized successfully!")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Bước 3: Sử dụng VietnameseVanna class (tối ưu cho tiếng Việt)
# Không cần define class mới, dùng trực tiếp VietnameseVanna

print("\n🎯 Creating Vanna instance with BGE-M3 + Vietnamese optimization...")

# ⚠️ Important: Xóa ChromaDB collections cũ để tránh dimension mismatch
import shutil
chroma_path = './chroma_db_bge'
if os.path.exists(chroma_path):
    print(f"🗑️  Removing old ChromaDB data at {chroma_path}...")
    shutil.rmtree(chroma_path)
    print("✅ Old data removed!")

vn = VietnameseVanna(config={
    'api_key': os.environ['OPENAI_API_KEY'],
    'model': 'gpt-4o-mini',  # ← GPT-4o mini for better accuracy
    'embedding_function': bge_m3_ef,  # ← Custom BGE-M3!
    'language': 'Vietnamese',  # ← Response in Vietnamese
    'dialect': 'PostgreSQL',  # ← Database dialect
    'temperature': 0.7,  # ← Creativity level
    'n_results_sql': 5,  # ← Top-5 SQL examples
    'n_results_ddl': 3,  # ← Top-3 table schemas
    'n_results_documentation': 7  # ← Top-7 docs
})

print("✅ Vanna initialized with BGE-M3 + GPT-4o-mini + Vietnamese prompt optimization!")

# Bước 4: Test embedding
print("\n" + "=" * 70)
print("🧪 TEST EMBEDDING GENERATION")
print("=" * 70)

test_texts = [
    "SELECT * FROM customers WHERE id = 1",
    "Tổng doanh thu của tháng này là bao nhiêu?",
    "What are the top 10 products by revenue?"
]

print("\n📝 Testing BGE-M3 embeddings...")
for i, text in enumerate(test_texts, 1):
    print(f"\n{i}. Text: {text}")
    try:
        embedding = vn.generate_embedding(text)
        print(f"   ✅ Dimensions: {len(embedding)}")
        print(f"   ✅ Sample: [{embedding[0]:.4f}, {embedding[1]:.4f}, {embedding[2]:.4f}, ...]")
    except Exception as e:
        print(f"   ❌ Error: {e}")

# Bước 5: Connect to database và train
print("\n" + "=" * 70)
print("📊 CONNECT TO DATABASE & TRAIN")
print("=" * 70)

print("\n🔌 Connecting to PostgreSQL...")
try:
    vn.connect_to_postgres(
        host='nozomi.proxy.rlwy.net',
        dbname='railway',
        user='postgres',
        password='aLBazSQAKvyCNllyngDjoiTdMIjHLTDC',
        port=26750
    )
    print("✅ Connected to PostgreSQL!")
except Exception as e:
    print(f"❌ Connection error: {e}")
    exit(1)

# Lấy danh sách tables
print("\n📋 Getting tables list...")
df_tables = vn.run_sql("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    ORDER BY table_name
""")
print(f"✅ Found {len(df_tables)} tables:")
for table in df_tables['table_name']:
    print(f"   • {table}")

# Train với DDL của table sale (quan trọng nhất)
print("\n🎓 Training with DDL...")
ddl_sale = """
CREATE TABLE public.sale (
    id INTEGER PRIMARY KEY,
    name TEXT,
    date DATE,
    sales MONEY
);
"""
vn.train(ddl=ddl_sale)
print("✅ Trained with sale table DDL")

# Train với documentation
print("\n📝 Training with documentation...")
vn.train(documentation="""
Table 'sale' chứa dữ liệu bán hàng với:
- id: Mã giao dịch
- name: Tên sản phẩm hoặc khách hàng
- date: Ngày giao dịch
- sales: Doanh thu (kiểu money)

Để tính tổng doanh thu, dùng SUM(sales::numeric)
""")
print("✅ Trained with documentation")

# Train với SQL examples
print("\n💡 Training with SQL examples...")
vn.train(
    question="Tổng doanh thu là bao nhiêu?",
    sql="SELECT SUM(sales::numeric) as total_revenue FROM public.sale"
)
vn.train(
    question="Top 5 sản phẩm có doanh thu cao nhất?",
    sql="SELECT name, SUM(sales::numeric) as total FROM public.sale GROUP BY name ORDER BY total DESC LIMIT 5"
)
print("✅ Trained with 2 SQL examples")

# Bước 6: Test với câu hỏi
print("\n" + "=" * 70)
print("🎯 TEST SQL GENERATION WITH BGE-M3")
print("=" * 70)

questions = [
    "Có bao nhiêu giao dịch trong bảng sale?",
    "Tổng doanh thu của tất cả sản phẩm?",
    "Top 3 sản phẩm bán chạy nhất?"
]

for i, question in enumerate(questions, 1):
    print(f"\n{'─' * 70}")
    print(f"❓ Câu hỏi {i}: {question}")
    print(f"{'─' * 70}")
    
    try:
        print("\n🤖 Generating SQL with BGE-M3 embeddings...")
        sql = vn.generate_sql(question)
        
        print(f"\n🔧 Generated SQL:")
        print("─" * 70)
        print(sql)
        print("─" * 70)
        
        print(f"\n📊 Executing SQL...")
        df = vn.run_sql(sql)
        
        print(f"\n✅ Results ({len(df)} rows):")
        print(df.to_string(index=False))
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 70)
print("✅ DEMO COMPLETED!")
print("=" * 70)

print("""
📊 So sánh Embedding Models:

┌─────────────────────────┬────────┬──────────┬──────────────┐
│ Model                   │ Dims   │ Cost     │ Multilingual │
├─────────────────────────┼────────┼──────────┼──────────────┤
│ all-MiniLM-L6-v2 (old) │ 384    │ FREE     │ ⭐⭐⭐        │
│ BGE-M3 (new) ✨        │ 1024   │ FREE*    │ ⭐⭐⭐⭐⭐     │
│ text-embedding-ada-002  │ 1536   │ $$$      │ ⭐⭐⭐⭐      │
└─────────────────────────┴────────┴──────────┴──────────────┘

* FREE với API (có rate limit), hoặc chạy local

🎯 BGE-M3 advantages:
✅ Better multilingual support (especially Vietnamese)
✅ Larger dimensions (1024 vs 384) → better accuracy
✅ SOTA performance for retrieval tasks
✅ Support up to 8192 tokens context

💡 Next steps:
• Compare accuracy between all-MiniLM-L6-v2 and BGE-M3
• Try local BGE-M3 (no API limit)
• Fine-tune retrieval parameters (n_results)
""")
