"""
Diem danh summary service.

Contains business logic for student attendance summaries.
"""

from fastapi import HTTPException, status
from sqlmodel import Session

from app.crud.diemdanh_summary_crud import (
    get_attendance_semester_counts_by_sinh_vien,
)
from app.crud.sinhvien_crud import get_sinh_vien
from app.models import TongBuoiCoMatHocKyPublic


def get_tong_buoi_co_mat_hoc_ky(
    *,
    session: Session,
    ma_sinh_vien: int,
    hoc_ky: int,
    nam_hoc: str,
) -> TongBuoiCoMatHocKyPublic:
    """Build total present attendance summary for a student in one semester."""
    if not get_sinh_vien(session=session, ma_sinh_vien=ma_sinh_vien):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    counts = get_attendance_semester_counts_by_sinh_vien(
        session=session,
        ma_sinh_vien=ma_sinh_vien,
        hoc_ky=hoc_ky,
        nam_hoc=nam_hoc,
    )
    ty_le_co_mat = (
        0.0
        if counts.total_lesson_count == 0
        else round(counts.present_count / counts.total_lesson_count * 100, 2)
    )
    return TongBuoiCoMatHocKyPublic(
        ma_sinh_vien=ma_sinh_vien,
        hoc_ky=hoc_ky,
        nam_hoc=nam_hoc,
        so_buoi_co_mat=counts.present_count,
        tong_so_buoi_hoc=counts.total_lesson_count,
        ty_le_co_mat=ty_le_co_mat,
        mo_ta=f"{counts.present_count}/{counts.total_lesson_count} buổi trong học kỳ",
    )
