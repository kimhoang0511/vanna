# 🇻🇳 Vietnamese Vanna API

> Vietnamese-optimized SQL generation API using Vanna RAG framework

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

## 🌟 Features

- ✅ **Vietnamese Language Support**: Optimized prompts for Vietnamese questions and documentation
- ✅ **BGE-M3 Embeddings**: 1024-dimensional multilingual embeddings
- ✅ **GPT-4o-mini**: Latest OpenAI model for better accuracy
- ✅ **PostgreSQL**: Direct database connection
- ✅ **REST API**: Easy integration with n8n, webhooks, or any HTTP client
- ✅ **RAG Framework**: Retrieval-Augmented Generation for context-aware SQL

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env

# Run server
python api_server.py
```

Server runs at: http://localhost:8000

Documentation: http://localhost:8000/docs

### Deploy to Railway

1. Push code to GitHub
2. Create new project on [Railway](https://railway.app)
3. Connect GitHub repository
4. Add environment variables
5. Deploy! 🚂

See [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) for detailed guide.

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/init` | POST | Initialize Vanna |
| `/connect/postgres` | POST | Connect to PostgreSQL |
| `/train/ddl` | POST | Train with table schema |
| `/train/documentation` | POST | Train with documentation (Vietnamese) |
| `/train/sql` | POST | Train with SQL examples |
| `/generate_sql` | POST | Generate SQL from question |
| `/execute_sql` | POST | Execute SQL query |
| `/ask` | POST | All-in-one: generate + execute |
| `/training_data` | GET | Get all training data |

## 🧪 Example Usage

### Generate SQL (Vietnamese)

```bash
curl -X POST http://localhost:8000/generate_sql \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Tổng doanh thu trong tháng 10 là bao nhiêu?",
    "allow_llm_to_see_data": false
  }'
```

Response:
```json
{
  "success": true,
  "message": "SQL generated successfully",
  "data": {
    "sql": "SELECT SUM(sales::numeric) FROM sale WHERE EXTRACT(MONTH FROM date) = 10",
    "question": "Tổng doanh thu trong tháng 10 là bao nhiêu?"
  }
}
```

### All-in-one: Generate + Execute

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Top 5 sản phẩm bán chạy nhất?"
  }'
```

Response:
```json
{
  "success": true,
  "message": "Question answered successfully",
  "data": {
    "question": "Top 5 sản phẩm bán chạy nhất?",
    "sql": "SELECT name, COUNT(*) as total FROM sale GROUP BY name ORDER BY total DESC LIMIT 5",
    "rows": 5,
    "data": [
      {"name": "iPhone", "total": 15},
      {"name": "MacBook", "total": 12}
    ]
  }
}
```

## 🔧 Configuration

### Environment Variables

```env
# OpenAI API Key
OPENAI_API_KEY=sk-proj-xxx

# Hugging Face API Key (for BGE-M3)
HUGGINGFACE_API_KEY=hf_xxx

# PostgreSQL Connection
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mydb
DB_USER=postgres
DB_PASSWORD=xxx

# API Configuration
API_KEY=your-secret-key
ENVIRONMENT=production
ALLOWED_ORIGINS=*
```

### Model Parameters

```python
{
  "model": "gpt-4o-mini",
  "temperature": 0.7,
  "n_results_sql": 5,
  "n_results_ddl": 3,
  "n_results_documentation": 7
}
```

## 🔗 Integration

### n8n Workflow

See [N8N_INTEGRATION.md](N8N_INTEGRATION.md) for complete guide.

Example n8n HTTP Request node:
```json
{
  "method": "POST",
  "url": "https://your-app.railway.app/ask",
  "headers": {
    "Content-Type": "application/json",
    "X-API-Key": "your-secret-key"
  },
  "body": {
    "question": "{{$json.question}}"
  }
}
```

### Webhook Integration

```javascript
// Express.js example
app.post('/webhook', async (req, res) => {
  const response = await fetch('https://your-app.railway.app/ask', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'your-secret-key'
    },
    body: JSON.stringify({
      question: req.body.question
    })
  });
  
  const data = await response.json();
  res.json(data);
});
```

## 📚 Documentation

- [Configuration Parameters](CONFIG_PARAMETERS.md) - All config options explained
- [Prompt Construction](PROMPT_CONSTRUCTION.md) - How prompts are built
- [Vietnamese Optimization](PROMPT_COMPARISON.md) - Before/after comparison
- [Railway Deployment](RAILWAY_DEPLOYMENT.md) - Deploy to Railway guide
- [n8n Integration](N8N_INTEGRATION.md) - n8n workflow examples

## 🏗️ Architecture

```
┌─────────────┐
│   Client    │ (n8n, webhook, etc.)
└──────┬──────┘
       │ HTTP/REST
       ▼
┌─────────────────────────────────────┐
│      FastAPI Server                 │
│  ┌───────────────────────────────┐  │
│  │   VietnameseVanna             │  │
│  │   - Custom prompts            │  │
│  │   - Vietnamese optimization   │  │
│  └───────────┬───────────────────┘  │
│              │                       │
│  ┌───────────▼───────────┐          │
│  │   BGE-M3 Embedding    │          │
│  │   (1024 dims)         │          │
│  └───────────┬───────────┘          │
│              │                       │
│  ┌───────────▼───────────┐          │
│  │   ChromaDB Vector DB  │          │
│  │   (RAG retrieval)     │          │
│  └───────────┬───────────┘          │
│              │                       │
│  ┌───────────▼───────────┐          │
│  │   GPT-4o-mini         │          │
│  │   (SQL generation)    │          │
│  └───────────┬───────────┘          │
└──────────────┼───────────────────────┘
               │
               ▼
        ┌─────────────┐
        │  PostgreSQL │
        └─────────────┘
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Test specific file
pytest tests/test_vanna.py

# Test with coverage
pytest --cov=src tests/
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Vanna AI](https://github.com/vanna-ai/vanna) - Original framework
- [BGE-M3](https://huggingface.co/BAAI/bge-m3) - Multilingual embedding model
- [OpenAI](https://openai.com) - GPT-4o-mini model
- [Railway](https://railway.app) - Deployment platform

## 📧 Contact

- GitHub: [@kimhoang0511](https://github.com/kimhoang0511)
- Repository: [vanna](https://github.com/kimhoang0511/vanna)

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

---

Made with ❤️ for Vietnamese developers
