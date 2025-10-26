"""
Demo thực tế với OpenAI + ChromaDB
QUAN TRỌNG: Cần có OPENAI_API_KEY để chạy
"""

import os

# Kiểm tra API key
if 'OPENAI_API_KEY' not in os.environ:
    print("⚠️  ERROR: Chưa set OPENAI_API_KEY")
    print("\nCách set API key:")
    print("  export OPENAI_API_KEY='sk-...'")
    print("\nHoặc trong Python:")
    print("  os.environ['OPENAI_API_KEY'] = 'sk-...'")
    exit(1)

from vanna.chromadb import ChromaDB_VectorStore
from vanna.openai import OpenAI_Chat

# Bước 1: Tạo class kết hợp ChromaDB + OpenAI
class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

# Bước 2: Khởi tạo với config
vn = MyVanna(config={
    'api_key': os.environ['OPENAI_API_KEY'],
    'model': 'gpt-3.5-turbo'  # Hoặc 'gpt-4' nếu có quyền
})

print("=" * 60)
print("🚀 VANNA DEMO - OpenAI + ChromaDB + SQLite")
print("=" * 60)

# Bước 3: Kết nối database
print("\n📊 Kết nối tới Chinook SQLite database...")
vn.connect_to_sqlite('https://vanna.ai/Chinook.sqlite')
print("✅ Đã kết nối!")

# Bước 4: Xóa training data cũ (nếu có)
print("\n🧹 Dọn dẹp training data cũ...")
existing_training_data = vn.get_training_data()
if len(existing_training_data) > 0:
    for _, training_data in existing_training_data.iterrows():
        vn.remove_training_data(training_data['id'])
    print(f"  ✓ Đã xóa {len(existing_training_data)} records cũ")
else:
    print("  ✓ Không có data cũ")

# Bước 5: Train với DDL
print("\n📚 Train với database schema (DDL)...")
df_ddl = vn.run_sql("SELECT type, sql FROM sqlite_master WHERE sql is not null")
count = 0
for ddl in df_ddl['sql'].to_list():
    vn.train(ddl=ddl)
    count += 1
print(f"  ✓ Đã train {count} DDL statements")

# Bước 6: Train với documentation
print("\n📝 Train với documentation...")
vn.train(documentation="""
Chinook Database là database mẫu về cửa hàng nhạc số:
- Album: Chứa thông tin về albums
- Artist: Thông tin nghệ sĩ
- Track: Bài hát
- Customer: Khách hàng
- Invoice: Hóa đơn
- InvoiceLine: Chi tiết hóa đơn
Để tính tổng doanh thu của khách hàng, join Customer với Invoice.
""")
print("  ✓ Đã train documentation")

# Bước 7: Train với ví dụ SQL
print("\n💡 Train với ví dụ SQL...")
vn.train(
    question="Who are the top customers by sales?",
    sql="""
        SELECT c.FirstName || ' ' || c.LastName as CustomerName,
               SUM(i.Total) as TotalSales
        FROM Customer c
        JOIN Invoice i ON c.CustomerId = i.CustomerId
        GROUP BY c.CustomerId
        ORDER BY TotalSales DESC
        LIMIT 10
    """
)
print("  ✓ Đã train 1 SQL example")

# Bước 8: ASK - Hỏi câu hỏi
print("\n" + "=" * 60)
print("🎯 HỎI CÂU HỎI BẰNG NGÔN NGỮ TỰ NHIÊN")
print("=" * 60)

questions = [
    "What are the top 5 customers by total sales?",
    "How many tracks are there in the database?",
    "Which artist has the most albums?"
]

for i, question in enumerate(questions, 1):
    print(f"\n{'─' * 60}")
    print(f"❓ Câu hỏi {i}: {question}")
    print(f"{'─' * 60}")
    
    try:
        # Generate SQL
        sql = vn.generate_sql(question)
        print(f"\n🔧 SQL được sinh:")
        print(sql)
        
        # Run SQL
        print(f"\n📊 Kết quả:")
        df = vn.run_sql(sql)
        print(df.to_string(index=False))
        
        # Generate chart (optional)
        # fig = vn.get_plotly_figure(plotly_code=vn.generate_plotly_code(question, sql, df), df=df)
        # fig.show()
        
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("✅ DEMO HOÀN THÀNH")
print("=" * 60)
print("""
📌 Các bước đã thực hiện:
1. Khởi tạo Vanna với OpenAI + ChromaDB
2. Kết nối SQLite database
3. Train với DDL (schema)
4. Train với documentation
5. Train với SQL examples
6. Hỏi câu hỏi và nhận SQL + kết quả

💡 Tips:
• Càng train nhiều → càng chính xác
• Có thể auto-train trên successful queries
• Hỗ trợ visualization với Plotly
• Có thể deploy lên web với Streamlit/Flask
""")
