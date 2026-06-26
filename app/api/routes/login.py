from typing import Annotated, Any

import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm

from app import crud
from app.api.deps import CurrentAccount, SessionDep, login_rate_limiter
from app.models import (
    LoginRequest,
    LogoutRequest,
    Message,
    NewPassword,
    RefreshTokenRequest,
    TaiKhoanPublic,
    TaiKhoanUpdate,
    Token,
)
from app.services.auth_token_service import (
    issue_login_tokens,
    logout_all_refresh_tokens,
    logout_refresh_token,
    refresh_access_token,
)
from app.services.audit_log_service import write_audit_log
from app.utils import verify_password_reset_token

router = APIRouter(tags=["login"])
logger = logging.getLogger("app.auth")


@router.post("/login/access-token", dependencies=[Depends(login_rate_limiter)])
def login_access_token(
    request: Request,
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    account = crud.authenticate_account(
        session=session,
        ten_dang_nhap=form_data.username,
        password=form_data.password,
    )
    if not account:
        logger.warning("password_login_failed username=%s", form_data.username)
        write_audit_log(
            session=session,
            hanh_dong="DANG_NHAP",
            doi_tuong="TaiKhoan",
            doi_tuong_id=form_data.username,
            request=request,
            trang_thai="FAILED",
            chi_tiet="Sai ten dang nhap hoac mat khau",
        )
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    write_audit_log(
        session=session,
        account=account,
        hanh_dong="DANG_NHAP",
        doi_tuong="TaiKhoan",
        doi_tuong_id=account.ma_tai_khoan,
        request=request,
    )
    token = issue_login_tokens(session=session, account=account, remember_me=False)
    token.refresh_token = None
    return token


@router.post("/login/json", dependencies=[Depends(login_rate_limiter)])
def login_json(
    *,
    request: Request,
    session: SessionDep,
    body: LoginRequest,
) -> Token:
    """
    Đăng nhập bằng JSON và hỗ trợ Remember Me.

    Khi remember_me=True, backend cấp thêm refresh token dài hạn để client có thể
    xin access token mới mà không cần nhập lại mật khẩu.
    """
    account = crud.authenticate_account(
        session=session,
        ten_dang_nhap=body.username,
        password=body.password,
    )
    if not account:
        logger.warning("json_login_failed username=%s", body.username)
        write_audit_log(
            session=session,
            hanh_dong="DANG_NHAP",
            doi_tuong="TaiKhoan",
            doi_tuong_id=body.username,
            request=request,
            trang_thai="FAILED",
            chi_tiet="Sai ten dang nhap hoac mat khau",
        )
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    write_audit_log(
        session=session,
        account=account,
        hanh_dong="DANG_NHAP",
        doi_tuong="TaiKhoan",
        doi_tuong_id=account.ma_tai_khoan,
        request=request,
    )

    return issue_login_tokens(
        session=session,
        account=account,
        remember_me=body.remember_me,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )


@router.post("/login/refresh")
def refresh_token(session: SessionDep, body: RefreshTokenRequest) -> Token:
    """Cấp access token mới từ refresh token hợp lệ."""
    return refresh_access_token(
        session=session,
        raw_refresh_token=body.refresh_token,
    )


@router.post("/login/logout", response_model=Message)
def logout(session: SessionDep, body: LogoutRequest) -> Message:
    """Đăng xuất một phiên bằng cách thu hồi refresh token hiện tại."""
    logout_refresh_token(session=session, raw_refresh_token=body.refresh_token)
    return Message(message="Logged out successfully")


@router.post("/login/logout-all", response_model=Message)
def logout_all(session: SessionDep, current_account: CurrentAccount) -> Message:
    """Đăng xuất khỏi tất cả thiết bị bằng cách thu hồi mọi refresh token."""
    revoked_count = logout_all_refresh_tokens(
        session=session,
        account=current_account,
    )
    return Message(message=f"Logged out from {revoked_count} session(s)")


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
