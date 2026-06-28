"""
Attendance summary service.

Contains business logic for calculating monthly attendance rates and comparing
current month performance with the previous month.
"""

from datetime import date
from typing import Any

from sqlmodel import Session

from app.crud.attendance_summary_crud import get_attendance_counts_for_teacher
from app.core.exceptions import ClassSectionNotFoundError, PermissionDeniedError
from app.models import MonthlyAttendanceSummary


def get_month_range(reference_date: date) -> tuple[date, date]:
    """
    Get the inclusive/exclusive date range for the month containing a date.

    Args:
        reference_date: Date used to determine the month.

    Returns:
        Tuple containing start date inclusive and end date exclusive.
    """
    start_date = reference_date.replace(day=1)
    if reference_date.month == 12:
        end_date = date(reference_date.year + 1, 1, 1)
    else:
        end_date = date(reference_date.year, reference_date.month + 1, 1)
    return start_date, end_date


def get_previous_month_range(reference_date: date) -> tuple[date, date]:
    """
    Get the inclusive/exclusive date range for the month before a date.

    Args:
        reference_date: Date used to determine the current month.

    Returns:
        Tuple containing previous month start date inclusive and end date exclusive.
    """
    current_month_start = reference_date.replace(day=1)
    if current_month_start.month == 1:
        previous_reference = date(current_month_start.year - 1, 12, 1)
    else:
        previous_reference = date(
            current_month_start.year,
            current_month_start.month - 1,
            1,
        )
    return get_month_range(previous_reference)


def format_month(value: date) -> str:
    """
    Format a date as YYYY-MM for API responses.

    Args:
        value: Date to format.

    Returns:
        Month label in YYYY-MM format.
    """
    return value.strftime("%Y-%m")


def calculate_attendance_rate(present_count: int, total_count: int) -> float | None:
    """
    Calculate attendance percentage from present and total counts.

    Args:
        present_count: Number of records counted as present.
        total_count: Total attendance records.

    Returns:
        Attendance rate rounded to two decimals, or None when total_count is zero.
    """
    if total_count == 0:
        return None
    return round((present_count / total_count) * 100, 2)


def calculate_change_percentage(
    current_rate: float | None,
    previous_rate: float | None,
) -> float | None:
    """
    Calculate percentage-point change between current and previous attendance rates.

    Args:
        current_rate: Current month attendance rate.
        previous_rate: Previous month attendance rate.

    Returns:
        Difference in percentage points, or None when either rate is missing.
    """
    if current_rate is None or previous_rate is None:
        return None
    return round(current_rate - previous_rate, 2)


def build_change_description(
    *,
    current_rate: float | None,
    previous_rate: float | None,
    change_percentage: float | None,
) -> str:
    """
    Build Vietnamese description for monthly attendance change.

    Args:
        current_rate: Current month attendance rate.
        previous_rate: Previous month attendance rate.
        change_percentage: Difference in percentage points.

    Returns:
        Human-readable comparison description.
    """
    if current_rate is None and previous_rate is None:
        return "Chưa có dữ liệu điểm danh để thống kê"
    if current_rate is None:
        return "Chưa có dữ liệu điểm danh trong tháng hiện tại"
    if previous_rate is None:
        return "Không có dữ liệu tháng trước để so sánh"
    if change_percentage is None:
        return "Không đủ dữ liệu để so sánh"
    sign = "+" if change_percentage >= 0 else ""
    return f"{sign}{change_percentage}% so với tháng trước"


