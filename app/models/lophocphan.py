from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


class LopHocPhanBase(SQLModel):
    ma_hoc_phan: int
    ma_can_bo: int
    hoc_ky: int | None = None
    nam_hoc: str | None = Field(default=None, max_length=20)
    ty_le_chuyen_can_toi_thieu: float = 0.8
    trang_thai: bool = True


class LopHocPhanCreate(LopHocPhanBase):
    pass


class LopHocPhanUpdate(SQLModel):
    ma_hoc_phan: int | None = None
    ma_can_bo: int | None = None
    hoc_ky: int | None = None
    nam_hoc: str | None = Field(default=None, max_length=20)
    ty_le_chuyen_can_toi_thieu: float | None = None
    trang_thai: bool | None = None


class LopHocPhan(LopHocPhanBase, table=True):
    __tablename__ = "lophocphan"

    ma_lop_hoc_phan: int | None = Field(default=None, primary_key=True)
    ma_hoc_phan: int = Field(foreign_key="hocphan.ma_hoc_phan")
    ma_can_bo: int = Field(foreign_key="canbo.ma_can_bo")
    ngay_tao: datetime = Field(default_factory=get_datetime_utc)


class LopHocPhanPublic(LopHocPhanBase):
    ma_lop_hoc_phan: int
    ngay_tao: datetime


class LopHocPhansPublic(SQLModel):
    data: list[LopHocPhanPublic]
    count: int
