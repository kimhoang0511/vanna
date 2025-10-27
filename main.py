"""
API Server cho VietnameseVanna
Cho phép gọi các hàm từ bên ngoài qua HTTP REST API

Usage:
    python api_server.py

Endpoints:
    POST /init - Initialize Vanna
    POST /connect/postgres - Connect to PostgreSQL
    POST /train/ddl - Train với DDL
    POST /train/documentation - Train với documentation
    POST /train/sql - Train với SQL examples
    POST /generate_sql - Generate SQL từ question
    POST /execute_sql - Execute SQL và trả về kết quả
    POST /ask - All-in-one (generate + execute)
    GET /health - Health check
    GET /training_data - Get training data
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from vietnamese_vanna import VietnameseVanna
from bge_m3_embedding import BGE_M3_EmbeddingFunction

# Initialize FastAPI
app = FastAPI(
    title="Vietnamese Vanna API",
    description="API for Vietnamese-optimized SQL generation using Vanna",
    version="1.0.0"
)

# CORS Configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key Authentication (Optional)
API_KEY = os.getenv("API_KEY")

async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Optional API key verification"""
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return x_api_key


# ============================================================================
# Singleton Service
# ============================================================================

class VannaService:
    """Singleton service để quản lý Vanna instance"""
    
    def __init__(self):
        self.vn: Optional[VietnameseVanna] = None
        self.config: Optional[Dict[str, Any]] = None
    
    def initialize(
        self,
        openai_api_key: str,
        huggingface_api_key: str,
        model: str = "gpt-4o-mini",
        dialect: str = "PostgreSQL",
        temperature: float = 0.7,
        n_results_sql: int = 5,
        n_results_ddl: int = 3,
        n_results_documentation: int = 7
    ):
        """Initialize Vanna instance"""
        
        # Set environment variables
        os.environ['OPENAI_API_KEY'] = openai_api_key
        if huggingface_api_key:
            os.environ['HUGGINGFACE_API_KEY'] = huggingface_api_key
        
        # Create BGE-M3 embedding function
        bge_m3_ef = BGE_M3_EmbeddingFunction(api_key=huggingface_api_key)
        
        # Initialize Vanna
        from vanna.chromadb import ChromaDB_VectorStore
        from vanna.openai import OpenAI_Chat
        
        class MyVanna(VietnameseVanna, ChromaDB_VectorStore, OpenAI_Chat):
            def __init__(self, config=None):
                ChromaDB_VectorStore.__init__(self, config=config)
                OpenAI_Chat.__init__(self, config=config)
        
        config = {
            'model': model,
            'api_key': openai_api_key,
            'embedding_function': bge_m3_ef,
            'temperature': temperature,
            'n_results_sql': n_results_sql,
            'n_results_ddl': n_results_ddl,
            'n_results_documentation': n_results_documentation,
            'language': 'Vietnamese'
        }
        
        self.vn = MyVanna(config=config)
        self.config = config
        
        return self.vn
    
    def get_instance(self) -> VietnameseVanna:
        """Get Vanna instance (raise error if not initialized)"""
        if self.vn is None:
            raise HTTPException(
                status_code=400,
                detail="Vanna not initialized. Call /init endpoint first."
            )
        return self.vn


# Global service instance
vanna_service = VannaService()


# ============================================================================
# Pydantic Models (Request/Response schemas)
# ============================================================================

class InitRequest(BaseModel):
    """Request để khởi tạo Vanna"""
    openai_api_key: Optional[str] = None
    huggingface_api_key: Optional[str] = None
    model: str = "gpt-4o-mini"
    dialect: str = "PostgreSQL"
    temperature: float = 0.7
    n_results_sql: int = 5
    n_results_ddl: int = 3
    n_results_documentation: int = 7


class PostgresConnectionRequest(BaseModel):
    """Request để connect PostgreSQL"""
    host: Optional[str] = None
    port: Optional[int] = 5432
    database: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None


class TrainDDLRequest(BaseModel):
    """Request để train với DDL"""
    ddl: str


class TrainDocumentationRequest(BaseModel):
    """Request để train với documentation"""
    documentation: str


