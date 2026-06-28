"""Define complaint database and response models."""

from datetime import date, datetime, timezone

from sqlmodel import Field, SQLModel


def get_datetime_utc() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(timezone.utc)


class AppealBase(SQLModel):
    """Represent shared complaint fields."""

    attendance_id: int
    student_id: int
    reason: str = Field(max_length=500)
    status: str = Field(default="CHO_XU_LY", max_length=30)
    resolver_staff_id: int | None = None
    resolution_note: str | None = Field(default=None, max_length=255)
    resolved_at: datetime | None = None


class AppealCreate(SQLModel):
    """Represent data required to create a complaint."""

    attendance_id: int
    student_id: int
    reason: str = Field(max_length=500)


class AppealUpdate(SQLModel):
    """Represent fields that can update a complaint."""

    status: str | None = Field(default=None, max_length=30)
    resolver_staff_id: int | None = None
    resolution_note: str | None = Field(default=None, max_length=255)
    resolved_at: datetime | None = None


class PendingAppealItem(SQLModel):
    """Represent a summary of a complaint pending staff review."""

    appeal_id: int
    attendance_id: int
    student_id: int
    student_full_name: str | None = None
    class_section_id: int
    course_name: str | None = None
    class_date: date
    attendance_status: str
    reason: str
    submitted_at: datetime
    session_number: int | None = None


class PendingAppealsPublic(SQLModel):
    """Represent complaints pending review for one staff member."""

    data: list[PendingAppealItem]
    count: int


class PendingAppealDetail(SQLModel):
    """Represent complaint details for staff review."""

    appeal_id: int
    attendance_id: int
    student_id: int
    student_full_name: str | None = None
    class_section_id: int
    course_name: str | None = None
    class_date: date
    attendance_status: str
    reason: str
    status: str
    submitted_at: datetime
    resolution_note: str | None = None
    session_number: int | None = None


class AppealResolutionRequest(SQLModel):
    """Represent staff-provided complaint review data."""

    resolution_note: str | None = Field(default=None, max_length=255)


class AppealApprovalRequest(AppealResolutionRequest):
    """Represent data used to approve a complaint."""

    new_attendance_status: str | None = Field(default=None, max_length=30)


class AppealResolutionResult(SQLModel):
    """Represent the result after staff review a complaint."""

    appeal_id: int
    status: str
    resolver_staff_id: int
    resolution_note: str | None = None
    resolved_at: datetime
    attendance_status: str


class Appeal(AppealBase, table=True):
    """Represent the complaint database table."""

    __tablename__ = "appeals"

    appeal_id: int | None = Field(default=None, primary_key=True)
    attendance_id: int = Field(foreign_key="attendance.attendance_id")
    student_id: int = Field(foreign_key="students.student_id")
    resolver_staff_id: int | None = Field(default=None, foreign_key="staff.staff_id")
    submitted_at: datetime = Field(default_factory=get_datetime_utc)


class AppealPublic(AppealBase):
    """Represent complaint data returned by the API."""

    appeal_id: int
    submitted_at: datetime
    class_section_id: int | None = None
    course_id: int | None = None
    course_name: str | None = None
    class_date: date | None = None
    session_number: int | None = None
    attendance_status: str | None = None


class AppealsPublic(SQLModel):
    """Represent a paginated list of complaints."""

    data: list[AppealPublic]
    count: int


class PendingAppealMetric(SQLModel):
    """Represent a dashboard metric for pending complaints."""

    pending_count: int
    calculated_at: datetime
