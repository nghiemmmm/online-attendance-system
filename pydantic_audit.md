# 📊 Pydantic Audit Report

**Ngày audit:** 2026-06-26  
**Phiên bản Pydantic:** 2.11.7  
**Phiên bản Pydantic Settings:** 2.x

---

## 🎯 Kết quả Audit

| Tiêu chí | Kết quả | Điểm |
|---------|---------|------|
| **Validators** | ⚠️ Cơ bản | 60/100 |
| **Custom Base Model** | ❌ Không có | 0/100 |
| **BaseSettings (Domain Separation)** | ❌ Monolithic | 20/100 |
| **Field Validators** | ⚠️ Tối thiểu | 40/100 |
| **Serializers** | ❌ Không có | 0/100 |
| **Overall Score** | ⚠️ Cải thiện được | **36/100** |

---

## 📋 Chi tiết Phát hiện

### 1. ✅ Validators - HỮU DỤNG NHƯNG CĂN BẢN

**Location:** `app/core/config.py`

**Hiện tại (TỐT):**
```python
@model_validator(mode="after")
def _set_default_emails_from(self) -> Self:
    if not self.EMAILS_FROM_NAME:
        self.EMAILS_FROM_NAME = self.PROJECT_NAME
    return self

@model_validator(mode="after")
def _enforce_non_default_secrets(self) -> Self:
    self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
    self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
    self._check_default_secret("FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD)
    return self
```

**Vấn đề:**
- ✅ Sử dụng Pydantic v2 `model_validator(mode="after")` đúng
- ✅ Có helper method `_check_default_secret()` cho DRY
- ⚠️ Thiếu `field_validator` cho từng field
- ⚠️ Validator xử lý CORS và DEBUG có thể tối ưu

**Cải thiện:** Thêm field-level validators
```python
# ❌ CURRENT (custom function)
def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i.strip()]
    ...

# ✅ SHOULD BE (field_validator)
from pydantic import field_validator

@field_validator('BACKEND_CORS_ORIGINS', mode='before')
@classmethod
def validate_cors(cls, v: Any) -> list[str] | str:
    # cùng logic nhưng rõ ràng hơn
```

---

### 2. ❌ Custom Base Model - KHÔNG CÓ

**Vấn đề:**
- Không có base Pydantic model để share chung validators/config
- Mỗi model lặp lại cùng constraints (max_length, etc.)
- Khó maintain và scale

**Giải pháp (PRIORITY):**
```python
# app/models/base.py
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class BaseResponse(BaseModel):
    """Base response model với config chung."""
    model_config = ConfigDict(
        populate_by_name=True,  # Accept both snake_case và PascalCase
        from_attributes=True,   # Support ORM mode
        json_schema_extra={
            "example": {
                "message": "Success",
                "timestamp": "2026-06-26T10:30:00Z"
            }
        }
    )

class BaseCreateRequest(BaseModel):
    """Base model cho CREATE requests với validation chung."""
    model_config = ConfigDict(
        str_strip_whitespace=True,      # Trim strings
        validate_default=True,          # Validate default values
    )

class BaseUpdateRequest(BaseModel):
    """Base model cho UPDATE requests (all fields optional)."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        # Không validate None/missing fields
    )

# Usage:
class SinhVienCreate(BaseCreateRequest):
    ho: str = Field(max_length=50, min_length=1)
    ten: str = Field(max_length=50, min_length=1)
```

---

### 3. ❌ BaseSettings - MONOLITHIC (Không Split theo Domain)

**Current Issue:** `app/core/config.py` - TẤT CẢ settings trong 1 file

```python
class Settings(BaseSettings):
    # 🚗 APP SETTINGS
    APP_NAME: str = "diemdanh"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    HOST: str = "0.0.0.0"
    PORT: int = 5050
    DEBUG: bool = False
    
    # 🔐 SECURITY SETTINGS
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    
    # 📧 EMAIL SETTINGS
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    
    # 🗄️ DATABASE SETTINGS
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5433
    POSTGRES_USER: str = "root"
    
    # 🌐 CORS SETTINGS
    BACKEND_CORS_ORIGINS: list[AnyUrl] | str = []
    
    # ... tất cả trộn lẫn
```

**Vấn đề:**
- ❌ Khó navigate (1 class quá lớn)
- ❌ Khó test (phải mock tất cả)
- ❌ Khó maintain (dependencies không rõ)
- ❌ Khó reuse (không thể chỉ import email settings)

