"""
Vietnamese Chart Test - Chart với câu hỏi tiếng Việt
"""
import os
import uuid
from dotenv import load_dotenv

# Load from .env file
load_dotenv()

from vanna.chromadb import ChromaDB_VectorStore
from vanna.openai import OpenAI_Chat

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        if config is None:
            config = {}
        config['path'] = f'./vietnamese_test_{uuid.uuid4().hex[:8]}'
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

print("🇻🇳 Vietnamese Chart Test")
print("=" * 70)

vn = MyVanna(config={'api_key': os.environ['OPENAI_API_KEY'], 'model': 'gpt-4o-mini'})

print("\n📊 Kết nối database...")
vn.connect_to_sqlite('https://vanna.ai/Chinook.sqlite')
print("✅ Đã kết nối!")

print("\n📚 Training schema...")
df_ddl = vn.run_sql("SELECT type, sql FROM sqlite_master WHERE sql is not null LIMIT 5")
for ddl in df_ddl['sql'].to_list():
    vn.train(ddl=ddl)
print("✅ Training xong!")

# Test với nhiều câu hỏi tiếng Việt
questions = [
    {
        "vn": "10 nghệ sĩ có nhiều album nhất",
        "en": "Top 10 artists by album count",
        "file": "chart_top_artists.html"
    },
    {
        "vn": "Tổng số khách hàng theo quốc gia",
        "en": "Total customers by country", 
        "file": "chart_customers_by_country.html"
    },
    {
        "vn": "5 thể loại nhạc phổ biến nhất",
        "en": "Top 5 most popular music genres",
        "file": "chart_popular_genres.html"
    }
]

for i, q in enumerate(questions, 1):
    print("\n" + "=" * 70)
    print(f"🎯 TEST {i}/3")
    print("=" * 70)
    print(f"❓ Câu hỏi (Tiếng Việt): {q['vn']}")
    print(f"❓ Question (English): {q['en']}")
    
    try:
        # Generate SQL (dùng English để stable hơn)
        print(f"\n🔧 Generating SQL...")
        sql = vn.generate_sql(q['en'])
        print(f"SQL:\n{sql}")
        
        # Execute
        print(f"\n📊 Executing...")
        df = vn.run_sql(sql)
        print(f"Results ({len(df)} rows):")
        print(df.head().to_string(index=False))
        
        # Create chart
        print(f"\n📈 Creating chart...")
        
        if vn.should_generate_chart(df):
            plotly_code = vn.generate_plotly_code(
                question=q['en'],
                sql=sql,
                df_metadata=f"Running df.dtypes gives:\n{df.dtypes}"
            )
            
            fig = vn.get_plotly_figure(
                plotly_code=plotly_code,
                df=df,
                dark_mode=False
            )
            
            fig.write_html(q['file'])
            print(f"✅ Chart saved: {q['file']}")
            print(f"   Open: file://{os.path.abspath(q['file'])}")
        else:
            print("⚠️  Data không phù hợp cho chart")
            
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "=" * 70)
print("📊 SUMMARY")
print("=" * 70)

# List all created charts
import glob
charts = glob.glob("chart_*.html")
if charts:
    print(f"\n✅ Created {len(charts)} charts:")
    for chart in charts:
        size = os.path.getsize(chart) / 1024 / 1024
        print(f"   • {chart} ({size:.1f} MB)")
    
    print(f"\n💡 Mở tất cả charts:")
    print(f"   open {' '.join(charts)}")
else:
    print("\n⚠️  No charts created")

print("\n" + "=" * 70)
print("✅ TEST HOÀN THÀNH!")
print("=" * 70)
