from datetime import datetime, timezone

from pydantic import EmailStr
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


class OAuthIdentity(SQLModel, table=True):
    __tablename__ = "oauth_identity"
    __table_args__ = (
        UniqueConstraint(
            "provider",
            "provider_subject",
            name="uq_oauth_identity_provider_subject",
        ),
    )

    ma_oauth_identity: int | None = Field(default=None, primary_key=True)
    provider: str = Field(max_length=30, index=True)
    provider_subject: str = Field(max_length=255, index=True)
    email: EmailStr = Field(max_length=255, index=True)
    ma_tai_khoan: int = Field(foreign_key="taikhoan.ma_tai_khoan", index=True)
    created_at: datetime = Field(default_factory=get_datetime_utc)
    last_login_at: datetime | None = None
