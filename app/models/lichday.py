from datetime import date, time

from sqlmodel import SQLModel


class BuoiHocGanDayItem(SQLModel):
    """Mot buoi hoc gan day cua can bo dung cho dashboard."""

    ma_lop_hoc_phan: int
    ten_hoc_phan: str | None = None
    ngay_hoc: date
    so_sinh_vien_co_mat: int
    so_sinh_vien_di_muon: int
    so_sinh_vien_vang_mat: int


class BuoiHocGanDaysPublic(SQLModel):
    """Danh sach buoi hoc gan day cua can bo."""

    data: list[BuoiHocGanDayItem]
    count: int


class LichDayItem(SQLModel):
    """Một dòng lịch dạy của cán bộ, gồm lớp học phần, lịch mẫu và buổi học thực tế."""

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
    """Danh sách lịch dạy của cán bộ kèm tổng số bản ghi sau khi lọc."""

    data: list[LichDayItem]
    count: int


class SoLuongLopHocPhanDangDayPublic(SQLModel):
    """Số lượng lớp học phần cán bộ đang giảng dạy trong học kỳ hiện tại."""

    ma_can_bo: int
    hoc_ky: int
    nam_hoc: str
    as_of_date: date
    count: int
