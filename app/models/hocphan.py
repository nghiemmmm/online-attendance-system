"""Define course database and response models."""

from sqlmodel import Field, SQLModel


class HocPhanBase(SQLModel):
    """Represent shared course fields."""

    ten_hoc_phan: str | None = Field(default=None, max_length=100)
    mo_ta: str | None = Field(default=None, max_length=200)
    so_tin_chi: int | None = None
    trang_thai: bool = True


class HocPhanCreate(HocPhanBase):
    """Represent data required to create a course."""

    ma_hoc_phan: int


class HocPhanUpdate(SQLModel):
    """Represent fields that can update a course."""

    ten_hoc_phan: str | None = Field(default=None, max_length=100)
    mo_ta: str | None = Field(default=None, max_length=200)
    so_tin_chi: int | None = None
    trang_thai: bool | None = None


class HocPhan(HocPhanBase, table=True):
    """Represent the course database table."""

    __tablename__ = "hocphan"

    ma_hoc_phan: int = Field(primary_key=True)


class HocPhanPublic(HocPhanBase):
    """Represent course data returned by the API."""

    ma_hoc_phan: int


class HocPhansPublic(SQLModel):
    """Represent a paginated list of courses."""

    data: list[HocPhanPublic]
    count: int
