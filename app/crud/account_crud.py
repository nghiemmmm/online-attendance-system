from datetime import datetime, timedelta, timezone
from typing import Any

from sqlmodel import Session, select

from fastapi import HTTPException
from app.core.exceptions import AccountLockedError
from app.core.security import get_password_hash, verify_password
from app.models import Staff, Student, Account, AccountCreate, AccountUpdate


def get_account_by_username(
    *, session: Session, username: str
) -> Account | None:
    statement = select(Account).where(Account.username == username)
    return session.exec(statement).first()


def get_account_by_profile_google_email(
    *, session: Session, google_email: str
) -> Account | None:
    student = session.exec(
        select(Student).where(Student.google_email == google_email)
    ).first()
    if student and student.account_id:
        return session.get(Account, student.account_id)

    staff = session.exec(
        select(Staff).where(Staff.google_email == google_email)
    ).first()
    if staff and staff.account_id:
        return session.get(Account, staff.account_id)

    return None


def get_account_by_profile_email(*, session: Session, email: str) -> Account | None:
    return get_account_by_profile_google_email(
        session=session, google_email=email
    )


def get_account_profile(*, session: Session, account: Account) -> dict | None:
    if account.role == "SINH_VIEN":
        profile = session.exec(
            select(Student).where(Student.account_id == account.account_id)
        ).first()
        if profile:
            profile_dict = profile.model_dump()
            from app.models import FaceImage, Major
            from sqlalchemy import func
            face_count = session.exec(
                select(func.count(FaceImage.image_id)).where(FaceImage.student_id == profile.student_id)
            ).first() or 0
            major = session.get(Major, profile.major_id) if profile.major_id else None
            profile_dict["major_name"] = major.major_name if major else f"Ngành {profile.major_id}"
            profile_dict["face_registered"] = face_count > 0
            profile_dict["registered_faces_count"] = face_count
            return profile_dict
        return None
    elif account.role in {"GIANG_VIEN", "CAN_BO"}:
        profile = session.exec(
            select(Staff).where(Staff.account_id == account.account_id)
        ).first()
    else:
        profile = None

    return profile.model_dump() if profile else None


def create_account(*, session: Session, account_create: AccountCreate) -> Account:
    db_account = Account(
        username=account_create.username,
        password_hash=get_password_hash(account_create.password),
        role=account_create.role,
        status=account_create.status,
    )
    session.add(db_account)
    session.commit()
    session.refresh(db_account)
    return db_account


def update_account(
    *, session: Session, db_account: Account, account_in: AccountUpdate
) -> Account:
    account_data: dict[str, Any] = account_in.model_dump(
        exclude_unset=True, exclude_none=True
    )
    password = account_data.pop("password", None)
    if password:
        account_data["password_hash"] = get_password_hash(password)

    for field, value in account_data.items():
        setattr(db_account, field, value)

    session.add(db_account)
    session.commit()
    session.refresh(db_account)
    return db_account


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

def authenticate_account(
    *, session: Session, username: str, password: str
) -> Account | None:
    db_account = get_account_by_username(
        session=session, username=username
    )
    if not db_account:
        db_account = get_account_by_profile_email(session=session, email=username)
    if not db_account:
        raise HTTPException(
            status_code=400,
            detail=f"Không tìm thấy tài khoản với MSSV hoặc Email '{username}'. Vui lòng kiểm tra lại hoặc Đăng ký tài khoản.",
        )

    if not db_account.status:
        raise HTTPException(
            status_code=400,
            detail="Tài khoản của bạn hiện đang bị khóa hoặc ngưng hoạt động.",
        )

    # Check if account is locked
    if db_account.locked_until and db_account.locked_until > get_datetime_utc():
        raise HTTPException(
            status_code=400,
            detail="Tài khoản tạm thời bị khóa do nhập sai mật khẩu quá 5 lần. Vui lòng thử lại sau 15 phút.",
        )

    verified, new_hash = verify_password(password, db_account.password_hash)
    if not verified:
        # Increment failed login attempts
        db_account.failed_login_count += 1
        remaining = 5 - db_account.failed_login_count
        if db_account.failed_login_count >= 5:
            db_account.locked_until = get_datetime_utc() + timedelta(minutes=15)
            session.add(db_account)
            session.commit()
            raise HTTPException(
                status_code=400,
                detail="Tài khoản đã bị tạm khóa 15 phút do nhập sai mật khẩu quá 5 lần liên tiếp.",
            )

        session.add(db_account)
        session.commit()
        raise HTTPException(
            status_code=400,
            detail=f"Mật khẩu nhập vào không chính xác. (Bạn còn {remaining} lần thử trước khi tài khoản bị khóa tạm thời).",
        )

    # Successful login, reset lockout
    db_account.failed_login_count = 0
    db_account.locked_until = None
    if new_hash:
        db_account.password_hash = new_hash
    session.add(db_account)
    session.commit()

    return db_account


def create_user(*, session: Session, user_create: AccountCreate) -> Account:
    return create_account(session=session, account_create=user_create)


def get_user_by_email(*, session: Session, username: str) -> Account | None:
    return get_account_by_username(session=session, username=username)


def update_user(*, session: Session, db_user: Account, user_in: AccountUpdate) -> Account:
    return update_account(session=session, db_account=db_user, account_in=user_in)
