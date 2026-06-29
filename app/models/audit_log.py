"""Define audit log database and response models."""

from datetime import datetime, timezone

from pydantic import field_serializer
from sqlalchemy import Column, JSON, Integer, String, DateTime
from sqlmodel import Field, SQLModel
from app.models.base import AppBaseModel

def get_datetime_utc() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(timezone.utc)


class AuditLogBase(SQLModel):
    """Represent shared audit log fields."""

    account_id: int | None = Field(default=None, sa_column=Column("ma_tai_khoan", Integer, nullable=True))
    role: str | None = Field(default=None, sa_column=Column("vai_tro", String(20), nullable=True))
    action: str = Field(sa_column=Column("hanh_dong", String(100), nullable=False))
    target_type: str | None = Field(default=None, sa_column=Column("doi_tuong", String(100), nullable=True))
    target_id: str | None = Field(default=None, sa_column=Column("doi_tuong_id", String(100), nullable=True))
    before_data: dict | None = Field(
        default=None,
        sa_column=Column("du_lieu_truoc", JSON, nullable=True),
    )
    after_data: dict | None = Field(
        default=None,
        sa_column=Column("du_lieu_sau", JSON, nullable=True),
    )
    ip: str | None = Field(default=None, max_length=45)
    user_agent: str | None = Field(default=None, max_length=255)
    status: str = Field(default="SUCCESS", sa_column=Column("trang_thai", String(30), nullable=False))
    detail: str | None = Field(default=None, sa_column=Column("chi_tiet", String(500), nullable=True))


class AuditLogCreate(AuditLogBase):
    """Represent data required to create an audit log entry."""

    pass


class AuditLog(AuditLogBase, table=True):
    """Represent the audit log database table."""

    __tablename__ = "auditlog"

    audit_log_id: int | None = Field(default=None, sa_column=Column("ma_audit_log", Integer, primary_key=True))
    timestamp: datetime = Field(default_factory=get_datetime_utc, sa_column=Column("thoi_gian", DateTime, index=True))


class AuditLogPublic(AppBaseModel, AuditLogBase):
    """Represent audit log data returned by the API."""

    audit_log_id: int
    timestamp: datetime

    @field_serializer("timestamp")
    def _serialize_datetime(self, value: datetime) -> str:
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class AuditLogsPublic(SQLModel):
    """Represent a paginated list of audit log entries."""

    data: list[AuditLogPublic]
    count: int
