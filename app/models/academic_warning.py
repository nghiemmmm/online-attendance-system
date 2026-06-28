"""Define academic warning response models."""

from sqlmodel import SQLModel


class AbsenceWarningItem(SQLModel):
    """Represent one course with an absence warning."""

    class_section_id: int
    course_name: str | None = None
    total_class_sessions: int
    absent_session_count: int
    absence_rate: float
    warning_threshold: float
    warning_status: str


class AbsenceWarningsPublic(SQLModel):
    """Represent absence warning data for one student."""

    student_id: int
    data: list[AbsenceWarningItem]
    count: int
