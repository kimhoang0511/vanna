"""
Demo tạo biểu đồ với Vanna + Plotly
Hướng dẫn chi tiết về visualization
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Kiểm tra API key
if 'OPENAI_API_KEY' not in os.environ:
    print("⚠️  ERROR: Chưa set OPENAI_API_KEY")
    exit(1)

from vanna.chromadb import ChromaDB_VectorStore
from vanna.openai import OpenAI_Chat
import uuid

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        # Add unique path to avoid dimension conflicts
        if config is None:
            config = {}
        config['path'] = f'./demo_chroma_{uuid.uuid4().hex[:8]}'
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

# Khởi tạo
vn = MyVanna(config={
    'api_key': os.environ['OPENAI_API_KEY'],
    'model': 'gpt-4o-mini'
})

print("=" * 70)
print("📊 VANNA CHART VISUALIZATION DEMO")
print("=" * 70)

# Kết nối database
print("\n🔌 Kết nối database...")
vn.connect_to_sqlite('https://vanna.ai/Chinook.sqlite')
print("✅ Connected!")

# Train nhanh (chỉ cần DDL để demo)
print("\n📚 Training database schema...")
df_ddl = vn.run_sql("SELECT type, sql FROM sqlite_master WHERE sql is not null")
for ddl in df_ddl['sql'].to_list()[:5]:  # Chỉ train 5 cái đầu để nhanh
    vn.train(ddl=ddl)
print("✅ Training done!")

print("\n" + "=" * 70)
print("🎨 DEMO 1: CƠ BẢN - Tạo biểu đồ từ câu hỏi")
print("=" * 70)

# Câu hỏi phù hợp với visualization
question = "What are the top 10 artists by number of albums?"

print(f"\n❓ Question: {question}")

# Bước 1: Generate SQL
print("\n🔧 Bước 1: Generate SQL...")
sql = vn.generate_sql(question)
print(f"SQL:\n{sql}")

# Bước 2: Execute SQL
print("\n📊 Bước 2: Execute SQL and get data...")
df = vn.run_sql(sql)
print(f"\nData preview:")
print(df.head().to_string(index=False))
print(f"\nDataFrame shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")

# Bước 3: Generate Plotly code
print("\n🎨 Bước 3: Generate Plotly visualization code...")
plotly_code = vn.generate_plotly_code(
    question=question,
    sql=sql,
    df_metadata=f"Running df.dtypes gives:\n{df.dtypes}"
)
print(f"Generated Plotly code:\n{plotly_code}")

# Bước 4: Create figure
print("\n📈 Bước 4: Create Plotly figure...")
try:
    fig = vn.get_plotly_figure(
        plotly_code=plotly_code,
        df=df,
        dark_mode=False  # True nếu muốn dark theme
    )
    
    # Save to HTML
    output_file = "chart_demo1.html"
    fig.write_html(output_file)
    print(f"✅ Chart saved to: {output_file}")
    print(f"   Open in browser: file://{os.path.abspath(output_file)}")
    
    # Optionally show in browser
    # fig.show()  # Mở browser tự động
    
except Exception as e:
    print(f"❌ Error creating chart: {e}")

print("\n" + "=" * 70)
print("🎨 DEMO 2: NÂNG CAO - Custom chart instructions")
print("=" * 70)

question2 = "What are the total sales by country?"

print(f"\n❓ Question: {question2}")

# Generate SQL
sql2 = vn.generate_sql(question2)
print(f"\n🔧 SQL:\n{sql2}")

# Execute
df2 = vn.run_sql(sql2)
print(f"\n📊 Data preview:")
print(df2.head().to_string(index=False))

# Custom chart với instructions
custom_instructions = "Create a horizontal bar chart sorted by sales amount in descending order. Use a blue color scheme."

print(f"\n🎨 Custom instructions: {custom_instructions}")

plotly_code2 = vn.generate_plotly_code(
    question=f"{question2}. {custom_instructions}",
    sql=sql2,
    df_metadata=f"Running df.dtypes gives:\n{df2.dtypes}"
)

try:
    fig2 = vn.get_plotly_figure(
        plotly_code=plotly_code2,
        df=df2,
        dark_mode=False
    )
    
    output_file2 = "chart_demo2.html"
    fig2.write_html(output_file2)
    print(f"✅ Custom chart saved to: {output_file2}")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 70)
print("🎨 DEMO 3: XỬ LÝ NHIỀU LOẠI CHART")
print("=" * 70)

chart_examples = [
    {
        "question": "How many albums were released each year?",
        "type": "Line Chart (time series)",
        "output": "chart_timeline.html"
    },
    {
        "question": "What is the distribution of track lengths?",
        "type": "Histogram",
        "output": "chart_histogram.html"
    },
    {
        "question": "Compare sales across genres",
        "type": "Bar Chart",
        "output": "chart_comparison.html"
    }
]

for i, example in enumerate(chart_examples, 1):
    print(f"\n{'─' * 70}")
    print(f"Example {i}: {example['type']}")
    print(f"Question: {example['question']}")
    print(f"{'─' * 70}")
    
    try:
        # Generate and execute
        sql_ex = vn.generate_sql(example['question'])
        df_ex = vn.run_sql(sql_ex)
        
        # Generate chart
        code_ex = vn.generate_plotly_code(
            question=example['question'],
            sql=sql_ex,
            df_metadata=f"Running df.dtypes gives:\n{df_ex.dtypes}"
        )
        
        fig_ex = vn.get_plotly_figure(
            plotly_code=code_ex,
            df=df_ex
        )
        
        fig_ex.write_html(example['output'])
        print(f"✅ Saved to: {example['output']}")
        
    except Exception as e:
        print(f"⚠️  Skipped: {e}")

print("\n" + "=" * 70)
print("💡 BEST PRACTICES & TIPS")
print("=" * 70)
print("""
1️⃣  CÁC LOẠI CHART PHÙ HỢP:
   • Bar Chart: So sánh categories (top 10, rankings)
   • Line Chart: Time series (trends over time)
   • Pie Chart: Proportions/percentages
   • Scatter Plot: Correlations
   • Histogram: Distributions

