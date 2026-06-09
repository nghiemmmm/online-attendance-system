"""
Lich hoc schemas.

Defines response schemas for student study schedules.
"""

from datetime import date, time

from sqlmodel import SQLModel


class LichHocHomNayItem(SQLModel):
    """Mot buoi hoc trong ngay cua sinh vien."""

    ma_lop_hoc_phan: int
    ten_hoc_phan: str | None = None
    phong_hoc: str | None = None
    gio_bat_dau: time | None = None
    gio_ket_thuc: time | None = None


class LichHocHomNayPublic(SQLModel):
    """Danh sach buoi hoc trong ngay cua sinh vien."""

    ma_sinh_vien: int
    ngay_hoc: date
    data: list[LichHocHomNayItem]
    count: int
