"""
Diem danh summary schemas.

Defines response schemas for student attendance summary APIs.
"""

from sqlmodel import SQLModel


class TongBuoiCoMatHocKyPublic(SQLModel):
    """Thong ke tong so buoi co mat cua sinh vien trong hoc ky."""

    ma_sinh_vien: int
    hoc_ky: int
    nam_hoc: str
    so_buoi_co_mat: int
    tong_so_buoi_hoc: int
    ty_le_co_mat: float
    mo_ta: str
