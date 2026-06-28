"""
Diem danh summary service.

Contains business logic for student attendance summaries.
"""

from typing import Any
from sqlmodel import Session

from app.crud.attendance_stats_crud import (
    get_attendance_semester_counts_by_student,
)
from app.crud.student_crud import get_student
from app.models import SemesterAttendanceSummaryPublic
from app.core.exceptions import StudentNotFoundError, LessonNotFoundError, PermissionDeniedError, AppException


def get_semester_present_lesson_total(
    *,
    session: Session,
    student_id: int,
    semester: int,
    academic_year: str,
) -> SemesterAttendanceSummaryPublic:
    """Build total present attendance summary for a student in one semester."""
    if not get_student(session=session, student_id=student_id):
        raise StudentNotFoundError("Student profile not found")

    counts = get_attendance_semester_counts_by_student(
        session=session,
        student_id=student_id,
        semester=semester,
        academic_year=academic_year,
    )
    attendance_rate = (
        0.0
        if counts.total_lesson_count == 0
        else round(counts.present_count / counts.total_lesson_count * 100, 2)
    )
    return SemesterAttendanceSummaryPublic(
        student_id=student_id,
        semester=semester,
        academic_year=academic_year,
        present_session_count=counts.present_count,
        total_class_sessions=counts.total_lesson_count,
        attendance_rate=attendance_rate,
        description=f"{counts.present_count}/{counts.total_lesson_count} buổi trong học kỳ",
    )


def mark_attendance_automatically_service(
    *,
    session: Session,
    class_session_id: int,
    student_ids: list[int],
    average_confidence: float,
) -> dict:
    """Process automatic attendance marking by Lora/AI."""
    from app.crud import attendance_crud

    result = attendance_crud.mark_attendance_by_lora(
        session=session,
        class_session_id=class_session_id,
        student_ids=student_ids,
        average_confidence=average_confidence,
    )
    if not result.get("success"):
        raise AppException(result.get("message"), status_code=400)
    return result


def mark_attendance_manually_service(
    *,
    session: Session,
    current_account: Any,
    class_session_id: int,
    student_id: int,
    status: str,
    note: str | None = None,
) -> Any:
    """Process manual attendance modification by a lecturer."""
    from app.crud import class_session_crud, staff_crud, attendance_crud
    from app.models import ClassSection

    class_session = class_session_crud.get_class_session(session=session, class_session_id=class_session_id)
    if not class_session:
        raise LessonNotFoundError("Buổi học không tồn tại")

    # Check permissions
    class_section = session.get(ClassSection, class_session.class_section_id)
    staff = staff_crud.get_staff_member_by_account_id(session=session, account_id=current_account.account_id)
    if current_account.role != "ADMIN" and (
        not staff or class_section.staff_id != staff.staff_id
    ):
        raise PermissionDeniedError("Không có quyền thao tác trên buổi học này")

    return attendance_crud.mark_attendance_manually(
        session=session,
        class_session_id=class_session_id,
        student_id=student_id,
        status=status,
        note=note,
    )
