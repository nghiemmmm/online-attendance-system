"""Define course database and response models."""

from sqlmodel import Field, SQLModel


class CourseBase(SQLModel):
    """Represent shared course fields."""

    course_name: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=200)
    credit_count: int | None = None
    status: bool = True


class CourseCreate(CourseBase):
    """Represent data required to create a course."""

    course_id: int


class CourseUpdate(SQLModel):
    """Represent fields that can update a course."""

    course_name: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=200)
    credit_count: int | None = None
    status: bool | None = None


class Course(CourseBase, table=True):
    """Represent the course database table."""

    __tablename__ = "courses"

    course_id: int = Field(primary_key=True)


class CoursePublic(CourseBase):
    """Represent course data returned by the API."""

    course_id: int


class CoursesPublic(SQLModel):
    """Represent a paginated list of courses."""

    data: list[CoursePublic]
    count: int
