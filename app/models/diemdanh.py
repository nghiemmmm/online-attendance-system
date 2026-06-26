"""Define attendance record database and response models."""

from datetime import datetime

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class DiemDanhBase(SQLModel):
    """Represent shared attendance record fields."""

    ma_sinh_vien: int
    ma_buoi_hoc: int
    trang_thai: str = Field(max_length=30)
    phuong_thuc: str = Field(default="KHUON_MAT", max_length=20)
    do_tin_cay: float | None = None
    thoi_diem_diem_danh: datetime | None = None
    ly_do_chinh_sua: str | None = Field(default=None, max_length=255)


class DiemDanhCreate(DiemDanhBase):
    """Represent data required to create an attendance record."""

    pass


class DiemDanhUpdate(SQLModel):
    """Represent fields that can update an attendance record."""

    trang_thai: str | None = Field(default=None, max_length=30)
    phuong_thuc: str | None = Field(default=None, max_length=20)
    do_tin_cay: float | None = None
    thoi_diem_diem_danh: datetime | None = None
    ly_do_chinh_sua: str | None = Field(default=None, max_length=255)


class DiemDanh(DiemDanhBase, table=True):
    """Represent the attendance record database table."""

    __tablename__ = "diemdanh"
    __table_args__ = (
        UniqueConstraint("ma_sinh_vien", "ma_buoi_hoc", name="uq_diemdanh_sv_buoi"),
    )

    ma_diem_danh: int | None = Field(default=None, primary_key=True)
    ma_sinh_vien: int = Field(foreign_key="sinhvien.ma_sinh_vien")
    ma_buoi_hoc: int = Field(foreign_key="buoihoc.ma_buoi_hoc")


class DiemDanhPublic(DiemDanhBase):
    """Represent attendance record data returned by the API."""

    ma_diem_danh: int


class DiemDanhsPublic(SQLModel):
    """Represent a paginated list of attendance records."""

    data: list[DiemDanhPublic]
    count: int
