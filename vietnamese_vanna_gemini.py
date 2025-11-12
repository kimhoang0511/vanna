"""
Custom Vanna class sử dụng Google Gemini thay vì OpenAI
Tối ưu cho tiếng Việt với BGE-M3 embeddings

Tại sao sử dụng Gemini:
- FREE API với 15 requests/minute (đủ dùng cho development)
- Hiểu tiếng Việt rất tốt (được train trên nhiều ngôn ngữ)
- Gemini 1.5 Pro có context window 2M tokens (lớn hơn nhiều so với OpenAI)
- Phản hồi nhanh và chính xác

So sánh:
- OpenAI GPT-4: $0.03/1K tokens (đắt, nhưng rất tốt)
- Gemini 1.5 Pro: FREE (15 req/min) hoặc $0.00025/1K tokens
- Gemini 1.5 Flash: FREE (15 req/min) hoặc $0.000125/1K tokens
"""

import os
from vanna.chromadb import ChromaDB_VectorStore
from vanna.google import GoogleGeminiChat


class VietnameseVannaGemini(ChromaDB_VectorStore, GoogleGeminiChat):
    """
    Custom Vanna class với:
    - Google Gemini LLM (thay vì OpenAI)
    - BGE-M3 embeddings cho tiếng Việt
    - Prompt được tối ưu cho documentation tiếng Việt
    """
    
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        GoogleGeminiChat.__init__(self, config=config)
    
    def get_sql_prompt(
        self,
        initial_prompt: str,
        question: str,
        question_sql_list: list,
        ddl_list: list,
        doc_list: list,
        **kwargs,
    ):
        """
        Override để thêm Vietnamese-specific instructions
        Prompt này được tối ưu cho Gemini
        """
        
        # 1. Build initial prompt với Vietnamese instruction
        if initial_prompt is None:
            initial_prompt = f"""You are a {self.dialect} expert with excellent Vietnamese language understanding.
Your task is to generate SQL queries based on user questions, which may be in Vietnamese.

IMPORTANT GUIDELINES:
• Documentation and context may be written in Vietnamese - understand them correctly
• User questions may be in Vietnamese - interpret them accurately
• Your SQL output MUST use standard English SQL syntax (SELECT, FROM, WHERE, etc.)
• Only respond with the SQL query, no explanations or markdown formatting
• Ensure the SQL is {self.dialect}-compliant and executable

Your response should ONLY be based on the given context and follow the response guidelines.
"""
        
        # 2. Add DDL
        initial_prompt = self.add_ddl_to_prompt(
            initial_prompt, ddl_list, max_tokens=self.max_tokens
        )
        
        # 3. Add documentation với Vietnamese note
        if self.static_documentation != "":
            doc_list.append(self.static_documentation)
        
        if len(doc_list) > 0:
            initial_prompt += "\n===Additional Context (May include Vietnamese documentation)\n\n"
            
            for documentation in doc_list:
                if (
                    self.str_to_approx_token_count(initial_prompt)
                    + self.str_to_approx_token_count(documentation)
                    < self.max_tokens
                ):
                    initial_prompt += f"{documentation}\n\n"
        
        # 4. Add Response Guidelines
        initial_prompt += (
            "===Response Guidelines\n"
            "1. Understand Vietnamese documentation and context if provided\n"
            "2. If the provided context is sufficient, generate a valid SQL query without explanations\n"
            "3. If context requires knowledge of specific column values, generate intermediate SQL with comment 'intermediate_sql'\n"
            "4. If context is insufficient, explain why in English\n"
            "5. Use the most relevant table(s)\n"
            "6. If question was asked before, repeat the exact answer\n"
            f"7. Ensure output SQL is {self.dialect}-compliant and executable\n"
            "8. SQL syntax must be in English even if documentation is Vietnamese\n"
            "9. Do not wrap SQL in markdown code blocks - return plain SQL only\n"
        )
        
        # 5. Build message log với examples
        # Note: Gemini xử lý message format khác với OpenAI
        # Gemini submit_prompt() nhận một string đơn, không phải list of messages
        prompt_text = initial_prompt + "\n\n"
        
        # Add examples
        if question_sql_list:
            prompt_text += "===Previous Question-SQL Examples\n\n"
            for example in question_sql_list:
                if example is not None and "question" in example and "sql" in example:
                    prompt_text += f"Question: {example['question']}\n"
                    prompt_text += f"SQL: {example['sql']}\n\n"
        
        # Add current question
        prompt_text += f"===Current Question\n{question}\n\n"
        prompt_text += "===Your SQL Response (plain SQL only, no markdown):\n"
        
        return prompt_text


