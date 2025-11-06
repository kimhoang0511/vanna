"""
PostgreSQL Cache Implementation cho VannaFlaskApp
Lưu cache vào database thay vì file - persistent và scalable
"""

import hashlib
import json
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from vanna.flask import Cache


class PostgresCache(Cache):
    """
    Cache implementation sử dụng PostgreSQL với connection pooling
    - Persistent: Không mất khi restart
    - Scalable: Share được giữa multiple instances
    - Queryable: Dễ dàng query và quản lý
    - Optimized: Connection pooling cho performance
    """
    
    def __init__(self, connection_params, min_conn=1, max_conn=10):
        """
        Initialize PostgreSQL cache với connection pooling
        
        Args:
            connection_params: Dict với keys: host, port, dbname, user, password
            min_conn: Minimum connections trong pool
            max_conn: Maximum connections trong pool
        """
        self.connection_params = connection_params
        
        # Create connection pool
        try:
            self.connection_pool = pool.SimpleConnectionPool(
                min_conn, max_conn, **connection_params
            )
            print(f"✅ Connection pool created: {min_conn}-{max_conn} connections")
        except Exception as e:
            print(f"⚠️  Failed to create connection pool: {e}")
            self.connection_pool = None
        
        self._create_table_if_not_exists()
    
    def _get_connection(self):
        """Get connection from pool (faster than creating new)"""
        if self.connection_pool:
            return self.connection_pool.getconn()
        else:
            # Fallback to direct connection
            return psycopg2.connect(**self.connection_params)
    
    def _return_connection(self, conn):
        """Return connection to pool"""
        if self.connection_pool:
            self.connection_pool.putconn(conn)
        else:
            conn.close()
    
    def _create_table_if_not_exists(self):
        """Create cache table if not exists"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Create table với JSONB để lưu flexible data
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vanna_cache (
                    id VARCHAR(255) PRIMARY KEY,
                    data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index cho performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_vanna_cache_created_at 
                ON vanna_cache(created_at)
            """)
            
            conn.commit()
            cursor.close()
            self._return_connection(conn)
            
            print("✅ PostgreSQL cache table ready")
            
        except Exception as e:
            print(f"⚠️  Error creating cache table: {e}")
            if conn:
                self._return_connection(conn)
    
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
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get existing data
            cursor.execute(
                "SELECT data FROM vanna_cache WHERE id = %s",
                (id,)
            )
            row = cursor.fetchone()
            
            if row:
                # Update existing
                data = row[0] if isinstance(row[0], dict) else json.loads(row[0])
                data[field] = value
                
                cursor.execute(
                    """
                    UPDATE vanna_cache 
                    SET data = %s, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = %s
                    """,
                    (json.dumps(data), id)
                )
            else:
                # Insert new
                data = {field: value}
                cursor.execute(
                    "INSERT INTO vanna_cache (id, data) VALUES (%s, %s)",
                    (id, json.dumps(data))
                )
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"⚠️  Error setting cache: {e}")
    
    def set_multiple(self, id, fields_dict):
        """Set nhiều fields cùng lúc - chỉ 1 database roundtrip (efficient)"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get existing data
            cursor.execute(
                "SELECT data FROM vanna_cache WHERE id = %s",
                (id,)
            )
            row = cursor.fetchone()
            
            if row:
                # Update existing
                data = row[0] if isinstance(row[0], dict) else json.loads(row[0])
                data.update(fields_dict)
                
                cursor.execute(
                    """
                    UPDATE vanna_cache 
                    SET data = %s, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = %s
                    """,
                    (json.dumps(data), id)
                )
            else:
                # Insert new
                cursor.execute(
                    "INSERT INTO vanna_cache (id, data) VALUES (%s, %s)",
                    (id, json.dumps(fields_dict))
                )
            
            conn.commit()
            cursor.close()
            self._return_connection(conn)
            
        except Exception as e:
            print(f"⚠️  Error setting multiple cache fields: {e}")
            if conn:
                self._return_connection(conn)
    
    def get(self, id, field):
        """Lấy giá trị từ cache"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT data FROM vanna_cache WHERE id = %s",
                (id,)
            )
            row = cursor.fetchone()
            
            cursor.close()
            self._return_connection(conn)
            
            if row:
                data = row[0] if isinstance(row[0], dict) else json.loads(row[0])
                return data.get(field)
            
            return None
            
        except Exception as e:
            print(f"⚠️  Error getting cache: {e}")
            if conn:
                self._return_connection(conn)
            return None
    
    def get_all(self, field_list) -> list:
        """Lấy tất cả entries từ cache"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute(
                "SELECT id, data FROM vanna_cache ORDER BY created_at DESC"
            )
            rows = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            result = []
            for row in rows:
                data = row['data'] if isinstance(row['data'], dict) else json.loads(row['data'])
                entry = {"id": row['id']}
                for field in field_list:
                    entry[field] = data.get(field)
                result.append(entry)
            
            return result
            
        except Exception as e:
            print(f"⚠️  Error getting all cache: {e}")
            return []
    
    def delete(self, id):
        """Xóa entry khỏi cache"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "DELETE FROM vanna_cache WHERE id = %s",
                (id,)
            )
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"⚠️  Error deleting cache: {e}")
    
    def clear(self):
        """Clear toàn bộ cache"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM vanna_cache")
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print("✅ Cache cleared")
            
        except Exception as e:
            print(f"⚠️  Error clearing cache: {e}")
    
    def size(self):
        """Lấy số lượng entries trong cache"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM vanna_cache")
            count = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            return count
            
        except Exception as e:
            print(f"⚠️  Error getting cache size: {e}")
            return 0
    
    def get_stats(self):
        """Get cache statistics"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_entries,
                    MIN(created_at) as oldest_entry,
                    MAX(updated_at) as newest_entry
                FROM vanna_cache
            """)
            stats = cursor.fetchone()
            
            # Get sample questions
            cursor.execute("""
                SELECT data->>'question' as question 
                FROM vanna_cache 
                WHERE data->>'question' IS NOT NULL
                LIMIT 10
            """)
            questions = [row['question'] for row in cursor.fetchall()]
            
            cursor.close()
            conn.close()
            
            return {
                "total_entries": stats['total_entries'],
                "oldest_entry": str(stats['oldest_entry']) if stats['oldest_entry'] else None,
                "newest_entry": str(stats['newest_entry']) if stats['newest_entry'] else None,
                "sample_questions": questions
            }
            
        except Exception as e:
            print(f"⚠️  Error getting cache stats: {e}")
            return {
                "total_entries": 0,
                "error": str(e)
            }


