# ⚡ Async Routes Audit - FastAPI Best Practices

**Ngày kiểm tra:** 2026-06-26  
**Tiêu chuẩn:** [AGENTS.md - Async Routes](d:\TTCS\.agents\skills\FastAPI-Coding-Standards\AGENTS.md)

---

## 📊 Tóm tắt

| Hạng mục | Trạng thái | Chi tiết |
|---------|----------|---------|
| **Database Setup** | ⚠️ KHÔNG ĐẠT | Đang dùng SYNC `Session` thay vì `AsyncSession` |
| **Routes** | ✅ HẦU HẾT ĐẠT | ~95% routes dùng `def` (sync) - phù hợp với sync DB |
| **Async Routes** | ❌ CÓ VẤN ĐỀ | 2-3 routes dùng `async def` nhưng gọi sync operations |
| **Blocking Calls** | ✅ OK | Không tìm thấy `time.sleep` / `requests.get` trong routes |
| **Anti-patterns** | ⚠️ CÓ 1 | Async route nhưng dùng sync `Session` + sync DB calls |

---

## 🔴 Vấn đề Chính

### 1. **Kiến trúc Database - SYNC thay vì ASYNC** ⚠️ [CRITICAL]

**Tập tin:** [app/core/db.py](app/core/db.py)

```python
# ❌ HIỆN TẠI - SYNC
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
SessionFactory = async_sessionmaker(engine, expire_on_commit=False)

def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_db)]
```

**Vấn đề:**
- ❌ Dùng `Session` (sync) thay vì `AsyncSession` (async)
- ❌ Khi route là `async def` nhưng dùng sync `Session`, nó **BLOCKS event loop**
- ❌ Không tận dụng được khả năng của FastAPI async

**Khuyến cáo:** Nâng cấp lên AsyncSession (xem phần "Khắc phục")

---

### 2. **Async Routes Không Thực Sự Async** ❌

**Tập tin:** [app/api/routes/anhkhuonmat.py](app/api/routes/anhkhuonmat.py:126)

```python
# ❌ VẤNĐỀ: async def nhưng gọi sync database operations
async def admin_dang_ky_khuon_mat(
    request: Request,
    session: SessionDep,  # Đây là SYNC Session!
    current_account: CurrentAccount,
    ma_sinh_vien: Annotated[int, Form()],
    file: Annotated[UploadFile, File()],
) -> Any:
    # ✅ OK - async file read
    content = await file.read()
    
    # ❌ BLOCKING - gọi async service nhưng service dùng sync Session
    db_anh = await face_service.register_student_face_db(
        session=session,
        ma_sinh_vien=ma_sinh_vien,
        content=content,
    )
```

**Tập tin:** [app/services/face_service.py](app/services/face_service.py:327)

```python
# ❌ VẤNĐỀ: async def nhưng dùng sync operations
async def register_student_face_db(self, *, session: Session, ma_sinh_vien: int, content: bytes) -> Any:
    # ❌ BLOCKING - sync database call trong async function
    sinh_vien = session.get(SinhVien, ma_sinh_vien)
    
    # ❌ BLOCKING - sync method trong async function
    success, message, quality_score, embedding = self.assess_face_image(image_bytes=content)
    
    # ✅ OK - async file write
    async with aiofiles.open(filepath, "wb") as image_file:
        await image_file.write(content)
    
    # ❌ BLOCKING - sync database commit
    session.add(db_anh)
    session.commit()
    session.refresh(db_anh)
```

**Vấn đề:**
- ❌ Function là `async` nhưng hầu hết là sync operations
- ❌ Gây lãng phí vì không tận dụng async benefits
- ⚠️ Có thể gây deadlock hoặc timeout nếu tải cao

---

## ✅ Điểm Tốt

### 1. **Hầu hết Routes là Sync** ✅

**Tập tin:** [app/api/routes/login.py](app/api/routes/login.py:31) 

```python
# ✅ ĐÚNG: def (sync) để sử dụng sync Session
@router.post("/login/access-token")
def login_access_token(
    request: Request,
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    account = crud.authenticate_account(
        session=session,
        ten_dang_nhap=form_data.username,
        password=form_data.password,
    )
    # ...
```

**Các routes sync đúng:**
- ✅ [app/api/routes/sinhvien.py](app/api/routes/sinhvien.py) - 13 endpoints, tất cả `def`
- ✅ [app/api/routes/diemdanh.py](app/api/routes/diemdanh.py) - Tất cả `def`
- ✅ [app/api/routes/login.py](app/api/routes/login.py) - Tất cả `def`
- ✅ [app/api/routes/user.py](app/api/routes/user.py) - Tất cả `def`

### 2. **Không có Blocking Calls trong Routes** ✅

```python
# ✅ KHÔNG TÌM THẤY những anti-patterns này:
❌ time.sleep(...)        # Không tìm thấy trong routes
❌ requests.get(...)      # Không tìm thấy trong routes  
❌ open(...).read()       # Không tìm thấy trong routes
❌ subprocess.run(...)    # Không tìm thấy trong routes
```

