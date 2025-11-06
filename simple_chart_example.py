"""
SIMPLE CHART EXAMPLE - Copy & Run
Ví dụ đơn giản nhất để tạo chart với Vanna
"""

# =============================================================================
# SETUP (Chỉ cần làm 1 lần)
# =============================================================================

import os
os.environ['OPENAI_API_KEY'] = 'sk-your-key-here'  # ← Thay bằng key thật

from vanna.chromadb import ChromaDB_VectorStore
from vanna.openai import OpenAI_Chat

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

vn = MyVanna(config={
    'api_key': os.environ['OPENAI_API_KEY'],
    'model': 'gpt-4o-mini'
})

# Connect to your database
vn.connect_to_postgres(
    host='nozomi.proxy.rlwy.net',
    port=26750,
    dbname='railway',
    user='postgres',
    password='aLBazSQAKvyCNllyngDjoiTdMIjHLTDC'
)

# =============================================================================
# CÁCH 1: TỐI GIẢN (1 dòng)
# =============================================================================

question = "Top 10 khách hàng có doanh thu cao nhất"

# Generate SQL
sql = vn.generate_sql(question)

# Execute
df = vn.run_sql(sql)

# Create chart (ALL IN ONE)
fig = vn.get_plotly_figure(
    plotly_code=vn.generate_plotly_code(question, sql, f"df.dtypes:\n{df.dtypes}"),
    df=df
)

# Save hoặc show
fig.write_html("chart.html")  # Save to file
# fig.show()                   # Open in browser

# =============================================================================
# CÁCH 2: TỪNG BƯỚC (Rõ ràng hơn)
# =============================================================================

question = "Top 10 khách hàng có doanh thu cao nhất"

# Bước 1: Generate SQL
sql = vn.generate_sql(question)
print(f"SQL: {sql}")

# Bước 2: Execute SQL
df = vn.run_sql(sql)
print(f"Data shape: {df.shape}")
print(df.head())

# Bước 3: Generate Plotly code
plotly_code = vn.generate_plotly_code(
    question=question,
    sql=sql,
    df_metadata=f"Running df.dtypes gives:\n{df.dtypes}"
)
print(f"Plotly code:\n{plotly_code}")

# Bước 4: Create figure
fig = vn.get_plotly_figure(
    plotly_code=plotly_code,
    df=df,
    dark_mode=False  # True cho dark theme
)

# Bước 5: Save/Show
fig.write_html("my_chart.html")
print("✅ Chart saved!")

# =============================================================================
# CÁCH 3: VỚI ERROR HANDLING (Production ready)
# =============================================================================

def create_chart_safe(question):
    """
    Tạo chart với error handling đầy đủ
    """
    try:
        # 1. Generate SQL
        sql = vn.generate_sql(question)
        
        # 2. Execute
        df = vn.run_sql(sql)
        
        # 3. Check if chart is suitable
        if not vn.should_generate_chart(df):
            print("⚠️  Data không phù hợp để tạo chart")
            return None
        
        # 4. Generate chart code
        plotly_code = vn.generate_plotly_code(
            question=question,
            sql=sql,
            df_metadata=f"Running df.dtypes gives:\n{df.dtypes}"
        )
        
        # 5. Create figure
        fig = vn.get_plotly_figure(
            plotly_code=plotly_code,
            df=df
        )
        
        return fig
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

# Usage
fig = create_chart_safe("Top 10 sản phẩm bán chạy")
if fig:
    fig.write_html("product_chart.html")

# =============================================================================
# CÁCH 4: CUSTOM CHART APPEARANCE
# =============================================================================

question = "Doanh thu theo tháng"
custom_instructions = "Create a line chart with blue color, add trend line, and show data labels"

sql = vn.generate_sql(question)
df = vn.run_sql(sql)

# Add custom instructions to question
plotly_code = vn.generate_plotly_code(
    question=f"{question}. {custom_instructions}",
    sql=sql,
    df_metadata=f"Running df.dtypes gives:\n{df.dtypes}"
)

fig = vn.get_plotly_figure(plotly_code, df)
fig.write_html("custom_chart.html")

# =============================================================================
# CÁCH 5: SAVE NHIỀU FORMATS
# =============================================================================

fig = create_chart_safe("Top 10 khách hàng")

if fig:
    # HTML (interactive)
    fig.write_html("chart.html")
    
    # JSON (for API)
    chart_json = fig.to_json()
    
    # PNG/PDF (static - requires kaleido)
    # pip install kaleido
    # fig.write_image("chart.png")
    # fig.write_image("chart.pdf")
    
    print("✅ Charts saved in multiple formats")

# =============================================================================
# CÁCH 6: DARK MODE
# =============================================================================

fig_light = vn.get_plotly_figure(
    plotly_code=vn.generate_plotly_code(question, sql, f"df.dtypes:\n{df.dtypes}"),
    df=df,
    dark_mode=False  # Light theme
)

fig_dark = vn.get_plotly_figure(
    plotly_code=vn.generate_plotly_code(question, sql, f"df.dtypes:\n{df.dtypes}"),
    df=df,
    dark_mode=True  # Dark theme
)

fig_light.write_html("chart_light.html")
fig_dark.write_html("chart_dark.html")

# =============================================================================
# TÓM TẮT
# =============================================================================

"""
3 BƯỚC CƠ BẢN:
1. plotly_code = vn.generate_plotly_code(question, sql, df_metadata)
2. fig = vn.get_plotly_figure(plotly_code, df)
3. fig.write_html("chart.html") hoặc fig.show()

PARAMETERS QUAN TRỌNG:
• question: Câu hỏi ban đầu
• sql: SQL query
• df_metadata: Thông tin về DataFrame (dtypes)
• df: DataFrame chứa data
• dark_mode: True/False cho theme

OUTPUT:
• fig.write_html() → Interactive HTML file
• fig.to_json() → JSON cho API
• fig.show() → Mở browser
• fig.write_image() → PNG/PDF (cần kaleido)

BEST PRACTICES:
✅ Luôn dùng vn.should_generate_chart(df) để check
✅ Wrap trong try/except
✅ Provide df_metadata rõ ràng
✅ Custom instructions cho chart đẹp hơn
❌ Không vẽ chart nếu data < 2 rows
❌ Không ignore exceptions
"""
