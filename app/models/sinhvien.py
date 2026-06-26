"""Define student profile database and response models."""

from datetime import date, datetime, timezone, time

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


def get_datetime_utc() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(timezone.utc)


class SinhVienBase(SQLModel):
    """Represent shared student profile fields."""

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
    """Represent data required to create a student profile."""

    pass


class SinhVienUpdate(SQLModel):
    """Represent fields that can update a student profile."""

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
    """Represent the student profile database table."""

    __tablename__ = "sinhvien"

    ma_sinh_vien: int | None = Field(default=None, primary_key=True)
    google_email: EmailStr | None = Field(default=None, max_length=100, unique=True)
    ma_nganh: int = Field(foreign_key="nganh.ma_nganh")
    ma_tai_khoan: int | None = Field(
        default=None, foreign_key="taikhoan.ma_tai_khoan", unique=True
    )
    thoi_gian_bat_dau_hoc: datetime = Field(default_factory=get_datetime_utc)


class SinhVienPublic(SinhVienBase):
    """Represent student profile data returned by the API."""

    ma_sinh_vien: int
    thoi_gian_bat_dau_hoc: datetime


class SinhViensPublic(SQLModel):
    """Represent a paginated list of student profiles."""

    data: list[SinhVienPublic]
    count: int


class StudentScheduleItem(SQLModel):
    """Represent schedule item for current student."""

    ma_buoi_hoc: int
    ma_lop_hoc_phan: int
    ma_hoc_phan: int
    ten_hoc_phan: str
    ngay_hoc: date
    gio_bat_dau: time | None = None
    gio_ket_thuc: time | None = None
    trang_thai: str


class StudentSchedulePublic(SQLModel):
    """Represent schedule list for current student."""

    data: list[StudentScheduleItem]
    count: int


class StudentAttendanceItem(SQLModel):
    """Represent attendance record item for current student."""

    ma_diem_danh: int
    ma_lop_hoc_phan: int
    ten_hoc_phan: str
    ngay_hoc: date
    trang_thai: str
    thoi_diem_diem_danh: datetime | None = None
    ghi_chu: str | None = None


class StudentAttendancePublic(SQLModel):
    """Represent attendance list for current student."""

    data: list[StudentAttendanceItem]
    count: int


class StudentAvailableClassItem(SQLModel):
    """Represent available class section item for student course registration."""

    ma_lop_hoc_phan: int
    ma_hoc_phan: int
    ten_hoc_phan: str
    so_tin_chi: int
    ten_giang_vien: str
    hoc_ky: int
    nam_hoc: str
    ty_le_chuyen_can_toi_thieu: float
    is_registered: bool


class StudentAvailableClassPublic(SQLModel):
    """Represent available class section list."""

    data: list[StudentAvailableClassItem]
    count: int

