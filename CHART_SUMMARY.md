# 📊 Tổng hợp: Cách tạo biểu đồ với Vanna

## 🎯 Câu trả lời ngắn gọn

```python
# 3 dòng code để tạo chart:
sql = vn.generate_sql("Top 10 customers")
df = vn.run_sql(sql)
fig = vn.get_plotly_figure(
    plotly_code=vn.generate_plotly_code(question, sql, f"df.dtypes:\n{df.dtypes}"),
    df=df
)
fig.write_html("chart.html")  # hoặc fig.show()
```

## 📚 Files đã tạo

| File | Mô tả | Khi nào dùng |
|------|-------|--------------|
| **simple_chart_example.py** | ✨ BẮT ĐẦU ĐÂY | Copy & paste, có 6 cách khác nhau |
| **demo_chart_visualization.py** | Demo đầy đủ với examples | Học chi tiết, nhiều loại charts |
| **CHART_GUIDE.md** | Quick reference guide | Tra cứu nhanh syntax, parameters |
| **demo_real.py** | Updated với chart code | Xem integration trong demo thật |

## 🚀 Quick Start

### 1. Copy từ simple_chart_example.py

```python
# CÁCH ĐƠN GIẢN NHẤT:
question = "Top 10 customers by sales"
sql = vn.generate_sql(question)
df = vn.run_sql(sql)

# Tạo chart (1 dòng)
fig = vn.get_plotly_figure(
    plotly_code=vn.generate_plotly_code(question, sql, f"df.dtypes:\n{df.dtypes}"),
    df=df
)

fig.write_html("chart.html")
```

### 2. Với Error Handling (Production)

```python
try:
    sql = vn.generate_sql(question)
    df = vn.run_sql(sql)
    
    if vn.should_generate_chart(df):
        plotly_code = vn.generate_plotly_code(
            question=question,
            sql=sql,
            df_metadata=f"Running df.dtypes gives:\n{df.dtypes}"
        )
        fig = vn.get_plotly_figure(plotly_code, df)
        fig.write_html("chart.html")
    else:
        print("Data không phù hợp cho chart")
        
except Exception as e:
    print(f"Error: {e}")
```

## 🎨 Customization

### Dark Mode
```python
fig = vn.get_plotly_figure(plotly_code, df, dark_mode=True)
```

### Custom Appearance
```python
question_with_style = "Top 10 products. Use blue gradient colors and add data labels."
plotly_code = vn.generate_plotly_code(question_with_style, sql, df_metadata)
```

### Multiple Formats
```python
fig.write_html("chart.html")      # Interactive HTML
fig.to_json()                     # JSON for API
fig.show()                        # Open browser
# fig.write_image("chart.png")    # PNG (needs kaleido)
```

## 📖 Chi tiết 3 bước

### Bước 1: Generate Plotly Code
```python
plotly_code = vn.generate_plotly_code(
    question="Your question",           # Câu hỏi gốc
    sql="SELECT ...",                   # SQL query
    df_metadata="Running df.dtypes gives:\n..."  # DataFrame info
)
```

**Output:** Python code string (Plotly syntax)

### Bước 2: Create Figure
```python
fig = vn.get_plotly_figure(
    plotly_code=plotly_code,    # Code từ bước 1
    df=df,                      # Data
    dark_mode=False             # Theme
)
```

**Output:** Plotly Figure object

### Bước 3: Save/Display
```python
fig.write_html("chart.html")   # Save to file
fig.show()                     # Open in browser
fig.to_json()                  # Get JSON
```

## 🔧 Integration với Railway API

### Thêm endpoint vào main.py:

