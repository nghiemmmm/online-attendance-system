"""
Diem danh summary CRUD operations.

Contains database count queries for student attendance summaries.
"""

from dataclasses import dataclass

from sqlmodel import Session, select

from app.models import BuoiHoc, DangKyHocPhan, DiemDanh, LopHocPhan

PRESENT_ATTENDANCE_STATUSES = {"CO_MAT", "DI_MUON"}


@dataclass(frozen=True)
class AttendanceSemesterCountResult:
    """Attendance counts for one student in one semester."""

    present_count: int
    total_lesson_count: int


def get_registered_class_ids_by_sinh_vien_semester(
    *,
    session: Session,
    ma_sinh_vien: int,
    hoc_ky: int,
    nam_hoc: str,
) -> list[int]:
    """Get active class section ids registered by a student in one semester."""
    statement = (
        select(LopHocPhan.ma_lop_hoc_phan)
        .join(
            DangKyHocPhan,
            DangKyHocPhan.ma_lop_hoc_phan == LopHocPhan.ma_lop_hoc_phan,
        )
        .where(
            DangKyHocPhan.ma_sinh_vien == ma_sinh_vien,
            DangKyHocPhan.trang_thai == True,
            LopHocPhan.hoc_ky == hoc_ky,
            LopHocPhan.nam_hoc == nam_hoc,
        )
    )
    return list(session.exec(statement).all())


def get_lesson_ids_by_class_ids(*, session: Session, class_ids: list[int]) -> list[int]:
    """Get lesson ids belonging to the provided class section ids."""
    if not class_ids:
        return []
    statement = select(BuoiHoc.ma_buoi_hoc).where(
        BuoiHoc.ma_lop_hoc_phan.in_(class_ids)
    )
    return list(session.exec(statement).all())


def count_present_attendance_by_sinh_vien_lessons(
    *,
    session: Session,
    ma_sinh_vien: int,
    lesson_ids: list[int],
) -> int:
    """Count present attendance records for one student in provided lessons."""
    if not lesson_ids:
        return 0
    statement = select(DiemDanh.trang_thai).where(
        DiemDanh.ma_sinh_vien == ma_sinh_vien,
        DiemDanh.ma_buoi_hoc.in_(lesson_ids),
    )
    statuses = session.exec(statement).all()
    return sum(1 for status in statuses if status in PRESENT_ATTENDANCE_STATUSES)


def get_attendance_semester_counts_by_sinh_vien(
    *,
    session: Session,
    ma_sinh_vien: int,
    hoc_ky: int,
    nam_hoc: str,
) -> AttendanceSemesterCountResult:
    """Count present lessons and total lessons for a student in one semester."""
    class_ids = get_registered_class_ids_by_sinh_vien_semester(
        session=session,
        ma_sinh_vien=ma_sinh_vien,
        hoc_ky=hoc_ky,
        nam_hoc=nam_hoc,
    )
    lesson_ids = get_lesson_ids_by_class_ids(session=session, class_ids=class_ids)
    present_count = count_present_attendance_by_sinh_vien_lessons(
        session=session,
        ma_sinh_vien=ma_sinh_vien,
        lesson_ids=lesson_ids,
    )
    return AttendanceSemesterCountResult(
        present_count=present_count,
        total_lesson_count=len(lesson_ids),
    )
