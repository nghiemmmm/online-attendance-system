"""
Lich hoc CRUD operations.

Contains database queries for student study schedules.
"""

from datetime import date

from sqlmodel import Session, select

from app.models import (
    BuoiHoc,
    DangKyHocPhan,
    HocPhan,
    LichHocHomNayItem,
    LopHocPhan,
)


def get_today_schedule_by_student(
    *,
    session: Session,
    ma_sinh_vien: int,
    target_date: date,
) -> tuple[list[LichHocHomNayItem], int]:
    """Lay danh sach buoi hoc trong ngay cua sinh vien."""
    statement = (
        select(BuoiHoc, LopHocPhan, HocPhan)
        .join(LopHocPhan, BuoiHoc.ma_lop_hoc_phan == LopHocPhan.ma_lop_hoc_phan)
        .join(HocPhan, LopHocPhan.ma_hoc_phan == HocPhan.ma_hoc_phan)
        .join(
            DangKyHocPhan,
            DangKyHocPhan.ma_lop_hoc_phan == LopHocPhan.ma_lop_hoc_phan,
        )
        .where(
            DangKyHocPhan.ma_sinh_vien == ma_sinh_vien,
            DangKyHocPhan.trang_thai.is_(True),
            LopHocPhan.trang_thai.is_(True),
            BuoiHoc.ngay_hoc == target_date,
        )
        .order_by(BuoiHoc.gio_bat_dau, LopHocPhan.ma_lop_hoc_phan)
    )

    rows = session.exec(statement).all()
    items = [
        LichHocHomNayItem(
            ma_lop_hoc_phan=lop_hoc_phan.ma_lop_hoc_phan,
            ten_hoc_phan=hoc_phan.ten_hoc_phan,
            phong_hoc=None,
            gio_bat_dau=buoi_hoc.gio_bat_dau,
            gio_ket_thuc=buoi_hoc.gio_ket_thuc,
        )
        for buoi_hoc, lop_hoc_phan, hoc_phan in rows
    ]
    return items, len(items)
