"""Define class section database and response models."""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


def get_datetime_utc() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(UTC)


class ClassSectionBase(SQLModel):
    """Represent shared class section fields."""

    course_id: int
    staff_id: int
    semester_id: int | None = Field(
        default=None, foreign_key="semesters.semester_id", index=True
    )
    semester: int | None = None
    academic_year: str | None = Field(default=None, max_length=20)
    minimum_attendance_rate: float = 0.8
    status: bool = True


class ClassSectionCreate(ClassSectionBase):
    """Represent data required to create a class section."""

    pass


class ClassSectionUpdate(SQLModel):
    """Represent fields that can update a class section."""

    course_id: int | None = None
    staff_id: int | None = None
    semester_id: int | None = None
    semester: int | None = None
    academic_year: str | None = Field(default=None, max_length=20)
    minimum_attendance_rate: float | None = None
    status: bool | None = None


class ClassSection(ClassSectionBase, table=True):
    """Represent the class section database table."""

    __tablename__ = "class_sections"

    class_section_id: int | None = Field(default=None, primary_key=True)
    course_id: int = Field(foreign_key="courses.course_id")
    staff_id: int = Field(foreign_key="staff.staff_id")
    semester_id: int | None = Field(
        default=None, foreign_key="semesters.semester_id", index=True
    )
    created_at: datetime = Field(default_factory=get_datetime_utc)


class ClassSectionPublic(ClassSectionBase):
    """Represent class section data returned by the API."""

    class_section_id: int
    created_at: datetime


class ClassSectionsPublic(SQLModel):
    """Represent a paginated list of class sections."""

    data: list[ClassSectionPublic]
    count: int
