from datetime import datetime, timezone

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
