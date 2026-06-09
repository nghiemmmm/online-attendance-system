"""
SinhVien CRUD operations.

Contains database operations for student profiles.
"""

from sqlalchemy import or_
from sqlmodel import Session, col, func, select

from app.models import SinhVien, SinhVienCreate, SinhVienUpdate


def get_sinh_vien(*, session: Session, ma_sinh_vien: int) -> SinhVien | None:
    """Lay thong tin mot sinh vien theo ma sinh vien."""
    return session.get(SinhVien, ma_sinh_vien)


def get_sinh_vien_by_google_email(
    *, session: Session, google_email: str
) -> SinhVien | None:
    """Tim sinh vien theo Google email de kiem tra trung du lieu."""
    statement = select(SinhVien).where(SinhVien.google_email == google_email)
    return session.exec(statement).first()


def get_sinh_vien_by_account_id(
    *, session: Session, ma_tai_khoan: int
) -> SinhVien | None:
    """Tim sinh vien theo tai khoan lien ket."""
    statement = select(SinhVien).where(SinhVien.ma_tai_khoan == ma_tai_khoan)
    return session.exec(statement).first()


def get_sinh_viens(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
    q: str | None = None,
    ma_nganh: int | None = None,
    trang_thai_hoc: bool | None = None,
) -> tuple[list[SinhVien], int]:
    """Lay danh sach sinh vien, ho tro tim kiem va loc co ban."""
    conditions = []
    if q:
        search = f"%{q.strip()}%"
        conditions.append(
            or_(
                SinhVien.ho.ilike(search),
                SinhVien.ten.ilike(search),
                SinhVien.google_email.ilike(search),
                SinhVien.dien_thoai.ilike(search),
            )
        )
    if ma_nganh is not None:
        conditions.append(SinhVien.ma_nganh == ma_nganh)
    if trang_thai_hoc is not None:
        conditions.append(SinhVien.trang_thai_hoc == trang_thai_hoc)

    count_statement = select(func.count()).select_from(SinhVien)
    statement = select(SinhVien).order_by(col(SinhVien.ma_sinh_vien).desc())
    for condition in conditions:
        count_statement = count_statement.where(condition)
        statement = statement.where(condition)

    count = session.exec(count_statement).one()
    sinh_viens = session.exec(statement.offset(skip).limit(limit)).all()
    return list(sinh_viens), count


def create_sinh_vien(
    *, session: Session, sinh_vien_create: SinhVienCreate
) -> SinhVien:
    """Tao ho so sinh vien moi."""
    db_sinh_vien = SinhVien.model_validate(sinh_vien_create)
    session.add(db_sinh_vien)
    session.commit()
    session.refresh(db_sinh_vien)
    return db_sinh_vien


def update_sinh_vien(
    *,
    session: Session,
    db_sinh_vien: SinhVien,
    sinh_vien_update: SinhVienUpdate,
) -> SinhVien:
    """Cap nhat mot phan thong tin sinh vien."""
    sinh_vien_data = sinh_vien_update.model_dump(exclude_unset=True)
    for field, value in sinh_vien_data.items():
        setattr(db_sinh_vien, field, value)

    session.add(db_sinh_vien)
    session.commit()
    session.refresh(db_sinh_vien)
    return db_sinh_vien


def delete_sinh_vien(*, session: Session, db_sinh_vien: SinhVien) -> None:
    """Xoa ho so sinh vien khoi database."""
    session.delete(db_sinh_vien)
    session.commit()
