# 📊 Vanna Chart Visualization - Quick Guide

## 🎯 Quy trình cơ bản (3 bước)

```python
# Bước 1: Generate SQL
sql = vn.generate_sql("What are the top 10 customers?")

# Bước 2: Execute SQL
df = vn.run_sql(sql)

# Bước 3: Create Chart
plotly_code = vn.generate_plotly_code(question, sql, df_metadata=f"df.dtypes:\n{df.dtypes}")
fig = vn.get_plotly_figure(plotly_code=plotly_code, df=df)
fig.show()  # Hoặc fig.write_html("chart.html")
```

## 📈 Chi tiết từng bước

### 1. Generate Plotly Code

```python
plotly_code = vn.generate_plotly_code(
    question="Your question here",           # Câu hỏi gốc
    sql="SELECT ...",                        # SQL đã generate
    df_metadata="Running df.dtypes gives:\n...",  # Metadata của DataFrame
)
```

**Tham số:**
- `question` (str): Câu hỏi ban đầu
- `sql` (str): SQL query
- `df_metadata` (str): Thông tin về DataFrame (dtypes, shape, columns)

**Output:** Python code string để tạo Plotly figure

### 2. Create Plotly Figure

```python
fig = vn.get_plotly_figure(
    plotly_code=plotly_code,    # Code từ bước 1
    df=df,                      # DataFrame với data
    dark_mode=False             # True = dark theme
)
```

**Tham số:**
- `plotly_code` (str): Python code tạo chart
- `df` (DataFrame): Data để visualize
- `dark_mode` (bool): Dark/light theme

**Output:** Plotly Figure object

### 3. Display/Save Chart

```python
# Option 1: Show in browser
fig.show()

# Option 2: Save to HTML (interactive)
fig.write_html("chart.html")

# Option 3: Save to PNG (static image, cần kaleido)
fig.write_image("chart.png")

# Option 4: Get JSON (cho API)
chart_json = fig.to_json()
```

## 🎨 Custom Chart Instructions

```python
question = "Top 10 products by revenue"
custom_instructions = "Create a horizontal bar chart with green color scheme and show data labels"

plotly_code = vn.generate_plotly_code(
    question=f"{question}. {custom_instructions}",
    sql=sql,
    df_metadata=f"df.dtypes:\n{df.dtypes}"
)
```

## 🔍 Check if Chart is Suitable

```python
df = vn.run_sql(sql)

# Vanna tự động kiểm tra
if vn.should_generate_chart(df):
    # Tạo chart
    plotly_code = vn.generate_plotly_code(question, sql, df_metadata=...)
    fig = vn.get_plotly_figure(plotly_code, df)
else:
    # Chỉ hiển thị table
    print(df)
```

## 📊 Các loại Chart phổ biến

```python
# Bar Chart - So sánh categories
"What are the top 10 products by sales?"

# Line Chart - Time series
"Show revenue trend over the last 12 months"

# Pie Chart - Proportions
"What is the market share by region?"

# Scatter Plot - Correlation
"Plot price vs quantity sold"

# Histogram - Distribution
"Show distribution of order amounts"
```

## 🚀 Integration với FastAPI (main.py)

```python
from fastapi import FastAPI
import pandas as pd

app = FastAPI()

@app.post("/generate_chart")
async def generate_chart(question: str, sql: str = None):
    """
    Generate chart from question or SQL
    Returns: Chart as JSON
    """
    try:
        # Generate SQL if not provided
        if not sql:
            sql = vn.generate_sql(question)
        
        # Execute SQL
        df = vn.run_sql(sql)
        
        # Check if chart is suitable
        if not vn.should_generate_chart(df):
            return {
                "success": False,
                "message": "Data not suitable for chart visualization",
                "table": df.to_dict(orient='records')
            }
        
        # Generate chart
        plotly_code = vn.generate_plotly_code(
            question=question,
            sql=sql,
            df_metadata=f"Running df.dtypes gives:\n{df.dtypes}"
        )
        
        fig = vn.get_plotly_figure(
            plotly_code=plotly_code,
            df=df,
            dark_mode=False
        )
        
        return {
            "success": True,
            "chart_json": fig.to_json(),
            "chart_html": fig.to_html(),
            "data": df.to_dict(orient='records')
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

## 🌐 Usage với n8n

```json
{
  "method": "POST",
  "url": "https://vanna-production.up.railway.app/generate_chart",
  "headers": {
    "Content-Type": "application/json",
    "X-API-Key": "your-api-key"
  },
  "body": {
    "question": "Top 10 sản phẩm bán chạy nhất"
  }
}
```

Response:
```json
{
  "success": true,
  "chart_json": "{\"data\": [...], \"layout\": {...}}",
  "data": [
    {"product": "A", "sales": 1000},
    {"product": "B", "sales": 900}
  ]
}
```

## ⚠️ Error Handling

```python
try:
    # Generate chart
    plotly_code = vn.generate_plotly_code(question, sql, df_metadata=...)
    fig = vn.get_plotly_figure(plotly_code, df)
    fig.write_html("chart.html")
    
