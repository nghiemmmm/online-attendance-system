"""Define timetable database and response models."""

from datetime import date, time

from sqlalchemy import CheckConstraint
from sqlmodel import Field, SQLModel


class TimetableBase(SQLModel):
    """Represent shared timetable fields."""

    class_section_id: int
    weekday: int
    start_period: int | None = None
    end_period: int | None = None
    start_time: time | None = None
    end_time: time | None = None
    start_date: date
    end_date: date


class TimetableCreate(TimetableBase):
    """Represent data required to create a timetable entry."""

    pass


class TimetableUpdate(SQLModel):
    """Represent fields that can update a timetable entry."""

    class_section_id: int | None = None
    weekday: int | None = None
    start_period: int | None = None
    end_period: int | None = None
    start_time: time | None = None
    end_time: time | None = None
    start_date: date | None = None
    end_date: date | None = None


class Timetable(TimetableBase, table=True):
    """Represent the timetable database table."""

    __tablename__ = "timetables"
    __table_args__ = (
        CheckConstraint("start_date < end_date", name="ck_timetable_dates"),
    )

    timetable_id: int | None = Field(default=None, primary_key=True)
    class_section_id: int = Field(foreign_key="class_sections.class_section_id")


class TimetablePublic(TimetableBase):
    """Represent timetable data returned by the API."""

    timetable_id: int


class TimetablesPublic(SQLModel):
    """Represent a paginated list of timetable entries."""

    data: list[TimetablePublic]
    count: int
