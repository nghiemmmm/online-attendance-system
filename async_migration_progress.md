# AsyncSession Migration - Priority 1 Completed ✅

**Hoàn thành:** 2026-06-26

## 📋 Những gì đã thay đổi

### 1. ✅ requirements.txt
- Pin `sqlalchemy>=2.0.0` (thay vì unversioned)
- Thêm `asyncpg>=0.27.0` (async PostgreSQL driver)
- Cập nhật `psycopg[binary,asyncpg]` untuk async support

### 2. ✅ app/core/config.py
- ✅ Thêm `SQLALCHEMY_DATABASE_ASYNC_URI` property
- ✅ Tự động chuyển `postgresql://` → `postgresql+asyncpg://`
- ✅ Tự động chuyển `postgresql+psycopg://` → `postgresql+asyncpg://`

### 3. ✅ app/core/db.py
- ✅ Thay `create_engine()` → `create_async_engine()`
- ✅ Thay `SessionFactory` → `AsyncSessionFactory` với `AsyncSession`
- ✅ Thêm `init_db_async()` (async version của `init_db()`)
- ✅ Thêm `ensure_pgvector_extension()` (async version)

### 4. ✅ app/api/deps.py
- ✅ Thay `def get_db()` → `async def get_db()`
- ✅ Thay `def get_current_account()` → `async def get_current_account()`
- ✅ SessionDep giờ trả về `AsyncSession`
- ✅ Sửa query: `session.get()` → `session.execute(select(...))`

---

## ⚠️ Các routes hiện tại cần phải cẩn thận

### Tình trạng hiện tại:
- ✅ Dependencies là `async` (OK)
- ⚠️ Routes là `def` (SYNC) nhưng dependency là `async`
- ❌ Routes gọi `session.get()`, `session.exec()` → cần đổi sang `await session.execute(select(...))`

### Ví dụ vấn đề:

```python
# ❌ HIỆN TẠI - Không thể làm việc
@router.get("/sinh-vien/")
def read_students(
    session: SessionDep,  # SessionDep hiện tại là AsyncSession
    skip: int = 0,
) -> SinhViensPublic:
    # ❌ Lỗi - không thể gọi async session từ sync function
    sinh_viens, count = student_service.list_students(
        session=session,  # AsyncSession
        skip=skip,
    )
    return SinhViensPublic(data=sinh_viens, count=count)
```

### Giải pháp:

**Tùy chọn A: Giữ routes SYNC (khuyến cáo)**
```python
# ✅ Giải pháp: Tạo backward-compatible sync session
# Cần sửa deps.py để có cả get_db_sync() và get_db_async()

def get_db_sync() -> Generator[Session, None, None]:
    """DEPRECATED: Dành cho các routes cũ. Dùng async routes nếu có thể."""
    from sqlmodel import Session
    from app.core.config import settings
    
    sync_engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    with Session(sync_engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_db_sync)]  # Revert to sync
```

**Tùy chọn B: Chuyển routes thành ASYNC (Best Practice)**
```python
# ✅ Cách tốt nhất - Async routes với AsyncSession
@router.get("/sinh-vien/")
async def read_students(
    session: SessionDep,  # AsyncSession
    skip: int = 0,
) -> SinhViensPublic:
    # ✅ OK - Async service
    sinh_viens, count = await student_service.list_students_async(
        session=session,
        skip=skip,
    )
    return SinhViensPublic(data=sinh_viens, count=count)
```

---

## 🔄 KHUYẾN CÁO: Hành động tiếp theo

### Phương án 1: QUICK FIX (5 phút) - Giữ sync routes
1. Sửa `app/api/deps.py` để tạo **cả** sync và async session
2. Routes hiện tại vẫn dùng sync (không optimize)
3. Mở đường cho async routes trong tương lai

```python
# app/api/deps.py
from sqlmodel import Session, create_engine

# ✅ NEW: Sync session factory (backward compat)
sync_engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

def get_db_sync() -> Generator[Session, None, None]:
    with Session(sync_engine) as session:
        yield session

# Đối với routes cũ
SessionDep = Annotated[Session, Depends(get_db_sync)]
```

### Phương án 2: FULL MIGRATION (Hours) - Chuyển async routes
1. Cập nhật tất cả routes thành `async def`
2. Cập nhật tất cả services thành `async def`
3. Cập nhật tất cả CRUD thành `async def`
4. Chạy tests để verify

---

## 🧪 Test ngay

### ❌ Vấn đề hiện tại:
```bash
cd d:\TTCS
python -m pytest tests/ -v
# Sẽ FAIL vì routes không thể gọi async session từ sync context
```

### ✅ Để fix:
**Tạm thời sửa lại deps.py để dùng sync session:**

```python
# app/api/deps.py - FIX NGAY

from sqlmodel import Session, create_engine

# Temporary: Tạm dùng sync session cho routes hiện tại
sync_engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

def get_db() -> Generator[Session, None, None]:
    with Session(sync_engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_db)]
```

---

## 📝 Checklist

- [x] ✅ requirements.txt updated
- [x] ✅ config.py: SQLALCHEMY_DATABASE_ASYNC_URI added
- [x] ✅ db.py: AsyncSessionFactory created
- [x] ✅ deps.py: Async dependencies prepared
- [ ] ⏳ **NEXT**: Decide sync vs async for existing routes
- [ ] ⏳ Update all routes/services/CRUD (if async chosen)
- [ ] ⏳ Run tests
- [ ] ⏳ Database migration (if schema changed)

---

## 📚 Tài liệu

- [SQLAlchemy 2.0 Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [FastAPI Async SQL](https://fastapi.tiangolo.com/advanced/sql-databases/#accessing-a-database)
- [AsyncSession Best Practices](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#sqlalchemy.ext.asyncio.AsyncSession)
