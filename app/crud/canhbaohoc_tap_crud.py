"""
Canh bao hoc tap CRUD operations.

Contains database queries for student academic warning data.
"""

from dataclasses import dataclass

from sqlmodel import Session, func, select

from app.models import BuoiHoc, DangKyHocPhan, DiemDanh, HocPhan, LopHocPhan

ABSENT_ATTENDANCE_STATUSES = {"VANG", "VANG_MAT"}


@dataclass(frozen=True)
class AbsenceWarningSource:
    """Raw absence warning data for one class section."""

    ma_lop_hoc_phan: int
    ten_hoc_phan: str | None
    tong_so_buoi_hoc: int
    so_buoi_vang: int


def count_buoi_hoc_by_lop_hoc_phan(
    *, session: Session, ma_lop_hoc_phan: int
) -> int:
    """Count lessons for one class section."""
    statement = (
        select(func.count())
        .select_from(BuoiHoc)
        .where(BuoiHoc.ma_lop_hoc_phan == ma_lop_hoc_phan)
    )
    return session.exec(statement).one()


def count_buoi_vang_by_sinh_vien_and_lop_hoc_phan(
    *,
    session: Session,
    ma_sinh_vien: int,
    ma_lop_hoc_phan: int,
) -> int:
    """Count absent attendance records for one student in one class section."""
    statement = (
        select(func.count())
        .select_from(DiemDanh)
        .join(BuoiHoc, DiemDanh.ma_buoi_hoc == BuoiHoc.ma_buoi_hoc)
        .where(
            DiemDanh.ma_sinh_vien == ma_sinh_vien,
            BuoiHoc.ma_lop_hoc_phan == ma_lop_hoc_phan,
            DiemDanh.trang_thai.in_(ABSENT_ATTENDANCE_STATUSES),
        )
    )
    return session.exec(statement).one()


def get_absence_warning_sources_by_sinh_vien(
    *,
    session: Session,
    ma_sinh_vien: int,
) -> list[AbsenceWarningSource]:
    """Lay du lieu diem danh de tinh canh bao vang cua sinh vien."""
    statement = (
        select(LopHocPhan, HocPhan)
        .join(
            DangKyHocPhan,
            DangKyHocPhan.ma_lop_hoc_phan == LopHocPhan.ma_lop_hoc_phan,
        )
        .join(HocPhan, LopHocPhan.ma_hoc_phan == HocPhan.ma_hoc_phan)
        .where(
            DangKyHocPhan.ma_sinh_vien == ma_sinh_vien,
            DangKyHocPhan.trang_thai == True,
            LopHocPhan.trang_thai == True,
        )
        .order_by(LopHocPhan.ma_lop_hoc_phan)
    )
    rows = session.exec(statement).all()
    sources: list[AbsenceWarningSource] = []

    for lop_hoc_phan, hoc_phan in rows:
        tong_so_buoi_hoc = count_buoi_hoc_by_lop_hoc_phan(
            session=session,
            ma_lop_hoc_phan=lop_hoc_phan.ma_lop_hoc_phan,
        )
        so_buoi_vang = count_buoi_vang_by_sinh_vien_and_lop_hoc_phan(
            session=session,
            ma_sinh_vien=ma_sinh_vien,
            ma_lop_hoc_phan=lop_hoc_phan.ma_lop_hoc_phan,
        )
        sources.append(
            AbsenceWarningSource(
                ma_lop_hoc_phan=lop_hoc_phan.ma_lop_hoc_phan,
                ten_hoc_phan=hoc_phan.ten_hoc_phan,
                tong_so_buoi_hoc=tong_so_buoi_hoc,
                so_buoi_vang=so_buoi_vang,
            )
        )

    return sources
