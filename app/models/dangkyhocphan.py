"""Define class registration database and response models."""

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def get_datetime_utc() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(timezone.utc)


class DangKyHocPhanBase(SQLModel):
    """Represent shared class registration fields."""

    ma_sinh_vien: int
    ma_lop_hoc_phan: int
    trang_thai: bool = True


class DangKyHocPhanCreate(DangKyHocPhanBase):
    """Represent data required to create a class registration."""

    pass


class DangKyHocPhanUpdate(SQLModel):
    """Represent fields that can update a class registration."""

    trang_thai: bool | None = None


class DangKyHocPhan(DangKyHocPhanBase, table=True):
    """Represent the class registration database table."""

    __tablename__ = "dangkyhocphan"

    ma_sinh_vien: int = Field(
        foreign_key="sinhvien.ma_sinh_vien", primary_key=True
    )
    ma_lop_hoc_phan: int = Field(
        foreign_key="lophocphan.ma_lop_hoc_phan", primary_key=True
    )
    ngay_dang_ky: datetime = Field(default_factory=get_datetime_utc)


class DangKyHocPhanPublic(DangKyHocPhanBase):
    """Represent class registration data returned by the API."""

    ngay_dang_ky: datetime


class DangKyHocPhansPublic(SQLModel):
    """Represent a paginated list of class registrations."""

    data: list[DangKyHocPhanPublic]
    count: int
