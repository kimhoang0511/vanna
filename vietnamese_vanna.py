"""
Custom Vanna class với Prompt Construction tối ưu cho tiếng Việt
"""

import os
from vanna.chromadb import ChromaDB_VectorStore
from vanna.openai import OpenAI_Chat


class VietnameseVanna(ChromaDB_VectorStore, OpenAI_Chat):
    """
    Custom Vanna class với prompt được tối ưu cho documentation tiếng Việt
    """
    
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)
    
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
        """
        
        # 1. Build initial prompt với Vietnamese instruction
        if initial_prompt is None:
            initial_prompt = f"""You are a {self.dialect} expert who understands both English and Vietnamese.
Please help to generate a SQL query to answer the question.

IMPORTANT NOTES:
• The documentation and context may be written in Vietnamese
• Question may be in Vietnamese
• Please understand Vietnamese context and generate correct SQL
• Your SQL output should use standard English SQL syntax
• Only respond with SQL query, no explanations

Your response should ONLY be based on the given context and follow the response guidelines and format instructions.
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
            "===Response Guidelines \n"
            "1. Understand Vietnamese documentation and context if provided \n"
            "2. If the provided context is sufficient, generate a valid SQL query without explanations \n"
            "3. If context requires knowledge of specific column values, generate intermediate SQL with comment 'intermediate_sql' \n"
            "4. If context is insufficient, explain why in English \n"
            "5. Use the most relevant table(s) \n"
            "6. If question was asked before, repeat the exact answer \n"
            f"7. Ensure output SQL is {self.dialect}-compliant and executable \n"
            "8. SQL syntax must be in English (SELECT, FROM, WHERE, etc.) even if documentation is Vietnamese \n"
        )
        
        # 5. Build message log với examples
        message_log = [self.system_message(initial_prompt)]
        
        for example in question_sql_list:
            if example is not None and "question" in example and "sql" in example:
                message_log.append(self.user_message(example["question"]))
                message_log.append(self.assistant_message(example["sql"]))
        
        message_log.append(self.user_message(question))
        
        return message_log


class BilingualVanna(ChromaDB_VectorStore, OpenAI_Chat):
    """
    Vanna class với dual-language support (English + Vietnamese)
    Tự động detect ngôn ngữ và adjust prompt
    """
    
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)
        
        # Custom instruction cho Vietnamese
        self.vietnamese_instruction = """
📌 HƯỚNG DẪN CHO TÀI LIỆU TIẾNG VIỆT:
- Tài liệu có thể được viết bằng tiếng Việt
- Hãy hiểu đúng ý nghĩa của tài liệu tiếng Việt
- Tuy nhiên, SQL query phải dùng cú pháp tiếng Anh chuẩn
- Ví dụ: "Tổng doanh thu" → SELECT SUM(sales) FROM ...
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
        """
        
        # Detect Vietnamese content
        has_vietnamese = self._detect_vietnamese(
            doc_list + [question] + [ex.get('question', '') for ex in question_sql_list if ex]
        )
        
        # Build initial prompt
        if initial_prompt is None:
            initial_prompt = f"You are a {self.dialect} expert. "
            initial_prompt += "Please help to generate a SQL query to answer the question. "
            initial_prompt += "Your response should ONLY be based on the given context and follow the response guidelines and format instructions. "
        
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
        guidelines = (
            "===Response Guidelines \n"
            "1. If the provided context is sufficient, please generate a valid SQL query without any explanations for the question. \n"
        )
        
        if has_vietnamese:
            guidelines += "2. Documentation may be in Vietnamese - please understand it correctly. SQL output must be in standard English syntax. \n"
            guidelines += "3. If the provided context is almost sufficient but requires knowledge of a specific string in a particular column, please generate an intermediate SQL query to find the distinct strings in that column. Prepend the query with a comment saying intermediate_sql \n"
        else:
            guidelines += "2. If the provided context is almost sufficient but requires knowledge of a specific string in a particular column, please generate an intermediate SQL query to find the distinct strings in that column. Prepend the query with a comment saying intermediate_sql \n"
        
        guidelines += (
            "3. If the provided context is insufficient, please explain why it can't be generated. \n"
            "4. Please use the most relevant table(s). \n"
            "5. If the question has been asked and answered before, please repeat the answer exactly as it was given before. \n"
            f"6. Ensure that the output SQL is {self.dialect}-compliant and executable, and free of syntax errors. \n"
        )
        
        initial_prompt += guidelines
        
        # Build message log
        message_log = [self.system_message(initial_prompt)]
        
        for example in question_sql_list:
            if example is not None and "question" in example and "sql" in example:
                message_log.append(self.user_message(example["question"]))
                message_log.append(self.assistant_message(example["sql"]))
        
        message_log.append(self.user_message(question))
        
        return message_log


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("VIETNAMESE-OPTIMIZED VANNA")
    print("=" * 70)
    
    # Option 1: VietnameseVanna (Always Vietnamese-aware)
    print("\n1️⃣ VietnameseVanna - Always Vietnamese-aware:")
    vn1 = VietnameseVanna(config={
        'client': 'in-memory',
        'dialect': 'PostgreSQL'
    })
    print("   ✅ Best for: Projects with mostly Vietnamese documentation")
    
    # Option 2: BilingualVanna (Auto-detect)
    print("\n2️⃣ BilingualVanna - Auto-detect language:")
    vn2 = BilingualVanna(config={
        'client': 'in-memory',
        'dialect': 'PostgreSQL'
    })
    print("   ✅ Best for: Mixed English/Vietnamese projects")
    
    # Test Vietnamese detection
    doc_vietnamese = ["Table sale chứa dữ liệu bán hàng"]
    doc_english = ["Table sale contains sales data"]
    
    print("\n3️⃣ Testing Vietnamese detection:")
    print(f"   Vietnamese doc: {vn2._detect_vietnamese(doc_vietnamese)}")
    print(f"   English doc: {vn2._detect_vietnamese(doc_english)}")
    
    print("\n" + "=" * 70)
    print("Use these classes in your production code!")
    print("=" * 70)
