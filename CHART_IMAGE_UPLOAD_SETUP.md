# 📸 Chart Image Upload - Setup Guide

## 🎯 Overview

The `/api/v0/ask` endpoint now supports automatic chart conversion to PNG format and cloud hosting with shareable URLs.

**Features:**
- ✅ Converts Plotly charts to high-quality PNG (1200x800, 2x scale)
- ✅ Uploads images to ImgBB cloud hosting (permanent URLs)
- ✅ Creates beautiful HTML page with embedded chart image
- ✅ Uploads HTML to tmpfiles.org (temporary hosting)
- ✅ Returns both image URL and HTML page URL in API response
- ✅ Graceful fallback if dependencies/API keys are missing

## 🔧 Requirements

### 1. Python Dependencies

Already in `requirements.txt`:
```
plotly==5.18.0
kaleido==0.2.1  # Required for PNG export
pillow==10.1.0
```

### 2. ImgBB API Key (FREE)

**Get your API key:**
1. Go to: https://api.imgbb.com/
2. Login or create account (free)
3. Copy your API key

**Set environment variable:**

**Local development:**
```bash
export IMGBB_API_KEY="your_api_key_here"
```

**Railway deployment:**
1. Go to your Railway project
2. Navigate to "Variables" tab
3. Add new variable:
   - Name: `IMGBB_API_KEY`
   - Value: `your_api_key_here`
4. Save and redeploy

## 📊 API Response Format

### With Image Upload Enabled

```json
{
  "success": true,
  "question": "Tổng hợp doanh số bán hàng",
  "sql": "SELECT ...",
  "data": [...],
  "rows_count": 24,
  "cache_id": "8e61ae65edd1f99f844f6691c2465350",
  "should_generate_chart": true,
  "has_chart": true,
  "chart": {...},  // Plotly JSON format
  
  // NEW FIELDS:
  "chart_image_url": "https://i.ibb.co/xyz123/vanna_chart.png",
  "chart_image_format": "png",
  "chart_image_size": "1200x800",
  "chart_html_url": "https://tmpfiles.org/dl/123456",
  "chart_html_note": "Temporary URL (expires after period of inactivity)"
}
```

### Without Image Upload (Missing API Key)

```json
{
  "success": true,
  "question": "...",
  "sql": "...",
  "data": [...],
  "has_chart": true,
  "chart": {...}  // Only Plotly JSON, no image/HTML URLs
}
```

## 🧪 Testing

### Test 1: Without API Key

```bash
# Should work but skip image upload
python test_ask_endpoint_with_chart.py
```

Expected console output:
```
✅ Chart generated successfully
⚠️  IMGBB_API_KEY not set, skipping image upload
   Get free API key at: https://api.imgbb.com/
```

### Test 2: With API Key

```bash
# Set API key
export IMGBB_API_KEY="your_key_here"

# Run test
python test_ask_endpoint_with_chart.py
```

Expected console output:
```
✅ Chart generated successfully
📸 Converting chart to PNG...
☁️  Uploading to ImgBB...
✅ Chart image uploaded: https://i.ibb.co/xyz123/vanna_chart.png
✅ Chart HTML uploaded: https://tmpfiles.org/dl/123456
```

### Test 3: cURL Test

```bash
curl -X POST "https://vanna-production.up.railway.app/api/v0/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Top 10 khách hàng có doanh thu cao nhất"}'
```

## 🎨 HTML Page Features

The generated HTML page includes:

- **Beautiful gradient design** with purple theme
- **Responsive layout** - works on mobile and desktop
- **Clickable image** - opens full resolution in new tab
- **Query information** - shows row count, format, hosting details
- **Direct image URL** - easy copy/paste for sharing
- **Right-click download** - save image directly

## 🔍 Troubleshooting

### Issue: "kaleido not installed"

**Solution:**
```bash
pip install kaleido==0.2.1
```

### Issue: "IMGBB_API_KEY not set"

**Solution:** Get API key from https://api.imgbb.com/ and set environment variable

### Issue: "ImgBB upload failed: HTTP 400"

**Possible causes:**
- Invalid API key
- Image too large (max 32MB)
- Rate limit exceeded (free tier: 5000 uploads/month)

**Solution:** Check API key, verify image size

### Issue: "tmpfiles.org upload failed"

**Note:** tmpfiles.org is for temporary hosting only. Files expire after period of inactivity.

**Alternative:** Save HTML locally or use other hosting:
```python
# The HTML content is available in the code
# You can modify to use your preferred hosting service
```

## 🚀 Deployment Checklist

- [x] `kaleido` in requirements.txt
- [ ] Get ImgBB API key
- [ ] Add `IMGBB_API_KEY` to Railway environment variables
- [ ] Commit and push code
- [ ] Test API endpoint
- [ ] Verify image upload works
- [ ] Check HTML page renders correctly

## 📝 Technical Details

### Image Specifications

- **Format:** PNG
- **Width:** 1200px
- **Height:** 800px
- **Scale:** 2x (high DPI)
- **Quality:** Lossless PNG compression

### Hosting Services

**ImgBB:**
- Free tier: 5000 uploads/month
- Max file size: 32MB
- Permanent URLs
- No account required for viewing
- API docs: https://api.imgbb.com/

**tmpfiles.org:**
- Free temporary file hosting
- No registration required
- Files expire after inactivity
- Direct download URLs
- Alternative: Use your own hosting

## 🔄 Upgrade Path

### Phase 1 (Current)
- ✅ PNG conversion
- ✅ ImgBB upload
- ✅ HTML page generation
- ✅ tmpfiles.org hosting

### Phase 2 (Future)
- [ ] Support multiple image formats (JPG, SVG, PDF)
- [ ] Custom image dimensions via API parameters
- [ ] Permanent HTML hosting option
- [ ] Image optimization/compression
- [ ] Watermark/branding options
- [ ] Custom HTML templates

## 💡 Usage Examples

### Example 1: Display Image in Your App

```javascript
// Fetch data
const response = await fetch('https://vanna-production.up.railway.app/api/v0/ask', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ question: 'Top 10 khách hàng' })
});

const data = await response.json();

// Display image
if (data.chart_image_url) {
  document.getElementById('chart').innerHTML = 
    `<img src="${data.chart_image_url}" alt="Chart">`;
}
```

### Example 2: Share via Email/Slack

```
Quick chart for you:
📊 Question: Top 10 khách hàng
🖼️  Image: https://i.ibb.co/xyz123/vanna_chart.png
📄 Interactive: https://tmpfiles.org/dl/123456
```

### Example 3: Embed in HTML

```html
<!-- Direct image -->
<img src="https://i.ibb.co/xyz123/vanna_chart.png" 
     alt="Sales Chart" 
     style="max-width: 100%; height: auto;">

<!-- Or embed full HTML page -->
<iframe src="https://tmpfiles.org/dl/123456" 
        style="width: 100%; height: 600px; border: none;">
</iframe>
```

## 🎓 Best Practices

1. **Always check `has_chart` before accessing image URLs**
2. **Handle missing image URLs gracefully** (fallback to Plotly JSON)
3. **Cache image URLs** to avoid re-generating charts
4. **Use ImgBB URLs for permanent sharing** (HTML URLs expire)
5. **Test without API key first** to verify basic functionality

## 📞 Support

If you encounter issues:
1. Check Railway logs for error messages
2. Verify API key is set correctly
3. Test locally with the same data
4. Check ImgBB API limits
5. Review console output for warnings

---

**Last Updated:** 2025-11-12  
**Version:** 1.0  
**Status:** ✅ Production Ready
