"""
Canh bao hoc tap schemas.

Defines response schemas for student academic warnings.
"""

from sqlmodel import SQLModel


class CanhBaoVangItem(SQLModel):
    """Mot mon hoc co canh bao vang cua sinh vien."""

    ma_lop_hoc_phan: int
    ten_hoc_phan: str | None = None
    tong_so_buoi_hoc: int
    so_buoi_vang: int
    ty_le_vang: float
    nguong_canh_bao: float
    trang_thai_canh_bao: str


class CanhBaoVangPublic(SQLModel):
    """Danh sach mon hoc co canh bao vang cua sinh vien."""

    ma_sinh_vien: int
    data: list[CanhBaoVangItem]
    count: int
