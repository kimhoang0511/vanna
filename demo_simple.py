"""
Demo đơn giản về cách hoạt động của Vanna
Ví dụ này MINH HỌA workflow mà KHÔNG cần API key thực

LƯU Ý: File này chỉ để hiểu workflow, không generate SQL thực tế.
Để chạy thực tế, xem file demo_real.py
"""

print("=" * 60)
print("🚀 DEMO VANNA - Workflow Overview (Không cần API key)")
print("=" * 60)
print("\n⚠️  LƯU Ý: Demo này chỉ MINH HỌA workflow của Vanna")
print("Để sinh SQL thực tế, cần dùng OpenAI/Claude - xem demo_real.py\n")

# Mock các function để demo workflow
class MockVanna:
    def __init__(self):
        self.training_data = []
        self.db_connected = False
    
    def connect_to_sqlite(self, url):
        self.db_connected = True
        print(f"✅ [Mock] Đã kết nối tới: {url}")
    
    def run_sql(self, sql):
        print(f"✅ [Mock] Đang chạy SQL: {sql[:50]}...")
        # Mock return some data
        import pandas as pd
        return pd.DataFrame({
            'type': ['table', 'table', 'index'],
            'sql': [
                'CREATE TABLE Album (AlbumId INTEGER PRIMARY KEY, Title TEXT, ArtistId INTEGER)',
                'CREATE TABLE Artist (ArtistId INTEGER PRIMARY KEY, Name TEXT)',
                'CREATE INDEX idx_album ON Album(ArtistId)'
            ]
        })
    
    def train(self, ddl=None, documentation=None, question=None, sql=None):
        if ddl:
            self.training_data.append({'type': 'ddl', 'content': ddl})
            return True
        elif documentation:
            self.training_data.append({'type': 'doc', 'content': documentation})
            return True
        elif question and sql:
            self.training_data.append({'type': 'sql', 'question': question, 'sql': sql})
            return True
    
    def generate_sql(self, question):
        print(f"\n🤖 [Mock LLM] Đang phân tích câu hỏi: {question}")
        print("   → Tìm kiếm training data liên quan...")
        print(f"   → Tìm thấy {len(self.training_data)} training items")
        print("   → Gửi prompt tới LLM...")
        print("   → Nhận response từ LLM...")
        
        # Mock SQL response
        mock_sql = """
        SELECT c.FirstName || ' ' || c.LastName as CustomerName,
               SUM(i.Total) as TotalSales
        FROM Customer c
        JOIN Invoice i ON c.CustomerId = i.CustomerId
        GROUP BY c.CustomerId
        ORDER BY TotalSales DESC
        LIMIT 3
        """
        return mock_sql.strip()

# Khởi tạo Mock Vanna
vn = MockVanna()

print("=" * 60)
print("🚀 DEMO VANNA - Chuyển câu hỏi thành SQL")
print("=" * 60)

# Bước 3: Kết nối database (ví dụ với SQLite)
print("\n📊 Bước 1: Kết nối database...")
vn.connect_to_sqlite('https://vanna.ai/Chinook.sqlite')
print("✅ Đã kết nối tới Chinook.sqlite (database mẫu về âm nhạc)")

# Bước 4: Lấy schema của database để train
print("\n📚 Bước 2: Train model với DDL (database schema)...")
df_ddl = vn.run_sql("SELECT type, sql FROM sqlite_master WHERE sql is not null")

for ddl in df_ddl['sql'].to_list()[:3]:  # Lấy 3 tables đầu tiên
    vn.train(ddl=ddl)
    print(f"  ✓ Đã train: {ddl[:50]}...")

# Bước 5: Train với documentation
print("\n📝 Bước 3: Train model với documentation...")
vn.train(documentation="Chinook là database về cửa hàng nhạc số với thông tin về albums, artists, tracks, customers và invoices")
print("  ✓ Đã train documentation")

# Bước 6: Train với ví dụ SQL
print("\n💡 Bước 4: Train model với ví dụ SQL...")
vn.train(
    question="Who are the top 5 customers by sales?",
    sql="""
        SELECT c.CustomerId, c.FirstName, c.LastName, SUM(i.Total) as TotalSales
        FROM Customer c
        JOIN Invoice i ON c.CustomerId = i.CustomerId
        GROUP BY c.CustomerId
        ORDER BY TotalSales DESC
        LIMIT 5
    """
)
print("  ✓ Đã train với ví dụ SQL")

# Bước 7: Hỏi câu hỏi và sinh SQL
print("\n" + "=" * 60)
print("🎯 Bước 5: Hỏi câu hỏi bằng ngôn ngữ tự nhiên...")
print("=" * 60)

question = "What are the top 3 customers by total sales?"
print(f"\n❓ Câu hỏi: {question}")

# Generate SQL từ câu hỏi
sql = vn.generate_sql(question)
print(f"\n🔧 SQL được sinh ra:")
print("-" * 60)
print(sql)
print("-" * 60)

# Chạy SQL và lấy kết quả
print("\n📊 Kết quả:")
try:
    df = vn.run_sql(sql)
    print(df.to_string())
except Exception as e:
    print(f"⚠️  Lưu ý: Mock LLM không sinh SQL thực, chỉ demo workflow. Error: {e}")

print("\n" + "=" * 60)
print("✨ WORKFLOW HOÀN CHỈNH")
print("=" * 60)
print("""
Quy trình làm việc của Vanna:

1️⃣  TRAIN (Huấn luyện):
   • Train với DDL (schema database)
   • Train với Documentation (tài liệu nghiệp vụ)
   • Train với SQL examples (ví dụ câu hỏi-SQL)

2️⃣  ASK (Hỏi đáp):
   • User đặt câu hỏi bằng ngôn ngữ tự nhiên
   • Vanna tìm kiếm training data liên quan (RAG)
   • LLM sinh SQL dựa trên context
   • Chạy SQL trên database
   • Trả về kết quả (DataFrame + Chart)

3️⃣  IMPROVE (Cải thiện):
   • Auto-train trên SQL thành công
   • User feedback để fine-tune
   • Càng nhiều data → càng chính xác
""")

print("\n💡 Để chạy với LLM thực (OpenAI, Claude, v.v.), xem file demo_real.py")
