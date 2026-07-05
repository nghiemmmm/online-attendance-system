"""Define attendance evidence image database and response models."""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


def get_datetime_utc() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(UTC)


class AttendanceImageBase(SQLModel):
    """Represent shared attendance evidence image fields."""

    attendance_id: int
    image_path: str | None = Field(default=None, max_length=255)
    confidence: float | None = None

    # Storage Abstraction Fields
    storage_provider: str = Field(default="LOCAL", max_length=30)
    public_id: str | None = Field(default=None, max_length=255)
    secure_url: str | None = Field(default=None, max_length=512)
    version: str | None = Field(default=None, max_length=100)
    file_size: int | None = Field(default=None)
    mime_type: str | None = Field(default=None, max_length=50)
    width: int | None = Field(default=None)
    height: int | None = Field(default=None)


class AttendanceImageCreate(AttendanceImageBase):
    """Represent data required to create an attendance evidence image."""

    pass


class AttendanceImageUpdate(SQLModel):
    """Represent fields that can update an attendance evidence image."""

    image_path: str | None = Field(default=None, max_length=255)
    confidence: float | None = None

    storage_provider: str | None = Field(default=None, max_length=30)
    public_id: str | None = Field(default=None, max_length=255)
    secure_url: str | None = Field(default=None, max_length=512)
    version: str | None = Field(default=None, max_length=100)
    file_size: int | None = Field(default=None)
    mime_type: str | None = Field(default=None, max_length=50)
    width: int | None = Field(default=None)
    height: int | None = Field(default=None)


class AttendanceImage(AttendanceImageBase, table=True):
    """Represent the attendance evidence image database table."""

    __tablename__ = "attendance_images"

    image_id: int | None = Field(default=None, primary_key=True)
    attendance_id: int = Field(foreign_key="attendance.attendance_id")
    created_at: datetime = Field(default_factory=get_datetime_utc)


class AttendanceImagePublic(AttendanceImageBase):
    """Represent attendance evidence image data returned by the API."""

    image_id: int
    created_at: datetime


class AttendanceImagesPublic(SQLModel):
    """Represent a paginated list of attendance evidence images."""

    data: list[AttendanceImagePublic]
    count: int
