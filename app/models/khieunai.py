"""Define complaint database and response models."""

from datetime import date, datetime, timezone

from sqlmodel import Field, SQLModel


def get_datetime_utc() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(timezone.utc)


class KhieuNaiBase(SQLModel):
    """Represent shared complaint fields."""

    ma_diem_danh: int
    ma_sinh_vien: int
    ly_do: str = Field(max_length=500)
    trang_thai: str = Field(default="CHO_XU_LY", max_length=30)
    ma_can_bo_xu_ly: int | None = None
    ghi_chu_xu_ly: str | None = Field(default=None, max_length=255)
    ngay_xu_ly: datetime | None = None


class KhieuNaiCreate(SQLModel):
    """Represent data required to create a complaint."""

    ma_diem_danh: int
    ma_sinh_vien: int
    ly_do: str = Field(max_length=500)


class KhieuNaiUpdate(SQLModel):
    """Represent fields that can update a complaint."""

    trang_thai: str | None = Field(default=None, max_length=30)
    ma_can_bo_xu_ly: int | None = None
    ghi_chu_xu_ly: str | None = Field(default=None, max_length=255)
    ngay_xu_ly: datetime | None = None


class KhieuNaiCanXuLyItem(SQLModel):
    """Represent a summary of a complaint pending staff review."""

    ma_khieu_nai: int
    ma_diem_danh: int
    ma_sinh_vien: int
    ho_ten_sinh_vien: str | None = None
    ma_lop_hoc_phan: int
    ten_hoc_phan: str | None = None
    ngay_hoc: date
    trang_thai_diem_danh: str
    ly_do: str
    ngay_gui: datetime
    so_buoi: int | None = None


class KhieuNaiCanXuLysPublic(SQLModel):
    """Represent complaints pending review for one staff member."""

    data: list[KhieuNaiCanXuLyItem]
    count: int


class KhieuNaiCanXuLyDetail(SQLModel):
    """Represent complaint details for staff review."""

    ma_khieu_nai: int
    ma_diem_danh: int
    ma_sinh_vien: int
    ho_ten_sinh_vien: str | None = None
    ma_lop_hoc_phan: int
    ten_hoc_phan: str | None = None
    ngay_hoc: date
    trang_thai_diem_danh: str
    ly_do: str
    trang_thai: str
    ngay_gui: datetime
    ghi_chu_xu_ly: str | None = None
    so_buoi: int | None = None


class KhieuNaiXuLyRequest(SQLModel):
    """Represent staff-provided complaint review data."""

    ghi_chu_xu_ly: str | None = Field(default=None, max_length=255)


class KhieuNaiChapThuanRequest(KhieuNaiXuLyRequest):
    """Represent data used to approve a complaint."""

    trang_thai_diem_danh_moi: str | None = Field(default=None, max_length=30)


class KhieuNaiXuLyResult(SQLModel):
    """Represent the result after staff review a complaint."""

    ma_khieu_nai: int
    trang_thai: str
    ma_can_bo_xu_ly: int
    ghi_chu_xu_ly: str | None = None
    ngay_xu_ly: datetime
    trang_thai_diem_danh: str


class KhieuNai(KhieuNaiBase, table=True):
    """Represent the complaint database table."""

    __tablename__ = "khieunai"

    ma_khieu_nai: int | None = Field(default=None, primary_key=True)
    ma_diem_danh: int = Field(foreign_key="diemdanh.ma_diem_danh")
    ma_sinh_vien: int = Field(foreign_key="sinhvien.ma_sinh_vien")
    ma_can_bo_xu_ly: int | None = Field(default=None, foreign_key="canbo.ma_can_bo")
    ngay_gui: datetime = Field(default_factory=get_datetime_utc)


class KhieuNaiPublic(KhieuNaiBase):
    """Represent complaint data returned by the API."""

    ma_khieu_nai: int
    ngay_gui: datetime
    ma_lop_hoc_phan: int | None = None
    ma_hoc_phan: int | None = None
    ten_hoc_phan: str | None = None
    ngay_hoc: date | None = None
    so_buoi: int | None = None
    trang_thai_diem_danh: str | None = None


class KhieuNaisPublic(SQLModel):
    """Represent a paginated list of complaints."""

    data: list[KhieuNaiPublic]
    count: int


class KhieuNaiChoXuLyMetric(SQLModel):
    """Represent a dashboard metric for pending complaints."""

    so_luong_cho_xu_ly: int
    thoi_diem_thong_ke: datetime
