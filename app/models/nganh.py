from sqlmodel import Field, SQLModel


class NganhBase(SQLModel):
    ten_nganh: str = Field(max_length=100)
    mo_ta: str | None = Field(default=None, max_length=255)


class NganhCreate(NganhBase):
    pass


class NganhUpdate(SQLModel):
    ten_nganh: str | None = Field(default=None, max_length=100)
    mo_ta: str | None = Field(default=None, max_length=255)


class Nganh(NganhBase, table=True):
    __tablename__ = "nganh"

    ma_nganh: int | None = Field(default=None, primary_key=True)


class NganhPublic(NganhBase):
    ma_nganh: int


class NganhsPublic(SQLModel):
    data: list[NganhPublic]
    count: int
