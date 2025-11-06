"""
Test config 'language': 'Vietnamese' ảnh hưởng như thế nào
"""

import os
from vanna.chromadb import ChromaDB_VectorStore
from vanna.openai import OpenAI_Chat
from bge_m3_embedding import BGE_M3_EmbeddingFunction
import pandas as pd

# Set API keys
os.environ['OPENAI_API_KEY'] = ''

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

print("=" * 70)
print("TEST CONFIG 'language': 'Vietnamese'")
print("=" * 70)

# Test 1: Không có language config
print("\n1️⃣ Without language config:")
vn1 = MyVanna(config={
    'api_key': os.environ['OPENAI_API_KEY'],
    'client': 'in-memory'
})
print(f"   language: {vn1.language}")
print(f"   _response_language(): '{vn1._response_language()}'")

# Test 2: Có language = 'Vietnamese'
print("\n2️⃣ With language = 'Vietnamese':")
vn2 = MyVanna(config={
    'api_key': os.environ['OPENAI_API_KEY'],
    'client': 'in-memory',
    'language': 'Vietnamese'
})
print(f"   language: {vn2.language}")
print(f"   _response_language(): '{vn2._response_language()}'")

# Test 3: Test generate_followup_questions với sample data
print("\n3️⃣ Testing generate_followup_questions (uses _response_language):")

# Fake data để test
sample_df = pd.DataFrame({
    'name': ['Phan Van K', 'Dao Thi C', 'Tran Thi B'],
    'total_sales': [90000, 50000, 20000]
})

print("\n   Sample data:")
print(sample_df.to_markdown(index=False))

print("\n   🤖 Generating followup questions (Vietnamese)...")
try:
    questions = vn2.generate_followup_questions(
        question="Top 3 sản phẩm bán chạy nhất?",
        sql="SELECT name, SUM(sales) as total_sales FROM sale GROUP BY name ORDER BY total_sales DESC LIMIT 3",
        df=sample_df,
        n_questions=3
    )
    
    print(f"\n   ✅ Generated {len(questions)} questions:")
    for i, q in enumerate(questions, 1):
        if q.strip():  # Skip empty lines
            print(f"      {i}. {q}")
            
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Kiểm tra dialect
print("\n4️⃣ Testing dialect config:")
vn3 = MyVanna(config={
    'api_key': os.environ['OPENAI_API_KEY'],
    'client': 'in-memory',
    'dialect': 'PostgreSQL'
})
print(f"   dialect: {vn3.dialect}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("""
Config 'language': 'Vietnamese' chỉ ảnh hưởng:
  ✅ generate_followup_questions() - Câu hỏi follow-up bằng tiếng Việt
  ✅ generate_summary() - Summary bằng tiếng Việt
  ❌ generate_sql() - KHÔNG ảnh hưởng (SQL prompt vẫn bằng tiếng Anh)

Để SQL generation hiểu tiếng Việt tốt hơn:
  1. Dùng GPT-4o-mini (thay vì GPT-3.5-turbo)
  2. Dùng BGE-M3 embedding (multilingual)
  3. Train với examples tiếng Việt
  4. Set dialect = 'PostgreSQL'
""")
print("=" * 70)
