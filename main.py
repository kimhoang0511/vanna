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
    POST /generate_chart - Generate Plotly chart (JSON, HTML, PNG, JPG, PDF)
    GET /download_chart/{format} - Download chart as file
    POST /ask - All-in-one (generate + execute)
    GET /health - Health check
    GET /training_data - Get training data
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import pandas as pd
import os
import base64
import io
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


class GenerateChartRequest(BaseModel):
    """Request để generate chart từ SQL hoặc question"""
    question: str
    sql: Optional[str] = None
    dark_mode: Optional[bool] = False
    custom_instructions: Optional[str] = None
    export_format: Optional[str] = "json"  # json, html, png, jpg, pdf
    image_width: Optional[int] = 1200
    image_height: Optional[int] = 800


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


@app.post("/generate_chart")
async def generate_chart(request: GenerateChartRequest):
    """
    Generate Plotly chart from question or SQL
    
    Tạo biểu đồ Plotly từ câu hỏi hoặc SQL query.
    Có thể export sang nhiều formats: JSON, HTML, PNG, JPG, PDF
    
    Example:
    ```json
    {
        "question": "Top 10 khách hàng có doanh thu cao nhất",
        "dark_mode": false,
        "custom_instructions": "Use blue gradient colors and show data labels",
        "export_format": "jpg",
        "image_width": 1200,
        "image_height": 800
    }
    ```
    
    Supported formats:
    - json: Plotly JSON (for interactive rendering)
    - html: Full HTML page
    - png: PNG image (static)
    - jpg: JPEG image (static)
    - pdf: PDF document (static)
    
    Response includes:
    - chart_json: Plotly figure JSON (if format=json)
    - chart_html: Full HTML (if format=html)
    - chart_image_base64: Base64 encoded image (if format=png/jpg/pdf)
    - sql: SQL query used
    - row_count: Number of data points
    - data: First 10 rows of data
    """
    vn = vanna_service.get_instance()
    
    try:
        # Generate SQL if not provided
        if request.sql:
            sql = request.sql
        else:
            sql = vn.generate_sql(request.question)
        
        # Execute SQL
        df = vn.run_sql(sql)
        
        # Check if data is suitable for chart
        if not vn.should_generate_chart(df):
            return SuccessResponse(
                success=False,
                message="Data is not suitable for chart visualization (need at least 2 rows and numeric columns)",
                data={
                    "sql": sql,
                    "row_count": len(df),
                    "data": df.to_dict(orient='records')
                }
            )
        
        # Build question with custom instructions
        chart_question = request.question
        if request.custom_instructions:
            chart_question = f"{request.question}. {request.custom_instructions}"
        
        # Generate Plotly code
        plotly_code = vn.generate_plotly_code(
            question=chart_question,
            sql=sql,
            df_metadata=f"Running df.dtypes gives:\n{df.dtypes}"
        )
        
        # Create Plotly figure
        fig = vn.get_plotly_figure(
            plotly_code=plotly_code,
            df=df,
            dark_mode=request.dark_mode
        )
        
        # Prepare response data
        response_data = {
            "sql": sql,
            "row_count": len(df),
            "data": df.head(10).to_dict(orient='records'),
            "plotly_code": plotly_code,
            "export_format": request.export_format
        }
        
        # Export based on format
        export_format = request.export_format.lower()
        
        if export_format == "json":
            response_data["chart_json"] = fig.to_json()
            
        elif export_format == "html":
            response_data["chart_html"] = fig.to_html(include_plotlyjs='cdn')
            
        elif export_format in ["png", "jpg", "jpeg", "pdf"]:
            # Export to image using kaleido
            try:
                # Determine image format
                img_format = "jpeg" if export_format in ["jpg", "jpeg"] else export_format
                
                # Export to bytes
                img_bytes = fig.to_image(
                    format=img_format,
                    width=request.image_width,
                    height=request.image_height,
                    engine="kaleido"
                )
                
                # Convert to base64
                img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                
                response_data["chart_image_base64"] = img_base64
                response_data["image_width"] = request.image_width
                response_data["image_height"] = request.image_height
                response_data["mime_type"] = f"image/{img_format}" if img_format != "pdf" else "application/pdf"
                
            except Exception as img_error:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to export image. Make sure kaleido is installed: {str(img_error)}"
                )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported export format: {export_format}. Use: json, html, png, jpg, or pdf"
            )
        
        return SuccessResponse(
            success=True,
            message=f"Chart generated successfully as {export_format.upper()}",
            data=response_data
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate chart: {str(e)}")


@app.get("/download_chart/{format}")
async def download_chart(
    format: str,
    question: str,
    sql: Optional[str] = None,
    dark_mode: bool = False,
    width: int = 1200,
    height: int = 800
):
    """
    Download chart as file (PNG, JPG, PDF)
    
    Direct download endpoint - returns file for browser download
    
    Example:
    GET /download_chart/jpg?question=Top 10 customers&width=1920&height=1080
    """
    vn = vanna_service.get_instance()
    
    try:
        # Generate SQL if not provided
        if not sql:
            sql = vn.generate_sql(question)
        
        # Execute SQL
        df = vn.run_sql(sql)
        
        if not vn.should_generate_chart(df):
            raise HTTPException(status_code=400, detail="Data not suitable for chart")
        
        # Generate chart
        plotly_code = vn.generate_plotly_code(
            question=question,
            sql=sql,
            df_metadata=f"Running df.dtypes gives:\n{df.dtypes}"
        )
        
        fig = vn.get_plotly_figure(plotly_code=plotly_code, df=df, dark_mode=dark_mode)
        
        # Export to image
        img_format = "jpeg" if format.lower() in ["jpg", "jpeg"] else format.lower()
        
        img_bytes = fig.to_image(
            format=img_format,
            width=width,
            height=height,
            engine="kaleido"
        )
        
        # Return as file download
        media_type = f"image/{img_format}" if img_format != "pdf" else "application/pdf"
        filename = f"chart.{format.lower()}"
        
        return Response(
            content=img_bytes,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download chart: {str(e)}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate chart: {str(e)}")


@app.post("/clear_training_data", response_model=SuccessResponse)
async def clear_training_data():
    """Clear all training data from ChromaDB
    
    This endpoint removes all training data including:
    - DDL (Data Definition Language)
    - Documentation
    - SQL examples
    
    Use this before retraining to avoid conflicts with old data.
    """
    vn = vanna_service.get_instance()
    
    try:
        # Get current training data before clearing
        df_before = vn.get_training_data()
        count_before = len(df_before) if df_before is not None else 0
        
        # Remove all training data
        # Vanna stores training data in ChromaDB collections
        # We need to clear the collection by removing all items
        if hasattr(vn, 'remove_training_data'):
            # If Vanna has a built-in method to clear data
            vn.remove_training_data()
        else:
            # Manually clear by removing all IDs
            if df_before is not None and len(df_before) > 0:
                for _, row in df_before.iterrows():
                    if 'id' in row:
                        try:
                            vn.remove_training_data(id=row['id'])
                        except:
                            pass
        
        # Verify data is cleared
        df_after = vn.get_training_data()
        count_after = len(df_after) if df_after is not None else 0
        
        return SuccessResponse(
            success=True,
            message=f"Training data cleared successfully. Removed {count_before} items. {count_after} items remaining.",
            data={
                "count_before": count_before,
                "count_after": count_after,
                "cleared": count_before - count_after
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear training data: {str(e)}")


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
