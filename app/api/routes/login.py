from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app import crud
from app.api.deps import CurrentAccount, SessionDep
from app.core import security
from app.core.config import settings
from app.models import Message, NewPassword, TaiKhoanPublic, TaiKhoanUpdate, Token
from app.utils import verify_password_reset_token

router = APIRouter(tags=["login"])


@router.post("/login/access-token")
def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    account = crud.authenticate_account(
        session=session,
        ten_dang_nhap=form_data.username,
        password=form_data.password,
    )
    if not account:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not account.trang_thai:
        raise HTTPException(status_code=400, detail="Inactive account")

    account.lan_dang_nhap_cuoi = datetime.now(timezone.utc)
    session.add(account)
    session.commit()

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            account.ma_tai_khoan,
            data={"role": account.vai_tro},
            expires_delta=access_token_expires,
        )
    )


@router.post("/login/test-token", response_model=TaiKhoanPublic)
def test_token(current_account: CurrentAccount) -> Any:
    return current_account


@router.post("/reset-password/")
def reset_password(session: SessionDep, body: NewPassword) -> Message:
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")

    account = crud.get_account_by_profile_google_email(
        session=session, google_email=email
    )
    if not account:
        raise HTTPException(status_code=400, detail="Invalid token")
    if not account.trang_thai:
        raise HTTPException(status_code=400, detail="Inactive account")

    crud.update_account(
        session=session,
        db_account=account,
        account_in=TaiKhoanUpdate(password=body.new_password),
    )
    return Message(message="Password updated successfully")
