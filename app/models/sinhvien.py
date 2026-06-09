from datetime import date, datetime, timezone

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


class SinhVienBase(SQLModel):
    ho: str = Field(max_length=50)
    ten: str = Field(max_length=50)
    ngay_sinh: date | None = None
    gioi_tinh: str | None = Field(default=None, max_length=10)
    dien_thoai: str | None = Field(default=None, max_length=15)
    google_email: EmailStr | None = Field(default=None, max_length=100)
    ma_nganh: int
    ma_tai_khoan: int | None = None
    trang_thai_hoc: bool = True


class SinhVienCreate(SinhVienBase):
    pass


class SinhVienUpdate(SQLModel):
    ho: str | None = Field(default=None, max_length=50)
    ten: str | None = Field(default=None, max_length=50)
    ngay_sinh: date | None = None
    gioi_tinh: str | None = Field(default=None, max_length=10)
    dien_thoai: str | None = Field(default=None, max_length=15)
    google_email: EmailStr | None = Field(default=None, max_length=100)
    ma_nganh: int | None = None
    ma_tai_khoan: int | None = None
    trang_thai_hoc: bool | None = None


class SinhVien(SinhVienBase, table=True):
    __tablename__ = "sinhvien"

    ma_sinh_vien: int | None = Field(default=None, primary_key=True)
    google_email: EmailStr | None = Field(default=None, max_length=100, unique=True)
    ma_nganh: int = Field(foreign_key="nganh.ma_nganh")
    ma_tai_khoan: int | None = Field(
        default=None, foreign_key="taikhoan.ma_tai_khoan", unique=True
    )
    thoi_gian_bat_dau_hoc: datetime = Field(default_factory=get_datetime_utc)


class SinhVienPublic(SinhVienBase):
    ma_sinh_vien: int
    thoi_gian_bat_dau_hoc: datetime


class SinhViensPublic(SQLModel):
    data: list[SinhVienPublic]
    count: int
