"""Define attendance evidence image database and response models."""

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def get_datetime_utc() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(timezone.utc)


class AnhDiemDanhBase(SQLModel):
    """Represent shared attendance evidence image fields."""

    ma_diem_danh: int
    duong_dan_anh: str | None = Field(default=None, max_length=255)
    do_tin_cay: float | None = None


class AnhDiemDanhCreate(AnhDiemDanhBase):
    """Represent data required to create an attendance evidence image."""

    pass


class AnhDiemDanhUpdate(SQLModel):
    """Represent fields that can update an attendance evidence image."""

    duong_dan_anh: str | None = Field(default=None, max_length=255)
    do_tin_cay: float | None = None


class AnhDiemDanh(AnhDiemDanhBase, table=True):
    """Represent the attendance evidence image database table."""

    __tablename__ = "anhdiemdanh"

    ma_anh: int | None = Field(default=None, primary_key=True)
    ma_diem_danh: int = Field(foreign_key="diemdanh.ma_diem_danh")
    ngay_tao: datetime = Field(default_factory=get_datetime_utc)


class AnhDiemDanhPublic(AnhDiemDanhBase):
    """Represent attendance evidence image data returned by the API."""

    ma_anh: int
    ngay_tao: datetime


class AnhDiemDanhsPublic(SQLModel):
    """Represent a paginated list of attendance evidence images."""

    data: list[AnhDiemDanhPublic]
    count: int
