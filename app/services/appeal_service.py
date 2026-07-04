"""
Appeal service.

Contains business logic for complaint metrics used by dashboard APIs.
"""

from datetime import UTC, datetime
from typing import Any

from sqlmodel import Session

from app.core.exceptions import (
    AppealNotFoundError,
    AppealTimeLimitExceededError,
    AppException,
    DuplicateAppealError,
    LessonNotFoundError,
    PermissionDeniedError,
    StaffNotFoundError,
)
from app.crud.appeal_crud import (
    APPROVED_STATUS,
    PENDING_STATUS,
    REJECTED_STATUS,
    count_pending_appeals_by_staff,
    get_actionable_appeal_detail_by_staff,
    get_actionable_appeals_by_staff,
    get_appeal_detail_context_by_staff,
    update_appeal_resolution,
)
from app.crud.staff_crud import get_staff_member
from app.models import (
    Appeal,
    AppealApprovalRequest,
    AppealCreate,
    AppealPublic,
    AppealResolutionRequest,
    AppealResolutionResult,
    AppealsPublic,
    PendingAppealDetail,
    PendingAppealMetric,
    PendingAppealsPublic,
)

TRANG_THAI_DIEM_DANH_HOP_LE = {"CO_MAT", "DI_MUON", "VANG", "VANG_MAT"}


def get_pending_appeal_metric(
    *, session: Session, staff_id: int
) -> PendingAppealMetric:
    """
    Build pending complaint metric for a staff member.

    Args:
        session: Database session.
        staff_id: Staff/teacher identifier.

    Returns:
        Metric containing pending complaints and generated timestamp.
    """
    return PendingAppealMetric(
        pending_count=count_pending_appeals_by_staff(
            session=session,
            staff_id=staff_id,
        ),
        calculated_at=datetime.now(UTC),
    )


def ensure_staff_exists(*, session: Session, staff_id: int) -> None:
    """Raise 404 when staff profile does not exist."""
    if not get_staff_member(session=session, staff_id=staff_id):
        raise StaffNotFoundError("Staff profile not found")


def list_actionable_appeals(
    *,
    session: Session,
    staff_id: int,
    skip: int = 0,
    limit: int = 100,
) -> PendingAppealsPublic:
    """Build pending complaint list for a staff member."""
    ensure_staff_exists(session=session, staff_id=staff_id)
    items, count = get_actionable_appeals_by_staff(
        session=session,
        staff_id=staff_id,
        skip=skip,
        limit=limit,
    )
    return PendingAppealsPublic(data=items, count=count)


def get_actionable_appeal_detail(
    *,
    session: Session,
    staff_id: int,
    appeal_id: int,
) -> PendingAppealDetail:
    """Build pending complaint detail for a staff member."""
    ensure_staff_exists(session=session, staff_id=staff_id)
    detail = get_actionable_appeal_detail_by_staff(
        session=session,
        staff_id=staff_id,
        appeal_id=appeal_id,
    )
    if not detail:
        raise AppealNotFoundError("Pending complaint not found")
    return detail


def ensure_actionable_appeal(
    *,
    session: Session,
    staff_id: int,
    appeal_id: int,
):
    """Return complaint context and ensure it can still be processed."""
    ensure_staff_exists(session=session, staff_id=staff_id)
    context = get_appeal_detail_context_by_staff(
        session=session,
        staff_id=staff_id,
        appeal_id=appeal_id,
    )
    if not context:
        raise AppealNotFoundError("Complaint not found")

    appeal = context[0]
    if appeal.status != PENDING_STATUS or appeal.resolved_at:
        raise AppException("Complaint has already been processed", status_code=409)
    return context


def build_appeal_resolution_result(
    *,
    appeal_id: int,
    status: str,
    resolver_staff_id: int,
    resolution_note: str | None,
    resolved_at: datetime,
    attendance_status: str,
) -> AppealResolutionResult:
    """Build complaint processing result response."""
    return AppealResolutionResult(
        appeal_id=appeal_id,
        status=status,
        resolver_staff_id=resolver_staff_id,
        resolution_note=resolution_note,
        resolved_at=resolved_at,
        attendance_status=attendance_status,
    )


def approve_appeal(
    *,
    session: Session,
    staff_id: int,
    appeal_id: int,
    payload: AppealApprovalRequest,
) -> AppealResolutionResult:
    """Approve a pending complaint and optionally update attendance status."""
    if (
        payload.new_attendance_status
        and payload.new_attendance_status not in TRANG_THAI_DIEM_DANH_HOP_LE
    ):
        raise AppException("Invalid attendance status", status_code=400)

    appeal, attendance, *_ = ensure_actionable_appeal(
        session=session,
        staff_id=staff_id,
        appeal_id=appeal_id,
    )
    resolved_at = datetime.now(UTC)
    update_appeal_resolution(
        session=session,
        appeal=appeal,
        attendance=attendance,
        appeal_status=APPROVED_STATUS,
        resolver_staff_id=staff_id,
        resolved_at=resolved_at,
        resolution_note=payload.resolution_note,
        new_attendance_status=payload.new_attendance_status,
    )
    return build_appeal_resolution_result(
        appeal_id=appeal.appeal_id,
        status=appeal.status,
        resolver_staff_id=staff_id,
        resolution_note=appeal.resolution_note,
        resolved_at=appeal.resolved_at,
        attendance_status=attendance.status,
    )


