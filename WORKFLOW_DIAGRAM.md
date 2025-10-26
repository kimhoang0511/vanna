# 📊 VANNA WORKFLOW DIAGRAM

## 🔄 Quy trình hoạt động tổng quan

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         VANNA ARCHITECTURE                              │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   USER       │         │   VANNA      │         │  DATABASE    │
│              │         │   FRAMEWORK  │         │              │
└──────┬───────┘         └──────┬───────┘         └──────┬───────┘
       │                        │                        │
       │  1. Natural Language   │                        │
       │─────Question──────────>│                        │
       │                        │                        │
       │                        │  2. RAG Search         │
       │                        │    (Vector DB)         │
       │                        ├───────────┐            │
       │                        │<──────────┘            │
       │                        │                        │
       │                        │  3. Build Prompt       │
       │                        │    + Context           │
       │                        ├───────────┐            │
       │                        │<──────────┘            │
       │                        │                        │
       │                        │  4. Call LLM           │
       │                        │    (OpenAI/Claude)     │
       │                        ├──────────>│            │
       │                        │<───SQL────┤            │
       │                        │                        │
       │                        │  5. Execute SQL        │
       │                        │────────────────────────>│
       │                        │<─────Result────────────┤
       │                        │                        │
       │  6. Return Results     │                        │
       │<──(SQL + DataFrame +───┤                        │
       │      Chart)            │                        │
       │                        │                        │
```

---

## 🎯 Chi tiết từng bước

### **BƯỚC 1: TRAINING (Huấn luyện)**

```
┌─────────────────────────────────────────────────────────────┐
│                      TRAINING PHASE                         │
└─────────────────────────────────────────────────────────────┘

    ┌─────────────┐
    │   DDL       │────┐
    │ (Schema)    │    │
    └─────────────┘    │
                       │
    ┌─────────────┐    │      ┌──────────────┐      ┌──────────────┐
    │Documentation│────┼─────>│  Embedding   │─────>│  Vector DB   │
    │  (Business) │    │      │   Generator  │      │  (ChromaDB/  │
    └─────────────┘    │      │              │      │   Pinecone)  │
                       │      └──────────────┘      └──────────────┘
    ┌─────────────┐    │
    │SQL Examples │────┘
    │(Q&A Pairs)  │
    └─────────────┘

Mục đích: Lưu trữ metadata để LLM có context khi generate SQL
```

### **BƯỚC 2: ASKING (Hỏi đáp)**

```
┌─────────────────────────────────────────────────────────────┐
│                       ASK PHASE                             │
└─────────────────────────────────────────────────────────────┘

USER QUESTION: "What are the top 10 customers by sales?"
      │
      ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: Similarity Search (RAG)                           │
│  ─────────────────────────────────────────────────────────  │
│  Query Vector DB to find:                                   │
│    • Similar SQL queries                                    │
│    • Related DDL (tables/columns)                           │
│    • Relevant documentation                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: Build Prompt                                      │
│  ─────────────────────────────────────────────────────────  │
│  Combine:                                                   │
│    • User question                                          │
│    • Retrieved context (DDL + docs + examples)              │
│    • System instructions                                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: LLM Generation                                    │
│  ─────────────────────────────────────────────────────────  │
│  Send to: OpenAI / Anthropic / Gemini / Ollama             │
│  Receive: SQL Query                                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: Execute SQL                                       │
│  ─────────────────────────────────────────────────────────  │
│  Run on: PostgreSQL / MySQL / Snowflake / etc.             │
│  Return: Pandas DataFrame                                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 5: Visualization (Optional)                          │
│  ─────────────────────────────────────────────────────────  │
│  Generate: Plotly chart code                                │
│  Render: Interactive chart                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧩 Component Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                      VANNA COMPONENTS                            │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                         VannaBase                                │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  • train()          - Main training method                 │ │
│  │  • ask()            - Main query method                    │ │
│  │  • generate_sql()   - Generate SQL from question           │ │
│  │  • run_sql()        - Execute SQL                          │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                        │                    │
        ┌───────────────┴─────────┐          └──────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   LLM Layer     │    │  Vector Store   │    │  DB Connector   │
│                 │    │     Layer       │    │     Layer       │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • OpenAI_Chat   │    │ • ChromaDB      │    │ • PostgreSQL    │
│ • Anthropic     │    │ • Pinecone      │    │ • MySQL         │
│ • Gemini        │    │ • FAISS         │    │ • Snowflake     │
│ • Ollama        │    │ • Qdrant        │    │ • BigQuery      │
│ • Mistral       │    │ • Milvus        │    │ • SQLite        │
│ • Cohere        │    │ • Weaviate      │    │ • DuckDB        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 🔄 Data Flow trong RAG

