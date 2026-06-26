"""Define attendance summary response models."""

from sqlmodel import SQLModel


class TongBuoiCoMatHocKyPublic(SQLModel):
    """Represent a student's semester attendance summary."""

    ma_sinh_vien: int
    hoc_ky: int
    nam_hoc: str
    so_buoi_co_mat: int
    tong_so_buoi_hoc: int
    ty_le_co_mat: float
    mo_ta: str
