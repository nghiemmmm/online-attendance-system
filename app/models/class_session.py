"""Define lesson database and response models."""

from datetime import date, time

from sqlmodel import Field, SQLModel


class ClassSessionBase(SQLModel):
    """Represent shared lesson fields."""

    class_section_id: int
    class_date: date
    start_time: time | None = None
    end_time: time | None = None
    session_number: int | None = None
    status: str | None = Field(default=None, max_length=20)
    recognition_threshold: float = 0.5
    late_grace_minutes: int = 15
    note: str | None = Field(default=None, max_length=255)


class ClassSessionCreate(ClassSessionBase):
    """Represent data required to create a lesson."""

    pass


class ClassSessionUpdate(SQLModel):
    """Represent fields that can update a lesson."""

    class_section_id: int | None = None
    class_date: date | None = None
    start_time: time | None = None
    end_time: time | None = None
    session_number: int | None = None
    status: str | None = Field(default=None, max_length=20)
    recognition_threshold: float | None = None
    late_grace_minutes: int | None = None
    note: str | None = Field(default=None, max_length=255)


class ClassSession(ClassSessionBase, table=True):
    """Represent the lesson database table."""

    __tablename__ = "class_sessions"

    class_session_id: int | None = Field(default=None, primary_key=True)
    class_section_id: int = Field(foreign_key="class_sections.class_section_id")


class ClassSessionPublic(ClassSessionBase):
    """Represent lesson data returned by the API."""

    class_session_id: int


class ClassSessionsPublic(SQLModel):
    """Represent a paginated list of lessons."""

    data: list[ClassSessionPublic]
    count: int