```
USER QUESTION: "Show me revenue by month"
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ 1. Embedding Generator                                       │
│    Question → Vector [0.123, 0.456, 0.789, ...]            │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. Vector DB Search (Top-K Similarity)                      │
│                                                              │
│    Training Data:                                            │
│    ┌──────────────────────────────────────────────────────┐ │
│    │ ID  │ Type │ Content                    │ Similarity │ │
│    ├─────┼──────┼────────────────────────────┼───────────┤ │
│    │ 123 │ DDL  │ CREATE TABLE revenue...   │   0.95    │ │
│    │ 456 │ SQL  │ SELECT date, SUM(...)     │   0.89    │ │
│    │ 789 │ DOC  │ Revenue is calculated by..│   0.85    │ │
│    └──────────────────────────────────────────────────────┘ │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. Prompt Construction                                       │
│                                                              │
│    System: You are a SQL expert...                          │
│    Context:                                                  │
│      - Table: revenue (date, amount, category)              │
│      - Example: SELECT date, SUM(amount) ...                │
│      - Note: Revenue is calculated by ...                   │
│    Question: Show me revenue by month                       │
│    Instruction: Generate SQL query                          │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────┐
│ 4. LLM Processing                                           │
│                                                              │
│    Input: Full Prompt                                        │
│    Output: SELECT DATE_TRUNC('month', date) as month,       │
│            SUM(amount) as total_revenue                      │
│            FROM revenue                                      │
│            GROUP BY month                                    │
│            ORDER BY month                                    │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────┐
│ 5. SQL Execution                                            │
│                                                              │
│    Run on Database → Return DataFrame                        │
└──────────────────────────────────────────────────────────────┘
```

---

## 🎨 Các Patterns Sử dụng

### **Pattern 1: Mix & Match Components**

```python
# OpenAI + ChromaDB
class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    pass

# Claude + Pinecone
class MyVanna(Pinecone_VectorStore, Anthropic_Chat):
    pass

# Ollama + FAISS (Fully Local)
class MyVanna(FAISS_VectorStore, Ollama_Chat):
    pass
```

### **Pattern 2: Configuration**

```python
vn = MyVanna(config={
    # LLM config
    'api_key': 'sk-...',
    'model': 'gpt-4',
    'temperature': 0.1,
    
    # Vector DB config
    'n_results': 10,        # Số training items để retrieve
    'n_results_sql': 5,     # Số SQL examples
    'n_results_ddl': 3,     # Số DDL statements
    
    # Other
    'language': 'Vietnamese',
    'dialect': 'PostgreSQL'
})
```

---

## 🚀 Quick Start Flowchart

```
START
  │
  ▼
┌─────────────────────┐
│ Install Vanna       │──> pip install 'vanna[openai,chromadb]'
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Initialize Vanna    │──> vn = MyVanna(config={...})
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Connect to DB       │──> vn.connect_to_postgres(...)
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐     ┌──────────────────┐
│ Train with DDL      │────>│ vn.train(ddl=...)│
└──────┬──────────────┘     └──────────────────┘
       │
       ▼
┌─────────────────────┐     ┌──────────────────┐
│ Train with Docs     │────>│ vn.train(doc=...)│
└──────┬──────────────┘     └──────────────────┘
       │
       ▼
┌─────────────────────┐     ┌──────────────────┐
│ Train with SQL      │────>│ vn.train(sql=...)│
└──────┬──────────────┘     └──────────────────┘
       │
       ▼
┌─────────────────────┐
│ Ask Questions       │──> sql = vn.generate_sql("...")
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Run SQL             │──> df = vn.run_sql(sql)
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Visualize (opt)     │──> fig = vn.get_plotly_figure(...)
└──────┬──────────────┘
       │
       ▼
      END
```

---

## 💡 Key Concepts

| Concept | Giải thích |
|---------|-----------|
| **RAG** | Retrieval-Augmented Generation - Tìm kiếm context trước khi generate |
| **Vector DB** | Database lưu embeddings để similarity search |
| **Embedding** | Vector representation của text (DDL, SQL, docs) |
| **Training** | Lưu metadata vào Vector DB |
| **Context** | Thông tin liên quan được retrieve từ Vector DB |
| **Prompt** | Câu hỏi + context gửi cho LLM |
| **Auto-train** | Tự động train trên successful queries |

---

Diagram này giúp hiểu rõ cách Vanna hoạt động từ high-level architecture đến chi tiết implementation! 🎯
