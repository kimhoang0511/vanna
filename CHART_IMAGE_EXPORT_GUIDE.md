# 📊 Chart Image Export - Quick Guide

## 🎯 Tổng quan

API bây giờ support export chart sang nhiều formats:
- **JSON** - Plotly JSON (interactive charts)
- **HTML** - Full HTML page
- **PNG** - PNG image (static, high quality)
- **JPG/JPEG** - JPEG image (static, smaller file size)  
- **PDF** - PDF document (static, printable)

## 🚀 Cách sử dụng

### Method 1: POST /generate_chart (với base64 response)

```bash
curl -X POST "https://vanna-production.up.railway.app/generate_chart" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -d '{
    "question": "Top 10 khách hàng có doanh thu cao nhất",
    "export_format": "jpg",
    "image_width": 1920,
    "image_height": 1080,
    "custom_instructions": "Use blue gradient colors"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Chart generated successfully as JPG",
  "data": {
    "chart_image_base64": "iVBORw0KGgoAAAANSUhEUg...",
    "sql": "SELECT ...",
    "row_count": 10,
    "data": [...],
    "image_width": 1920,
    "image_height": 1080,
    "mime_type": "image/jpeg"
  }
}
```

### Method 2: GET /download_chart/{format} (direct file download)

```bash
# Download as PNG
curl "https://vanna-production.up.railway.app/download_chart/png?question=Top+10+customers&width=1600&height=900" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -o chart.png

# Download as JPG
curl "https://vanna-production.up.railway.app/download_chart/jpg?question=Sales+by+month&width=1920&height=1080" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -o chart.jpg

# Download as PDF
curl "https://vanna-production.up.railway.app/download_chart/pdf?question=Revenue+trend" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -o chart.pdf
```

## 📝 Request Parameters

### POST /generate_chart

```json
{
  "question": "Your question here",
  "sql": "Optional SQL query",
  "export_format": "png|jpg|jpeg|pdf|json|html",
  "image_width": 1200,
  "image_height": 800,
  "dark_mode": false,
  "custom_instructions": "Optional chart styling instructions"
}
```

### GET /download_chart/{format}

Query parameters:
- `question` (required): Question in Vietnamese or English
- `sql` (optional): Pre-generated SQL
- `width` (optional, default=1200): Image width in pixels
- `height` (optional, default=800): Image height in pixels
- `dark_mode` (optional, default=false): Use dark theme

## 💻 Frontend Integration

### Display base64 image in HTML

```html
<img src="data:image/png;base64,{base64_data}" alt="Chart" />
```

### JavaScript example

```javascript
// Fetch chart as base64
const response = await fetch('https://vanna-production.up.railway.app/generate_chart', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'YOUR_API_KEY_HERE'
  },
  body: JSON.stringify({
    question: 'Top 10 customers',
    export_format: 'png',
    image_width: 1600,
    image_height: 900
  })
});

const data = await response.json();

// Display image
const img = document.createElement('img');
img.src = `data:${data.data.mime_type};base64,${data.data.chart_image_base64}`;
document.body.appendChild(img);

// Or download
const link = document.createElement('a');
link.href = img.src;
link.download = 'chart.png';
link.click();
```

### React example

```jsx
function ChartComponent() {
  const [chartImage, setChartImage] = useState(null);
  
  const generateChart = async () => {
    const response = await fetch('/generate_chart', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
      },
      body: JSON.stringify({
        question: 'Top 10 customers',
        export_format: 'png'
      })
    });
    
    const data = await response.json();
    setChartImage(`data:image/png;base64,${data.data.chart_image_base64}`);
  };
  
  return (
    <div>
      <button onClick={generateChart}>Generate Chart</button>
      {chartImage && <img src={chartImage} alt="Chart" />}
    </div>
  );
}
```

## 🔧 n8n Integration

### Workflow Node: Generate Chart Image

```json
{
  "method": "POST",
  "url": "https://vanna-production.up.railway.app/generate_chart",
  "headers": {
    "Content-Type": "application/json",
    "X-API-Key": "YOUR_API_KEY_HERE"
  },
  "body": {
    "question": "{{$json.question}}",
    "export_format": "jpg",
    "image_width": 1920,
    "image_height": 1080
  }
}
```

### Save Image to File (n8n)

```javascript
// In Function node
const base64Data = $json.data.chart_image_base64;
const buffer = Buffer.from(base64Data, 'base64');

return {
  json: {
    filename: 'chart.jpg',
    data: buffer
  }
};
```

## 📊 Format Comparison

| Format | Size | Quality | Use Case |
|--------|------|---------|----------|
| **PNG** | Large | Best | High quality, transparency |
| **JPG** | Medium | Good | General use, smaller files |
| **PDF** | Medium | Vector | Printing, documents |
| **JSON** | Small | N/A | Interactive web charts |
| **HTML** | Medium | N/A | Full page embed |

## 🎨 Custom Styling

```json
{
  "question": "Sales trend over time",
  "export_format": "png",
  "custom_instructions": "Create line chart with blue gradient, add trend line, show data labels, use dark theme",
  "dark_mode": true,
  "image_width": 1920,
  "image_height": 1080
}
```

## ⚡ Performance Tips

1. **Use appropriate image size:**
   - Web display: 1200x800
   - HD: 1920x1080
   - 4K: 3840x2160

2. **Choose right format:**
   - PNG: High quality, transparency needed
   - JPG: Smaller size, no transparency
   - PDF: For printing

3. **Cache results:**
   - Save generated images
   - Reuse for same queries

## 🐛 Troubleshooting

### Error: "kaleido not installed"
```bash
# On Railway, this should auto-install from requirements.txt
# Locally:
pip install kaleido pillow
```

### Image too large
- Reduce width/height
- Use JPG instead of PNG
- Compress base64 string

### Base64 decode error
```javascript
// Make sure to include data URI prefix
const imgSrc = `data:image/png;base64,${base64String}`;
```

## 📦 Test Script

Run the test script to verify all formats:

```bash
python3 test_chart_image_export.py
```

This will:
- Test JSON format
- Test PNG format (save to test_chart.png)
- Test JPG format (save to test_chart.jpg)
- Test download endpoint (save to downloaded_chart.png)

## 🔗 Complete Example

```python
import requests
import base64

# Generate chart as PNG
response = requests.post(
    "https://vanna-production.up.railway.app/generate_chart",
    headers={
        "Content-Type": "application/json",
        "X-API-Key": "YOUR_API_KEY_HERE"
    },
    json={
        "question": "Top 10 sản phẩm bán chạy nhất",
        "export_format": "png",
        "image_width": 1600,
        "image_height": 900,
        "custom_instructions": "Use blue colors and show percentages"
    }
)

# Save to file
if response.status_code == 200:
    data = response.json()
    img_data = base64.b64decode(data['data']['chart_image_base64'])
    
    with open('chart.png', 'wb') as f:
        f.write(img_data)
    
    print(f"✅ Saved chart.png ({len(img_data)/1024:.1f} KB)")
```

---

**Ready to use!** 🚀

Railway đang rebuild với kaleido support. Sau khi rebuild xong (~2-3 phút), chạy:

```bash
python3 test_chart_image_export.py
```
