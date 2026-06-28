"""Define student study schedule response models."""

from datetime import date, time

from sqlmodel import SQLModel


class TodayScheduleItem(SQLModel):
    """Represent one lesson in a student's daily schedule."""

    class_session_id: int | None = None
    class_section_id: int
    course_name: str | None = None
    phong_hoc: str | None = None
    start_time: time | None = None
    end_time: time | None = None
    status: str | None = None
    class_date: date | None = None
    session_number: int | None = None


class TodaySchedulePublic(SQLModel):
    """Represent a student's daily schedule."""

    student_id: int
    class_date: date
    data: list[TodayScheduleItem]
    count: int
