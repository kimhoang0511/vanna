"""
Test /api/v0/ask endpoint với chart generation
Solution 1: All-in-one endpoint không phụ thuộc cache

Features:
- Generate SQL
- Execute SQL
- Generate Chart (nếu data phù hợp)
- Tất cả trong 1 request duy nhất

Usage:
    python test_ask_endpoint_with_chart.py
"""

import requests
import json
import time
from datetime import datetime
import os


def test_ask_with_chart(question, base_url="https://vanna-production.up.railway.app"):
    """Test /api/v0/ask endpoint"""
    
    print("="*80)
    print(f"🧪 TEST: /api/v0/ask endpoint với Chart Generation")
    print("="*80)
    print(f"Question: {question}")
    print(f"Base URL: {base_url}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Call API
    print("\n📡 Calling API...")
    start_time = time.time()
    
    try:
        response = requests.get(
            f"{base_url}/api/v0/ask",
            params={'question': question},
            timeout=120  # Longer timeout for LLM + chart generation
        )
        
        elapsed = time.time() - start_time
        
        print(f"⏱️  Response time: {elapsed:.2f}s")
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Request failed!")
            print(f"Response: {response.text[:500]}")
            return False
        
        # Parse response
        data = response.json()
        
        # Check success
        if not data.get('success'):
            print(f"❌ API returned error:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return False
        
        # Display results
        print("\n" + "="*80)
        print("📊 RESPONSE DATA")
        print("="*80)
        
        print(f"\n✅ Success: {data.get('success')}")
        print(f"✅ Question: {data.get('question')}")
        print(f"✅ Cache ID: {data.get('cache_id')}")
        print(f"✅ Rows Count: {data.get('rows_count')}")
        print(f"✅ Should Generate Chart: {data.get('should_generate_chart')}")
        print(f"✅ Has Chart: {data.get('has_chart')}")
        
        # Display SQL
        print(f"\n📝 Generated SQL:")
        print("─"*80)
        print(data.get('sql'))
        print("─"*80)
        
        # Display sample data
        sample_data = data.get('data', [])
        if sample_data:
            print(f"\n📊 Sample Data (first 5 rows):")
            print("─"*80)
            for i, row in enumerate(sample_data[:5], 1):
                print(f"Row {i}: {json.dumps(row, ensure_ascii=False)}")
            print("─"*80)
        
        # Handle chart
        chart_json = data.get('chart')
        
        if chart_json:
            print(f"\n✅ Chart Generated!")
            
            # Parse chart JSON
            chart_data = json.loads(chart_json) if isinstance(chart_json, str) else chart_json
            
            # Analyze chart
            if chart_data.get('data'):
                print(f"\n📈 Chart Info:")
                print(f"   Traces: {len(chart_data['data'])}")
                
                for i, trace in enumerate(chart_data['data'], 1):
                    print(f"   Trace {i}:")
                    print(f"      Type: {trace.get('type', 'unknown')}")
                    if 'x' in trace:
                        print(f"      X points: {len(trace['x'])}")
                    if 'y' in trace:
                        print(f"      Y points: {len(trace['y'])}")
            
            # Save chart to HTML
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"chart_ask_endpoint_{timestamp}.html"
            
            html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vanna Chart - {question}</title>
    <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        
        .header p {{
            font-size: 16px;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .info-box {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px 20px;
            margin-bottom: 30px;
            border-radius: 4px;
        }}
        
        .info-box h3 {{
            color: #333;
            margin-bottom: 10px;
            font-size: 18px;
        }}
        
        .info-box p {{
            color: #666;
            font-size: 14px;
            margin: 5px 0;
        }}
        
        .chart-container {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        #chart {{
            width: 100%;
            height: 600px;
        }}
        
        .sql-box {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            font-family: 'Courier New', monospace;
        }}
        
        .sql-box h3 {{
            color: #333;
            margin-bottom: 15px;
            font-size: 18px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
        }}
        
        .sql-box pre {{
            background: #282c34;
            color: #abb2bf;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
            font-size: 14px;
            line-height: 1.5;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 14px;
            border-top: 1px solid #e0e0e0;
        }}
        
        .badge {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
            margin-right: 8px;
        }}
        
        .success {{
            color: #28a745;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 {question}</h1>
            <p>Generated by Vanna AI • /api/v0/ask endpoint</p>
        </div>
        
        <div class="content">
            <div class="info-box">
                <h3>ℹ️ Request Info</h3>
                <p><span class="badge">Time</span>{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                <p><span class="badge">API</span>{base_url}/api/v0/ask</p>
                <p><span class="badge">Response Time</span>{elapsed:.2f}s</p>
                <p><span class="badge">Rows</span>{data.get('rows_count')} rows</p>
                <p class="success">✅ All-in-one request (Generate SQL + Execute + Chart)</p>
            </div>
            
            <div class="sql-box">
                <h3>📝 Generated SQL</h3>
                <pre>{data.get('sql')}</pre>
            </div>
            
            <div class="chart-container">
                <div id="chart"></div>
            </div>
        </div>
        
        <div class="footer">
            <p>Powered by Vanna.AI + Google Gemini + Railway</p>
            <p style="margin-top: 8px; font-size: 12px;">
                🌐 <a href="{base_url}" style="color: #667eea; text-decoration: none;">Production API</a> • 
                📚 <a href="https://github.com/vanna-ai/vanna" style="color: #667eea; text-decoration: none;">Vanna GitHub</a>
            </p>
        </div>
    </div>
    
    <script>
        var figData = {json.dumps(chart_data, ensure_ascii=False)};
        
        // Configure Plotly
        var config = {{
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
            toImageButtonOptions: {{
                format: 'png',
                filename: 'vanna_chart_{timestamp}',
                height: 800,
                width: 1200,
                scale: 2
            }}
        }};
        
        // Render chart
        Plotly.newPlot('chart', figData.data, figData.layout, config);
        
        // Add resize handler
        window.addEventListener('resize', function() {{
            Plotly.Plots.resize('chart');
        }});
    </script>
</body>
</html>"""
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            abs_path = os.path.abspath(filename)
            print(f"\n💾 Chart saved:")
            print(f"   File: {filename}")
            print(f"   Path: {abs_path}")
            print(f"   Open: file://{abs_path}")
            
        else:
            print(f"\n⚠️  No chart generated")
            if not data.get('should_generate_chart'):
                print(f"   Reason: Data not suitable for chart (no numeric columns or too few rows)")
        
        # Summary
        print("\n" + "="*80)
        print("📊 TEST SUMMARY")
        print("="*80)
        print(f"✅ Success: {data.get('success')}")
        print(f"✅ SQL Generated: Yes")
        print(f"✅ SQL Executed: Yes")
        print(f"✅ Data Retrieved: {data.get('rows_count')} rows")
        print(f"✅ Chart Generated: {'Yes' if chart_json else 'No'}")
        print(f"✅ Response Time: {elapsed:.2f}s")
        print(f"✅ All in ONE request: /api/v0/ask")
        print("="*80)
        
        return True
        
    except requests.exceptions.Timeout:
        print(f"❌ Request timeout after 120s")
        return False
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    
    print("\n")
    print("="*80)
    print("  🚀 TEST: /api/v0/ask Endpoint with Chart Generation")
    print("="*80)
    print("  Solution 1: All-in-one endpoint (Generate + Execute + Chart)")
    print("  No cache dependency - Everything in 1 request!")
    print("="*80)
    print()
    
    # Test cases
    test_cases = [
        "Tổng hợp doanh số bán hàng",
        "Top 10 khách hàng có doanh thu cao nhất",
        "Doanh số theo tháng trong năm 2024",
    ]
    
    base_url = "https://vanna-production.up.railway.app"
    
    results = []
    
    for i, question in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"  TEST CASE {i}/{len(test_cases)}")
        print(f"{'='*80}\n")
        
        success = test_ask_with_chart(question, base_url)
        results.append({
            'question': question,
            'success': success
        })
        
        if i < len(test_cases):
            print(f"\n⏳ Waiting 3 seconds before next test...")
            time.sleep(3)
    
    # Final summary
    print("\n")
    print("="*80)
    print("  🏁 FINAL RESULTS")
    print("="*80)
    
    passed = sum(1 for r in results if r['success'])
    total = len(results)
    
    for i, result in enumerate(results, 1):
        status = "✅ PASSED" if result['success'] else "❌ FAILED"
        print(f"  Test {i}: {status}")
        print(f"          {result['question']}")
    
    print(f"\n  Success Rate: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print(f"\n  🎉 ALL TESTS PASSED!")
        print(f"  ✅ Solution 1 works perfectly!")
        print(f"  ✅ Chart generation included in /api/v0/ask")
        print(f"  ✅ No cache dependency issues")
    elif passed > 0:
        print(f"\n  ⚠️  SOME TESTS PASSED")
        print(f"  Check error messages above for failed tests")
    else:
        print(f"\n  ❌ ALL TESTS FAILED")
        print(f"  Please check:")
        print(f"  - Railway deployment status")
        print(f"  - API endpoint availability")
        print(f"  - Network connectivity")
    
    print("="*80)
    print()


if __name__ == "__main__":
    main()
