from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import TaiKhoan, TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/login/access-token")


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_account(session: SessionDep, token: TokenDep) -> TaiKhoan:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    if not token_data.sub:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    try:
        account_id = int(token_data.sub)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    account = session.get(TaiKhoan, account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Account not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not account.trang_thai:
        raise HTTPException(status_code=400, detail="Inactive account")
    return account


CurrentAccount = Annotated[TaiKhoan, Depends(get_current_account)]
CurrentUser = CurrentAccount


def get_current_active_superuser(current_account: CurrentAccount) -> TaiKhoan:
    if current_account.vai_tro != "ADMIN":
        raise HTTPException(
            status_code=403, detail="The account doesn't have enough privileges"
        )
    return current_account

def get_current_active_sinhvien(current_account: CurrentAccount) -> TaiKhoan:
    if current_account.vai_tro != "SINH_VIEN":
        raise HTTPException(
            status_code=403, detail="The account doesn't have enough privileges"
        )
    return current_account

def get_current_active_giangvien(current_account: CurrentAccount) -> TaiKhoan:
    if current_account.vai_tro != "GIANG_VIEN":
        raise HTTPException(
            status_code=403, detail="The account doesn't have enough privileges"
        )
    return current_account
