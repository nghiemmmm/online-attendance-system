from datetime import datetime

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class DiemDanhBase(SQLModel):
    ma_sinh_vien: int
    ma_buoi_hoc: int
    trang_thai: str = Field(max_length=30)
    phuong_thuc: str = Field(default="KHUON_MAT", max_length=20)
    do_tin_cay: float | None = None
    thoi_diem_diem_danh: datetime | None = None
    ly_do_chinh_sua: str | None = Field(default=None, max_length=255)


class DiemDanhCreate(DiemDanhBase):
    pass


class DiemDanhUpdate(SQLModel):
    trang_thai: str | None = Field(default=None, max_length=30)
    phuong_thuc: str | None = Field(default=None, max_length=20)
    do_tin_cay: float | None = None
    thoi_diem_diem_danh: datetime | None = None
    ly_do_chinh_sua: str | None = Field(default=None, max_length=255)


class DiemDanh(DiemDanhBase, table=True):
    __tablename__ = "diemdanh"
    __table_args__ = (
        UniqueConstraint("ma_sinh_vien", "ma_buoi_hoc", name="uq_diemdanh_sv_buoi"),
    )

    ma_diem_danh: int | None = Field(default=None, primary_key=True)
    ma_sinh_vien: int = Field(foreign_key="sinhvien.ma_sinh_vien")
    ma_buoi_hoc: int = Field(foreign_key="buoihoc.ma_buoi_hoc")


class DiemDanhPublic(DiemDanhBase):
    ma_diem_danh: int


class DiemDanhsPublic(SQLModel):
    data: list[DiemDanhPublic]
    count: int
