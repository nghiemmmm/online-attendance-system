from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


class RefreshToken(SQLModel, table=True):
    """Lưu refresh token đã hash để hỗ trợ ghi nhớ đăng nhập và thu hồi phiên."""

    __tablename__ = "refresh_token"

    ma_refresh_token: int | None = Field(default=None, primary_key=True)
    ma_tai_khoan: int = Field(foreign_key="taikhoan.ma_tai_khoan", index=True)
    token_hash: str = Field(max_length=255, unique=True, index=True)
    expires_at: datetime = Field(index=True)
    created_at: datetime = Field(default_factory=get_datetime_utc)
    last_used_at: datetime | None = None
    revoked_at: datetime | None = Field(default=None, index=True)
    user_agent: str | None = Field(default=None, max_length=255)
    ip_address: str | None = Field(default=None, max_length=45)