```python
@app.post("/generate_chart")
async def generate_chart(
    request: ChartRequest,
    api_key: str = Depends(verify_api_key)
):
    """Generate chart from question"""
    try:
        service = get_vanna_service()
        
        # Generate SQL if not provided
        sql = request.sql or service.vn.generate_sql(request.question)
        
        # Execute
        df = service.vn.run_sql(sql)
        
        # Check suitability
        if not service.vn.should_generate_chart(df):
            return {
                "success": False,
                "message": "Data not suitable for chart",
                "data": df.to_dict(orient='records')
            }
        
        # Generate chart
        plotly_code = service.vn.generate_plotly_code(
            question=request.question,
            sql=sql,
            df_metadata=f"Running df.dtypes gives:\n{df.dtypes}"
        )
        
        fig = service.vn.get_plotly_figure(
            plotly_code=plotly_code,
            df=df,
            dark_mode=request.dark_mode or False
        )
        
        return {
            "success": True,
            "data": {
                "chart_json": fig.to_json(),
                "sql": sql,
                "row_count": len(df)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Request Model:
```python
class ChartRequest(BaseModel):
    question: str
    sql: Optional[str] = None
    dark_mode: Optional[bool] = False
```

## 🌐 Test với Railway

```bash
curl -X POST "https://vanna-production.up.railway.app/generate_chart" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: L8WBBkJndxkbEJkMpCdOPmGc29HfWSTz" \
  -d '{
    "question": "Top 10 khách hàng có doanh thu cao nhất",
    "dark_mode": false
  }'
```

## 💡 Tips & Best Practices

### ✅ DO:
```python
# 1. Kiểm tra trước khi vẽ
if vn.should_generate_chart(df) and len(df) >= 2:
    # Create chart

# 2. Dùng try/except
try:
    fig = vn.get_plotly_figure(...)
except Exception as e:
    # Handle error

# 3. Provide metadata đầy đủ
df_metadata = f"Running df.dtypes gives:\n{df.dtypes}"

# 4. Custom instructions cho chart đẹp
question = "Top 10 products. Use gradient blue colors and show percentages."
```

### ❌ DON'T:
```python
# 1. Không check data
fig = vn.get_plotly_figure(...)  # Có thể fail nếu data không phù hợp

# 2. Không provide metadata
plotly_code = vn.generate_plotly_code(question, sql)  # Missing df_metadata

# 3. Ignore exceptions
# BAD: No error handling
# GOOD: Wrap in try/except
```

## 🎓 Learning Path

1. **Start**: Đọc `simple_chart_example.py` (6 cách khác nhau)
2. **Practice**: Chạy `demo_chart_visualization.py` 
3. **Reference**: Dùng `CHART_GUIDE.md` để tra cứu
4. **Integration**: Add endpoint vào `main.py`
5. **Production**: Deploy to Railway, test với n8n

## 📊 Các loại Chart phổ biến

```python
# Bar Chart - So sánh
"Top 10 products by revenue"

# Line Chart - Trends
"Sales trend over last 12 months"

# Pie Chart - Proportions
"Market share by region"

# Scatter - Correlation
"Price vs quantity relationship"

# Histogram - Distribution
"Distribution of order amounts"
```

## 🆘 Troubleshooting

### Chart không hiển thị?
```python
print(type(fig))  # Check if it's a Figure object
print(fig)        # Show figure details
```

### "No numeric columns"?
```python
print(df.dtypes)
print(df.select_dtypes(include=['number']).columns)
```

### Code generation failed?
```python
# Provide more metadata
df_metadata = f"""
Running df.dtypes gives:
{df.dtypes}

Running df.head() gives:
{df.head()}

Shape: {df.shape}
"""
```

## 🎯 Next Steps

- [ ] Đọc `simple_chart_example.py`
- [ ] Test local với demo files
- [ ] Add `/generate_chart` endpoint to main.py
- [ ] Deploy to Railway
- [ ] Test với n8n
- [ ] Create n8n workflow với chart visualization

---

## 📁 File Structure

```
vanna/
├── simple_chart_example.py          ← 🌟 START HERE
├── demo_chart_visualization.py      ← Full examples
├── CHART_GUIDE.md                   ← Quick reference
├── demo_real.py                     ← Updated with charts
└── main.py                          ← Add chart endpoint here
```

## 🔗 Related Resources

- [Plotly Documentation](https://plotly.com/python/)
- [Vanna Documentation](https://vanna.ai/docs/)
- Railway API: https://vanna-production.up.railway.app/docs
- N8N Integration Guide: `N8N_INTEGRATION.md` (coming soon)

---

**Ready for n8n integration? Let me know!** 🚀
