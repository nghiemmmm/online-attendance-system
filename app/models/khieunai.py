from datetime import date, datetime, timezone

from sqlmodel import Field, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


class KhieuNaiBase(SQLModel):
    ma_diem_danh: int
    ma_sinh_vien: int
    ly_do: str = Field(max_length=500)
    trang_thai: str = Field(default="CHO_XU_LY", max_length=30)
    ma_can_bo_xu_ly: int | None = None
    ghi_chu_xu_ly: str | None = Field(default=None, max_length=255)
    ngay_xu_ly: datetime | None = None


class KhieuNaiCreate(SQLModel):
    ma_diem_danh: int
    ma_sinh_vien: int
    ly_do: str = Field(max_length=500)


class KhieuNaiUpdate(SQLModel):
    trang_thai: str | None = Field(default=None, max_length=30)
    ma_can_bo_xu_ly: int | None = None
    ghi_chu_xu_ly: str | None = Field(default=None, max_length=255)
    ngay_xu_ly: datetime | None = None


class KhieuNaiCanXuLyItem(SQLModel):
    """Thong tin rut gon cua khieu nai can xu ly."""

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


class KhieuNaiCanXuLysPublic(SQLModel):
    """Danh sach khieu nai can xu ly cua can bo."""

    data: list[KhieuNaiCanXuLyItem]
    count: int


class KhieuNaiCanXuLyDetail(SQLModel):
    """Chi tiet khieu nai can xu ly cua can bo."""

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


class KhieuNaiXuLyRequest(SQLModel):
    """Du lieu can bo gui len khi xu ly khieu nai."""

    ghi_chu_xu_ly: str | None = Field(default=None, max_length=255)


class KhieuNaiChapThuanRequest(KhieuNaiXuLyRequest):
    """Du lieu chap thuan khieu nai va cap nhat diem danh neu can."""

    trang_thai_diem_danh_moi: str | None = Field(default=None, max_length=30)


class KhieuNaiXuLyResult(SQLModel):
    """Ket qua sau khi can bo xu ly khieu nai."""

    ma_khieu_nai: int
    trang_thai: str
    ma_can_bo_xu_ly: int
    ghi_chu_xu_ly: str | None = None
    ngay_xu_ly: datetime
    trang_thai_diem_danh: str


class KhieuNai(KhieuNaiBase, table=True):
    __tablename__ = "khieunai"

    ma_khieu_nai: int | None = Field(default=None, primary_key=True)
    ma_diem_danh: int = Field(foreign_key="diemdanh.ma_diem_danh")
    ma_sinh_vien: int = Field(foreign_key="sinhvien.ma_sinh_vien")
    ma_can_bo_xu_ly: int | None = Field(default=None, foreign_key="canbo.ma_can_bo")
    ngay_gui: datetime = Field(default_factory=get_datetime_utc)


class KhieuNaiPublic(KhieuNaiBase):
    ma_khieu_nai: int
    ngay_gui: datetime


class KhieuNaisPublic(SQLModel):
    data: list[KhieuNaiPublic]
    count: int


class KhieuNaiChoXuLyMetric(SQLModel):
    """Chỉ số dashboard cho số lượng khiếu nại đang chờ xử lý."""

    so_luong_cho_xu_ly: int
    thoi_diem_thong_ke: datetime
