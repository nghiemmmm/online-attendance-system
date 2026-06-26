"""Define student study schedule response models."""

from datetime import date, time

from sqlmodel import SQLModel


class LichHocHomNayItem(SQLModel):
    """Represent one lesson in a student's daily schedule."""

    ma_lop_hoc_phan: int
    ten_hoc_phan: str | None = None
    phong_hoc: str | None = None
    gio_bat_dau: time | None = None
    gio_ket_thuc: time | None = None


class LichHocHomNayPublic(SQLModel):
    """Represent a student's daily schedule."""

    ma_sinh_vien: int
    ngay_hoc: date
    data: list[LichHocHomNayItem]
    count: int