class BilingualVannaGemini(ChromaDB_VectorStore, GoogleGeminiChat):
    """
    Vanna class với dual-language support (English + Vietnamese)
    Sử dụng Google Gemini
    Tự động detect ngôn ngữ và adjust prompt
    """
    
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        GoogleGeminiChat.__init__(self, config=config)
        
        # Custom instruction cho Vietnamese
        self.vietnamese_instruction = """
📌 VIETNAMESE DOCUMENTATION DETECTED:
- Documentation is written in Vietnamese - please understand it correctly
- SQL queries must still use standard English syntax
- Example: "Tổng doanh thu" → SELECT SUM(sales) FROM ...
"""
    
    def _detect_vietnamese(self, text_list: list) -> bool:
        """
        Detect nếu có Vietnamese content trong list
        """
        vietnamese_chars = ['ă', 'â', 'đ', 'ê', 'ô', 'ơ', 'ư', 'á', 'à', 'ả', 'ã', 'ạ']
        
        combined_text = " ".join([str(t) for t in text_list if t is not None]).lower()
        
        for char in vietnamese_chars:
            if char in combined_text:
                return True
        return False
    
    def get_sql_prompt(
        self,
        initial_prompt: str,
        question: str,
        question_sql_list: list,
        ddl_list: list,
        doc_list: list,
        **kwargs,
    ):
        """
        Smart prompt construction với auto Vietnamese detection
        Tối ưu cho Gemini
        """
        
        # Detect Vietnamese content
        has_vietnamese = self._detect_vietnamese(
            doc_list + [question] + [ex.get('question', '') for ex in question_sql_list if ex]
        )
        
        # Build initial prompt
        if initial_prompt is None:
            initial_prompt = f"You are a {self.dialect} expert. "
            initial_prompt += "Please help to generate a SQL query to answer the question. "
            initial_prompt += "Your response should ONLY be based on the given context and follow the response guidelines. "
        
        # Add Vietnamese instruction nếu detect được Vietnamese
        if has_vietnamese:
            initial_prompt += "\n" + self.vietnamese_instruction + "\n"
        
        # Standard processing
        initial_prompt = self.add_ddl_to_prompt(
            initial_prompt, ddl_list, max_tokens=self.max_tokens
        )
        
        if self.static_documentation != "":
            doc_list.append(self.static_documentation)
        
        initial_prompt = self.add_documentation_to_prompt(
            initial_prompt, doc_list, max_tokens=self.max_tokens
        )
        
        # Response guidelines với Vietnamese note
        guidelines = "===Response Guidelines\n"
        guidelines += "1. If the provided context is sufficient, generate a valid SQL query without explanations.\n"
        
        if has_vietnamese:
            guidelines += "2. Documentation may be in Vietnamese - please understand it correctly. SQL output must be in standard English syntax.\n"
        
        guidelines += (
            "3. If context requires knowledge of specific column values, generate intermediate SQL with comment 'intermediate_sql'.\n"
            "4. If the provided context is insufficient, explain why it can't be generated.\n"
            "5. Please use the most relevant table(s).\n"
            "6. If the question has been asked before, repeat the answer exactly.\n"
            f"7. Ensure that the output SQL is {self.dialect}-compliant and executable.\n"
            "8. Do not wrap SQL in markdown code blocks - return plain SQL only.\n"
        )
        
        initial_prompt += guidelines
        
        # Build prompt text (Gemini doesn't use message format like OpenAI)
        prompt_text = initial_prompt + "\n\n"
        
        # Add examples
        if question_sql_list:
            prompt_text += "===Previous Question-SQL Examples\n\n"
            for example in question_sql_list:
                if example is not None and "question" in example and "sql" in example:
                    prompt_text += f"Question: {example['question']}\n"
                    prompt_text += f"SQL: {example['sql']}\n\n"
        
        # Add current question
        prompt_text += f"===Current Question\n{question}\n\n"
        prompt_text += "===Your SQL Response:\n"
        
        return prompt_text


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("VIETNAMESE-OPTIMIZED VANNA WITH GOOGLE GEMINI")
    print("=" * 70)
    
    print("\n✨ LỢI ÍCH CỦA GEMINI:")
    print("   • FREE API (15 requests/minute)")
    print("   • Hiểu tiếng Việt tốt")
    print("   • Context window lớn (2M tokens)")
    print("   • Nhanh và chính xác")
    
    print("\n📦 MODELS:")
    print("   • gemini-2.0-flash-exp: Mới nhất (experimental), nhanh nhất")
    print("   • gemini-1.5-pro: Ổn định nhất, context 2M tokens")
    print("   • gemini-1.5-flash: Nhanh, context 1M tokens")
    print("   • gemini-pro: Model cũ (deprecated)")
    
    # Option 1: VietnameseVannaGemini (Always Vietnamese-aware)
    print("\n1️⃣ VietnameseVannaGemini - Always Vietnamese-aware:")
    print("   ✅ Best for: Projects with mostly Vietnamese documentation")
    print("   Usage:")
    print("""
    from vietnamese_vanna_gemini import VietnameseVannaGemini
    from bge_m3_embedding import BGE_M3_EmbeddingFunction
    
    bge_m3_ef = BGE_M3_EmbeddingFunction(api_key='hf_xxx')
    
    vn = VietnameseVannaGemini(config={
        'api_key': 'your-google-api-key',
        'model_name': 'gemini-2.0-flash-exp',  # hoặc 'gemini-1.5-pro', 'gemini-1.5-flash'
        'temperature': 0.7,
        'embedding_function': bge_m3_ef
    })
    """)
    
    # Option 2: BilingualVannaGemini (Auto-detect)
    print("\n2️⃣ BilingualVannaGemini - Auto-detect language:")
    print("   ✅ Best for: Mixed English/Vietnamese projects")
    
    print("\n" + "=" * 70)
    print("🔑 Get your FREE Gemini API Key:")
    print("   https://makersuite.google.com/app/apikey")
    print("=" * 70)
