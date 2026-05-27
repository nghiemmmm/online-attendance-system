from sqlmodel import Field, SQLModel


class HocPhanBase(SQLModel):
    ten_hoc_phan: str | None = Field(default=None, max_length=100)
    mo_ta: str | None = Field(default=None, max_length=200)
    so_tin_chi: int | None = None
    trang_thai: bool = True


class HocPhanCreate(HocPhanBase):
    ma_hoc_phan: int


class HocPhanUpdate(SQLModel):
    ten_hoc_phan: str | None = Field(default=None, max_length=100)
    mo_ta: str | None = Field(default=None, max_length=200)
    so_tin_chi: int | None = None
    trang_thai: bool | None = None


class HocPhan(HocPhanBase, table=True):
    __tablename__ = "hocphan"

    ma_hoc_phan: int = Field(primary_key=True)


class HocPhanPublic(HocPhanBase):
    ma_hoc_phan: int


class HocPhansPublic(SQLModel):
    data: list[HocPhanPublic]
    count: int
