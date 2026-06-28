"""Define attendance summary response models."""

from sqlmodel import SQLModel


class SemesterAttendanceSummaryPublic(SQLModel):
    """Represent a student's semester attendance summary."""

    student_id: int
    semester: int
    academic_year: str
    present_session_count: int
    total_class_sessions: int
    attendance_rate: float
    description: str
