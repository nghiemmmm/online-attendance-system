"""Define account database and response models."""

from datetime import UTC, datetime
from typing import ClassVar

from pydantic import field_serializer
from sqlalchemy.orm import synonym
from sqlmodel import Field, SQLModel

from app.core.email_compat import EmailStr
from app.models.base import AppBaseModel


def get_datetime_utc() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(UTC)


class AccountBase(SQLModel):
    """Represent shared account fields."""

    username: str = Field(max_length=50)
    role: str = Field(default="SINH_VIEN", max_length=20)
    status: bool = True


class AccountCreate(AccountBase):
    """Represent data required to create an account."""

    password: str = Field(min_length=5, max_length=128)


class AccountRegister(SQLModel):
    """Represent account registration data."""

    username: str = Field(max_length=50)
    password: str = Field(min_length=5, max_length=128)
    role: str = Field(default="SINH_VIEN", max_length=20)
    email: EmailStr | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=50)
    first_name: str | None = Field(default=None, max_length=50)
    phone: str | None = Field(default=None, max_length=15)
    gender: str | None = Field(default=None, max_length=10)


class AccountUpdate(SQLModel):
    """Represent fields that can update an account."""

    username: str | None = Field(default=None, max_length=50)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    role: str | None = Field(default=None, max_length=20)
    status: bool | None = None


class Account(AccountBase, table=True):
    """Represent the account database table."""

    __tablename__ = "accounts"

    account_id: int | None = Field(default=None, primary_key=True)
    username: str = Field(max_length=50, unique=True, index=True)
    password_hash: str = Field(max_length=255)
    last_login_at: datetime | None = None
    failed_login_count: int = Field(default=0)
    locked_until: datetime | None = None
    created_at: datetime = Field(default_factory=get_datetime_utc)

    # Legacy field aliases retained for compatibility with older routes/tests.
    ma_tai_khoan: ClassVar = synonym("account_id")
    ten_dang_nhap: ClassVar = synonym("username")
    vai_tro: ClassVar = synonym("role")
    trang_thai: ClassVar = synonym("status")
    mat_khau_hash: ClassVar = synonym("password_hash")
    lan_dang_nhap_cuoi: ClassVar = synonym("last_login_at")
    so_lan_dang_nhap_sai: ClassVar = synonym("failed_login_count")
    khoa_den: ClassVar = synonym("locked_until")
    ngay_tao: ClassVar = synonym("created_at")


class AccountPublic(AppBaseModel, AccountBase):
    """Represent account data returned by the API."""

    account_id: int
    last_login_at: datetime | None = None
    created_at: datetime

    @field_serializer("last_login_at", "created_at")
    def _serialize_datetime(self, value: datetime | None) -> str | None:
        if value is None:
            return None
        return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


class AccountsPublic(SQLModel):
    """Represent a paginated list of accounts."""

    data: list[AccountPublic]
    count: int


AccountListPublic = AccountsPublic


class AccountProfile(SQLModel):
    """Represent an account with its linked profile data."""

    account: AccountPublic
    profile: dict | None = None
