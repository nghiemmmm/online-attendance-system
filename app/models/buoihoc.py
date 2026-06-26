"""Define lesson database and response models."""

from datetime import date, time

from sqlmodel import Field, SQLModel


class BuoiHocBase(SQLModel):
    """Represent shared lesson fields."""

    ma_lop_hoc_phan: int
    ngay_hoc: date
    gio_bat_dau: time | None = None
    gio_ket_thuc: time | None = None
    so_buoi: int | None = None
    trang_thai: str | None = Field(default=None, max_length=20)
    nguong_nhan_dien: float = 0.5
    so_phut_muon_toi_da: int = 15
    ghi_chu: str | None = Field(default=None, max_length=255)


class BuoiHocCreate(BuoiHocBase):
    """Represent data required to create a lesson."""

    pass


class BuoiHocUpdate(SQLModel):
    """Represent fields that can update a lesson."""

    ma_lop_hoc_phan: int | None = None
    ngay_hoc: date | None = None
    gio_bat_dau: time | None = None
    gio_ket_thuc: time | None = None
    so_buoi: int | None = None
    trang_thai: str | None = Field(default=None, max_length=20)
    nguong_nhan_dien: float | None = None
    so_phut_muon_toi_da: int | None = None
    ghi_chu: str | None = Field(default=None, max_length=255)


class BuoiHoc(BuoiHocBase, table=True):
    """Represent the lesson database table."""

    __tablename__ = "buoihoc"

    ma_buoi_hoc: int | None = Field(default=None, primary_key=True)
    ma_lop_hoc_phan: int = Field(foreign_key="lophocphan.ma_lop_hoc_phan")


class BuoiHocPublic(BuoiHocBase):
    """Represent lesson data returned by the API."""

    ma_buoi_hoc: int


class BuoiHocsPublic(SQLModel):
    """Represent a paginated list of lessons."""

    data: list[BuoiHocPublic]
    count: int
