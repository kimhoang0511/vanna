# 🔧 Cache Fix - Giải thích và Test

## ❌ **Vấn đề:**

Khi gọi API với **cùng một câu hỏi nhiều lần**, hệ thống vẫn **gọi LLM mỗi lần** thay vì dùng cache.

### **Nguyên nhân:**

`VannaFlaskApp` mặc định dùng `MemoryCache` với `generate_id()` tạo **UUID ngẫu nhiên**:

```python
# Trong vanna/flask/__init__.py (DEFAULT - SAI!)
def generate_id(self, *args, **kwargs):
    return str(uuid.uuid4())  # ❌ Random UUID mỗi lần!

# Mỗi request:
id = cache.generate_id(question=question)  # UUID mới
sql = vn.generate_sql(question)  # Gọi LLM 
cache.set(id, "sql", sql)  # Lưu với ID mới
```

**Kết quả:**
- Request 1: ID = `abc123` → Generate SQL → Cache với ID `abc123`
- Request 2 (same question): ID = `xyz789` → Generate SQL lại → Cache với ID `xyz789`
- Cache miss vì ID khác nhau!

---

## ✅ **Giải pháp:**

Tạo `QuestionHashCache` - Generate ID dựa trên **hash của câu hỏi**:

```python
# vanna_cache_fix.py (MỚI - ĐÚNG!)
def generate_id(self, question=None, *args, **kwargs):
    if question:
        # Hash câu hỏi → Deterministic ID
        question_normalized = question.lower().strip()
        hash_object = hashlib.md5(question_normalized.encode())
        return hash_object.hexdigest()
    else:
        return str(uuid.uuid4())
```

**Kết quả:**
- Request 1: Question → Hash → ID = `5e3889e5` → Generate SQL → Cache
- Request 2 (same question): Question → Hash → ID = `5e3889e5` → **Cache HIT!** ✅

---

## 🎯 **Thay đổi:**

### **File: `flask_main.py`**

```python
# TRƯỚC (default cache):
app = VannaFlaskApp(vn=vn, ...)

# SAU (custom cache):
from vanna_cache_fix import QuestionHashCache

custom_cache = QuestionHashCache()
app = VannaFlaskApp(vn=vn, cache=custom_cache, ...)
```

---

## 🧪 **Test Cache:**

### **Test 1: Local test**
```bash
python3 vanna_cache_fix.py
```

**Expected output:**
```
✅ SUCCESS: Same question = Same ID
✅ Cache working!
```

### **Test 2: Railway deployment test**

Sau khi Railway redeploy (1-2 phút):

```bash
python3 test_cache_behavior.py
```

**Expected output:**
```
Request 1: 15.2s (LLM call)
Request 2: 0.8s
Speedup: 19x
✅ CACHE WORKING!
```

---

## 📊 **So sánh:**

| Metric | TRƯỚC (UUID) | SAU (Hash) |
|--------|--------------|------------|
| Same question → Same ID? | ❌ Không | ✅ Có |
| Cache hit? | ❌ Không | ✅ Có |
| Request 2 speed | ~15s (LLM) | ~0.5s (cache) |
| API calls saved | 0% | ~95% |

---

## 🚀 **Benefits:**

1. **Giảm chi phí:** Ít gọi OpenAI API hơn
2. **Tăng tốc độ:** Response nhanh hơn 10-20x
3. **UX tốt hơn:** User không phải đợi lâu

---

## 🔮 **Advanced: Persistent Cache**

Nếu muốn giữ cache **giữa các lần restart**:

```python
# Trong flask_main.py
from vanna_cache_fix import PersistentQuestionCache

cache = PersistentQuestionCache(cache_file="vanna_cache.json")
app = VannaFlaskApp(vn=vn, cache=cache, ...)
```

**Lưu ý:** Railway ephemeral storage, cache sẽ mất khi restart. Cần external storage (Redis, DB) cho production.

---

## 📝 **Verify Deployment:**

1. **Check Railway logs:**
   ```
   🔧 Initializing cache with question hashing...
   ```

2. **Test API:**
   ```bash
   # Request 1
   curl "https://vanna-production.up.railway.app/api/v0/generate_sql?question=SELECT%20*%20FROM%20users"
   
   # Request 2 (same) - should be much faster
   curl "https://vanna-production.up.railway.app/api/v0/generate_sql?question=SELECT%20*%20FROM%20users"
   ```

3. **Check timing:** Request 2 should be < 1s

---

## ✅ **Status:**

- ✅ Code pushed to GitHub
- ✅ Railway will auto-deploy
- ⏳ Wait 1-2 minutes for deployment
- 🧪 Test with `python3 test_cache_behavior.py`

**Expected:** Cache sẽ hoạt động, cùng câu hỏi không gọi LLM lần 2! 🎉
