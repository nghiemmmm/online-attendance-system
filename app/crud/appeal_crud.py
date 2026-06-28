"""
Appeal CRUD operations.

Contains database queries related to complaint records and complaint metrics.
"""

from datetime import datetime

from sqlmodel import Session, func, select

from app.models import (
    ClassSession,
    Attendance,
    Course,
    Appeal,
    PendingAppealDetail,
    PendingAppealItem,
    ClassSection,
    Student,
)

PENDING_STATUS = "CHO_XU_LY"
APPROVED_STATUS = "DA_CHAP_THUAN"
REJECTED_STATUS = "DA_TU_CHOI"


def count_pending_appeals_by_staff(
    *, session: Session, staff_id: int
) -> int:
    """
    Count pending complaints in classes taught by a staff member.

    Args:
        session: Database session.
        staff_id: Staff/teacher identifier.

    Returns:
        Number of pending complaints for class sections owned by the staff member.
    """
    statement = (
        select(func.count())
        .select_from(Appeal)
        .join(Attendance, Appeal.attendance_id == Attendance.attendance_id)
        .join(ClassSession, Attendance.class_session_id == ClassSession.class_session_id)
        .join(ClassSection, ClassSession.class_section_id == ClassSection.class_section_id)
        .where(
            ClassSection.staff_id == staff_id,
            Appeal.status == PENDING_STATUS,
            Appeal.resolved_at.is_(None),
        )
    )
    return session.exec(statement).one()


def build_student_full_name(student: Student | None) -> str | None:
    """Build student full name for complaint response data."""
    if not student:
        return None
    return " ".join(part for part in [student.last_name, student.first_name] if part)


def build_actionable_appeal_item(
    *,
    appeal: Appeal,
    attendance: Attendance,
    class_session: ClassSession,
    class_section: ClassSection,
    course: Course | None,
    student: Student | None,
) -> PendingAppealItem:
    """Map joined complaint data to a pending complaint list item."""
    return PendingAppealItem(
        appeal_id=appeal.appeal_id,
        attendance_id=appeal.attendance_id,
        student_id=appeal.student_id,
        student_full_name=build_student_full_name(student),
        class_section_id=class_section.class_section_id,
        course_name=course.course_name if course else None,
        class_date=class_session.class_date,
        attendance_status=attendance.status,
        reason=appeal.reason,
        submitted_at=appeal.submitted_at,
        session_number=class_session.session_number,
    )


def build_actionable_appeal_detail(
    *,
    appeal: Appeal,
    attendance: Attendance,
    class_session: ClassSession,
    class_section: ClassSection,
    course: Course | None,
    student: Student | None,
) -> PendingAppealDetail:
    """Map joined complaint data to a pending complaint detail response."""
    return PendingAppealDetail(
        appeal_id=appeal.appeal_id,
        attendance_id=appeal.attendance_id,
        student_id=appeal.student_id,
        student_full_name=build_student_full_name(student),
        class_section_id=class_section.class_section_id,
        course_name=course.course_name if course else None,
        class_date=class_session.class_date,
        attendance_status=attendance.status,
        reason=appeal.reason,
        status=appeal.status,
        submitted_at=appeal.submitted_at,
        resolution_note=appeal.resolution_note,
        session_number=class_session.session_number,
    )