### 3. **Dependencies Tốt** ✅

```python
# ✅ ĐÚNG: JWT decode không block
def get_current_account(session: SessionDep, token: TokenDep) -> TaiKhoan:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )  # Nhanh - chỉ là string manipulation
        # ...
    except (InvalidTokenError, ValidationError):
        raise HTTPException(...)

# ✅ OK: Rate limiter dùng time.time() (không block)
class RateLimiter:
    def __call__(self, request: Request):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()  # ✅ OK - không block, chỉ lấy timestamp
```

---

## 🔧 Khắc Phục (Priority)

### Priority 1: Chuyển sang AsyncSession (HIGH IMPACT)

```python
# ✅ KHẮC PHỤC: app/core/db.py

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Thay đổi database URL
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/db"

engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False,  # Set True để debug
)

SessionFactory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_db)]
```

**Lợi ích:**
- ✅ Event loop không bị block
- ✅ Có thể handle nhiều requests đồng thời hơn
- ✅ Có thể dùng `async def` routes thực sự

### Priority 2: Cập nhật Async Routes

```python
# ✅ KHẮC PHỤC: app/api/routes/anhkhuonmat.py

@router.post("/admin/dang-ky-khuon-mat")
async def admin_dang_ky_khuon_mat(
    request: Request,
    session: AsyncSession,  # Đổi từ Session → AsyncSession
    current_account: CurrentAccount,
    ma_sinh_vien: Annotated[int, Form()],
    file: Annotated[UploadFile, File()],
) -> Any:
    content = await file.read()
    
    # Khắc phục async service
    db_anh = await face_service.register_student_face_db_async(
        session=session,
        ma_sinh_vien=ma_sinh_vien,
        content=content,
    )
    return db_anh
```

```python
# ✅ KHẮC PHỤC: app/services/face_service.py

async def register_student_face_db_async(
    self,
    *,
    session: AsyncSession,
    ma_sinh_vien: int,
    content: bytes,
) -> Any:
    # ✅ Async database query
    stmt = select(SinhVien).where(SinhVien.ma_sinh_vien == ma_sinh_vien)
    result = await session.execute(stmt)
    sinh_vien = result.scalar_one_or_none()
    
    if not sinh_vien:
        raise StudentNotFoundError("Khong tim thay sinh vien")
    
    # ✅ Async file write
    async with aiofiles.open(filepath, "wb") as image_file:
        await image_file.write(content)
    
    # Sync compute (CPU-bound) - OK vì rất nhanh
    success, message, quality_score, embedding = self.assess_face_image(
        image_bytes=content
    )
    
    # ✅ Async database commit
    db_anh = AnhKhuonMat(...)
    session.add(db_anh)
    await session.commit()
    await session.refresh(db_anh)
    
    return db_anh
```

### Priority 3: Audit các routes khác

Kiểm tra tất cả routes trong:
- ✅ [app/api/routes/ketnoi_router.py](app/api/routes/ketnoi_router.py) - Có 2 async routes (WebRTC)
- ✅ [app/api/routes/google_auth_router.py](app/api/routes/google_auth_router.py) - Có 3 async routes (OAuth redirect)

---

## 📋 Checklist Tuân Thủ

| Tiêu chí | Hiện tại | Lý tưởng | Trạng thái |
|---------|---------|---------|-----------|
| Database async | ❌ NO | ✅ YES | 🔴 FAIL |
| Routes async khi DB async | ⚠️ PARTIAL | ✅ YES | 🟡 PARTIAL |
| Không có blocking calls | ✅ YES | ✅ YES | 🟢 PASS |
| Dependencies tối ưu | ✅ YES | ✅ YES | 🟢 PASS |
| Error handling | ✅ YES | ✅ YES | 🟢 PASS |
| Rate limiting | ✅ YES | ✅ YES | 🟢 PASS |

---

## 🎯 Kết Luận

**Điểm số: 65/100** 🟡

### Điểm mạnh:
- ✅ Hầu hết routes dùng `def` (sync) - phù hợp với current setup
- ✅ Không có blocking calls như `time.sleep`, `requests.get`
- ✅ Dependencies được thiết kế tốt

### Điểm yếu:
- ❌ Database vẫn dùng SYNC `Session` (SQLModel)
- ❌ Một số routes muốn dùng `async def` nhưng lại gọi sync operations
- ⚠️ Không tận dụng được AsyncIO benefits

### Khuyến cáo:
1. **Nhanh:** Giữ hệ thống hiện tại cho đến khi ready để migrate
2. **Trung hạn:** Lập kế hoạch migrate sang SQLAlchemy 2.0 + AsyncSession
3. **Dài hạn:** Chuyển toàn bộ codebase thành async-first architecture

---

## 📚 Tài liệu Tham Khảo

- [SQLAlchemy 2.0 Async Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [AGENTS.md - Async Routes](d:\TTCS\.agents\skills\FastAPI-Coding-Standards\AGENTS.md)
