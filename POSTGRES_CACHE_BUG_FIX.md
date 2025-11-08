# 🐛 Bug Fix: Connection Pool Exhausted

## Vấn đề
Khi gọi API `/api/v0/generate_sql`, sau vài requests sẽ nhận lỗi:
```
⚠️  Error setting cache: connection pool exhausted
```

## Nguyên nhân
Trong file `postgres_cache.py`, có nhiều methods **không trả connection về pool đúng cách**:

### 1. Bug trong `set()` method (dòng 110-147)
```python
def set(self, id, field, value):
    try:
        conn = self._get_connection()
        # ... xử lý ...
        conn.close()  # ❌ SAI! Đang close thay vì return về pool
    except Exception as e:
        print(f"⚠️  Error setting cache: {e}")
```

**Vấn đề:**
- `conn.close()` sẽ đóng connection thật, không return về pool
- Pool sẽ mất dần connections
- Không có error handling → nếu exception xảy ra, connection bị leak

### 2. Bug trong `get()` method (dòng 195-219)
```python
def get(self, id, field):
    conn = None
    try:
        conn = self._get_connection()
        # ... xử lý ...
        cursor.close()
        self._return_connection(conn)  # ✅ Có return về pool
        # ... 
    except Exception as e:
        # ❌ KHÔNG có finally block để return connection nếu exception
        print(f"⚠️  Error getting cache: {e}")
        if conn:
            self._return_connection(conn)
        return None
```

**Vấn đề:**
- Nếu exception xảy ra TRƯỚC khi gọi `self._return_connection(conn)`, connection sẽ bị leak
- Cần dùng `finally` block để đảm bảo connection luôn được trả về

### 3. Pattern tương tự trong các methods khác
- `delete()`, `get_all()`, `clear()`, `size()`, `get_stats()` đều có vấn đề tương tự

## Luồng gây lỗi
```
API Request: /api/v0/generate_sql?question=...
  ↓
flask_main.py: cached_generate_sql()
  ↓
custom_cache.get(cache_id, "sql")  ← Lấy connection #1, có thể không return về
  ↓
original_generate_sql()  ← Gọi LLM
  ↓
custom_cache.set_multiple()  ← Lấy connection #2, có thể không return về
  ↓
Connection pool: 10 → 8 → 6 → 4 → 2 → 0 → EXHAUSTED!
```

## Giải pháp

### Fix 1: Sửa method `set()` 
```python
def set(self, id, field, value):
    conn = None
    try:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # ... xử lý ...
        
        conn.commit()
        cursor.close()
        
    except Exception as e:
        print(f"⚠️  Error setting cache: {e}")
        if conn:
            conn.rollback()  # Rollback nếu có lỗi
    finally:
        if conn:
            self._return_connection(conn)  # ✅ Luôn return về pool
```

### Fix 2: Sửa tất cả methods khác theo pattern:
```python
def method_name(self, ...):
    conn = None
    try:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # ... xử lý ...
        
        cursor.close()
        
    except Exception as e:
        print(f"⚠️  Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            self._return_connection(conn)  # ✅ Đảm bảo return trong mọi trường hợp
```

### Fix 3: Thêm connection pool monitoring
```python
def get_pool_stats(self):
    """Get connection pool statistics"""
    if self.connection_pool:
        return {
            "size": self.connection_pool.maxconn,
            "available": len(self.connection_pool._pool),
            "in_use": self.connection_pool.maxconn - len(self.connection_pool._pool)
        }
    return None
```

## Testing
Sau khi fix, test với:
```bash
# Gọi API nhiều lần liên tiếp
for i in {1..20}; do
  curl "http://localhost:8000/api/v0/generate_sql?question=test$i"
  echo "Request $i done"
done
```

Nên không còn lỗi "connection pool exhausted"!

## Checklist
- [ ] Fix method `set()`
- [ ] Fix method `get()`
- [ ] Fix method `delete()`
- [ ] Fix method `get_all()`
- [ ] Fix method `clear()`
- [ ] Fix method `size()`
- [ ] Fix method `get_stats()`
- [ ] Fix method `_create_table_if_not_exists()`
- [ ] Thêm connection pool monitoring
- [ ] Test với nhiều requests liên tiếp
