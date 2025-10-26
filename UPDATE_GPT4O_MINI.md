# Cập nhật sử dụng GPT-4o-mini

## Thay đổi

Đã cập nhật `demo_bge_m3_vanna.py` để sử dụng **GPT-4o-mini** thay vì GPT-3.5-turbo.

## Configuration

```python
vn = MyVanna_BGE(config={
    'api_key': os.environ['OPENAI_API_KEY'],
    'model': 'gpt-4o-mini',  # ← Updated!
    'embedding_function': bge_m3_ef
})
```

## Stack hiện tại

- **LLM**: GPT-4o-mini (OpenAI)
- **Embedding**: BAAI/bge-m3 (1024 dims, Hugging Face)
- **Vector Store**: ChromaDB
- **Database**: PostgreSQL

## Ưu điểm GPT-4o-mini

✅ Chất lượng SQL tốt hơn GPT-3.5-turbo  
✅ Hiểu ngữ cảnh tiếng Việt tốt hơn  
✅ Chi phí thấp hơn GPT-4  
✅ Tốc độ nhanh (~2x so với GPT-4)

## Test Results

```bash
HUGGINGFACE_API_KEY=hf_xxx python3 demo_bge_m3_vanna.py
```

**Câu hỏi 1:** "Có bao nhiêu giao dịch trong bảng sale?"
```sql
SELECT COUNT(*) as total_transactions FROM public.sale
```
✅ Kết quả: 4 giao dịch

**Câu hỏi 2:** "Tổng doanh thu của tất cả sản phẩm?"
```sql
SELECT SUM(sales::numeric) as total_revenue FROM public.sale
```
✅ Kết quả: $163,000.00

**Câu hỏi 3:** "Top 3 sản phẩm bán chạy nhất?"
⚠️ GPT-4o-mini muốn xem data trước (intermediate SQL) vì "bán chạy" có thể hiểu là:
- Số lượng giao dịch (COUNT)
- Tổng doanh thu (SUM)

→ Thông minh hơn GPT-3.5-turbo trong việc xử lý ambiguous questions!

## Chạy demo

```bash
export HUGGINGFACE_API_KEY="your_hf_key"
python3 demo_bge_m3_vanna.py
```

## So sánh Models

| Model | Context | Cost/1M tokens | Chất lượng |
|-------|---------|---------------|------------|
| GPT-3.5-turbo | 16K | $0.50 / $1.50 | ⭐⭐⭐ |
| **GPT-4o-mini** ✨ | 128K | **$0.15 / $0.60** | ⭐⭐⭐⭐ |
| GPT-4o | 128K | $2.50 / $10.00 | ⭐⭐⭐⭐⭐ |

→ **GPT-4o-mini**: Best balance giữa cost và quality!
