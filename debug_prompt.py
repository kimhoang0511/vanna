"""
Ví dụ debug và customize Prompt Construction trong Vanna
"""

import os
import json
from dotenv import load_dotenv
from vanna.chromadb import ChromaDB_VectorStore
from vanna.openai import OpenAI_Chat

# Load from .env file
load_dotenv()


class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)


print("=" * 70)
print("DEBUG PROMPT CONSTRUCTION")
print("=" * 70)

# ============================================================================
# 1. Xem cấu trúc prompt cơ bản
# ============================================================================
print("\n📝 1. CẤU TRÚC PROMPT CƠ BẢN")
print("-" * 70)

vn = MyVanna(config={
    'client': 'in-memory',
    'dialect': 'PostgreSQL',
    'max_tokens': 14000
})

# Sample data
ddl_list = [
    """CREATE TABLE public.sale (
    id INTEGER PRIMARY KEY,
    name TEXT,
    date DATE,
    sales MONEY
);"""
]

doc_list = [
    """Table 'sale' chứa dữ liệu bán hàng với:
- id: Mã giao dịch
- name: Tên sản phẩm hoặc khách hàng
- date: Ngày giao dịch
- sales: Doanh thu (kiểu money)

Để tính tổng doanh thu, dùng SUM(sales::numeric)"""
]

question_sql_list = [
    {
        "question": "Tổng doanh thu là bao nhiêu?",
        "sql": "SELECT SUM(sales::numeric) as total_revenue FROM public.sale"
    }
]

# Build prompt
prompt = vn.get_sql_prompt(
    initial_prompt=None,  # ← Will use default
    question="Có bao nhiêu giao dịch?",
    question_sql_list=question_sql_list,
    ddl_list=ddl_list,
    doc_list=doc_list
)

print("Prompt structure:")
for i, msg in enumerate(prompt):
    print(f"\n{i+1}. {msg['role'].upper()}:")
    content_preview = msg['content'][:200] + "..." if len(msg['content']) > 200 else msg['content']
    print(f"   {content_preview}")

print(f"\nTotal messages: {len(prompt)}")


# ============================================================================
# 2. Xem token count
# ============================================================================
print("\n\n📊 2. TOKEN COUNT MANAGEMENT")
print("-" * 70)

prompt_str = json.dumps(prompt, ensure_ascii=False)
token_count = vn.str_to_approx_token_count(prompt_str)
print(f"Estimated tokens: {token_count:.0f}")
print(f"Max tokens limit: {vn.max_tokens}")
print(f"Percentage used: {(token_count/vn.max_tokens)*100:.1f}%")


# ============================================================================
# 3. Test add_ddl_to_prompt
# ============================================================================
print("\n\n🗂️  3. TEST ADD_DDL_TO_PROMPT")
print("-" * 70)

initial = "You are a SQL expert."
result = vn.add_ddl_to_prompt(initial, ddl_list, max_tokens=14000)

print("Result:")
print(result)


# ============================================================================
# 4. Test add_documentation_to_prompt
# ============================================================================
print("\n\n📚 4. TEST ADD_DOCUMENTATION_TO_PROMPT")
print("-" * 70)

initial = "You are a SQL expert.\n===Tables\nCREATE TABLE sale(...);"
result = vn.add_documentation_to_prompt(initial, doc_list, max_tokens=14000)

print("Result:")
print(result[-300:])  # Last 300 chars


# ============================================================================
# 5. Custom Initial Prompt
# ============================================================================
print("\n\n✨ 5. CUSTOM INITIAL PROMPT")
print("-" * 70)

class MyCustomVanna(MyVanna):
    """Custom Vanna với Vietnamese-optimized prompt"""
    
    def get_sql_prompt_prefix(self, **kwargs):
        return """Bạn là chuyên gia PostgreSQL. 
Hãy tạo câu SQL để trả lời câu hỏi dựa trên context được cung cấp.
Chỉ trả về SQL, không giải thích."""

