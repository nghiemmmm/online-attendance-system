"""Define teaching schedule response models."""

from datetime import date, time

from sqlmodel import SQLModel


class RecentClassSessionItem(SQLModel):
    """Represent one recent lesson for a staff dashboard."""

    class_section_id: int
    course_name: str | None = None
    class_date: date
    present_student_count: int
    late_student_count: int
    absent_student_count: int


class RecentClassSessionsPublic(SQLModel):
    """Represent a list of recent lessons for a staff member."""

    data: list[RecentClassSessionItem]
    count: int


class TeachingScheduleItem(SQLModel):
    """Represent one teaching schedule row."""

    staff_id: int
    class_section_id: int
    course_id: int
    course_name: str | None = None
    timetable_id: int | None = None
    class_session_id: int | None = None
    class_date: date | None = None
    weekday: int | None = None
    start_period: int | None = None
    end_period: int | None = None
    start_time: time | None = None
    end_time: time | None = None
    semester: int | None = None
    academic_year: str | None = None
    class_status: bool
    class_session_status: str | None = None
    note: str | None = None
    session_number: int | None = None
    student_count: int = 0


class TeachingSchedulesPublic(SQLModel):
    """Represent a filtered list of teaching schedule rows."""

    data: list[TeachingScheduleItem]
    count: int


class ActiveClassSectionCountPublic(SQLModel):
    """Represent the number of class sections currently taught by staff."""

    staff_id: int
    semester: int
    academic_year: str
    as_of_date: date
    count: int