except Exception as e:
    print(f"Chart error: {e}")
    # Fallback: Show table only
    print(df)
```

## 💡 Best Practices

### ✅ DO:
```python
# 1. Kiểm tra data trước khi vẽ
if len(df) > 0 and vn.should_generate_chart(df):
    # Create chart

# 2. Provide clear metadata
df_metadata = f"Running df.dtypes gives:\n{df.dtypes}"

# 3. Handle errors gracefully
try:
    fig = vn.get_plotly_figure(plotly_code, df)
except:
    return {"table": df.to_dict()}

# 4. Use custom instructions for better charts
question_with_instruction = f"{question}. Use blue colors and add data labels."
```

### ❌ DON'T:
```python
# 1. Không vẽ chart cho data quá ít
if len(df) < 2:
    return  # Too few points

# 2. Không vẽ chart cho data không có numeric columns
if not df.select_dtypes(include=['number']).columns.any():
    return  # No numeric data

# 3. Không ignore exceptions
# BAD: fig = vn.get_plotly_figure(...)  # Có thể crash
# GOOD: try/except như trên
```

## 🎨 Chart Customization Examples

```python
# Example 1: Dark theme
fig = vn.get_plotly_figure(plotly_code, df, dark_mode=True)

# Example 2: Custom colors
question = "Top 10 products. Use gradient from blue to red."

# Example 3: Add annotations
question = "Sales by month. Add trend line and highlight peak month."

# Example 4: Different chart types
"Show as pie chart"
"Create stacked bar chart"
"Use scatter plot with trend line"
```

## 📚 Complete Example

```python
from vanna.chromadb import ChromaDB_VectorStore
from vanna.openai import OpenAI_Chat

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

vn = MyVanna(config={'api_key': 'sk-...', 'model': 'gpt-4o-mini'})
vn.connect_to_postgres(host='...', dbname='...', user='...', password='...')

# Question
question = "Top 10 khách hàng có doanh thu cao nhất"

# Generate SQL
sql = vn.generate_sql(question)
print(f"SQL: {sql}")

# Execute
df = vn.run_sql(sql)
print(f"Data shape: {df.shape}")

# Create chart
if vn.should_generate_chart(df):
    plotly_code = vn.generate_plotly_code(
        question=question,
        sql=sql,
        df_metadata=f"Running df.dtypes gives:\n{df.dtypes}"
    )
    
    fig = vn.get_plotly_figure(
        plotly_code=plotly_code,
        df=df,
        dark_mode=False
    )
    
    # Save
    fig.write_html("top_customers.html")
    print("✅ Chart saved!")
else:
    print("⚠️  Data not suitable for chart, showing table:")
    print(df)
```

## 🔗 Resources

- **Plotly Docs**: https://plotly.com/python/
- **Vanna Docs**: https://vanna.ai/docs/
- **Demo Script**: `demo_chart_visualization.py`
- **Railway API**: `main.py` - Add chart endpoint

## 🆘 Troubleshooting

### Issue: Chart không hiển thị
```python
# Solution: Check fig object
print(type(fig))  # Should be plotly.graph_objs._figure.Figure
print(fig)        # Should show figure details
```

### Issue: "No numeric columns"
```python
# Solution: Check DataFrame
print(df.dtypes)
print(df.select_dtypes(include=['number']).columns)
```

### Issue: Plotly code generation failed
```python
# Solution: Provide better metadata
df_metadata = f"""
Running df.dtypes gives:
{df.dtypes}

Running df.head() gives:
{df.head()}

Number of rows: {len(df)}
"""
```

---

💡 **Tip**: Start with `demo_chart_visualization.py` để xem examples đầy đủ!
