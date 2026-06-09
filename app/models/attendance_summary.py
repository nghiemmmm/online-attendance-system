"""
Attendance summary response schemas.

Defines API schemas for teacher monthly attendance analytics.
"""

from sqlmodel import SQLModel


class MonthlyAttendanceSummary(SQLModel):
    """
    Monthly attendance summary for a teacher.

    Includes current month rate, previous month rate, the percentage-point
    difference, and raw attendance counts used for the calculation.
    """

    ma_can_bo: int
    current_month: str
    previous_month: str
    current_month_attendance_rate: float | None
    previous_month_attendance_rate: float | None
    change_percentage: float | None
    description: str
    current_month_present_count: int
    current_month_total_count: int
    previous_month_present_count: int
    previous_month_total_count: int