class TrainSQLRequest(BaseModel):
    """Request để train với SQL examples"""
    question: str
    sql: str


class GenerateSQLRequest(BaseModel):
    """Request để generate SQL"""
    question: str
    allow_llm_to_see_data: bool = False


class ExecuteSQLRequest(BaseModel):
    """Request để execute SQL"""
    sql: str


class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool
    message: str
    data: Optional[Any] = None


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "service": "Vietnamese Vanna API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "repository": "https://github.com/kimhoang0511/vanna"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Vietnamese Vanna API",
        "initialized": vanna_service.vn is not None,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "model": vanna_service.config.get('model') if vanna_service.config else None
    }


@app.post("/init", response_model=SuccessResponse)
async def initialize_vanna(request: InitRequest):
    """
    Initialize Vanna with API keys and configuration
    
    Example:
    ```json
    {
        "openai_api_key": "sk-xxx",
        "huggingface_api_key": "hf_xxx",
        "model": "gpt-4o-mini"
    }
    ```
    
    Note: API keys có thể được truyền qua environment variables thay vì request body
    """
    try:
        # Use environment variables if not provided in request
        openai_key = request.openai_api_key or os.getenv("OPENAI_API_KEY")
        hf_key = request.huggingface_api_key or os.getenv("HUGGINGFACE_API_KEY")
        
        if not openai_key:
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key is required (via request or OPENAI_API_KEY env variable)"
            )
        
        if not hf_key:
            raise HTTPException(
                status_code=400,
                detail="Hugging Face API key is required (via request or HUGGINGFACE_API_KEY env variable)"
            )
        
        vanna_service.initialize(
            openai_api_key=openai_key,
            huggingface_api_key=hf_key,
            model=request.model,
            dialect=request.dialect,
            temperature=request.temperature,
            n_results_sql=request.n_results_sql,
            n_results_ddl=request.n_results_ddl,
            n_results_documentation=request.n_results_documentation
        )
        
        return SuccessResponse(
            success=True,
            message="Vanna initialized successfully",
            data={
                "model": request.model,
                "dialect": request.dialect,
                "temperature": request.temperature
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize: {str(e)}")


@app.post("/connect/postgres", response_model=SuccessResponse)
async def connect_postgres(request: PostgresConnectionRequest):
    """
    Kết nối đến PostgreSQL database
    
    Example:
    ```json
    {
        "host": "localhost",
        "port": 5432,
        "database": "mydb",
        "user": "postgres",
        "password": "password"
    }
    ```
    
    Note: Connection params có thể được truyền qua environment variables
    """
    vn = vanna_service.get_instance()
    
    try:
        # Use environment variables if not provided
        host = request.host or os.getenv("DB_HOST", "localhost")
        port = request.port or int(os.getenv("DB_PORT", "5432"))
        database = request.database or os.getenv("DB_NAME", "postgres")
        user = request.user or os.getenv("DB_USER", "postgres")
        password = request.password or os.getenv("DB_PASSWORD", "")
        
        vn.connect_to_postgres(
            host=host,
            port=port,
            dbname=database,
            user=user,
            password=password
        )
        
        return SuccessResponse(
            success=True,
            message="Connected to PostgreSQL successfully",
            data={"database": database, "host": host, "port": port}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect: {str(e)}")


@app.post("/train/ddl", response_model=SuccessResponse)
async def train_ddl(request: TrainDDLRequest):
    """
    Train với DDL (table schema)
    
    Example:
    ```json
    {
        "ddl": "CREATE TABLE sale (id INT PRIMARY KEY, name TEXT, sales MONEY);"
    }
    ```
    """
    vn = vanna_service.get_instance()
    
    try:
        training_id = vn.train(ddl=request.ddl)
        
        return SuccessResponse(
            success=True,
            message="DDL trained successfully",
            data={"training_id": training_id}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to train DDL: {str(e)}")


@app.post("/train/documentation", response_model=SuccessResponse)
async def train_documentation(request: TrainDocumentationRequest):
    """
    Train với documentation (có thể là tiếng Việt)
    
    Example:
    ```json
    {
        "documentation": "Bảng sale chứa dữ liệu bán hàng. Dùng SUM(sales::numeric) để tính tổng."
    }
    ```
    """
    vn = vanna_service.get_instance()
    
    try:
        training_id = vn.train(documentation=request.documentation)
        
        return SuccessResponse(
            success=True,
            message="Documentation trained successfully",
            data={"training_id": training_id}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to train documentation: {str(e)}")


@app.post("/train/sql", response_model=SuccessResponse)
async def train_sql(request: TrainSQLRequest):
    """
    Train với SQL examples (question + SQL pair)
    
    Example:
    ```json
    {
        "question": "Tổng doanh thu là bao nhiêu?",
        "sql": "SELECT SUM(sales::numeric) FROM sale"
    }
    ```
    """
    vn = vanna_service.get_instance()
    
    try:
        training_id = vn.train(question=request.question, sql=request.sql)
        
        return SuccessResponse(
            success=True,
            message="SQL example trained successfully",
            data={"training_id": training_id}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to train SQL: {str(e)}")


@app.post("/generate_sql", response_model=SuccessResponse)
async def generate_sql(request: GenerateSQLRequest):
    """
    Generate SQL từ câu hỏi (có thể là tiếng Việt)
    
    Example:
    ```json
    {
        "question": "Top 10 sản phẩm bán chạy nhất?",
        "allow_llm_to_see_data": false
    }
    ```
    """
    vn = vanna_service.get_instance()
    
    try:
        sql = vn.generate_sql(
            question=request.question,
            allow_llm_to_see_data=request.allow_llm_to_see_data
        )
        
        return SuccessResponse(
            success=True,
            message="SQL generated successfully",
            data={"sql": sql, "question": request.question}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate SQL: {str(e)}")


@app.post("/execute_sql", response_model=SuccessResponse)
async def execute_sql(request: ExecuteSQLRequest):
    """
    Execute SQL và trả về kết quả
    
    Example:
    ```json
    {
        "sql": "SELECT COUNT(*) FROM sale"
    }
    ```
    """
    vn = vanna_service.get_instance()
    
    try:
        df = vn.run_sql(request.sql)
        
        # Convert DataFrame to dict
        result = df.to_dict(orient='records')
        
        return SuccessResponse(
            success=True,
            message="SQL executed successfully",
            data={
                "sql": request.sql,
                "rows": len(result),
                "data": result
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute SQL: {str(e)}")


@app.post("/ask", response_model=SuccessResponse)
async def ask_question(request: GenerateSQLRequest):
    """
    All-in-one: Generate SQL + Execute + Return results
    
    Example:
    ```json
    {
        "question": "Có bao nhiêu giao dịch trong tháng 10?",
        "allow_llm_to_see_data": false
    }
    ```
    """
    vn = vanna_service.get_instance()
    
    try:
        # Generate SQL
        sql = vn.generate_sql(
            question=request.question,
            allow_llm_to_see_data=request.allow_llm_to_see_data
        )
        
        # Execute SQL
        df = vn.run_sql(sql)
        result = df.to_dict(orient='records')
        
        return SuccessResponse(
            success=True,
            message="Question answered successfully",
            data={
                "question": request.question,
                "sql": sql,
                "rows": len(result),
                "data": result
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to answer question: {str(e)}")


@app.get("/training_data", response_model=SuccessResponse)
async def get_training_data():
    """Get all training data"""
    vn = vanna_service.get_instance()
    
    try:
        df = vn.get_training_data()
        result = df.to_dict(orient='records')
        
        return SuccessResponse(
            success=True,
            message="Training data retrieved successfully",
            data={"count": len(result), "data": result}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get training data: {str(e)}")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    
    print("=" * 70)
    print("🚀 Vietnamese Vanna API Server")
    print("=" * 70)
    print(f"\n📝 Documentation: http://localhost:{port}/docs")
    print(f"🔍 Health check: http://localhost:{port}/health")
    print(f"🌐 Port: {port}")
    print(f"🔐 API Key: {'Enabled' if API_KEY else 'Disabled'}")
    print("\n" + "=" * 70 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
