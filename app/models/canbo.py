from datetime import date

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class CanBoBase(SQLModel):
    ho: str = Field(max_length=50)
    ten: str = Field(max_length=50)
    dien_thoai: str | None = Field(default=None, max_length=15)
    gioi_tinh: str | None = Field(default=None, max_length=10)
    ngay_sinh: date | None = None
    email: EmailStr | None = Field(default=None, max_length=100)
    ma_tai_khoan: int | None = None
    chuc_vu: str | None = Field(default=None, max_length=50)
    trang_thai: bool = True


class CanBoCreate(CanBoBase):
    pass


class CanBoUpdate(SQLModel):
    ho: str | None = Field(default=None, max_length=50)
    ten: str | None = Field(default=None, max_length=50)
    dien_thoai: str | None = Field(default=None, max_length=15)
    gioi_tinh: str | None = Field(default=None, max_length=10)
    ngay_sinh: date | None = None
    email: EmailStr | None = Field(default=None, max_length=100)
    ma_tai_khoan: int | None = None
    chuc_vu: str | None = Field(default=None, max_length=50)
    trang_thai: bool | None = None


class CanBo(CanBoBase, table=True):
    __tablename__ = "canbo"

    ma_can_bo: int | None = Field(default=None, primary_key=True)
    email: EmailStr | None = Field(default=None, max_length=100, unique=True)
    ma_tai_khoan: int | None = Field(
        default=None, foreign_key="taikhoan.ma_tai_khoan", unique=True
    )


class CanBoPublic(CanBoBase):
    ma_can_bo: int


class CanBosPublic(SQLModel):
    data: list[CanBoPublic]
    count: int
