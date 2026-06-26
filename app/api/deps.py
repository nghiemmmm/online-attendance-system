from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status, Request
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


def normalize_role(role: str | None) -> str:
    normalized = (role or "").strip().upper().replace("-", "_").replace(" ", "_")
    role_aliases = {
        "ADMIN": "ADMIN",
        "QUAN_TRI_VIEN": "ADMIN",
        "QTV": "ADMIN",
        "SINH_VIEN": "SINH_VIEN",
        "SINHVIEN": "SINH_VIEN",
        "STUDENT": "SINH_VIEN",
        "SV": "SINH_VIEN",
        "GIANG_VIEN": "GIANG_VIEN",
        "GIANGVIEN": "GIANG_VIEN",
        "CAN_BO": "GIANG_VIEN",
        "CANBO": "GIANG_VIEN",
        "LECTURER": "GIANG_VIEN",
        "TEACHER": "GIANG_VIEN",
        "GV": "GIANG_VIEN",
    }
    return role_aliases.get(normalized, normalized)


def get_current_active_superuser(current_account: CurrentAccount) -> TaiKhoan:
    if normalize_role(current_account.vai_tro) != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail=f"Yeu cau vai tro ADMIN, tai khoan hien tai la {current_account.vai_tro}",
        )
    return current_account

def get_current_active_student(current_account: CurrentAccount) -> TaiKhoan:
    if normalize_role(current_account.vai_tro) != "SINH_VIEN":
        raise HTTPException(
            status_code=403,
            detail=f"Yeu cau vai tro SINH_VIEN, tai khoan hien tai la {current_account.vai_tro}",
        )
    return current_account

def get_current_active_lecturer(current_account: CurrentAccount) -> TaiKhoan:
    if normalize_role(current_account.vai_tro) != "GIANG_VIEN":
        raise HTTPException(
            status_code=403,
            detail=f"Yeu cau vai tro GIANG_VIEN, tai khoan hien tai la {current_account.vai_tro}",
        )
    return current_account


from collections import defaultdict
import time


class RateLimiter:
    """A lightweight IP-based rate limiter dependency."""

    def __init__(self, times: int, seconds: int):
        self.times = times
        self.seconds = seconds
        self.history = defaultdict(list)

    def __call__(self, request: Request):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        # Clean up old timestamps
        self.history[client_ip] = [t for t in self.history[client_ip] if now - t < self.seconds]

        if len(self.history[client_ip]) >= self.times:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. Please try again later."
            )

        self.history[client_ip].append(now)


login_rate_limiter = RateLimiter(times=5, seconds=60)

