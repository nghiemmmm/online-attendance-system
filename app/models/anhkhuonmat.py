from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.types import Float
from sqlmodel import Field, SQLModel


class AnhKhuonMatBase(SQLModel):
    ma_sinh_vien: int
    duong_dan_anh: str = Field(max_length=255)
    loai_anh: str | None = Field(default=None, max_length=30)


class AnhKhuonMatCreate(AnhKhuonMatBase):
    embedding_vector: list[float] | None = None


class AnhKhuonMatUpdate(SQLModel):
    duong_dan_anh: str | None = Field(default=None, max_length=255)
    loai_anh: str | None = Field(default=None, max_length=30)
    embedding_vector: list[float] | None = None


class AnhKhuonMat(AnhKhuonMatBase, table=True):
    __tablename__ = "anhkhuonmat"

    ma_anh: int | None = Field(default=None, primary_key=True)
    ma_sinh_vien: int = Field(foreign_key="sinhvien.ma_sinh_vien")
    embedding_vector: list[float] | None = Field(
        default=None,
        sa_column=Column(ARRAY(Float), nullable=True),
    )


class AnhKhuonMatPublic(AnhKhuonMatBase):
    ma_anh: int


class AnhKhuonMatsPublic(SQLModel):
    data: list[AnhKhuonMatPublic]
    count: int
