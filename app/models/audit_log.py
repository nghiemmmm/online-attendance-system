"""Define audit log database and response models."""

from datetime import datetime, timezone

from pydantic import field_serializer
from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel

from app.models.base import AppBaseModel


def get_datetime_utc() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(timezone.utc)


class AuditLogBase(SQLModel):
    """Represent shared audit log fields."""

    account_id: int | None = Field(default=None, foreign_key="accounts.account_id")
    role: str | None = Field(default=None, max_length=20)
    action: str = Field(max_length=100)
    target_type: str | None = Field(default=None, max_length=100)
    target_id: str | None = Field(default=None, max_length=100)
    before_data: dict | None = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    after_data: dict | None = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    ip: str | None = Field(default=None, max_length=45)
    user_agent: str | None = Field(default=None, max_length=255)
    status: str = Field(default="SUCCESS", max_length=30)
    detail: str | None = Field(default=None, max_length=500)


class AuditLogCreate(AuditLogBase):
    """Represent data required to create an audit log entry."""

    pass


class AuditLog(AuditLogBase, table=True):
    """Represent the audit log database table."""

    __tablename__ = "auditlog"

    audit_log_id: int | None = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=get_datetime_utc, index=True)


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
