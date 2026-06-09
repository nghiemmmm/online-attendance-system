"""
Attendance summary CRUD operations.

Handles database count queries for teacher monthly attendance statistics.
"""

from dataclasses import dataclass
from datetime import date

from sqlmodel import Session, select

from app.models import BuoiHoc, DiemDanh, LopHocPhan

PRESENT_ATTENDANCE_STATUSES = {"CO_MAT", "DI_MUON"}


@dataclass(frozen=True)
class AttendanceCountResult:
    """
    Attendance counts for one date range.

    Attributes:
        present_count: Number of attendance records counted as present.
        total_count: Total attendance records in the period.
    """

    present_count: int
    total_count: int


def get_attendance_counts_for_teacher(
    *,
    session: Session,
    ma_can_bo: int,
    start_date: date,
    end_date: date,
) -> AttendanceCountResult:
    """
    Count attendance records for classes taught by a teacher in a date range.

    Args:
        session: Database session.
        ma_can_bo: Teacher/staff identifier.
        start_date: Inclusive start date.
        end_date: Exclusive end date.

    Returns:
        AttendanceCountResult containing present and total attendance records.
    """
    base_statement = (
        select(DiemDanh.trang_thai)
        .join(BuoiHoc, DiemDanh.ma_buoi_hoc == BuoiHoc.ma_buoi_hoc)
        .join(LopHocPhan, BuoiHoc.ma_lop_hoc_phan == LopHocPhan.ma_lop_hoc_phan)
        .where(
            LopHocPhan.ma_can_bo == ma_can_bo,
            BuoiHoc.ngay_hoc >= start_date,
            BuoiHoc.ngay_hoc < end_date,
        )
    )
    attendance_statuses = session.exec(base_statement).all()
    present_count = sum(
        1 for status in attendance_statuses if status in PRESENT_ATTENDANCE_STATUSES
    )
    return AttendanceCountResult(
        present_count=present_count,
        total_count=len(attendance_statuses),
    )
