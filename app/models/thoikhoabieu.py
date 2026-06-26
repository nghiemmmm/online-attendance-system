"""Define timetable database and response models."""

from datetime import date, time

from sqlalchemy import CheckConstraint
from sqlmodel import Field, SQLModel


class ThoiKhoaBieuBase(SQLModel):
    """Represent shared timetable fields."""

    ma_lop_hoc_phan: int
    thu: int
    tiet_bat_dau: int | None = None
    tiet_ket_thuc: int | None = None
    gio_bat_dau: time | None = None
    gio_ket_thuc: time | None = None
    ngay_bat_dau: date
    ngay_ket_thuc: date


class ThoiKhoaBieuCreate(ThoiKhoaBieuBase):
    """Represent data required to create a timetable entry."""

    pass


class ThoiKhoaBieuUpdate(SQLModel):
    """Represent fields that can update a timetable entry."""

    ma_lop_hoc_phan: int | None = None
    thu: int | None = None
    tiet_bat_dau: int | None = None
    tiet_ket_thuc: int | None = None
    gio_bat_dau: time | None = None
    gio_ket_thuc: time | None = None
    ngay_bat_dau: date | None = None
    ngay_ket_thuc: date | None = None


class ThoiKhoaBieu(ThoiKhoaBieuBase, table=True):
    """Represent the timetable database table."""

    __tablename__ = "thoikhoabieu"
    __table_args__ = (
        CheckConstraint("ngay_bat_dau < ngay_ket_thuc", name="ck_tkb_ngay"),
    )

    ma_thoi_khoa_bieu: int | None = Field(default=None, primary_key=True)
    ma_lop_hoc_phan: int = Field(foreign_key="lophocphan.ma_lop_hoc_phan")


class ThoiKhoaBieuPublic(ThoiKhoaBieuBase):
    """Represent timetable data returned by the API."""

    ma_thoi_khoa_bieu: int


class ThoiKhoaBieusPublic(SQLModel):
    """Represent a paginated list of timetable entries."""

    data: list[ThoiKhoaBieuPublic]
    count: int
