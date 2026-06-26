"""Define academic warning response models."""

from sqlmodel import SQLModel


class CanhBaoVangItem(SQLModel):
    """Represent one course with an absence warning."""

    ma_lop_hoc_phan: int
    ten_hoc_phan: str | None = None
    tong_so_buoi_hoc: int
    so_buoi_vang: int
    ty_le_vang: float
    nguong_canh_bao: float
    trang_thai_canh_bao: str


class CanhBaoVangPublic(SQLModel):
    """Represent absence warning data for one student."""

    ma_sinh_vien: int
    data: list[CanhBaoVangItem]
    count: int
