from datetime import datetime
from sqlalchemy import Column
from pgvector.sqlalchemy import Vector
from sqlmodel import Field, SQLModel


class AnhKhuonMatBase(SQLModel):
    ma_sinh_vien: int
    duong_dan_anh: str = Field(max_length=255)
    loai_anh: str | None = Field(default=None, max_length=30)
    diem_chat_luong: float | None = None
    trang_thai_duyet: str = Field(default="CHO_DUYET", max_length=30)
    ly_do_tu_choi: str | None = Field(default=None, max_length=255)
    thoi_gian_duyet: datetime | None = None


class AnhKhuonMatCreate(AnhKhuonMatBase):
    embedding_vector: list[float] | None = None


class AnhKhuonMatUpdate(SQLModel):
    duong_dan_anh: str | None = Field(default=None, max_length=255)
    loai_anh: str | None = Field(default=None, max_length=30)
    embedding_vector: list[float] | None = None
    diem_chat_luong: float | None = None
    trang_thai_duyet: str | None = Field(default=None, max_length=30)
    ly_do_tu_choi: str | None = Field(default=None, max_length=255)
    ma_nguoi_duyet: int | None = None
    thoi_gian_duyet: datetime | None = None


class AnhKhuonMat(AnhKhuonMatBase, table=True):
    __tablename__ = "anhkhuonmat"

    ma_anh: int | None = Field(default=None, primary_key=True)
    ma_sinh_vien: int = Field(foreign_key="sinhvien.ma_sinh_vien")
    ma_nguoi_duyet: int | None = Field(default=None, foreign_key="taikhoan.ma_tai_khoan")
    embedding_vector: list[float] | None = Field(
        default=None,
        sa_column=Column(Vector(512), nullable=True),
    )


class AnhKhuonMatPublic(AnhKhuonMatBase):
    ma_anh: int
    ma_nguoi_duyet: int | None = None


class AnhKhuonMatsPublic(SQLModel):
    data: list[AnhKhuonMatPublic]
    count: int
