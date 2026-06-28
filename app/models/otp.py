"""Define OTP database table and request models."""

from datetime import datetime, timezone
from pydantic import EmailStr, Field as PydanticField
from sqlmodel import Field, SQLModel
from app.models.base import AppBaseModel


def get_datetime_utc() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


class OTPRecord(SQLModel, table=True):
    """Represent OTP verification codes database table."""

    __tablename__ = "otp_codes"

    otp_id: int | None = Field(default=None, primary_key=True)
    email: str = Field(max_length=100, index=True)
    code: str = Field(max_length=6)
    expires_at: datetime
    is_used: bool = Field(default=False)
    created_at: datetime = Field(default_factory=get_datetime_utc)


class SendOtpRequest(AppBaseModel):
    """Represent request payload to send OTP code."""

    mssv: int = PydanticField(description="Mã số sinh viên")
    email: EmailStr = PydanticField(max_length=100)


class StudentRegisterRequest(AppBaseModel):
    """Represent request payload to register student account with OTP."""

    mssv: int = PydanticField(description="Mã số sinh viên")
    email: EmailStr = PydanticField(max_length=100)
    password: str = PydanticField(min_length=5, max_length=128)
    otp_code: str = PydanticField(min_length=6, max_length=6)