2️⃣  KIỂM TRA DF TRƯỚC KHI VẼ:
   • df.shape: Có đủ data không? (ít nhất 2 rows)
   • df.dtypes: Có numeric columns? (cần cho charts)
   • df.columns: Có đúng tên columns?

3️⃣  CUSTOM CHART APPEARANCE:
   plotly_code = vn.generate_plotly_code(
       question="Top 10 products. Use red color and add data labels.",
       sql=sql,
       df_metadata=f"df.dtypes:\\n{df.dtypes}"
   )

4️⃣  DARK MODE:
   fig = vn.get_plotly_figure(
       plotly_code=plotly_code,
       df=df,
       dark_mode=True  # ← Sáng/tối
   )

5️⃣  SAVE MULTIPLE FORMATS:
   fig.write_html("chart.html")      # Interactive HTML
   fig.write_image("chart.png")      # Static image (cần kaleido)
   fig.write_json("chart.json")      # JSON data

6️⃣  SHOW IN NOTEBOOK:
   fig.show()  # Jupyter/IPython
   
7️⃣  ERROR HANDLING:
   try:
       fig = vn.get_plotly_figure(plotly_code, df)
   except Exception as e:
       print(f"Cannot create chart: {e}")
       # Fallback: show table only

8️⃣  CHECK IF CHART IS NEEDED:
   should_chart = vn.should_generate_chart(df)
   if should_chart:
       # Generate chart
   else:
       # Just show table

9️⃣  INTEGRATE WITH RAILWAY API:
   # In main.py FastAPI endpoint
   @app.post("/generate_chart")
   def generate_chart(question: str, sql: str):
       df = vn.run_sql(sql)
       plotly_code = vn.generate_plotly_code(question, sql, df_metadata=...)
       fig = vn.get_plotly_figure(plotly_code, df)
       return {"chart_json": fig.to_json()}

🔟  VIETNAMESE QUESTIONS:
   question = "10 nghệ sĩ có nhiều album nhất"
   # Vanna sẽ translate → generate SQL → create chart
""")

print("\n" + "=" * 70)
print("✅ DEMO COMPLETED")
print("=" * 70)
print(f"""
📁 Files created:
   • chart_demo1.html - Top artists bar chart
   • chart_demo2.html - Sales by country (custom)
   • chart_timeline.html - Time series
   • chart_histogram.html - Distribution
   • chart_comparison.html - Comparison chart

🌐 Open in browser:
   open chart_demo1.html  # macOS
   
📚 Next steps:
   1. Integrate into Railway API (main.py)
   2. Return chart JSON to n8n
   3. Display in custom frontend
""")
