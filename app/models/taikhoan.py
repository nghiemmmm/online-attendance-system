from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


class TaiKhoanBase(SQLModel):
    ten_dang_nhap: str = Field(max_length=50)
    vai_tro: str = Field(default="SINH_VIEN", max_length=20)
    trang_thai: bool = True


class TaiKhoanCreate(TaiKhoanBase):
    password: str = Field(min_length=5, max_length=128)


class TaiKhoanRegister(SQLModel):
    ten_dang_nhap: str = Field(max_length=50)
    password: str = Field(min_length=5, max_length=128)
    vai_tro: str = Field(default="SINH_VIEN", max_length=20)


class TaiKhoanUpdate(SQLModel):
    ten_dang_nhap: str | None = Field(default=None, max_length=50)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    vai_tro: str | None = Field(default=None, max_length=20)
    trang_thai: bool | None = None


class TaiKhoan(TaiKhoanBase, table=True):
    __tablename__ = "taikhoan"

    ma_tai_khoan: int | None = Field(default=None, primary_key=True)
    ten_dang_nhap: str = Field(max_length=50, unique=True, index=True)
    mat_khau_hash: str = Field(max_length=255)
    lan_dang_nhap_cuoi: datetime | None = None
    ngay_tao: datetime = Field(default_factory=get_datetime_utc)


class TaiKhoanPublic(TaiKhoanBase):
    ma_tai_khoan: int
    lan_dang_nhap_cuoi: datetime | None = None
    ngay_tao: datetime


class TaiKhoansPublic(SQLModel):
    data: list[TaiKhoanPublic]
    count: int


TaiKhoanListPublic = TaiKhoansPublic


class TaiKhoanProfile(SQLModel):
    tai_khoan: TaiKhoanPublic
    profile: dict | None = None
