"""Define academic major database and response models."""

from sqlmodel import Field, SQLModel


class NganhBase(SQLModel):
    """Represent shared academic major fields."""

    ten_nganh: str = Field(max_length=100)
    mo_ta: str | None = Field(default=None, max_length=255)


class NganhCreate(NganhBase):
    """Represent data required to create an academic major."""

    pass


class NganhUpdate(SQLModel):
    """Represent fields that can update an academic major."""

    ten_nganh: str | None = Field(default=None, max_length=100)
    mo_ta: str | None = Field(default=None, max_length=255)


class Nganh(NganhBase, table=True):
    """Represent the academic major database table."""

    __tablename__ = "nganh"

    ma_nganh: int | None = Field(default=None, primary_key=True)


class NganhPublic(NganhBase):
    """Represent academic major data returned by the API."""

    ma_nganh: int


class NganhsPublic(SQLModel):
    """Represent a paginated list of academic majors."""

    data: list[NganhPublic]
    count: int
