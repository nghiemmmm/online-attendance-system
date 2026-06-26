"""Define class section database and response models."""

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def get_datetime_utc() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(timezone.utc)


class LopHocPhanBase(SQLModel):
    """Represent shared class section fields."""

    ma_hoc_phan: int
    ma_can_bo: int
    hoc_ky: int | None = None
    nam_hoc: str | None = Field(default=None, max_length=20)
    ty_le_chuyen_can_toi_thieu: float = 0.8
    trang_thai: bool = True


class LopHocPhanCreate(LopHocPhanBase):
    """Represent data required to create a class section."""

    pass


class LopHocPhanUpdate(SQLModel):
    """Represent fields that can update a class section."""

    ma_hoc_phan: int | None = None
    ma_can_bo: int | None = None
    hoc_ky: int | None = None
    nam_hoc: str | None = Field(default=None, max_length=20)
    ty_le_chuyen_can_toi_thieu: float | None = None
    trang_thai: bool | None = None


class LopHocPhan(LopHocPhanBase, table=True):
    """Represent the class section database table."""

    __tablename__ = "lophocphan"

    ma_lop_hoc_phan: int | None = Field(default=None, primary_key=True)
    ma_hoc_phan: int = Field(foreign_key="hocphan.ma_hoc_phan")
    ma_can_bo: int = Field(foreign_key="canbo.ma_can_bo")
    ngay_tao: datetime = Field(default_factory=get_datetime_utc)


class LopHocPhanPublic(LopHocPhanBase):
    """Represent class section data returned by the API."""

    ma_lop_hoc_phan: int
    ngay_tao: datetime


class LopHocPhansPublic(SQLModel):
    """Represent a paginated list of class sections."""

    data: list[LopHocPhanPublic]
    count: int
