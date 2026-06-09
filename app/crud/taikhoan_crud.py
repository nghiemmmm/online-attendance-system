from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import CanBo, SinhVien, TaiKhoan, TaiKhoanCreate, TaiKhoanUpdate


def get_account_by_username(
    *, session: Session, ten_dang_nhap: str
) -> TaiKhoan | None:
    statement = select(TaiKhoan).where(TaiKhoan.ten_dang_nhap == ten_dang_nhap)
    return session.exec(statement).first()


def get_account_by_profile_google_email(
    *, session: Session, google_email: str
) -> TaiKhoan | None:
    sinh_vien = session.exec(
        select(SinhVien).where(SinhVien.google_email == google_email)
    ).first()
    if sinh_vien and sinh_vien.ma_tai_khoan:
        return session.get(TaiKhoan, sinh_vien.ma_tai_khoan)

    can_bo = session.exec(
        select(CanBo).where(CanBo.google_email == google_email)
    ).first()
    if can_bo and can_bo.ma_tai_khoan:
        return session.get(TaiKhoan, can_bo.ma_tai_khoan)

    return None


def get_account_by_profile_email(*, session: Session, email: str) -> TaiKhoan | None:
    return get_account_by_profile_google_email(
        session=session, google_email=email
    )


def get_account_profile(*, session: Session, account: TaiKhoan) -> dict | None:
    if account.vai_tro == "SINH_VIEN":
        profile = session.exec(
            select(SinhVien).where(SinhVien.ma_tai_khoan == account.ma_tai_khoan)
        ).first()
    elif account.vai_tro in {"GIANG_VIEN", "CAN_BO"}:
        profile = session.exec(
            select(CanBo).where(CanBo.ma_tai_khoan == account.ma_tai_khoan)
        ).first()
    else:
        profile = None

    return profile.model_dump() if profile else None


def create_account(*, session: Session, account_create: TaiKhoanCreate) -> TaiKhoan:
    db_account = TaiKhoan(
        ten_dang_nhap=account_create.ten_dang_nhap,
        mat_khau_hash=get_password_hash(account_create.password),
        vai_tro=account_create.vai_tro,
        trang_thai=account_create.trang_thai,
    )
    session.add(db_account)
    session.commit()
    session.refresh(db_account)
    return db_account


def update_account(
    *, session: Session, db_account: TaiKhoan, account_in: TaiKhoanUpdate
) -> TaiKhoan:
    account_data: dict[str, Any] = account_in.model_dump(
        exclude_unset=True, exclude_none=True
    )
    password = account_data.pop("password", None)
    if password:
        account_data["mat_khau_hash"] = get_password_hash(password)

    for field, value in account_data.items():
        setattr(db_account, field, value)

    session.add(db_account)
    session.commit()
    session.refresh(db_account)
    return db_account


def authenticate_account(
    *, session: Session, ten_dang_nhap: str, password: str
) -> TaiKhoan | None:
    db_account = get_account_by_username(
        session=session, ten_dang_nhap=ten_dang_nhap
    )
    if not db_account:
        return None
    if not verify_password(password, db_account.mat_khau_hash):
        return None
    return db_account
