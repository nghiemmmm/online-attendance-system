from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import TaiKhoan, TaiKhoanCreate, TaiKhoanUpdate
from tests.utils.utils import random_email, random_lower_string


def user_authentication_headers(
    *, client: TestClient, email: str, password: str
) -> dict[str, str]:
    data = {"username": email, "password": password}

    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def create_random_user(db: Session) -> TaiKhoan:
    email = random_email()
    password = random_lower_string()
    user_in = TaiKhoanCreate(ten_dang_nhap=email, password=password)
    user = crud.create_account(session=db, account_create=user_in)
    return user


def authentication_token_from_email(
    *, client: TestClient, email: str, db: Session
) -> dict[str, str]:
    """
    Return a valid token for the user with given email.

    If the user doesn't exist it is created first.
    """
    password = random_lower_string()
    user = crud.get_account_by_profile_email(session=db, email=email)
    if not user:
        user_in_create = TaiKhoanCreate(ten_dang_nhap=email, password=password)
        user = crud.create_account(session=db, account_create=user_in_create)
    else:
        user_in_update = TaiKhoanUpdate(password=password)
        if not user.ma_tai_khoan:
            raise Exception("User id not set")
        user = crud.update_account(session=db, db_account=user, account_in=user_in_update)

    return user_authentication_headers(client=client, email=email, password=password)
