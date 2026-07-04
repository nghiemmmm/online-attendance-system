"""Define class registration database and response models."""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


def get_datetime_utc() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(UTC)


class CourseRegistrationBase(SQLModel):
    """Represent shared class registration fields."""

    student_id: int
    class_section_id: int
    status: bool = True


class CourseRegistrationCreate(CourseRegistrationBase):
    """Represent data required to create a class registration."""

    pass


class CourseRegistrationUpdate(SQLModel):
    """Represent fields that can update a class registration."""

    status: bool | None = None


class CourseRegistration(CourseRegistrationBase, table=True):
    """Represent the class registration database table."""

    __tablename__ = "course_registrations"

    student_id: int = Field(foreign_key="students.student_id", primary_key=True)
    class_section_id: int = Field(
        foreign_key="class_sections.class_section_id", primary_key=True
    )
    registered_at: datetime = Field(default_factory=get_datetime_utc)


class CourseRegistrationPublic(CourseRegistrationBase):
    """Represent class registration data returned by the API."""

    registered_at: datetime


class CourseRegistrationsPublic(SQLModel):
    """Represent a paginated list of class registrations."""

    data: list[CourseRegistrationPublic]
    count: int
