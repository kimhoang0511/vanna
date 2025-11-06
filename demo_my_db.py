"""
Demo kết nối với PostgreSQL thực tế + OpenAI
"""

import os
from vanna.chromadb import ChromaDB_VectorStore
from vanna.openai import OpenAI_Chat

# Set API key
os.environ['OPENAI_API_KEY'] = ''

print("=" * 70)
print("🚀 VANNA DEMO - Kết nối PostgreSQL + OpenAI thực tế")
print("=" * 70)

# Bước 1: Tạo class Vanna
class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

print("\n✅ Đã import Vanna components")

# Bước 2: Khởi tạo Vanna
print("\n🔧 Đang khởi tạo Vanna với OpenAI GPT-3.5-turbo...")
vn = MyVanna(config={
    'api_key': os.environ['OPENAI_API_KEY'],
    'model': 'gpt-3.5-turbo'
})
print("✅ Đã khởi tạo Vanna!")

# Bước 3: Parse PostgreSQL connection string
print("\n📊 Đang kết nối tới PostgreSQL...")
# postgresql://postgres:aLBazSQAKvyCNllyngDjoiTdMIjHLTDC@nozomi.proxy.rlwy.net:26750/railway

try:
    vn.connect_to_postgres(
        host='nozomi.proxy.rlwy.net',
        dbname='railway',
        user='postgres',
        password='aLBazSQAKvyCNllyngDjoiTdMIjHLTDC',
        port=26750
    )
    print("✅ Đã kết nối thành công tới PostgreSQL!")
except Exception as e:
    print(f"❌ Lỗi kết nối: {e}")
    print("\n⚠️  Kiểm tra:")
    print("  - Network connection")
    print("  - Firewall/Security groups")
    print("  - Database credentials")
    exit(1)

# Bước 4: Test connection với query đơn giản
print("\n🧪 Test query: Lấy danh sách tables...")
try:
    df_tables = vn.run_sql("""
        SELECT table_schema, table_name 
        FROM information_schema.tables 
        WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY table_schema, table_name
        LIMIT 20
    """)
    
    print(f"✅ Tìm thấy {len(df_tables)} tables:")
    print(df_tables.to_string(index=False))
    
except Exception as e:
    print(f"❌ Lỗi chạy query: {e}")
    exit(1)

# Bước 5: Lấy schema để train
print("\n" + "=" * 70)
print("📚 BƯỚC TRAIN: Lấy schema từ database")
print("=" * 70)

try:
    # Lấy thông tin columns
    df_columns = vn.run_sql("""
        SELECT 
            table_schema,
            table_name,
            column_name,
            data_type,
            is_nullable
        FROM information_schema.columns
        WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY table_schema, table_name, ordinal_position
    """)
    
    print(f"\n✅ Tìm thấy {len(df_columns)} columns")
    print("\n📋 Sample columns:")
    print(df_columns.head(10).to_string(index=False))
    
    # Train với DDL
    print("\n🎓 Đang train Vanna với schema...")
    
    # Tạo DDL statements từ thông tin columns
    tables_processed = set()
    train_count = 0
    
    for _, row in df_columns.iterrows():
        table_full_name = f"{row['table_schema']}.{row['table_name']}"
        
        if table_full_name not in tables_processed:
            tables_processed.add(table_full_name)
            
            # Lấy tất cả columns của table này
            table_cols = df_columns[
                (df_columns['table_schema'] == row['table_schema']) & 
                (df_columns['table_name'] == row['table_name'])
            ]
            
            # Tạo DDL statement
            ddl = f"-- Table: {table_full_name}\n"
            ddl += f"CREATE TABLE {table_full_name} (\n"
            
            col_defs = []
            for _, col in table_cols.iterrows():
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                col_defs.append(f"    {col['column_name']} {col['data_type']} {nullable}")
            
            ddl += ",\n".join(col_defs)
            ddl += "\n);"
            
            # Train
            vn.train(ddl=ddl)
            train_count += 1
            print(f"  ✓ Trained: {table_full_name}")
    
    print(f"\n✅ Đã train {train_count} tables!")
    
except Exception as e:
    print(f"❌ Lỗi khi train: {e}")
    import traceback
    traceback.print_exc()

# Bước 6: Train với documentation
print("\n📝 Train với documentation...")
vn.train(documentation="""
Database này chứa dữ liệu từ Railway PostgreSQL.
Các bảng có thể bao gồm thông tin về users, products, orders, v.v.
Để query dữ liệu, sử dụng schema.table_name format.
""")
print("✅ Đã train documentation")

# Bước 7: ASK - Test với câu hỏi
print("\n" + "=" * 70)
print("🎯 BƯỚC ASK: Hỏi câu hỏi và generate SQL")
print("=" * 70)

questions = [
    "Có bao nhiêu tables trong database?",
    "Liệt kê tất cả các tables và số lượng columns của mỗi table"
]

for i, question in enumerate(questions, 1):
    print(f"\n{'─' * 70}")
    print(f"❓ Câu hỏi {i}: {question}")
    print(f"{'─' * 70}")
    
    try:
        # Generate SQL
        print("\n🤖 Đang generate SQL với OpenAI...")
        sql = vn.generate_sql(question)
        
        print(f"\n🔧 SQL được sinh:")
        print("─" * 70)
        print(sql)
        print("─" * 70)
        
        # Run SQL
        print(f"\n📊 Đang chạy SQL...")
        df = vn.run_sql(sql)
        
        print(f"\n✅ Kết quả ({len(df)} rows):")
        print(df.to_string(index=False))
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 70)
print("✅ DEMO HOÀN THÀNH!")
print("=" * 70)

print("""
📌 Các bước đã thực hiện:
1. ✅ Kết nối PostgreSQL thành công
2. ✅ Lấy schema từ information_schema
3. ✅ Train Vanna với DDL của các tables
4. ✅ Train với documentation
5. ✅ Generate SQL từ câu hỏi tiếng Việt
6. ✅ Chạy SQL và trả về kết quả

💡 Tiếp theo bạn có thể:
• Thêm câu hỏi của riêng bạn
• Train với SQL examples cụ thể
• Tạo visualization với Plotly
• Deploy lên Streamlit web app
""")