**Giải pháp (RECOMMENDED):**

```
app/core/config/
├── __init__.py
├── base.py              # AppSettings (app info, debug, etc)
├── database.py          # DatabaseSettings
├── security.py          # SecuritySettings (JWT, passwords)
├── email.py             # EmailSettings (SMTP)
├── cors.py              # CORSSettings
└── settings.py          # Combine tất cả
```

**File mẫu:**

```python
# app/core/config/base.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    """App-level settings."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_",
    )
    
    APP_NAME: str = "diemdanh"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    HOST: str = "0.0.0.0"
    PORT: int = 5050
    DEBUG: Annotated[bool, BeforeValidator(parse_debug)] = False


# app/core/config/security.py
from pydantic_settings import BaseSettings

class SecuritySettings(BaseSettings):
    """Security settings (JWT, tokens, passwords)."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SECURITY_",
    )
    
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str
    
    @model_validator(mode="after")
    def validate_secrets(self) -> Self:
        # Specific security validation
        return self


# app/core/config/database.py
from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings

class DatabaseSettings(BaseSettings):
    """Database settings (PostgreSQL, async)."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="POSTGRES_",
    )
    
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5433
    POSTGRES_USER: str = "root"
    POSTGRES_PASSWORD: str = "123456"
    POSTGRES_DB: str = "diemdanh"
    DATABASE_URL: str | None = None
    
    @computed_field
    @property
    def SQLALCHEMY_DATABASE_ASYNC_URI(self) -> str:
        # Async database URL logic here
        ...
    
    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn | str:
        # Sync database URL logic here
        ...


# app/core/config/email.py
from pydantic import EmailStr
from pydantic_settings import BaseSettings

class EmailSettings(BaseSettings):
    """Email/SMTP settings."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SMTP_",
    )
    
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: str | None = None
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    
    @computed_field
    @property
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)


# app/core/config/cors.py
from pydantic import AnyUrl, BeforeValidator
from pydantic_settings import BaseSettings

class CORSSettings(BaseSettings):
    """CORS settings."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
    )
    
    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []
    FRONTEND_HOST: str = "http://localhost:5173"
    GOOGLE_ALLOWED_EMAIL_DOMAIN: str = ""
    
    @computed_field
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]


# app/core/config/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from .base import AppSettings
from .security import SecuritySettings
from .database import DatabaseSettings
from .email import EmailSettings
from .cors import CORSSettings

class Settings(BaseSettings):
    """Combined settings (Facade pattern)."""
    model_config = SettingsConfigDict(env_file=".env")
    
    # Import sub-settings
    app: AppSettings = AppSettings()
    security: SecuritySettings = SecuritySettings()
    database: DatabaseSettings = DatabaseSettings()
    email: EmailSettings = EmailSettings()
    cors: CORSSettings = CORSSettings()

# Usage:
settings = Settings()
settings.database.SQLALCHEMY_DATABASE_ASYNC_URI
settings.security.SECRET_KEY
settings.email.SMTP_HOST
settings.cors.all_cors_origins
```

---

### 4. ⚠️ Field Validators - CÒN ÍT

**Current State:**
- Chỉ 5 request models: `AutoAttendanceRequest`, `ManualAttendanceRequest`, `FaceReviewRequest`, `VerificationResult`, `UserWithProfileCreate`
- Hầu như không có field-level validation
- Constraints (max_length) có, nhưng logic validation không

**Cải thiện:**
```python
# app/api/routes/diemdanh.py

from pydantic import BaseModel, Field, field_validator
from typing import Annotated

class AutoAttendanceRequest(BaseModel):
    ma_buoi_hoc: Annotated[int, Field(gt=0, description="Buổi học ID")]
    danh_sach_ma_sinh_vien: Annotated[list[int], Field(min_length=1, description="Min 1 student")]
    do_tin_cay_trung_binh: Annotated[float, Field(ge=0.0, le=1.0, description="0.0 to 1.0")]
    
    @field_validator('danh_sach_ma_sinh_vien')
    @classmethod
    def validate_unique_students(cls, v: list[int]) -> list[int]:
        """Ensure no duplicates in student list."""
        if len(v) != len(set(v)):
            raise ValueError('Danh sách sinh viên không được trùng lặp')
        return v
    
    @field_validator('do_tin_cay_trung_binh')
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Log warning if confidence too low."""
        if v < 0.5:
            import warnings
            warnings.warn(f"Confidence {v} is very low, results may be unreliable")
        return v

class ManualAttendanceRequest(BaseModel):
    ma_buoi_hoc: Annotated[int, Field(gt=0)]
    ma_sinh_vien: Annotated[int, Field(gt=0)]
    trang_thai: Annotated[str, Field(pattern="^(CO_MAT|VAU_MAT|PHEP|KHONG_PHEP)$")]
    ghi_chu: Annotated[str | None, Field(None, max_length=500)]
```

