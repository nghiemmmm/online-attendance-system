from datetime import datetime, timezone

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


class AuditLogBase(SQLModel):
    ma_tai_khoan: int | None = Field(default=None, foreign_key="taikhoan.ma_tai_khoan")
    vai_tro: str | None = Field(default=None, max_length=20)
    hanh_dong: str = Field(max_length=100)
    doi_tuong: str | None = Field(default=None, max_length=100)
    doi_tuong_id: str | None = Field(default=None, max_length=100)
    du_lieu_truoc: dict | None = Field(default=None, sa_column=Column(JSON, nullable=True))
    du_lieu_sau: dict | None = Field(default=None, sa_column=Column(JSON, nullable=True))
    ip: str | None = Field(default=None, max_length=45)
    user_agent: str | None = Field(default=None, max_length=255)
    trang_thai: str = Field(default="SUCCESS", max_length=30)
    chi_tiet: str | None = Field(default=None, max_length=500)


class AuditLogCreate(AuditLogBase):
    pass


class AuditLog(AuditLogBase, table=True):
    __tablename__ = "auditlog"

    ma_audit_log: int | None = Field(default=None, primary_key=True)
    thoi_gian: datetime = Field(default_factory=get_datetime_utc, index=True)


class AuditLogPublic(AuditLogBase):
    ma_audit_log: int
    thoi_gian: datetime


class AuditLogsPublic(SQLModel):
    data: list[AuditLogPublic]
    count: int
