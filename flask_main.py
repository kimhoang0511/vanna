"""
Flask-based API Server cho VietnameseVanna
Sử dụng VannaFlaskApp tích hợp sẵn với đầy đủ tính năng + Web UI

Usage:
    python flask_main.py

Features:
    - Web UI tại http://localhost:8000
    - REST API endpoints tại /api/v0/*
    - Swagger docs tại /api/v0/
    - WebSocket debug mode
    - Tự động cache kết quả
    - Hỗ trợ tiếng Việt

API Endpoints (tự động có sẵn):
    GET  /api/v0/generate_questions - Tạo câu hỏi gợi ý
    GET  /api/v0/generate_sql - Generate SQL từ question
    GET  /api/v0/run_sql - Thực thi SQL
    GET/POST /api/v0/ask - 🆕 All-in-one: Generate + Run SQL
    POST /api/v0/fix_sql - Tự động sửa lỗi SQL
    POST /api/v0/update_sql - Cập nhật SQL
    GET  /api/v0/generate_plotly_figure - Tạo biểu đồ
    GET  /api/v0/download_csv - Download CSV
    GET  /api/v0/get_training_data - Lấy training data
    POST /api/v0/train - Thêm training data
    POST /api/v0/remove_training_data - Xóa training data
    POST /api/v0/clear_training_data - 🆕 Xóa TẤT CẢ training data
    GET  /api/v0/generate_followup_questions - Câu hỏi follow-up
    GET  /api/v0/generate_summary - Tóm tắt kết quả
    GET  /api/v0/load_question - Load lại câu hỏi từ cache
    GET  /api/v0/get_question_history - Lịch sử câu hỏi
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from vietnamese_vanna import VietnameseVanna
from bge_m3_embedding import BGE_M3_EmbeddingFunction
from vanna.chromadb import ChromaDB_VectorStore
from vanna.flask import VannaFlaskApp
from vanna_cache_fix import QuestionHashCache, PersistentQuestionCache
from postgres_cache import PostgresCache

# ============================================================================
# Define Custom Vanna Classes
# ============================================================================

# Determine which LLM to use based on environment variable
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()  # Default: gemini

if LLM_PROVIDER == "openai":
    print("🤖 Using OpenAI as LLM provider")
    from vanna.openai import OpenAI_Chat
    
    class MyVanna(VietnameseVanna, ChromaDB_VectorStore, OpenAI_Chat):
        """Custom Vanna class with Vietnamese support + ChromaDB + OpenAI"""
        
        def __init__(self, config=None):
            ChromaDB_VectorStore.__init__(self, config=config)
            OpenAI_Chat.__init__(self, config=config)

elif LLM_PROVIDER == "gemini":
    print("🤖 Using Google Gemini as LLM provider")
    from vietnamese_vanna_gemini import VietnameseVannaGemini
    
    class MyVanna(VietnameseVannaGemini):
        """Custom Vanna class with Vietnamese support + ChromaDB + Gemini"""
        pass

else:
    raise ValueError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}. Use 'openai' or 'gemini'")


# ============================================================================
# Initialize Vanna Instance
# ============================================================================

def initialize_vanna():
    """Initialize Vanna with BGE-M3 embedding and Vietnamese support"""
    
    # Get LLM provider
    llm_provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    
    # Get Hugging Face API key for embeddings (optional)
    huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")
    
    # Initialize embedding function
    if huggingface_api_key:
        print("🔧 Initializing BGE-M3 Embedding Function...")
        bge_m3_ef = BGE_M3_EmbeddingFunction(api_key=huggingface_api_key)
    else:
        print("⚠️  HUGGINGFACE_API_KEY not found. Using default ChromaDB embeddings.")
        bge_m3_ef = None
    
    print(f"🔧 Initializing Vanna with {llm_provider.upper()} provider...")
    
    # Configure based on LLM provider
    if llm_provider == "openai":
        # OpenAI Configuration
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables. "
                "Please set it in .env file or export it."
            )
        
        config = {
            'model': os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            'api_key': openai_api_key,
            'embedding_function': bge_m3_ef,
            'temperature': float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
            'n_results_sql': int(os.getenv("VANNA_N_RESULTS_SQL", "5")),
            'n_results_ddl': int(os.getenv("VANNA_N_RESULTS_DDL", "3")),
            'n_results_documentation': int(os.getenv("VANNA_N_RESULTS_DOCUMENTATION", "7")),
            'language': 'Vietnamese'
        }
        
    elif llm_provider == "gemini":
        # Gemini Configuration
        google_api_key = os.getenv("GOOGLE_API_KEY")
        
        if not google_api_key:
            raise ValueError(
                "GOOGLE_API_KEY not found in environment variables. "
                "Please set it in .env file or export it. "
                "Get FREE API key at: https://makersuite.google.com/app/apikey"
            )
        
        config = {
            'api_key': google_api_key,
            'model_name': os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp"),
            'embedding_function': bge_m3_ef,
            'temperature': float(os.getenv("GEMINI_TEMPERATURE", "0.7")),
            'n_results_sql': int(os.getenv("VANNA_N_RESULTS_SQL", "5")),
            'n_results_ddl': int(os.getenv("VANNA_N_RESULTS_DDL", "3")),
            'n_results_documentation': int(os.getenv("VANNA_N_RESULTS_DOCUMENTATION", "7")),
            'language': 'Vietnamese'
        }
    
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {llm_provider}")
    
    vn = MyVanna(config=config)
    
    print(f"✅ Vanna initialized successfully with {llm_provider.upper()}!")
    return vn


def connect_to_database(vn):
    """Connect to PostgreSQL database and return connection params"""
    
    # Railway recommends using DATABASE_URL for service-to-service connection
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        # Parse DATABASE_URL (format: postgresql://user:password@host:port/dbname)
        print(f"🔗 Using DATABASE_URL for connection...")
        try:
            from urllib.parse import urlparse
            parsed = urlparse(database_url)
            
            db_params = {
                'host': parsed.hostname,
                'port': parsed.port or 5432,
                'dbname': parsed.path[1:] if parsed.path else 'railway',  # Remove leading /
                'user': parsed.username,
                'password': parsed.password
            }
            
            print(f"🔗 Connecting to PostgreSQL: {db_params['host']}:{db_params['port']}/{db_params['dbname']}...")
            
            vn.connect_to_postgres(**db_params)
            print("✅ Database connected successfully!")
            return db_params
            
        except Exception as e:
            print(f"⚠️  Warning: Could not parse/connect DATABASE_URL: {str(e)}")
            print("   Falling back to individual environment variables...")
    
    # Fallback: Use individual environment variables
    db_host = (
        os.getenv("PGHOST") or
        os.getenv("DB_HOST") or
        "localhost"
    )
    db_port = int(os.getenv("DB_PORT") or os.getenv("PGPORT") or "5432")
    db_name = os.getenv("PGDATABASE") or os.getenv("POSTGRES_DB") or os.getenv("DB_NAME") or "railway"
    db_user = os.getenv("PGUSER") or os.getenv("POSTGRES_USER") or os.getenv("DB_USER") or "postgres"
    db_password = os.getenv("PGPASSWORD") or os.getenv("POSTGRES_PASSWORD") or os.getenv("DB_PASSWORD") or ""
    
    db_params = {
        'host': db_host,
        'port': db_port,
        'dbname': db_name,
        'user': db_user,
        'password': db_password
    }
    
    print(f"🔗 Connecting to PostgreSQL: {db_host}:{db_port}/{db_name}...")
    
    try:
        vn.connect_to_postgres(**db_params)
        print("✅ Database connected successfully!")
        return db_params
    except Exception as e:
        print(f"⚠️  Warning: Could not connect to database: {str(e)}")
        print("   You can connect later using the UI or API")
        return db_params  # Still return params for cache usage


# ============================================================================
# Main Application
# ============================================================================

def main():
    """Main entry point"""
    
    print("=" * 70)
    print("🚀 Vietnamese Vanna Flask App")
    print("=" * 70)
    print()
    
    # Initialize Vanna
    vn = initialize_vanna()
    
    # Try to connect to database and get connection params
    db_params = connect_to_database(vn)
    
    print()
    print("🌐 Starting Flask server...")
    print()
    
    # Get configuration from environment
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    allow_llm_to_see_data = os.getenv("ALLOW_LLM_TO_SEE_DATA", "True").lower() == "true"
    
    # Initialize custom cache with question hashing
    print("🔧 Initializing cache...")
    
    # Choose cache backend based on environment variable
    cache_backend = os.getenv("CACHE_BACKEND", "file").lower()
    
    if cache_backend == "postgres":
        print("📊 Using PostgreSQL cache (persistent, shared across instances)")
        try:
            custom_cache = PostgresCache(connection_params=db_params)
            print(f"✅ PostgreSQL cache initialized: {db_params['host']}:{db_params['port']}/{db_params['dbname']}")
        except Exception as e:
            print(f"⚠️  Failed to initialize PostgreSQL cache: {e}")
            print("   Falling back to file cache...")
            custom_cache = PersistentQuestionCache(cache_file="vanna_cache.json")
    else:
        print("📁 Using file-based cache (persistent on single instance)")
        custom_cache = PersistentQuestionCache(cache_file="vanna_cache.json")
    
    # Create Flask app with full UI and API
    app = VannaFlaskApp(
        vn=vn,
        cache=custom_cache,  # Use custom cache
        
        # Authentication (default: no auth)
        # auth=NoAuth(),  # You can implement custom auth here
        
        # Debug & Data visibility
        debug=debug,
        allow_llm_to_see_data=allow_llm_to_see_data,
        
        # UI Configuration
        logo=os.getenv("VANNA_LOGO", "https://img.vanna.ai/vanna-flask.svg"),
        title=os.getenv("VANNA_TITLE", "Vietnamese Vanna - SQL Assistant"),
        subtitle=os.getenv("VANNA_SUBTITLE", "AI-powered SQL generation với hỗ trợ tiếng Việt 🇻🇳"),
        
        # Feature toggles
        show_training_data=True,      # Hiển thị training data trong UI
        suggested_questions=True,      # Gợi ý câu hỏi
        sql=True,                      # Hiển thị SQL generated
        table=True,                    # Hiển thị bảng kết quả
        csv_download=True,             # Cho phép download CSV
        chart=True,                    # Hiển thị biểu đồ
        redraw_chart=True,             # Cho phép vẽ lại biểu đồ
        auto_fix_sql=True,             # Tự động sửa lỗi SQL
        ask_results_correct=True,      # Hỏi kết quả có đúng không
        followup_questions=True,       # Câu hỏi follow-up
        summarization=True,            # Tóm tắt kết quả
        function_generation=False,     # Function generation (nâng cao)
        
        # Custom assets (optional)
        # index_html_path=None,        # Custom index.html
        # assets_folder=None,          # Custom assets folder
    )
    
    # Monkey-patch the generate_sql method in VannaBase to add caching
    original_generate_sql = vn.generate_sql
    
    def cached_generate_sql(question, **kwargs):
        """Wrapper around generate_sql with caching"""
        # Generate cache ID from question hash
        cache_id = custom_cache.generate_id(question=question)
        
        # Check cache first
        cached_sql = custom_cache.get(cache_id, "sql")
        
        if cached_sql:
            # Cache HIT - return immediately without calling LLM
            print(f"✅ Cache HIT: {question[:60]}...")
            return cached_sql
        
        # Cache MISS - call original LLM method
        print(f"⚠️  Cache MISS: {question[:60]}... → Calling LLM")
        sql = original_generate_sql(question, **kwargs)
        
        # Save to cache for next time (batch save for performance)
        custom_cache.set_multiple(cache_id, {
            "question": question,
            "sql": sql
        })
        
        print(f"💾 Cached for future: {cache_id}")
        return sql
    
    # Replace the method
    vn.generate_sql = cached_generate_sql
    print("✅ Cache wrapper installed on generate_sql method")
    
    # Add new endpoint to load from custom cache
    @app.flask_app.route("/api/v0/get_cached_question", methods=["GET"])
    def get_cached_question():
        """
        Load question and SQL from cache by ID
        New endpoint to work with custom cache
        """
        from flask import request, jsonify
        
        cache_id = request.args.get("id")
        if not cache_id:
            return jsonify({"type": "error", "error": "No id provided"})
        
        # Get data from cache
        cached_question = custom_cache.get(cache_id, "question")
        cached_sql = custom_cache.get(cache_id, "sql")
        
        if cached_question or cached_sql:
            print(f"✅ Loaded from cache: {cache_id}")
            return jsonify({
                "type": "question_cache",
                "id": cache_id,
                "question": cached_question if cached_question else "N/A",
                "sql": cached_sql if cached_sql else "N/A"
            })
        else:
            print(f"❌ Cache miss: {cache_id}")
            return jsonify({
                "type": "error",
                "error": f"No cached data found for id: {cache_id}"
            })
    
    # Add endpoint to get cache stats
    @app.flask_app.route("/api/v0/cache_stats", methods=["GET"])
    def get_cache_stats():
        """Get cache statistics"""
        from flask import jsonify
        
        stats = custom_cache.get_stats()
        return jsonify({
            "type": "cache_stats",
            "stats": stats
        })
    
    # Add new endpoint: Ask (Generate + Run SQL in one request)
    @app.flask_app.route("/api/v0/ask", methods=["GET", "POST"])
    def ask_question():
        """
        All-in-one endpoint: Generate SQL and execute it
        Similar to n8n workflow 02 (Generate & Run SQL)
        
        GET Method:
            Query params: ?question=Your question here
            
        POST Method:
            JSON body: {"question": "Your question here", "allow_llm_to_see_data": false}
        
        Response:
            {
                "success": true,
                "question": "...",
                "sql": "SELECT ...",
                "data": [...],
                "rows_count": 10,
                "cache_id": "abc123"
            }
        """
        from flask import request, jsonify
        import pandas as pd
        
        # Get question from query params (GET) or JSON body (POST)
        if request.method == "GET":
            question = request.args.get("question")
            allow_llm_to_see_data = request.args.get("allow_llm_to_see_data", "false").lower() == "true"
        else:  # POST
            data = request.get_json() or {}
            question = data.get("question")
            allow_llm_to_see_data = data.get("allow_llm_to_see_data", False)
        
        # Validate question
        if not question:
            return jsonify({
                "success": False,
                "error": "No question provided",
                "usage": {
                    "GET": "?question=Your question here",
                    "POST": '{"question": "Your question here"}'
                }
            }), 400
        
        try:
            # Step 1: Generate SQL
            print(f"🔍 Question: {question}")
            cache_id = custom_cache.generate_id(question=question)
            
            sql = vn.generate_sql(
                question=question, 
                allow_llm_to_see_data=allow_llm_to_see_data
            )
            
            if not sql:
                return jsonify({
                    "success": False,
                    "error": "Failed to generate SQL",
                    "question": question
                }), 500
            
            print(f"✅ Generated SQL: {sql[:100]}...")
            
            # Validate SQL
            if not vn.is_sql_valid(sql=sql):
                return jsonify({
                    "success": False,
                    "error": "Generated SQL is not valid",
                    "question": question,
                    "sql": sql
                }), 500
            
            # Step 2: Execute SQL
            if not vn.run_sql_is_set:
                return jsonify({
                    "success": False,
                    "error": "Database not connected. Please connect to a database first.",
                    "question": question,
                    "sql": sql,
                    "hint": "Use vn.connect_to_postgres() or similar method"
                }), 503
            
            print(f"⚙️  Executing SQL...")
            df = vn.run_sql(sql=sql)
            
            # Convert DataFrame to JSON
            if df is not None and not df.empty:
                data_json = df.to_dict(orient='records')
                rows_count = len(df)
                print(f"✅ Query returned {rows_count} rows")
            else:
                data_json = []
                rows_count = 0
                print(f"⚠️  Query returned no data")
            
            # Save to cache
            custom_cache.set_multiple(cache_id, {
                "question": question,
                "sql": sql,
                "df": df
            })
            
            # Step 3: Generate chart if data is suitable
            chart_json = None
            chart_image_url = None
            chart_html_url = None
            should_generate_chart = False
            
            if df is not None and not df.empty:
                should_generate_chart = vn.should_generate_chart(df)
                
                if should_generate_chart:
                    try:
                        print(f"📊 Generating chart...")
                        
                        # Generate Plotly code
                        plotly_code = vn.generate_plotly_code(
                            question=question,
                            sql=sql,
                            df_metadata=f"Running df.dtypes gives:\n{df.dtypes}"
                        )
                        
                        # Create Plotly figure
                        fig = vn.get_plotly_figure(
                            plotly_code=plotly_code,
                            df=df,
                            dark_mode=False
                        )
                        
                        # Convert to JSON
                        chart_json = fig.to_json()
                        print(f"✅ Chart generated successfully")
                        
                        # Convert chart to PNG and upload to image hosting
                        try:
                            import io
                            import base64
                            import requests as req
                            
                            print(f"📸 Converting chart to PNG...")
                            
                            # Convert Plotly figure to PNG bytes
                            img_bytes = fig.to_image(format="png", width=1200, height=800, scale=2)
                            
                            print(f"☁️  Uploading to ImgBB...")
                            
                            # Upload to ImgBB (free, no account needed)
                            imgbb_api_key = os.getenv("IMGBB_API_KEY", "")
                            
                            if imgbb_api_key:
                                # Encode image to base64
                                img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                                
                                # Upload to ImgBB
                                upload_response = req.post(
                                    "https://api.imgbb.com/1/upload",
                                    data={
                                        "key": imgbb_api_key,
                                        "image": img_base64,
                                        "name": f"vanna_chart_{cache_id[:8]}"
                                    },
                                    timeout=30
                                )
                                
                                if upload_response.status_code == 200:
                                    upload_data = upload_response.json()
                                    if upload_data.get('success'):
                                        chart_image_url = upload_data['data']['url']
                                        
                                        # Create HTML page with image
                                        html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vanna Chart - {question}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .container {{
            max-width: 1400px;
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
        .header h1 {{ font-size: 32px; margin-bottom: 10px; }}
        .header p {{ font-size: 16px; opacity: 0.9; }}
        .content {{ padding: 40px; text-align: center; }}
        .chart-image {{ 
            max-width: 100%; 
            height: auto; 
            border-radius: 8px; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            cursor: pointer;
            transition: transform 0.3s ease;
        }}
        .chart-image:hover {{ transform: scale(1.02); }}
        .info {{ 
            background: #f8f9fa; 
            padding: 20px; 
            border-radius: 8px; 
            margin-top: 30px;
            text-align: left;
        }}
        .badge {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            margin: 5px;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 14px;
            border-top: 1px solid #e0e0e0;
        }}
        a {{ color: #667eea; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 {question}</h1>
            <p>Generated by Vanna AI • Chart Image</p>
        </div>
        <div class="content">
            <img src="{chart_image_url}" alt="Chart" class="chart-image" onclick="window.open('{chart_image_url}', '_blank')">
            <div class="info">
                <h3 style="margin-bottom: 15px;">📋 Query Info</h3>
                <p><span class="badge">Rows</span>{rows_count} rows</p>
                <p><span class="badge">Format</span>PNG Image (1200x800)</p>
                <p><span class="badge">Hosted</span>ImgBB Cloud</p>
                <p style="margin-top: 15px;"><strong>Direct Image URL:</strong></p>
                <p><a href="{chart_image_url}" target="_blank">{chart_image_url}</a></p>
            </div>
        </div>
        <div class="footer">
            <p>Powered by Vanna.AI + Plotly + ImgBB</p>
            <p style="margin-top: 8px; font-size: 12px;">
                Click image to open in new tab • Right-click to download
            </p>
        </div>
    </div>
</body>
</html>"""
                                        
                                        # Upload HTML to tmpfiles.org (free temporary file hosting)
                                        html_upload_response = req.post(
                                            "https://tmpfiles.org/api/v1/upload",
                                            files={'file': ('chart.html', html_content.encode('utf-8'), 'text/html')},
                                            timeout=30
                                        )
                                        
                                        if html_upload_response.status_code == 200:
                                            html_data = html_upload_response.json()
                                            if html_data.get('status') == 'success':
                                                # tmpfiles.org returns URL like https://tmpfiles.org/123456
                                                # Need to change to https://tmpfiles.org/dl/123456 for direct access
                                                temp_url = html_data['data']['url']
                                                chart_html_url = temp_url.replace('tmpfiles.org/', 'tmpfiles.org/dl/')
                                                print(f"✅ Chart HTML uploaded: {chart_html_url}")
                                        
                                        print(f"✅ Chart image uploaded: {chart_image_url}")
                                    else:
                                        print(f"⚠️  ImgBB upload failed: {upload_data.get('error', {}).get('message')}")
                                else:
                                    print(f"⚠️  ImgBB upload failed: HTTP {upload_response.status_code}")
                            else:
                                print(f"⚠️  IMGBB_API_KEY not set, skipping image upload")
                                print(f"   Get free API key at: https://api.imgbb.com/")
                                
                        except ImportError:
                            print(f"⚠️  kaleido not installed, skipping PNG conversion")
                            print(f"   Install with: pip install kaleido")
                        except Exception as img_error:
                            print(f"⚠️  Image upload failed: {str(img_error)}")
                            import traceback
                            traceback.print_exc()
                        
                    except Exception as chart_error:
                        print(f"⚠️  Chart generation failed: {str(chart_error)}")
                        # Continue without chart - not a critical error
                        import traceback
                        traceback.print_exc()
            
            # Return success response with optional chart
            response_data = {
                "success": True,
                "question": question,
                "sql": sql,
                "data": data_json,
                "rows_count": rows_count,
                "cache_id": cache_id,
                "should_generate_chart": should_generate_chart
            }
            
            # Add chart if generated
            if chart_json:
                response_data["chart"] = chart_json
                response_data["has_chart"] = True
                
                # Add image URL if uploaded
                if chart_image_url:
                    response_data["chart_image_url"] = chart_image_url
                    response_data["chart_image_format"] = "png"
                    response_data["chart_image_size"] = "1200x800"
                
                # Add HTML URL if uploaded
                if chart_html_url:
                    response_data["chart_html_url"] = chart_html_url
                    response_data["chart_html_note"] = "Temporary URL (expires after period of inactivity)"
            else:
                response_data["has_chart"] = False
            
            return jsonify(response_data)
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return jsonify({
                "success": False,
                "error": str(e),
                "question": question,
                "sql": sql if 'sql' in locals() else None,
                "error_type": type(e).__name__
            }), 500
    
    # Add new endpoint: Clear Training Data
    @app.flask_app.route("/api/v0/clear_training_data", methods=["POST"])
    def clear_training_data():
        """
        Clear all training data from Vanna AND clear cache
        
        ⚠️ WARNING: This will delete ALL:
        - Training data (DDL, Documentation, SQL examples)
        - Cache data (vanna_cache table in PostgreSQL)
        
        Use this before retraining with new data to avoid conflicts.
        
        POST Method:
            No body required
            
        Response:
            {
                "success": true,
                "message": "Training data and cache cleared successfully",
                "data": {
                    "training": {
                        "count_before": 15,
                        "count_after": 0,
                        "cleared": 15
                    },
                    "cache": {
                        "count_before": 50,
                        "cleared": 50
                    }
                }
            }
        """
        from flask import jsonify
        
        try:
            # Step 1: Get count of training data before clearing
            print("🗑️  Clearing training data...")
            training_data_before = vn.get_training_data()
            
            # Handle both DataFrame and list returns
            if training_data_before is not None:
                # Check if it's a DataFrame
                if hasattr(training_data_before, 'empty'):
                    # It's a DataFrame
                    training_count_before = 0 if training_data_before.empty else len(training_data_before)
                else:
                    # It's a list or other iterable
                    training_count_before = len(training_data_before)
            else:
                training_count_before = 0
            
            print(f"   Found {training_count_before} training items")
            
            # Step 2: Clear all training data
            training_cleared = 0
            if training_count_before > 0:
                # Convert to list if it's a DataFrame
                if hasattr(training_data_before, 'to_dict'):
                    training_data_list = training_data_before.to_dict(orient='records')
                else:
                    training_data_list = training_data_before
                
                # Get all training IDs
                training_ids = [item['id'] for item in training_data_list if 'id' in item]
                
                # Remove each item
                for training_id in training_ids:
                    try:
                        vn.remove_training_data(id=training_id)
                        training_cleared += 1
                        print(f"   ✅ Removed training: {training_id}")
                    except Exception as e:
                        print(f"   ⚠️  Failed to remove training {training_id}: {str(e)}")
                
                # Verify clearing
                training_data_after = vn.get_training_data()
                
                # Handle DataFrame/list for count_after
                if training_data_after is not None:
                    if hasattr(training_data_after, 'empty'):
                        training_count_after = 0 if training_data_after.empty else len(training_data_after)
                    else:
                        training_count_after = len(training_data_after)
                else:
                    training_count_after = 0
                
                print(f"✅ Cleared {training_cleared} training items. {training_count_after} remaining.")
            else:
                training_count_after = 0
                print("⚠️  No training data to clear")
            
            # Step 3: Clear cache from vanna_cache table
            print("🗑️  Clearing cache from vanna_cache table...")
            cache_cleared = 0
            cache_count_before = 0
            
            try:
                # Check if using PostgreSQL cache
                if isinstance(custom_cache, PostgresCache):
                    import psycopg2
                    
                    # Connect to database
                    conn = psycopg2.connect(**db_params)
                    cursor = conn.cursor()
                    
                    # Get count before clearing
                    cursor.execute("SELECT COUNT(*) FROM vanna_cache")
                    cache_count_before = cursor.fetchone()[0]
                    print(f"   Found {cache_count_before} cache entries")
                    
                    # Clear all cache entries
                    if cache_count_before > 0:
                        cursor.execute("DELETE FROM vanna_cache")
                        cache_cleared = cursor.rowcount
                        conn.commit()
                        print(f"✅ Cleared {cache_cleared} cache entries")
                    else:
                        print("⚠️  No cache entries to clear")
                    
                    cursor.close()
                    conn.close()
                else:
                    # File-based cache
                    print("   Using file-based cache - clearing in-memory cache...")
                    if hasattr(custom_cache, 'cache'):
                        cache_count_before = len(custom_cache.cache)
                        custom_cache.cache = {}
                        cache_cleared = cache_count_before
                        print(f"✅ Cleared {cache_cleared} cache entries from file cache")
                    else:
                        print("⚠️  No cache to clear")
                        
            except Exception as cache_error:
                print(f"⚠️  Warning: Failed to clear cache: {str(cache_error)}")
                # Continue execution even if cache clearing fails
            
            # Step 4: Return response
            return jsonify({
                "success": True,
                "message": f"Cleared {training_cleared} training items and {cache_cleared} cache entries",
                "data": {
                    "training": {
                        "count_before": training_count_before,
                        "count_after": training_count_after,
                        "cleared": training_cleared
                    },
                    "cache": {
                        "count_before": cache_count_before,
                        "cleared": cache_cleared
                    }
                }
            })
                
        except Exception as e:
            print(f"❌ Error clearing training data: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return jsonify({
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }), 500
    
    # Add new endpoint: Train Batch (Train multiple data in one request)
    @app.flask_app.route("/api/v0/train_batch", methods=["POST"])
    def train_batch():
        """
        Train multiple data items in a single request
        
        This endpoint allows you to submit an array of training data items,
        which can include combinations of:
        - question + sql (Question-SQL pairs)
        - ddl (Database schema definitions)
        - documentation (Database documentation)
        
        POST Method:
            JSON body: {
                "training_data": [
                    {
                        "question": "Top 10 khách hàng theo doanh thu?",
                        "sql": "SELECT customer_name, SUM(amount) as revenue FROM orders GROUP BY customer_name ORDER BY revenue DESC LIMIT 10"
                    },
                    {
                        "ddl": "CREATE TABLE orders (id INT, customer_name VARCHAR(100), amount DECIMAL(10,2))"
                    },
                    {
                        "documentation": "Bảng orders chứa tất cả đơn hàng của khách hàng"
                    },
                    {
                        "question": "Tổng doanh thu năm 2024?",
                        "sql": "SELECT SUM(amount) FROM orders WHERE YEAR(order_date) = 2024"
                    }
                ]
            }
            
        Response:
            {
                "success": true,
                "message": "Trained 4 items successfully",
                "results": {
                    "total": 4,
                    "successful": 4,
                    "failed": 0,
                    "items": [
                        {"index": 0, "status": "success", "id": "abc123", "type": "question-sql"},
                        {"index": 1, "status": "success", "id": "def456", "type": "ddl"},
                        {"index": 2, "status": "success", "id": "ghi789", "type": "documentation"},
                        {"index": 3, "status": "success", "id": "jkl012", "type": "question-sql"}
                    ],
                    "errors": []
                }
            }
        """
        from flask import request, jsonify
        
        try:
            # Get JSON body
            data = request.get_json()
            
            if not data:
                return jsonify({
                    "success": False,
                    "error": "No JSON body provided",
                    "usage": {
                        "example": {
                            "training_data": [
                                {"question": "...", "sql": "..."},
                                {"ddl": "CREATE TABLE ..."},
                                {"documentation": "..."}
                            ]
                        }
                    }
                }), 400
            
            # Get training_data array
            training_data = data.get("training_data")
            
            if not training_data:
                return jsonify({
                    "success": False,
                    "error": "No 'training_data' array provided in JSON body",
                    "usage": {
                        "example": {
                            "training_data": [
                                {"question": "...", "sql": "..."},
                                {"ddl": "CREATE TABLE ..."}
                            ]
                        }
                    }
                }), 400
            
            if not isinstance(training_data, list):
                return jsonify({
                    "success": False,
                    "error": "'training_data' must be an array",
                    "received_type": str(type(training_data).__name__)
                }), 400
            
            if len(training_data) == 0:
                return jsonify({
                    "success": False,
                    "error": "'training_data' array is empty"
                }), 400
            
            print(f"📚 Training {len(training_data)} items...")
            
            # Track results
            results = {
                "total": len(training_data),
                "successful": 0,
                "failed": 0,
                "items": [],
                "errors": []
            }
            
            # Train each item
            for index, item in enumerate(training_data):
                try:
                    # Extract fields from item
                    question = item.get("question")
                    sql = item.get("sql")
                    ddl = item.get("ddl")
                    documentation = item.get("documentation")
                    
                    # Validate: at least one field must be present
                    if not any([question, sql, ddl, documentation]):
                        error_msg = f"Item {index}: No training data provided (need at least one of: question, sql, ddl, documentation)"
                        print(f"   ⚠️  {error_msg}")
                        results["failed"] += 1
                        results["items"].append({
                            "index": index,
                            "status": "failed",
                            "error": error_msg
                        })
                        results["errors"].append({
                            "index": index,
                            "error": error_msg
                        })
                        continue
                    
                    # Determine training type
                    training_type = []
                    if question and sql:
                        training_type.append("question-sql")
                    elif question:
                        training_type.append("question")
                    elif sql:
                        training_type.append("sql")
                    if ddl:
                        training_type.append("ddl")
                    if documentation:
                        training_type.append("documentation")
                    
                    training_type_str = "+".join(training_type)
                    
                    # Train this item
                    print(f"   📝 Training item {index + 1}/{len(training_data)} ({training_type_str})...")
                    
                    training_id = vn.train(
                        question=question,
                        sql=sql,
                        ddl=ddl,
                        documentation=documentation
                    )
                    
                    print(f"   ✅ Trained successfully: {training_id}")
                    
                    results["successful"] += 1
                    results["items"].append({
                        "index": index,
                        "status": "success",
                        "id": training_id,
                        "type": training_type_str
                    })
                    
                except Exception as item_error:
                    error_msg = str(item_error)
                    print(f"   ❌ Failed to train item {index}: {error_msg}")
                    
                    results["failed"] += 1
                    results["items"].append({
                        "index": index,
                        "status": "failed",
                        "error": error_msg
                    })
                    results["errors"].append({
                        "index": index,
                        "error": error_msg,
                        "item": item
                    })
            
            # Print summary
            print(f"✅ Training completed: {results['successful']}/{results['total']} successful, {results['failed']} failed")
            
            # Return response
            if results["failed"] == 0:
                return jsonify({
                    "success": True,
                    "message": f"Trained {results['successful']} items successfully",
                    "results": results
                })
            elif results["successful"] == 0:
                return jsonify({
                    "success": False,
                    "message": f"All {results['failed']} items failed to train",
                    "results": results
                }), 500
            else:
                return jsonify({
                    "success": True,
                    "message": f"Trained {results['successful']}/{results['total']} items successfully, {results['failed']} failed",
                    "results": results,
                    "warning": "Some items failed to train"
                }), 207  # 207 Multi-Status
                
        except Exception as e:
            print(f"❌ Error in train_batch: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return jsonify({
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }), 500
    
    print("=" * 70)
    print("✅ Server is ready!")
    print("=" * 70)
    print()
    print(f"🌐 Web UI:          http://localhost:{port}")
    print(f"📝 API Endpoints:   http://localhost:{port}/api/v0/")
    print(f"📚 Swagger Docs:    http://localhost:{port}/api/v0/")
    if debug:
        print(f"🐛 Debug Console:   Enabled (WebSocket)")
    print()
    print(f"⚙️  Configuration:")
    llm_provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    if llm_provider == "openai":
        print(f"   - LLM Provider: OpenAI")
        print(f"   - Model: {vn.config.get('model', 'N/A')}")
    else:
        print(f"   - LLM Provider: Google Gemini")
        print(f"   - Model: {vn.config.get('model_name', 'gemini-2.0-flash-exp')}")
    print(f"   - Language: Vietnamese")
    print(f"   - Embedding: {'BGE-M3' if os.getenv('HUGGINGFACE_API_KEY') else 'Default'}")
    print(f"   - LLM can see data: {allow_llm_to_see_data}")
    print(f"   - Debug mode: {debug}")
    print()
    print("=" * 70)
    print()
    print("💡 Tip: Bạn có thể hỏi câu hỏi bằng tiếng Việt!")
    print("   Ví dụ: 'Top 10 khách hàng có doanh thu cao nhất'")
    print()
    print("📖 API Examples:")
    print(f"   GET  http://localhost:{port}/api/v0/ask?question=Tổng doanh thu là bao nhiêu")
    print(f"   GET  http://localhost:{port}/api/v0/generate_sql?question=Top 10 customers")
    print(f"   GET  http://localhost:{port}/api/v0/get_training_data")
    print(f"   POST http://localhost:{port}/api/v0/train")
    print(f"   POST http://localhost:{port}/api/v0/train_batch")
    print(f"   POST http://localhost:{port}/api/v0/clear_training_data")
    print()
    print("💡 New Endpoints:")
    print("   - /api/v0/ask - Generate + Run SQL in one request")
    print("   - /api/v0/train_batch - Train multiple data in one request")
    print("   - /api/v0/clear_training_data - Clear all training data")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 70)
    print()
    
    # Run the Flask app
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,  # Don't use Flask's debug mode (we have our own)
        use_reloader=False  # Avoid double initialization
    )


if __name__ == "__main__":
    main()
