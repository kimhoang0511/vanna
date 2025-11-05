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
    POST /api/v0/fix_sql - Tự động sửa lỗi SQL
    POST /api/v0/update_sql - Cập nhật SQL
    GET  /api/v0/generate_plotly_figure - Tạo biểu đồ
    GET  /api/v0/download_csv - Download CSV
    GET  /api/v0/get_training_data - Lấy training data
    POST /api/v0/train - Thêm training data
    POST /api/v0/remove_training_data - Xóa training data
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
from vanna_cache_fix import QuestionHashCache

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
    """Connect to PostgreSQL database"""
    
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", "5432"))
    db_name = os.getenv("DB_NAME", "postgres")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "")
    
    print(f"🔗 Connecting to PostgreSQL: {db_host}:{db_port}/{db_name}...")
    
    try:
        vn.connect_to_postgres(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_password
        )
        print("✅ Database connected successfully!")
        return True
    except Exception as e:
        print(f"⚠️  Warning: Could not connect to database: {str(e)}")
        print("   You can connect later using the UI or API")
        return False


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
    
    # Try to connect to database
    connect_to_database(vn)
    
    print()
    print("🌐 Starting Flask server...")
    print()
    
    # Get configuration from environment
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    allow_llm_to_see_data = os.getenv("ALLOW_LLM_TO_SEE_DATA", "True").lower() == "true"
    
    # Initialize custom cache with question hashing
    print("🔧 Initializing cache with question hashing...")
    custom_cache = QuestionHashCache()
    
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
    
    # Override generate_sql endpoint to check cache first
    @app.flask_app.route("/api/v0/generate_sql", methods=["GET"])
    def generate_sql_with_cache():
        """
        Generate SQL with cache lookup first
        Override default endpoint to check cache before calling LLM
        """
        from flask import request, jsonify
        
        question = request.args.get("question")
        if not question:
            return jsonify({"type": "error", "error": "No question provided"})
        
        # Generate cache ID from question hash
        cache_id = custom_cache.generate_id(question=question)
        
        # Check cache first
        cached_sql = custom_cache.get(cache_id, "sql")
        
        if cached_sql:
            # Cache HIT - return immediately without calling LLM
            print(f"✅ Cache HIT: {question[:60]}...")
            return jsonify({
                "type": "sql",
                "id": cache_id,
                "text": cached_sql,
                "cached": True
            })
        
        # Cache MISS - call LLM
        print(f"⚠️  Cache MISS: {question[:60]}... → Calling LLM")
        
        try:
            sql = vn.generate_sql(
                question=question,
                allow_llm_to_see_data=allow_llm_to_see_data
            )
            
            # Save to cache for next time
            custom_cache.set(cache_id, "question", question)
            custom_cache.set(cache_id, "sql", sql)
            
            print(f"💾 Cached for future: {cache_id}")
            
            if vn.is_sql_valid(sql=sql):
                return jsonify({
                    "type": "sql",
                    "id": cache_id,
                    "text": sql,
                    "cached": False
                })
            else:
                return jsonify({
                    "type": "text",
                    "id": cache_id,
                    "text": sql,
                    "cached": False
                })
        except Exception as e:
            return jsonify({
                "type": "error",
                "error": str(e)
            })
    
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
    print(f"   GET  http://localhost:{port}/api/v0/generate_sql?question=Tổng doanh thu là bao nhiêu")
    print(f"   GET  http://localhost:{port}/api/v0/get_training_data")
    print(f"   POST http://localhost:{port}/api/v0/train")
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