---

### 5. ❌ Field Serializers - KHÔNG DÙNG

**Vấn đề:**
- Không có custom serialization logic
- Mọi field serialize theo default Pydantic rules

**Cải thiện:**
```python
from datetime import datetime
from pydantic import BaseModel, field_serializer

class SinhVienPublic(BaseModel):
    ma_sinh_vien: int
    ho: str
    ten: str
    thoi_gian_bat_dau_hoc: datetime
    
    @field_serializer('thoi_gian_bat_dau_hoc')
    def serialize_datetime(self, value: datetime | None) -> str | None:
        """Custom datetime serialization (ISO 8601 with Z suffix)."""
        if value is None:
            return None
        return value.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    @field_serializer('ho', 'ten')
    def serialize_name(self, value: str) -> str:
        """Trim names and uppercase first letter."""
        return value.strip().capitalize() if value else ""
```

---

## 🚀 Priority Cải thiện

### Priority 1 (CRITICAL)
- ✅ **BaseSettings Domain Separation** (split config into modules)
- ✅ **Custom Base Model** (BaseResponse, BaseCreateRequest, BaseUpdateRequest)

### Priority 2 (HIGH)
- ✅ **Field Validators** (validation logic for request models)
- ✅ **Field Serializers** (custom datetime, name formatting)

### Priority 3 (MEDIUM)
- ✅ Improve existing validators (move parse_cors, parse_debug to field_validator)
- ✅ Add more request models for other routes

---

## 📊 Action Plan

```json
{
  "Phase 1": {
    "description": "Structure refactoring",
    "tasks": [
      "Create app/core/config/ directory",
      "Split Settings into 5 modules (base, security, database, email, cors)",
      "Create custom base models (BaseResponse, BaseCreateRequest, etc)",
      "Update imports in app/main.py and other files"
    ],
    "effort": "~3 hours",
    "impact": "HIGH - Better maintainability"
  },
  
  "Phase 2": {
    "description": "Add validation layer",
    "tasks": [
      "Add field_validator to existing request models",
      "Create request models for all routes (missing ones)",
      "Add field_serializer for datetime and name fields",
      "Document validation rules in models"
    ],
    "effort": "~2 hours",
    "impact": "MEDIUM - Better data integrity"
  },
  
  "Phase 3": {
    "description": "Documentation and testing",
    "tasks": [
      "Document custom validators in docstrings",
      "Add test cases for validator edge cases",
      "Update API documentation (FastAPI docs)"
    ],
    "effort": "~1 hour",
    "impact": "LOW - Better DX"
  }
}
```

---

## 💡 Recommendations

1. **Start with Phase 1** - Domain separation will reduce config.py from 200+ lines to manageable chunks
2. **Use computed_field** for URL generation (đã làm tốt!)
3. **Leverage EmailStr validation** (đã sử dụng ở TaiKhoan, SinhVien)
4. **Add strict mode** for production:
   ```python
   model_config = ConfigDict(strict=True)  # Enforce type coercion rules
   ```
5. **Document validator logic** in docstrings for team understanding

---

## 📝 Files cần update

```
app/core/config/
├── __init__.py              # NEW
├── base.py                  # NEW - AppSettings
├── database.py              # NEW - DatabaseSettings + async URL logic
├── security.py              # NEW - SecuritySettings
├── email.py                 # NEW - EmailSettings
├── cors.py                  # NEW - CORSSettings
└── settings.py              # NEW - Combined Settings

app/models/
├── base.py                  # NEW - Custom base models
├── taikhoan.py              # UPDATE - Add field validators
├── sinhvien.py              # UPDATE - Add field validators
└── ... others

app/api/routes/
├── diemdanh.py              # UPDATE - Add field validators + serializers
├── anhkhuonmat.py           # UPDATE - Add validators
└── ... others

app/main.py                  # UPDATE - Change import: from app.core.config.settings import settings
```

---

**Generated:** 2026-06-26  
**Reviewer:** Pydantic Audit Agent
