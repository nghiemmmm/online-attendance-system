from sqlalchemy import text
from sqlmodel import Session, create_engine, select

from app import crud
from app.core.config import settings
from app.models import TaiKhoan, TaiKhoanCreate

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def ensure_pgvector_extension(session: Session) -> None:
    session.exec(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    session.commit()


def init_db(session: Session) -> None:
    ensure_pgvector_extension(session)

    account = session.exec(
        select(TaiKhoan).where(TaiKhoan.ten_dang_nhap == settings.FIRST_SUPERUSER)
    ).first()
    if not account:
        account_in = TaiKhoanCreate(
            ten_dang_nhap=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            vai_tro="ADMIN",
        )
        crud.create_account(session=session, account_create=account_in)
