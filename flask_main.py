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
from vanna.openai import OpenAI_Chat
from vanna.flask import VannaFlaskApp
from vanna_cache_fix import QuestionHashCache, PersistentQuestionCache
from postgres_cache import PostgresCache

# ============================================================================
# Define Custom Vanna Class
# ============================================================================

class MyVanna(VietnameseVanna, ChromaDB_VectorStore, OpenAI_Chat):
    """Custom Vanna class kết hợp Vietnamese support + ChromaDB + OpenAI"""
    
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)


# ============================================================================
# Initialize Vanna Instance
# ============================================================================

def initialize_vanna():
    """Initialize Vanna with BGE-M3 embedding and Vietnamese support"""
    
    # Get API keys from environment
    openai_api_key = os.getenv("OPENAI_API_KEY")
    huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")
    
    if not openai_api_key:
        raise ValueError(
            "OPENAI_API_KEY not found in environment variables. "
            "Please set it in .env file or export it."
        )
    
    if not huggingface_api_key:
        raise ValueError(
            "HUGGINGFACE_API_KEY not found in environment variables. "
            "Please set it in .env file or export it."
        )
    
    print("🔧 Initializing BGE-M3 Embedding Function...")
    bge_m3_ef = BGE_M3_EmbeddingFunction(api_key=huggingface_api_key)
    
    print("🔧 Initializing Vanna with Vietnamese support...")
    config = {
        'model': os.getenv("VANNA_MODEL", "gpt-4o-mini"),
        'api_key': openai_api_key,
        'embedding_function': bge_m3_ef,
        'temperature': float(os.getenv("VANNA_TEMPERATURE", "0.7")),
        'n_results_sql': int(os.getenv("VANNA_N_RESULTS_SQL", "5")),
        'n_results_ddl': int(os.getenv("VANNA_N_RESULTS_DDL", "3")),
        'n_results_documentation': int(os.getenv("VANNA_N_RESULTS_DOCUMENTATION", "7")),
        'language': 'Vietnamese'
    }
    
    vn = MyVanna(config=config)
    
    print("✅ Vanna initialized successfully!")
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
            
            # Return success response
            return jsonify({
                "success": True,
                "question": question,
                "sql": sql,
                "data": data_json,
                "rows_count": rows_count,
                "cache_id": cache_id
            })
            
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
            training_count_before = len(training_data_before) if training_data_before else 0
            
            print(f"   Found {training_count_before} training items")
            
            # Step 2: Clear all training data
            training_cleared = 0
            if training_count_before > 0:
                # Get all training IDs
                training_ids = [item['id'] for item in training_data_before if 'id' in item]
                
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
                training_count_after = len(training_data_after) if training_data_after else 0
                
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
    print(f"   - Model: {vn.config.get('model', 'N/A')}")
    print(f"   - Language: Vietnamese")
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
    print(f"   POST http://localhost:{port}/api/v0/clear_training_data")
    print()
    print("💡 New Endpoints:")
    print("   - /api/v0/ask - Generate + Run SQL in one request")
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
