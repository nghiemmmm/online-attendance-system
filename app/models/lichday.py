"""Define teaching schedule response models."""

from datetime import date, time

from sqlmodel import SQLModel


class BuoiHocGanDayItem(SQLModel):
    """Represent one recent lesson for a staff dashboard."""

    ma_lop_hoc_phan: int
    ten_hoc_phan: str | None = None
    ngay_hoc: date
    so_sinh_vien_co_mat: int
    so_sinh_vien_di_muon: int
    so_sinh_vien_vang_mat: int


class BuoiHocGanDaysPublic(SQLModel):
    """Represent a list of recent lessons for a staff member."""

    data: list[BuoiHocGanDayItem]
    count: int


class LichDayItem(SQLModel):
    """Represent one teaching schedule row."""

    ma_can_bo: int
    ma_lop_hoc_phan: int
    ma_hoc_phan: int
    ten_hoc_phan: str | None = None
    ma_thoi_khoa_bieu: int | None = None
    ma_buoi_hoc: int | None = None
    ngay_hoc: date | None = None
    thu: int | None = None
    tiet_bat_dau: int | None = None
    tiet_ket_thuc: int | None = None
    gio_bat_dau: time | None = None
    gio_ket_thuc: time | None = None
    hoc_ky: int | None = None
    nam_hoc: str | None = None
    trang_thai_lop: bool
    trang_thai_buoi_hoc: str | None = None
    ghi_chu: str | None = None
    so_buoi: int | None = None


class LichDaysPublic(SQLModel):
    """Represent a filtered list of teaching schedule rows."""

    data: list[LichDayItem]
    count: int


class SoLuongLopHocPhanDangDayPublic(SQLModel):
    """Represent the number of class sections currently taught by staff."""

    ma_can_bo: int
    hoc_ky: int
    nam_hoc: str
    as_of_date: date
    count: int
