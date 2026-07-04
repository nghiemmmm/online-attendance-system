"""Define staff profile database and response models."""

from datetime import date

from sqlmodel import Field, SQLModel

from app.core.email_compat import EmailStr


class StaffBase(SQLModel):
    """Represent shared staff profile fields."""

    last_name: str = Field(max_length=50)
    first_name: str = Field(max_length=50)
    phone: str | None = Field(default=None, max_length=15)
    gender: str | None = Field(default=None, max_length=10)
    birth_date: date | None = None
    google_email: EmailStr | None = Field(default=None, max_length=100)
    account_id: int | None = None
    position: str | None = Field(default=None, max_length=50)
    status: bool = True


class StaffCreate(StaffBase):
    """Represent data required to create a staff profile."""

    pass


class StaffUpdate(SQLModel):
    """Represent fields that can update a staff profile."""

    last_name: str | None = Field(default=None, max_length=50)
    first_name: str | None = Field(default=None, max_length=50)
    phone: str | None = Field(default=None, max_length=15)
    gender: str | None = Field(default=None, max_length=10)
    birth_date: date | None = None
    google_email: EmailStr | None = Field(default=None, max_length=100)
    account_id: int | None = None
    position: str | None = Field(default=None, max_length=50)
    status: bool | None = None


class Staff(StaffBase, table=True):
    """Represent the staff profile database table."""

    __tablename__ = "staff"

    staff_id: int | None = Field(default=None, primary_key=True)
    google_email: EmailStr | None = Field(default=None, max_length=100, unique=True)
    account_id: int | None = Field(
        default=None, foreign_key="accounts.account_id", unique=True
    )


class StaffPublic(StaffBase):
    """Represent staff profile data returned by the API."""

    staff_id: int


class StaffMembersPublic(SQLModel):
    """Represent a paginated list of staff profiles."""

    data: list[StaffPublic]
    count: int


class StaffClassSectionItem(SQLModel):
    """Represent class section details taught by a staff member."""

    class_section_id: int
    course_id: int
    course_name: str
    semester: int
    academic_year: str
    status: bool
    current_students: int


class StaffClassSectionsPublic(SQLModel):
    """Represent list of class sections taught by a staff member."""

    data: list[StaffClassSectionItem]
    count: int


class AttendanceReportDataPoint(SQLModel):
    """Represent attendance stats for a single completed lesson."""

    date: str
    present: int
    late: int
    absent: int


class StaffAttendanceReportItem(SQLModel):
    """Represent overall attendance report for a class section taught by staff."""

    id: str
    subjectCode: str
    subjectName: str
    totalStudents: int
    completedSessions: int
    totalSessions: int
    averageAttendanceRate: float
    dataPoints: list[AttendanceReportDataPoint]