custom_vn = MyCustomVanna(config={
    'client': 'in-memory',
    'dialect': 'PostgreSQL'
})

# Build với custom prefix
custom_prompt = custom_vn.get_sql_prompt(
    initial_prompt=custom_vn.get_sql_prompt_prefix(),
    question="Tổng doanh thu?",
    question_sql_list=[],
    ddl_list=ddl_list,
    doc_list=[]
)

print("Custom system message:")
print(custom_prompt[0]['content'][:200] + "...")


# ============================================================================
# 6. Test với nhiều examples (Few-shot learning)
# ============================================================================
print("\n\n🎯 6. FEW-SHOT LEARNING (Multiple Examples)")
print("-" * 70)

many_examples = [
    {
        "question": "Tổng doanh thu là bao nhiêu?",
        "sql": "SELECT SUM(sales::numeric) FROM public.sale"
    },
    {
        "question": "Top 5 sản phẩm bán chạy?",
        "sql": "SELECT name, SUM(sales::numeric) as total FROM public.sale GROUP BY name ORDER BY total DESC LIMIT 5"
    },
    {
        "question": "Doanh thu tháng 10?",
        "sql": "SELECT SUM(sales::numeric) FROM public.sale WHERE EXTRACT(MONTH FROM date) = 10"
    }
]

prompt_many = vn.get_sql_prompt(
    initial_prompt=None,
    question="Doanh thu quý 1?",
    question_sql_list=many_examples,
    ddl_list=ddl_list,
    doc_list=doc_list
)

print(f"Total messages with 3 examples: {len(prompt_many)}")
print("\nMessage structure:")
for i, msg in enumerate(prompt_many):
    print(f"{i+1}. {msg['role']}: {msg['content'][:50]}...")


# ============================================================================
# 7. Static Documentation
# ============================================================================
print("\n\n📌 7. STATIC DOCUMENTATION")
print("-" * 70)

vn.static_documentation = """
IMPORTANT DATABASE RULES:
- Always use schema prefix: public.table_name
- Money calculations require ::numeric cast
- Date format: YYYY-MM-DD
"""

prompt_static = vn.get_sql_prompt(
    initial_prompt=None,
    question="Test",
    question_sql_list=[],
    ddl_list=[],
    doc_list=["Dynamic doc: Use indexes for better performance"]
)

system_msg = prompt_static[0]['content']
if "IMPORTANT DATABASE RULES" in system_msg:
    print("✅ Static documentation added!")
    print("\nStatic doc location in prompt:")
    idx = system_msg.find("IMPORTANT DATABASE RULES")
    print(system_msg[idx:idx+150] + "...")


# ============================================================================
# 8. Full prompt JSON export
# ============================================================================
print("\n\n💾 8. EXPORT FULL PROMPT AS JSON")
print("-" * 70)

output_file = "sample_prompt.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(prompt, f, indent=2, ensure_ascii=False)

print(f"✅ Saved to {output_file}")
print(f"File size: {os.path.getsize(output_file)} bytes")


# ============================================================================
# Summary
# ============================================================================
print("\n\n" + "=" * 70)
print("SUMMARY - KEY FINDINGS")
print("=" * 70)
print("""
1. Prompt Structure:
   • System message: Chứa DDL + Documentation + Guidelines
   • Few-shot examples: User-Assistant pairs
   • Actual question: User message cuối cùng

2. Token Management:
   • Default max_tokens: 14000
   • Formula: tokens ≈ string_length / 4
   • Priority: DDL > Documentation > Examples

3. Customization Points:
   • get_sql_prompt_prefix() - Custom initial prompt
   • dialect - Ảnh hưởng "You are a {dialect} expert"
   • static_documentation - Thêm vào mọi prompt
   • max_tokens - Giới hạn context length

4. Files to Check:
   • src/vanna/base/base.py - Main logic
     - get_sql_prompt() (line 569)
     - add_ddl_to_prompt() (line 518)
     - add_documentation_to_prompt() (line 534)
     - generate_sql() (line 93) - Orchestrator
""")
print("=" * 70)
