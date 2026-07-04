"""Define attendance record database and response models."""

from datetime import UTC, datetime

from pydantic import field_serializer
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel

from app.models.base import AppBaseModel


class AttendanceBase(SQLModel):
    """Represent shared attendance record fields."""

    student_id: int
    class_session_id: int
    status: str = Field(max_length=30)
    method: str = Field(default="KHUON_MAT", max_length=20)
    confidence: float | None = None
    attendance_time: datetime | None = None
    edit_reason: str | None = Field(default=None, max_length=255)


class AttendanceCreate(AttendanceBase):
    """Represent data required to create an attendance record."""

    pass


class AttendanceUpdate(SQLModel):
    """Represent fields that can update an attendance record."""

    status: str | None = Field(default=None, max_length=30)
    method: str | None = Field(default=None, max_length=20)
    confidence: float | None = None
    attendance_time: datetime | None = None
    edit_reason: str | None = Field(default=None, max_length=255)


class Attendance(AttendanceBase, table=True):
    """Represent the attendance record database table."""

    __tablename__ = "attendance"
    __table_args__ = (
        UniqueConstraint(
            "student_id", "class_session_id", name="uq_attendance_student_session"
        ),
    )

    attendance_id: int | None = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="students.student_id")
    class_session_id: int = Field(foreign_key="class_sessions.class_session_id")


class AttendancePublic(AppBaseModel, AttendanceBase):
    """Represent attendance record data returned by the API."""

    attendance_id: int

    @field_serializer("attendance_time")
    def _serialize_datetime(self, value: datetime | None) -> str | None:
        if value is None:
            return None
        return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


class AttendancesPublic(SQLModel):
    """Represent a paginated list of attendance records."""

    data: list[AttendancePublic]
    count: int
