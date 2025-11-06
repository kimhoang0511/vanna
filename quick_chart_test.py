"""
Quick Chart Test - Minimal example
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
        config['path'] = f'./quick_test_{uuid.uuid4().hex[:8]}'
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

print("🚀 Quick Chart Test")
print("=" * 60)

vn = MyVanna(config={'api_key': os.environ['OPENAI_API_KEY'], 'model': 'gpt-4o-mini'})

print("\n1️⃣ Connecting to database...")
vn.connect_to_sqlite('https://vanna.ai/Chinook.sqlite')
print("✅ Connected!")

print("\n2️⃣ Training schema (quick)...")
df_ddl = vn.run_sql("SELECT type, sql FROM sqlite_master WHERE sql is not null LIMIT 3")
for ddl in df_ddl['sql'].to_list():
    vn.train(ddl=ddl)
print("✅ Trained!")

print("\n3️⃣ Generating SQL...")
question = "What are the top 5 artists by number of albums?"
sql = vn.generate_sql(question)
print(f"SQL:\n{sql}\n")

print("4️⃣ Executing SQL...")
df = vn.run_sql(sql)
print(f"Results ({len(df)} rows):")
print(df.to_string(index=False))

print("\n5️⃣ Creating chart...")
try:
    plotly_code = vn.generate_plotly_code(
        question=question,
        sql=sql,
        df_metadata=f"Running df.dtypes gives:\n{df.dtypes}"
    )
    print("Generated Plotly code:")
    print(plotly_code[:200] + "...")
    
    fig = vn.get_plotly_figure(
        plotly_code=plotly_code,
        df=df,
        dark_mode=False
    )
    
    output_file = "quick_chart_test.html"
    fig.write_html(output_file)
    print(f"\n✅ SUCCESS! Chart saved to: {output_file}")
    print(f"📂 Open: file://{os.path.abspath(output_file)}")
    
except Exception as e:
    print(f"❌ Chart error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("✅ Test completed!")