def get_monthly_attendance_summary(
    *,
    session: Session,
    staff_id: int,
    reference_date: date,
) -> MonthlyAttendanceSummary:
    """
    Build monthly attendance summary for a teacher.

    Args:
        session: Database session.
        staff_id: Teacher/staff identifier.
        reference_date: Date used to determine current and previous month.

    Returns:
        MonthlyAttendanceSummary response model.
    """
    current_start, current_end = get_month_range(reference_date)
    previous_start, previous_end = get_previous_month_range(reference_date)

    current_counts = get_attendance_counts_for_teacher(
        session=session,
        staff_id=staff_id,
        start_date=current_start,
        end_date=current_end,
    )
    previous_counts = get_attendance_counts_for_teacher(
        session=session,
        staff_id=staff_id,
        start_date=previous_start,
        end_date=previous_end,
    )

    current_rate = calculate_attendance_rate(
        current_counts.present_count,
        current_counts.total_count,
    )
    previous_rate = calculate_attendance_rate(
        previous_counts.present_count,
        previous_counts.total_count,
    )
    change_percentage = calculate_change_percentage(current_rate, previous_rate)

    return MonthlyAttendanceSummary(
        staff_id=staff_id,
        current_month=format_month(current_start),
        previous_month=format_month(previous_start),
        current_month_attendance_rate=current_rate,
        previous_month_attendance_rate=previous_rate,
        change_percentage=change_percentage,
        description=build_change_description(
            current_rate=current_rate,
            previous_rate=previous_rate,
            change_percentage=change_percentage,
        ),
        current_month_present_count=current_counts.present_count,
        current_month_total_count=current_counts.total_count,
        previous_month_present_count=previous_counts.present_count,
        previous_month_total_count=previous_counts.total_count,
    )


def get_attendance_report_df(
    *,
    session: Session,
    current_account: Any,
    class_section_id: int,
    unsigned: bool = False,
) -> tuple[Any, int]:
    """Retrieve and format attendance records as a pandas DataFrame for exporting."""
    from app.models import ClassSection, ClassSession, Attendance, Student, CourseRegistration
    from app.crud import staff_crud
    from sqlmodel import select
    import pandas as pd

    # Check class section
    class_section = session.get(ClassSection, class_section_id)
    if not class_section:
        raise ClassSectionNotFoundError("Lớp học phần không tồn tại")

    # Check permissions
    staff = staff_crud.get_staff_member_by_account_id(session=session, account_id=current_account.account_id)
    if current_account.role != "ADMIN" and (
        not staff or class_section.staff_id != staff.staff_id
    ):
        raise PermissionDeniedError("Không có quyền truy cập dữ liệu lớp này")

    # Get enrolled students
    student_statement = select(Student).join(CourseRegistration).where(CourseRegistration.class_section_id == class_section_id)
    students = session.exec(student_statement).all()

    # Get lessons
    class_session_statement = select(ClassSession).where(ClassSession.class_section_id == class_section_id).order_by(ClassSession.class_date, ClassSession.start_time)
    class_sessions = session.exec(class_session_statement).all()

    # Optimize query: fetch all attendance records in ONE query
    class_session_ids = [
        class_session.class_session_id for class_session in class_sessions
    ]
    if class_session_ids:
        attendance_statement = select(Attendance).where(Attendance.class_session_id.in_(class_session_ids))
        attendances = session.exec(attendance_statement).all()
        # Map to dict: (class_session_id, student_id) -> status
        attendance_map = {
            (attendance.class_session_id, attendance.student_id): attendance.status
            for attendance in attendances
        }
    else:
        attendance_map = {}

    col_sid = "Student ID" if unsigned else "Mã sinh viên"
    col_name = "Full name" if unsigned else "Họ tên"
    unmarked_status = "CHUA_DIEM_DANH" if unsigned else "CHƯA_ĐIỂM_DANH"

    data = []
    for student in students:
        row = {
            col_sid: student.student_id,
            col_name: f"{student.last_name} {student.first_name}".strip(),
        }
        for class_session in class_sessions:
            date_label = class_session.class_date.strftime("%d/%m/%Y")
            status = attendance_map.get(
                (class_session.class_session_id, student.student_id),
                unmarked_status,
            )
            row[date_label] = status
        data.append(row)

    df = pd.DataFrame(data)
    if df.empty:
        df = pd.DataFrame(columns=[col_sid, col_name])

    return df, class_section_id
