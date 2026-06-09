"""
Attendance summary service.

Contains business logic for calculating monthly attendance rates and comparing
current month performance with the previous month.
"""

from datetime import date

from sqlmodel import Session

from app.crud.attendance_summary_crud import get_attendance_counts_for_teacher
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
    ma_can_bo: int,
    reference_date: date,
) -> MonthlyAttendanceSummary:
    """
    Build monthly attendance summary for a teacher.

    Args:
        session: Database session.
        ma_can_bo: Teacher/staff identifier.
        reference_date: Date used to determine current and previous month.

    Returns:
        MonthlyAttendanceSummary response model.
    """
    current_start, current_end = get_month_range(reference_date)
    previous_start, previous_end = get_previous_month_range(reference_date)

    current_counts = get_attendance_counts_for_teacher(
        session=session,
        ma_can_bo=ma_can_bo,
        start_date=current_start,
        end_date=current_end,
    )
    previous_counts = get_attendance_counts_for_teacher(
        session=session,
        ma_can_bo=ma_can_bo,
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
        ma_can_bo=ma_can_bo,
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
