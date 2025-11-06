"""
Custom Cache Implementation cho VannaFlaskApp
Sửa lỗi: Cache by question hash thay vì random UUID
"""

import hashlib
import json
from vanna.flask import Cache


class QuestionHashCache(Cache):
    """
    Cache implementation sử dụng hash của câu hỏi làm ID
    Giúp cache hoạt động giữa các request với cùng câu hỏi
    """
    
    def __init__(self):
        self.cache = {}
    
    def generate_id(self, question=None, *args, **kwargs):
        """
        Generate deterministic ID dựa trên question
        Cùng question → Cùng ID → Dùng lại cache
        """
        if question:
            # Hash câu hỏi để tạo ID deterministic
            question_normalized = question.lower().strip()
            hash_object = hashlib.md5(question_normalized.encode())
            return hash_object.hexdigest()
        else:
            # Fallback to UUID nếu không có question
            import uuid
            return str(uuid.uuid4())
    
    def set(self, id, field, value):
        """Set giá trị vào cache"""
        if id not in self.cache:
            self.cache[id] = {}
        self.cache[id][field] = value
    
    def set_multiple(self, id, fields_dict):
        """Set nhiều fields cùng lúc (efficient)"""
        if id not in self.cache:
            self.cache[id] = {}
        self.cache[id].update(fields_dict)
    
    def get(self, id, field):
        """Lấy giá trị từ cache"""
        if id not in self.cache:
            return None
        if field not in self.cache[id]:
            return None
        return self.cache[id][field]
    
    def get_all(self, field_list) -> list:
        """Lấy tất cả entries từ cache"""
        return [
            {"id": id, **{field: self.get(id=id, field=field) for field in field_list}}
            for id in self.cache
        ]
    
    def delete(self, id):
        """Xóa entry khỏi cache"""
        if id in self.cache:
            del self.cache[id]
    
    def clear(self):
        """Clear toàn bộ cache"""
        self.cache.clear()
    
    def size(self):
        """Lấy số lượng entries trong cache"""
        return len(self.cache)
    
    def get_stats(self):
        """Get cache statistics"""
        return {
            "total_entries": len(self.cache),
            "cached_questions": [
                self.cache[id].get("question", "N/A") 
                for id in self.cache
            ]
        }


class PersistentQuestionCache(QuestionHashCache):
    """
    Version nâng cao: Persist cache ra file/database
    Giữ cache giữa các lần restart
    """
    
    def __init__(self, cache_file="vanna_cache.json"):
        super().__init__()
        self.cache_file = cache_file
        self._load_cache()
    
    def _load_cache(self):
        """Load cache từ file khi khởi động"""
        try:
            import os
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                print(f"✅ Loaded {len(self.cache)} cache entries from {self.cache_file}")
        except Exception as e:
            print(f"⚠️  Could not load cache from file: {e}")
            self.cache = {}
    
    def _save_cache(self):
        """Save cache ra file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                # Convert DataFrame và các object phức tạp
                serializable_cache = {}
                for id, fields in self.cache.items():
                    serializable_cache[id] = {}
                    for field, value in fields.items():
                        try:
                            # Try serialize để test
                            json.dumps(value)
                            serializable_cache[id][field] = value
                        except (TypeError, ValueError):
                            # Skip non-serializable objects (như DataFrame)
                            serializable_cache[id][field] = str(type(value))
                
                json.dump(serializable_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save cache to file: {e}")
    
    def set(self, id, field, value):
        """Set và save"""
        super().set(id, field, value)
        self._save_cache()
    
    def set_multiple(self, id, fields_dict):
        """Set nhiều fields và save 1 lần duy nhất (efficient)"""
        super().set_multiple(id, fields_dict)
        self._save_cache()
    
    def delete(self, id):
        """Delete và save"""
        super().delete(id)
        self._save_cache()
    
    def clear(self):
        """Clear và save"""
        super().clear()
        self._save_cache()


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("🧪 Testing QuestionHashCache")
    print("=" * 70)
    
    # Test 1: Deterministic ID generation
    cache = QuestionHashCache()
    
    q1 = "Top 10 khách hàng có doanh thu cao nhất"
    q2 = "Top 10 khách hàng có doanh thu cao nhất"  # Same question
    q3 = "Top 10 customers with highest revenue"  # Different question
    
    id1 = cache.generate_id(question=q1)
    id2 = cache.generate_id(question=q2)
    id3 = cache.generate_id(question=q3)
    
    print(f"\nQuestion 1: {q1}")
    print(f"ID 1: {id1}")
    
    print(f"\nQuestion 2 (same): {q2}")
    print(f"ID 2: {id2}")
    
    print(f"\nQuestion 3 (different): {q3}")
    print(f"ID 3: {id3}")
    
    if id1 == id2:
        print("\n✅ SUCCESS: Same question = Same ID")
    else:
        print("\n❌ FAILED: Same question but different ID")
    
    if id1 != id3:
        print("✅ SUCCESS: Different question = Different ID")
    else:
        print("❌ FAILED: Different question but same ID")
    
    # Test 2: Cache functionality
    print("\n" + "=" * 70)
    print("Testing Cache Set/Get")
    print("=" * 70)
    
    cache.set(id1, "question", q1)
    cache.set(id1, "sql", "SELECT * FROM customers ORDER BY revenue DESC LIMIT 10")
    
    retrieved_sql = cache.get(id1, "sql")
    print(f"\nCached SQL: {retrieved_sql}")
    
    if retrieved_sql:
        print("✅ Cache working!")
    else:
        print("❌ Cache failed!")
    
    # Test 3: Persistent cache
    print("\n" + "=" * 70)
    print("Testing PersistentQuestionCache")
    print("=" * 70)
    
    pcache = PersistentQuestionCache(cache_file="test_cache.json")
    pcache.set(id1, "question", q1)
    pcache.set(id1, "sql", "SELECT * FROM customers")
    
    print(f"\n✅ Cache saved to test_cache.json")
    print(f"Stats: {pcache.get_stats()}")
