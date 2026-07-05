"""Define audit log database and response models."""

from datetime import UTC, datetime

from pydantic import field_serializer
from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

from app.models.base import AppBaseModel


def get_datetime_utc() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(UTC)


class AuditLogBase(SQLModel):
    """Represent shared audit log fields."""

    ma_tai_khoan: int | None = Field(default=None, foreign_key="accounts.account_id")
    vai_tro: str | None = Field(default=None, max_length=20)
    hanh_dong: str = Field(max_length=100)
    doi_tuong: str | None = Field(default=None, max_length=100)
    doi_tuong_id: str | None = Field(default=None, max_length=100)
    du_lieu_truoc: dict | None = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    du_lieu_sau: dict | None = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    ip: str | None = Field(default=None, max_length=45)
    user_agent: str | None = Field(default=None, max_length=255)
    trang_thai: str = Field(default="SUCCESS", max_length=30)
    chi_tiet: str | None = Field(default=None, max_length=500)


class AuditLogCreate(AuditLogBase):
    """Represent data required to create an audit log entry."""

    pass


class AuditLog(AuditLogBase, table=True):
    """Represent the audit log database table."""

    __tablename__ = "auditlog"

    ma_audit_log: int | None = Field(default=None, primary_key=True)
    thoi_gian: datetime = Field(default_factory=get_datetime_utc, index=True)


class AuditLogPublic(AppBaseModel, AuditLogBase):
    """Represent audit log data returned by the API."""

    ma_audit_log: int
    thoi_gian: datetime

    @field_serializer("thoi_gian")
    def _serialize_datetime(self, value: datetime) -> str:
        return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


class AuditLogsPublic(SQLModel):
    """Represent a paginated list of audit log entries."""

    data: list[AuditLogPublic]
    count: int
