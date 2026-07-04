"""
Canh bao hoc tap CRUD operations.

Contains database queries for student academic warning data.
"""

from dataclasses import dataclass

from sqlmodel import Session, func, select

from app.models import (
    Attendance,
    ClassSection,
    ClassSession,
    Course,
    CourseRegistration,
)

ABSENT_ATTENDANCE_STATUSES = {"VANG", "VANG_MAT"}


@dataclass(frozen=True)
class AbsenceWarningSource:
    """Raw absence warning data for one class section."""

    class_section_id: int
    course_name: str | None
    total_class_sessions: int
    absent_session_count: int


def count_lessons_by_class_section(*, session: Session, class_section_id: int) -> int:
    """Count lessons for one class section."""
    statement = (
        select(func.count())
        .select_from(ClassSession)
        .where(ClassSession.class_section_id == class_section_id)
    )
    return session.exec(statement).one()


def count_absences_by_student_and_class_section(
    *,
    session: Session,
    student_id: int,
    class_section_id: int,
) -> int:
    """Count absent attendance records for one student in one class section."""
    statement = (
        select(func.count())
        .select_from(Attendance)
        .join(
            ClassSession, Attendance.class_session_id == ClassSession.class_session_id
        )
        .where(
            Attendance.student_id == student_id,
            ClassSession.class_section_id == class_section_id,
            Attendance.status.in_(ABSENT_ATTENDANCE_STATUSES),
        )
    )
    return session.exec(statement).one()


def get_absence_warning_sources_by_student(
    *,
    session: Session,
    student_id: int,
) -> list[AbsenceWarningSource]:
    """Lay du lieu diem danh de tinh canh bao vang cua sinh vien."""
    statement = (
        select(ClassSection, Course)
        .join(
            CourseRegistration,
            CourseRegistration.class_section_id == ClassSection.class_section_id,
        )
        .join(Course, ClassSection.course_id == Course.course_id)
        .where(
            CourseRegistration.student_id == student_id,
            CourseRegistration.status.is_(True),
            ClassSection.status.is_(True),
        )
        .order_by(ClassSection.class_section_id)
    )
    rows = session.exec(statement).all()
    sources: list[AbsenceWarningSource] = []

    for class_section, course in rows:
        total_class_sessions = count_lessons_by_class_section(
            session=session,
            class_section_id=class_section.class_section_id,
        )
        absent_session_count = count_absences_by_student_and_class_section(
            session=session,
            student_id=student_id,
            class_section_id=class_section.class_section_id,
        )
        sources.append(
            AbsenceWarningSource(
                class_section_id=class_section.class_section_id,
                course_name=course.course_name,
                total_class_sessions=total_class_sessions,
                absent_session_count=absent_session_count,
            )
        )

    return sources