def get_appeal_joined_rows_by_staff(
    *,
    session: Session,
    staff_id: int,
    pending_only: bool = False,
    appeal_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[tuple[Appeal, Attendance, ClassSession, ClassSection, Course, Student]]:
    """Query complaint rows joined with attendance, lesson, class, subject and student."""
    statement = (
        select(Appeal, Attendance, ClassSession, ClassSection, Course, Student)
        .join(Attendance, Appeal.attendance_id == Attendance.attendance_id)
        .join(ClassSession, Attendance.class_session_id == ClassSession.class_session_id)
        .join(ClassSection, ClassSession.class_section_id == ClassSection.class_section_id)
        .join(Course, ClassSection.course_id == Course.course_id)
        .join(Student, Appeal.student_id == Student.student_id)
        .where(ClassSection.staff_id == staff_id)
        .order_by(Appeal.submitted_at.desc(), Appeal.appeal_id.desc())
    )
    if pending_only:
        statement = statement.where(
            Appeal.status == PENDING_STATUS,
            Appeal.resolved_at.is_(None),
        )
    if appeal_id is not None:
        statement = statement.where(Appeal.appeal_id == appeal_id)
    if appeal_id is None:
        statement = statement.offset(skip).limit(limit)

    return session.exec(statement).all()


def count_actionable_appeals_by_staff(
    *, session: Session, staff_id: int
) -> int:
    """Count pending complaints that belong to classes owned by a staff member."""
    statement = (
        select(func.count())
        .select_from(Appeal)
        .join(Attendance, Appeal.attendance_id == Attendance.attendance_id)
        .join(ClassSession, Attendance.class_session_id == ClassSession.class_session_id)
        .join(ClassSection, ClassSession.class_section_id == ClassSection.class_section_id)
        .where(
            ClassSection.staff_id == staff_id,
            Appeal.status == PENDING_STATUS,
            Appeal.resolved_at.is_(None),
        )
    )
    return session.exec(statement).one()


def get_actionable_appeals_by_staff(
    *,
    session: Session,
    staff_id: int,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[PendingAppealItem], int]:
    """Get pending complaints for a staff member."""
    rows = get_appeal_joined_rows_by_staff(
        session=session,
        staff_id=staff_id,
        pending_only=True,
        skip=skip,
        limit=limit,
    )
    items = [
        build_actionable_appeal_item(
            appeal=appeal,
            attendance=attendance,
            class_session=class_session,
            class_section=class_section,
            course=course,
            student=student,
        )
        for appeal, attendance, class_session, class_section, course, student in rows
    ]
    count = count_actionable_appeals_by_staff(
        session=session,
        staff_id=staff_id,
    )
    return items, count


def get_appeal_detail_context_by_staff(
    *,
    session: Session,
    staff_id: int,
    appeal_id: int,
) -> tuple[Appeal, Attendance, ClassSession, ClassSection, Course, Student] | None:
    """Get one complaint joined row if it belongs to a staff member."""
    rows = get_appeal_joined_rows_by_staff(
        session=session,
        staff_id=staff_id,
        appeal_id=appeal_id,
    )
    return rows[0] if rows else None


def get_actionable_appeal_detail_by_staff(
    *,
    session: Session,
    staff_id: int,
    appeal_id: int,
) -> PendingAppealDetail | None:
    """Get pending complaint detail for a staff member."""
    context = get_appeal_detail_context_by_staff(
        session=session,
        staff_id=staff_id,
        appeal_id=appeal_id,
    )
    if not context:
        return None
    appeal, attendance, class_session, class_section, course, student = context
    if appeal.status != PENDING_STATUS or appeal.resolved_at:
        return None
    return build_actionable_appeal_detail(
        appeal=appeal,
        attendance=attendance,
        class_session=class_session,
        class_section=class_section,
        course=course,
        student=student,
    )


def update_appeal_resolution(
    *,
    session: Session,
    appeal: Appeal,
    attendance: Attendance,
    appeal_status: str,
    resolver_staff_id: int,
    resolved_at: datetime,
    resolution_note: str | None = None,
    new_attendance_status: str | None = None,
) -> Appeal:
    """Update complaint processing fields and optionally update attendance status."""
    appeal.status = appeal_status
    appeal.resolver_staff_id = resolver_staff_id
    appeal.resolved_at = resolved_at
    appeal.resolution_note = resolution_note
    if new_attendance_status:
        attendance.status = new_attendance_status

    session.add(appeal)
    session.add(attendance)
    session.commit()
    session.refresh(appeal)
    session.refresh(attendance)
    return appeal
