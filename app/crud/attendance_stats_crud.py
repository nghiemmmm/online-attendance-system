"""
Diem danh summary CRUD operations.

Contains database count queries for student attendance summaries.
"""

from dataclasses import dataclass

from sqlmodel import Session, select

from app.models import ClassSession, CourseRegistration, Attendance, ClassSection

PRESENT_ATTENDANCE_STATUSES = {"PRESENT", "LATE", "CO_MAT", "DI_MUON"}


@dataclass(frozen=True)
class AttendanceSemesterCountResult:
    """Attendance counts for one student in one semester."""

    present_count: int
    total_lesson_count: int


def get_registered_class_ids_by_student_semester(
    *,
    session: Session,
    student_id: int,
    semester: int,
    academic_year: str,
) -> list[int]:
    """Get active class section ids registered by a student in one semester."""
    statement = (
        select(ClassSection.class_section_id)
        .join(
            CourseRegistration,
            CourseRegistration.class_section_id == ClassSection.class_section_id,
        )
        .where(
            CourseRegistration.student_id == student_id,
            CourseRegistration.status.is_(True),
            ClassSection.semester == semester,
            ClassSection.academic_year == academic_year,
        )
    )
    return list(session.exec(statement).all())


def get_lesson_ids_by_class_ids(*, session: Session, class_ids: list[int]) -> list[int]:
    """Get lesson ids belonging to the provided class section ids."""
    if not class_ids:
        return []
    statement = select(ClassSession.class_session_id).where(
        ClassSession.class_section_id.in_(class_ids)
    )
    return list(session.exec(statement).all())


def count_present_attendance_by_student_lessons(
    *,
    session: Session,
    student_id: int,
    lesson_ids: list[int],
) -> int:
    """Count present attendance records for one student in provided lessons."""
    if not lesson_ids:
        return 0
    statement = select(Attendance.status).where(
        Attendance.student_id == student_id,
        Attendance.class_session_id.in_(lesson_ids),
    )
    statuses = session.exec(statement).all()
    return sum(1 for status in statuses if status in PRESENT_ATTENDANCE_STATUSES)


def get_attendance_semester_counts_by_student(
    *,
    session: Session,
    student_id: int,
    semester: int,
    academic_year: str,
) -> AttendanceSemesterCountResult:
    """Count present lessons and total lessons for a student in one semester."""
    class_ids = get_registered_class_ids_by_student_semester(
        session=session,
        student_id=student_id,
        semester=semester,
        academic_year=academic_year,
    )
    lesson_ids = get_lesson_ids_by_class_ids(session=session, class_ids=class_ids)
    present_count = count_present_attendance_by_student_lessons(
        session=session,
        student_id=student_id,
        lesson_ids=lesson_ids,
    )
    return AttendanceSemesterCountResult(
        present_count=present_count,
        total_lesson_count=len(lesson_ids),
    )
