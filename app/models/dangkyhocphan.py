from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


class DangKyHocPhanBase(SQLModel):
    ma_sinh_vien: int
    ma_lop_hoc_phan: int
    trang_thai: bool = True


class DangKyHocPhanCreate(DangKyHocPhanBase):
    pass


class DangKyHocPhanUpdate(SQLModel):
    trang_thai: bool | None = None


class DangKyHocPhan(DangKyHocPhanBase, table=True):
    __tablename__ = "dangkyhocphan"

    ma_sinh_vien: int = Field(
        foreign_key="sinhvien.ma_sinh_vien", primary_key=True
    )
    ma_lop_hoc_phan: int = Field(
        foreign_key="lophocphan.ma_lop_hoc_phan", primary_key=True
    )
    ngay_dang_ky: datetime = Field(default_factory=get_datetime_utc)


class DangKyHocPhanPublic(DangKyHocPhanBase):
    ngay_dang_ky: datetime


class DangKyHocPhansPublic(SQLModel):
    data: list[DangKyHocPhanPublic]
    count: int
