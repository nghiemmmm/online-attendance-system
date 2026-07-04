"""
Canh bao hoc tap service.

Contains business logic for student academic warnings.
"""

from sqlmodel import Session

from app.core.exceptions import InvalidWarningThresholdError, StudentNotFoundError
from app.crud.academic_warning_crud import get_absence_warning_sources_by_student
from app.crud.student_crud import get_student
from app.models import AbsenceWarningItem, AbsenceWarningsPublic

TRANG_THAI_AN_TOAN = "AN_TOAN"
TRANG_THAI_CANH_BAO = "CANH_BAO"
TRANG_THAI_VUOT_NGUONG = "VUOT_NGUONG"


def validate_warning_thresholds(
    *, warning_threshold: float, absence_limit: float
) -> None:
    """Validate warning and absence limit values."""
    if warning_threshold > absence_limit:
        raise InvalidWarningThresholdError()


def classify_absence_warning(
    *,
    absence_rate: float,
    warning_threshold: float,
    absence_limit: float,
) -> str:
    """Classify absence warning status from absence rate."""
    if absence_rate >= absence_limit:
        return TRANG_THAI_VUOT_NGUONG
    if absence_rate >= warning_threshold:
        return TRANG_THAI_CANH_BAO
    return TRANG_THAI_AN_TOAN


def get_absence_warnings_by_student(
    *,
    session: Session,
    student_id: int,
    warning_threshold: float = 15.0,
    absence_limit: float = 20.0,
    include_safe: bool = False,
) -> AbsenceWarningsPublic:
    """Lay danh sach mon hoc gan vuot hoac da vuot nguong vang cua sinh vien."""
    validate_warning_thresholds(
        warning_threshold=warning_threshold,
        absence_limit=absence_limit,
    )
    if not get_student(session=session, student_id=student_id):
        raise StudentNotFoundError("Student profile not found")

    items: list[AbsenceWarningItem] = []
    for source in get_absence_warning_sources_by_student(
        session=session,
        student_id=student_id,
    ):
        absence_rate = (
            0.0
            if source.total_class_sessions == 0
            else round(
                source.absent_session_count / source.total_class_sessions * 100, 2
            )
        )
        status = classify_absence_warning(
            absence_rate=absence_rate,
            warning_threshold=warning_threshold,
            absence_limit=absence_limit,
        )
        if not include_safe and status == TRANG_THAI_AN_TOAN:
            continue

        items.append(
            AbsenceWarningItem(
                class_section_id=source.class_section_id,
                course_name=source.course_name,
                total_class_sessions=source.total_class_sessions,
                absent_session_count=source.absent_session_count,
                absence_rate=absence_rate,
                warning_threshold=absence_limit,
                warning_status=status,
            )
        )

    return AbsenceWarningsPublic(
        student_id=student_id,
        data=items,
        count=len(items),
    )
