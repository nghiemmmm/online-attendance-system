"""
Diem danh summary service.

Contains business logic for student attendance summaries.
"""

from typing import Any
from sqlmodel import Session

from app.crud.diemdanh_summary_crud import (
    get_attendance_semester_counts_by_student,
)
from app.crud.sinhvien_crud import get_student
from app.models import TongBuoiCoMatHocKyPublic
from app.core.exceptions import StudentNotFoundError, LessonNotFoundError, PermissionDeniedError, AppException


def get_semester_present_lesson_total(
    *,
    session: Session,
    ma_sinh_vien: int,
    hoc_ky: int,
    nam_hoc: str,
) -> TongBuoiCoMatHocKyPublic:
    """Build total present attendance summary for a student in one semester."""
    if not get_student(session=session, ma_sinh_vien=ma_sinh_vien):
        raise StudentNotFoundError("Student profile not found")

    counts = get_attendance_semester_counts_by_student(
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


def mark_attendance_automatically_service(
    *,
    session: Session,
    ma_buoi_hoc: int,
    danh_sach_ma_sinh_vien: list[int],
    do_tin_cay_trung_binh: float,
) -> dict:
    """Process automatic attendance marking by Lora/AI."""
    from app.crud import diemdanh_crud
    
    result = diemdanh_crud.mark_attendance_by_lora(
        session=session,
        ma_buoi_hoc=ma_buoi_hoc,
        danh_sach_ma_sinh_vien=danh_sach_ma_sinh_vien,
        do_tin_cay_trung_binh=do_tin_cay_trung_binh,
    )
    if not result.get("success"):
        raise AppException(result.get("message"), status_code=400)
    return result


def mark_attendance_manually_service(
    *,
    session: Session,
    current_account: Any,
    ma_buoi_hoc: int,
    ma_sinh_vien: int,
    trang_thai: str,
    ghi_chu: str | None = None,
) -> Any:
    """Process manual attendance modification by a lecturer."""
    from app.crud import buoihoc_crud, canbo_crud, diemdanh_crud
    from app.models import LopHocPhan

    buoi_hoc = buoihoc_crud.get_buoihoc(session=session, ma_buoi_hoc=ma_buoi_hoc)
    if not buoi_hoc:
        raise LessonNotFoundError("Buổi học không tồn tại")
    
    # Check permissions
    lhp = session.get(LopHocPhan, buoi_hoc.ma_lop_hoc_phan)
    can_bo = canbo_crud.get_staff_member_by_account_id(session=session, ma_tai_khoan=current_account.ma_tai_khoan)
    if current_account.vai_tro != "ADMIN" and (not can_bo or lhp.ma_can_bo != can_bo.ma_can_bo):
        raise PermissionDeniedError("Không có quyền thao tác trên buổi học này")
        
    return diemdanh_crud.mark_attendance_manually(
        session=session,
        ma_buoi_hoc=ma_buoi_hoc,
        ma_sinh_vien=ma_sinh_vien,
        trang_thai=trang_thai,
        ghi_chu=ghi_chu,
    )
