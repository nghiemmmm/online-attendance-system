"""Define academic major database and response models."""

from sqlmodel import Field, SQLModel


class MajorBase(SQLModel):
    """Represent shared academic major fields."""

    major_name: str = Field(max_length=100)
    description: str | None = Field(default=None, max_length=255)


class MajorCreate(MajorBase):
    """Represent data required to create an academic major."""

    pass


class MajorUpdate(SQLModel):
    """Represent fields that can update an academic major."""

    major_name: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=255)


class Major(MajorBase, table=True):
    """Represent the academic major database table."""

    __tablename__ = "majors"

    major_id: int | None = Field(default=None, primary_key=True)


class MajorPublic(MajorBase):
    """Represent academic major data returned by the API."""

    major_id: int


class MajorsPublic(SQLModel):
    """Represent a paginated list of academic majors."""

    data: list[MajorPublic]
    count: int
