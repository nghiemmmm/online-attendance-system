from fastapi.encoders import jsonable_encoder
from pwdlib.hashers.bcrypt import BcryptHasher
from sqlmodel import Session

from app import crud
from app.core.security import verify_password
from app.models import Account, AccountCreate, AccountUpdate
from tests.utils.utils import random_email, random_lower_string


def test_create_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = AccountCreate(username=email, password=password)
    user = crud.create_account(session=db, account_create=user_in)
    assert user.username == email
    assert hasattr(user, "password_hash")


def test_authenticate_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = AccountCreate(username=email, password=password)
    user = crud.create_account(session=db, account_create=user_in)
    authenticated_user = crud.authenticate_account(session=db, username=email, password=password)
    assert authenticated_user
    assert user.username == authenticated_user.username


def test_not_authenticate_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user = crud.authenticate_account(session=db, username=email, password=password)
    assert user is None


def test_check_if_user_is_active(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = AccountCreate(username=email, password=password)
    user = crud.create_account(session=db, account_create=user_in)
    assert user.status is True


def test_check_if_user_is_active_inactive(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = AccountCreate(username=email, password=password, status=False)
    user = crud.create_account(session=db, account_create=user_in)
    assert user.status is False


def test_check_if_user_is_superuser(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = AccountCreate(username=email, password=password, role="ADMIN")
    user = crud.create_account(session=db, account_create=user_in)
    assert (user.role == "ADMIN") is True


def test_check_if_user_is_superuser_normal_user(db: Session) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = AccountCreate(username=username, password=password)
    user = crud.create_account(session=db, account_create=user_in)
    assert (user.role == "ADMIN") is False


def test_get_user(db: Session) -> None:
    password = random_lower_string()
    username = random_email()
    user_in = AccountCreate(username=username, password=password, role="ADMIN")
    user = crud.create_account(session=db, account_create=user_in)
    user_2 = db.get(Account, user.account_id)
    assert user_2
    assert user.username == user_2.username
    assert jsonable_encoder(user) == jsonable_encoder(user_2)


def test_update_user(db: Session) -> None:
    password = random_lower_string()
    email = random_email()
    user_in = AccountCreate(username=email, password=password, role="ADMIN")
    user = crud.create_account(session=db, account_create=user_in)
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
    """Test that a user with bcrypt password hash gets upgraded to argon2 on login."""
    email = random_email()
    password = random_lower_string()

    # Create a bcrypt hash directly (simulating legacy password)
    bcrypt_hasher = BcryptHasher()
    bcrypt_hash = bcrypt_hasher.hash(password)
    assert bcrypt_hash.startswith("$2")  # bcrypt hashes start with $2

    # Create user with bcrypt hash directly in the database
    user = Account(username=email, password_hash=bcrypt_hash)
    db.add(user)
    db.commit()
    db.refresh(user)

    # Verify the hash is bcrypt before authentication
    assert user.password_hash.startswith("$2")

    # Authenticate - this should upgrade the hash to argon2
    authenticated_user = crud.authenticate_account(session=db, username=email, password=password)
    assert authenticated_user
    assert authenticated_user.username == email

    db.refresh(authenticated_user)

    # Verify the hash was upgraded to argon2
    assert authenticated_user.password_hash.startswith("$argon2")

    verified, updated_hash = verify_password(
        password, authenticated_user.password_hash
    )
    assert verified
    # Should not need another update since it's already argon2
    assert updated_hash is None
