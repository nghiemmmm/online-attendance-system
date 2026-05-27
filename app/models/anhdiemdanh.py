from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


class AnhDiemDanhBase(SQLModel):
    ma_diem_danh: int
    duong_dan_anh: str | None = Field(default=None, max_length=255)


class AnhDiemDanhCreate(AnhDiemDanhBase):
    pass


class AnhDiemDanhUpdate(SQLModel):
    duong_dan_anh: str | None = Field(default=None, max_length=255)


class AnhDiemDanh(AnhDiemDanhBase, table=True):
    __tablename__ = "anhdiemdanh"

    ma_anh: int | None = Field(default=None, primary_key=True)
    ma_diem_danh: int = Field(foreign_key="diemdanh.ma_diem_danh")
    ngay_tao: datetime = Field(default_factory=get_datetime_utc)


class AnhDiemDanhPublic(AnhDiemDanhBase):
    ma_anh: int
    ngay_tao: datetime


class AnhDiemDanhsPublic(SQLModel):
    data: list[AnhDiemDanhPublic]
    count: int