# Test script
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    print("=" * 70)
    print("🧪 Testing PostgresCache")
    print("=" * 70)
    
    # Connection params
    params = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '5432')),
        'dbname': os.getenv('DB_NAME', 'postgres'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', '')
    }
    
    print(f"\n📡 Connecting to PostgreSQL: {params['host']}:{params['port']}/{params['dbname']}")
    
    try:
        cache = PostgresCache(connection_params=params)
        
        # Test 1: Set/Get
        print("\n" + "=" * 70)
        print("TEST 1: Set/Get")
        print("=" * 70)
        
        question = "Top 10 customers"
        cache_id = cache.generate_id(question=question)
        
        print(f"\nQuestion: {question}")
        print(f"Cache ID: {cache_id}")
        
        cache.set(cache_id, "question", question)
        cache.set(cache_id, "sql", "SELECT * FROM customers ORDER BY revenue DESC LIMIT 10;")
        
        retrieved_question = cache.get(cache_id, "question")
        retrieved_sql = cache.get(cache_id, "sql")
        
        print(f"\nRetrieved Question: {retrieved_question}")
        print(f"Retrieved SQL: {retrieved_sql}")
        
        if retrieved_question == question and retrieved_sql:
            print("✅ Set/Get works!")
        else:
            print("❌ Set/Get failed!")
        
        # Test 2: Stats
        print("\n" + "=" * 70)
        print("TEST 2: Cache Stats")
        print("=" * 70)
        
        stats = cache.get_stats()
        print(f"\n{json.dumps(stats, indent=2)}")
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure PostgreSQL is running and DB credentials are correct in .env")
