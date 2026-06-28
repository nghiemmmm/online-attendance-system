"""Define semester database and API models."""

from datetime import date, datetime, timezone
from sqlmodel import Field, SQLModel
from app.models.base import AppBaseModel


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


class SemesterBase(SQLModel):
    semester_code: str = Field(max_length=30, unique=True, index=True)
    semester_name: str = Field(max_length=50)
    academic_year: str = Field(max_length=20)
    start_date: date = Field()
    end_date: date = Field()
    is_current: bool = Field(default=False, index=True)


class SemesterCreate(SemesterBase):
    pass


class SemesterUpdate(SQLModel):
    semester_code: str | None = Field(default=None, max_length=30)
    semester_name: str | None = Field(default=None, max_length=50)
    academic_year: str | None = Field(default=None, max_length=20)
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool | None = None


class Semester(SemesterBase, table=True):
    __tablename__ = "semesters"

    semester_id: int | None = Field(default=None, primary_key=True)


class SemesterPublic(AppBaseModel, SemesterBase):
    semester_id: int


class SemestersPublic(SQLModel):
    data: list[SemesterPublic]
    count: int