def reject_appeal(
    *,
    session: Session,
    staff_id: int,
    appeal_id: int,
    payload: AppealResolutionRequest,
) -> AppealResolutionResult:
    """Reject a pending complaint and keep attendance status unchanged."""
    appeal, attendance, *_ = ensure_actionable_appeal(
        session=session,
        staff_id=staff_id,
        appeal_id=appeal_id,
    )
    resolved_at = datetime.now(UTC)
    update_appeal_resolution(
        session=session,
        appeal=appeal,
        attendance=attendance,
        appeal_status=REJECTED_STATUS,
        resolver_staff_id=staff_id,
        resolved_at=resolved_at,
        resolution_note=payload.resolution_note,
    )
    return build_appeal_resolution_result(
        appeal_id=appeal.appeal_id,
        status=appeal.status,
        resolver_staff_id=staff_id,
        resolution_note=appeal.resolution_note,
        resolved_at=appeal.resolved_at,
        attendance_status=attendance.status,
    )


def create_appeal(
    *,
    session: Session,
    payload: AppealCreate,
    current_account: Any,
) -> Appeal:
    """Create a new complaint for attendance records."""
    from datetime import timedelta

    from sqlmodel import select

    from app.models import Attendance, ClassSession, Student

    student = session.exec(
        select(Student).where(Student.account_id == current_account.account_id)
    ).first()
    if not student:
        raise PermissionDeniedError("Not a student")
    if payload.student_id != student.student_id:
        raise PermissionDeniedError("Cannot submit claim for another student")

    existing_appeal = session.exec(
        select(Appeal).where(Appeal.attendance_id == payload.attendance_id)
    ).first()
    if existing_appeal:
        raise DuplicateAppealError("Đã tồn tại khiếu nại cho bản ghi điểm danh này")

    attendance = session.get(Attendance, payload.attendance_id)
    if not attendance:
        raise AppealNotFoundError("Bản ghi điểm danh không tồn tại")

    class_session = session.get(ClassSession, attendance.class_session_id)
    if not class_session:
        raise LessonNotFoundError("Buổi học không tồn tại")

    if class_session.end_time:
        end_datetime = datetime.combine(
            class_session.class_date, class_session.end_time
        )
    else:
        end_datetime = datetime.combine(class_session.class_date, datetime.max.time())

    if datetime.now() > end_datetime + timedelta(hours=48):
        raise AppealTimeLimitExceededError(
            "Đã quá thời hạn 48 giờ để gửi khiếu nại cho buổi học này"
        )

    db_appeal = Appeal.model_validate(payload)
    session.add(db_appeal)
    session.commit()
    session.refresh(db_appeal)
    return db_appeal


def list_my_appeals(
    *,
    session: Session,
    current_account: Any,
    skip: int = 0,
    limit: int = 100,
) -> AppealsPublic:
    """List appeals submitted by the current student."""
    from sqlmodel import col, func, select

    from app.models import Attendance, ClassSection, ClassSession, Course, Student

    student = session.exec(
        select(Student).where(Student.account_id == current_account.account_id)
    ).first()
    if not student:
        raise PermissionDeniedError("Not a student")

    count_statement = (
        select(func.count())
        .select_from(Appeal)
        .where(Appeal.student_id == student.student_id)
    )
    count = session.exec(count_statement).one()

    statement = (
        select(Appeal, Attendance, ClassSession, ClassSection, Course)
        .join(Attendance, Appeal.attendance_id == Attendance.attendance_id)
        .join(
            ClassSession, Attendance.class_session_id == ClassSession.class_session_id
        )
        .join(
            ClassSection, ClassSession.class_section_id == ClassSection.class_section_id
        )
        .join(Course, ClassSection.course_id == Course.course_id)
        .where(Appeal.student_id == student.student_id)
        .order_by(col(Appeal.submitted_at).desc())
        .offset(skip)
        .limit(limit)
    )
    # Wait, let's verify if ClassSection.class_section_id is correct. Yes, we saw it in appeals.py.
    # So we can just join(ClassSection, ClassSession.class_section_id == ClassSection.class_section_id)
    statement = (
        select(Appeal, Attendance, ClassSession, ClassSection, Course)
        .join(Attendance, Appeal.attendance_id == Attendance.attendance_id)
        .join(
            ClassSession, Attendance.class_session_id == ClassSession.class_session_id
        )
        .join(
            ClassSection, ClassSession.class_section_id == ClassSection.class_section_id
        )
        .join(Course, ClassSection.course_id == Course.course_id)
        .where(Appeal.student_id == student.student_id)
        .order_by(col(Appeal.submitted_at).desc())
        .offset(skip)
        .limit(limit)
    )

    rows = session.exec(statement).all()
    appeals = [
        AppealPublic(
            **appeal.model_dump(),
            class_section_id=class_section.class_section_id,
            course_id=course.course_id,
            course_name=course.course_name,
            class_date=class_session.class_date,
            session_number=class_session.session_number,
            attendance_status=attendance.status,
        )
        for appeal, attendance, class_session, class_section, course in rows
    ]
    return AppealsPublic(data=appeals, count=count)
