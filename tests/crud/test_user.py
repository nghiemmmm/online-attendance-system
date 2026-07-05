from pwdlib.hashers.bcrypt import BcryptHasher
from sqlmodel import Session

from app import crud
from app.core.security import verify_password
from app.models import Account, AccountCreate, AccountUpdate
from tests.utils.utils import random_email, random_lower_string


def test_create_user(db: Session) -> None:
    """Kiem tra tao tai khoan: username dung, hash ton tai, status/role mac dinh."""
    email = random_email()
    password = random_lower_string()

    user = crud.create_account(
        session=db, account_create=AccountCreate(username=email, password=password)
    )
    assert user.username == email
    assert hasattr(user, "password_hash")
    assert user.status is True
    assert user.role != "ADMIN"

    inactive = crud.create_account(
        session=db,
        account_create=AccountCreate(
            username=random_email(), password=password, status=False
        ),
    )
    assert inactive.status is False

    admin = crud.create_account(
        session=db,
        account_create=AccountCreate(
            username=random_email(), password=password, role="ADMIN"
        ),
    )
    assert admin.role == "ADMIN"


def test_authenticate_user(db: Session) -> None:
    """Kiem tra xac thuc tai khoan dung thong tin."""
    email = random_email()
    password = random_lower_string()
    user = crud.create_account(
        session=db, account_create=AccountCreate(username=email, password=password)
    )
    authenticated_user = crud.authenticate_account(
        session=db, username=email, password=password
    )
    assert authenticated_user
    assert user.username == authenticated_user.username


def test_not_authenticate_user(db: Session) -> None:
    """Kiem tra authenticate_account raise 400 khi tai khoan khong ton tai."""
    import pytest
    from fastapi import HTTPException

    email = random_email()
    password = random_lower_string()
    with pytest.raises(HTTPException) as exc_info:
        crud.authenticate_account(session=db, username=email, password=password)
    assert exc_info.value.status_code == 400


def test_update_user(db: Session) -> None:
    """Kiem tra cap nhat mat khau tai khoan."""
    password = random_lower_string()
    email = random_email()
    user = crud.create_account(
        session=db,
        account_create=AccountCreate(username=email, password=password, role="ADMIN"),
    )
    new_password = random_lower_string()
    user_in_update = AccountUpdate(password=new_password, role="ADMIN")
    if user.account_id is not None:
        crud.update_account(session=db, db_account=user, account_in=user_in_update)
    user_2 = db.get(Account, user.account_id)
    assert user_2
    assert user.username == user_2.username
    verified, _ = verify_password(new_password, user_2.password_hash)
    assert verified


def test_authenticate_user_with_bcrypt_upgrades_to_argon2(db: Session) -> None:
    """Kiem tra tai khoan co hash bcrypt duoc nang cap sang argon2 khi dang nhap."""
    email = random_email()
    password = random_lower_string()

    bcrypt_hasher = BcryptHasher()
    bcrypt_hash = bcrypt_hasher.hash(password)
    assert bcrypt_hash.startswith("$2")

    user = Account(username=email, password_hash=bcrypt_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    assert user.password_hash.startswith("$2")

    authenticated_user = crud.authenticate_account(
        session=db, username=email, password=password
    )
    assert authenticated_user
    assert authenticated_user.username == email

    db.refresh(authenticated_user)
    assert authenticated_user.password_hash.startswith("$argon2")

    verified, updated_hash = verify_password(password, authenticated_user.password_hash)
    assert verified
    assert updated_hash is None
