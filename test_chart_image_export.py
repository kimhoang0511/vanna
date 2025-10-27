"""
Test Chart Image Export
Demo các format: JSON, HTML, PNG, JPG, PDF
"""
import requests
import json
import base64

BASE_URL = "https://vanna-production.up.railway.app"
API_KEY = "L8WBBkJndxkbEJkMpCdOPmGc29HfWSTz"

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

print("=" * 70)
print("📊 TEST CHART IMAGE EXPORT")
print("=" * 70)

# Test 1: JSON format (default)
print("\n1️⃣ TEST JSON FORMAT")
print("-" * 70)
response = requests.post(
    f"{BASE_URL}/generate_chart",
    headers=headers,
    json={
        "question": "Top 5 customers by sales",
        "export_format": "json"
    },
    timeout=60
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"✅ Success: {data['message']}")
    print(f"   Has chart_json: {'chart_json' in data['data']}")
    print(f"   Row count: {data['data']['row_count']}")
else:
    print(f"❌ Error: {response.text}")

# Test 2: PNG format
print("\n2️⃣ TEST PNG FORMAT")
print("-" * 70)
response = requests.post(
    f"{BASE_URL}/generate_chart",
    headers=headers,
    json={
        "question": "Top 10 customers by sales",
        "export_format": "png",
        "image_width": 1600,
        "image_height": 900
    },
    timeout=120
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"✅ Success: {data['message']}")
    if 'chart_image_base64' in data['data']:
        # Save PNG file
        img_data = base64.b64decode(data['data']['chart_image_base64'])
        with open('test_chart.png', 'wb') as f:
            f.write(img_data)
        print(f"   ✅ Saved to: test_chart.png")
        print(f"   Size: {len(img_data) / 1024:.1f} KB")
        print(f"   Dimensions: {data['data']['image_width']}x{data['data']['image_height']}")
    else:
        print(f"   ⚠️  No image data (maybe kaleido not installed on server)")
else:
    print(f"❌ Error: {response.text}")

# Test 3: JPG format
print("\n3️⃣ TEST JPG FORMAT")
print("-" * 70)
response = requests.post(
    f"{BASE_URL}/generate_chart",
    headers=headers,
    json={
        "question": "Sales by country",
        "export_format": "jpg",
        "image_width": 1920,
        "image_height": 1080,
        "custom_instructions": "Use horizontal bar chart with blue colors"
    },
    timeout=120
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"✅ Success: {data['message']}")
    if 'chart_image_base64' in data['data']:
        img_data = base64.b64decode(data['data']['chart_image_base64'])
        with open('test_chart.jpg', 'wb') as f:
            f.write(img_data)
        print(f"   ✅ Saved to: test_chart.jpg")
        print(f"   Size: {len(img_data) / 1024:.1f} KB")
    else:
        print(f"   ⚠️  No image data")
else:
    print(f"❌ Error: {response.text}")

# Test 4: Download endpoint (direct file download)
print("\n4️⃣ TEST DOWNLOAD ENDPOINT")
print("-" * 70)
download_url = f"{BASE_URL}/download_chart/png"
params = {
    "question": "Top 10 products by revenue",
    "width": 1400,
    "height": 800
}
response = requests.get(
    download_url,
    params=params,
    headers={"X-API-Key": API_KEY},
    timeout=120
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    with open('downloaded_chart.png', 'wb') as f:
        f.write(response.content)
    print(f"✅ Downloaded to: downloaded_chart.png")
    print(f"   Size: {len(response.content) / 1024:.1f} KB")
    print(f"   Content-Type: {response.headers.get('Content-Type')}")
else:
    print(f"❌ Error: {response.text}")

print("\n" + "=" * 70)
print("📊 SUMMARY")
print("=" * 70)
print("""
✅ Các formats được support:
   • json - Plotly JSON (interactive)
   • html - Full HTML page
   • png - PNG image (static)
   • jpg - JPEG image (static)
   • pdf - PDF document

📁 Files created:
   • test_chart.png
   • test_chart.jpg
   • downloaded_chart.png

🔧 Usage examples:

1. POST /generate_chart (with base64 response):
   {
     "question": "Top 10 customers",
     "export_format": "jpg",
     "image_width": 1920,
     "image_height": 1080
   }

2. GET /download_chart/png (direct download):
   ?question=Top 10 customers&width=1920&height=1080

💡 Decode base64 in frontend:
   <img src="data:image/png;base64,{base64_data}" />
""")
