"""Define staff profile database and response models."""

from datetime import date

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class CanBoBase(SQLModel):
    """Represent shared staff profile fields."""

    ho: str = Field(max_length=50)
    ten: str = Field(max_length=50)
    dien_thoai: str | None = Field(default=None, max_length=15)
    gioi_tinh: str | None = Field(default=None, max_length=10)
    ngay_sinh: date | None = None
    google_email: EmailStr | None = Field(default=None, max_length=100)
    ma_tai_khoan: int | None = None
    chuc_vu: str | None = Field(default=None, max_length=50)
    trang_thai: bool = True


class CanBoCreate(CanBoBase):
    """Represent data required to create a staff profile."""

    pass


class CanBoUpdate(SQLModel):
    """Represent fields that can update a staff profile."""

    ho: str | None = Field(default=None, max_length=50)
    ten: str | None = Field(default=None, max_length=50)
    dien_thoai: str | None = Field(default=None, max_length=15)
    gioi_tinh: str | None = Field(default=None, max_length=10)
    ngay_sinh: date | None = None
    google_email: EmailStr | None = Field(default=None, max_length=100)
    ma_tai_khoan: int | None = None
    chuc_vu: str | None = Field(default=None, max_length=50)
    trang_thai: bool | None = None


class CanBo(CanBoBase, table=True):
    """Represent the staff profile database table."""

    __tablename__ = "canbo"

    ma_can_bo: int | None = Field(default=None, primary_key=True)
    google_email: EmailStr | None = Field(default=None, max_length=100, unique=True)
    ma_tai_khoan: int | None = Field(
        default=None, foreign_key="taikhoan.ma_tai_khoan", unique=True
    )


class CanBoPublic(CanBoBase):
    """Represent staff profile data returned by the API."""

    ma_can_bo: int


class CanBosPublic(SQLModel):
    """Represent a paginated list of staff profiles."""

    data: list[CanBoPublic]
    count: int


class StaffClassSectionItem(SQLModel):
    """Represent class section details taught by a staff member."""

    ma_lop_hoc_phan: int
    ma_hoc_phan: int
    ten_hoc_phan: str
    hoc_ky: int
    nam_hoc: str
    trang_thai: bool
    si_so_hien_tai: int


class StaffClassSectionsPublic(SQLModel):
    """Represent list of class sections taught by a staff member."""

    data: list[StaffClassSectionItem]
    count: int


class AttendanceReportDataPoint(SQLModel):
    """Represent attendance stats for a single completed lesson."""

    date: str
    present: int
    late: int
    absent: int


class StaffAttendanceReportItem(SQLModel):
    """Represent overall attendance report for a class section taught by staff."""

    id: str
    subjectCode: str
    subjectName: str
    totalStudents: int
    completedSessions: int
    totalSessions: int
    averageAttendanceRate: float
    dataPoints: list[AttendanceReportDataPoint]

