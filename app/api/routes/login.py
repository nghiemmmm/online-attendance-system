import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm

from app import crud
from app.api.deps import CurrentAccount, SessionDep, login_rate_limiter
from app.models import (
    AccountPublic,
    AccountUpdate,
    LoginRequest,
    LogoutRequest,
    Message,
    NewPassword,
    RefreshTokenRequest,
    Token,
)
from app.services.audit_log_service import write_audit_log
from app.services.auth_token_service import (
    issue_login_tokens,
    logout_all_refresh_tokens,
    logout_refresh_token,
    refresh_access_token,
)
from app.utils import (
    generate_password_reset_token,
    generate_reset_password_email,
    send_email,
    verify_password_reset_token,
)

router = APIRouter(tags=["login"])
logger = logging.getLogger("app.auth")


@router.post("/auth/access-tokens", dependencies=[Depends(login_rate_limiter)])
def login_access_token(
    request: Request,
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    try:
        account = crud.authenticate_account(
            session=session,
            username=form_data.username,
            password=form_data.password,
        )
    except HTTPException as e:
        logger.warning(
            "password_login_failed username=%s detail=%s", form_data.username, e.detail
        )
        write_audit_log(
            session=session,
            action="DANG_NHAP",
            target_type="Account",
            target_id=form_data.username,
            request=request,
            status="FAILED",
            detail=e.detail,
        )
        raise e

    write_audit_log(
        session=session,
        account=account,
        action="DANG_NHAP",
        target_type="Account",
        target_id=account.account_id,
        request=request,
    )
    token = issue_login_tokens(session=session, account=account, remember_me=False)
    token.refresh_token = None
    return token


@router.post("/auth/tokens", dependencies=[Depends(login_rate_limiter)])
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
    try:
        account = crud.authenticate_account(
            session=session,
            username=body.username,
            password=body.password,
        )
    except HTTPException as e:
        logger.warning(
            "json_login_failed username=%s detail=%s", body.username, e.detail
        )
        write_audit_log(
            session=session,
            action="DANG_NHAP",
            target_type="Account",
            target_id=body.username,
            request=request,
            status="FAILED",
            detail=e.detail,
        )
        raise e

    write_audit_log(
        session=session,
        account=account,
        action="DANG_NHAP",
        target_type="Account",
        target_id=account.account_id,
        request=request,
    )

    return issue_login_tokens(
        session=session,
        account=account,
        remember_me=body.remember_me,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )


@router.post("/auth/token-refreshes")
def refresh_token(session: SessionDep, body: RefreshTokenRequest) -> Token:
    """Cấp access token mới từ refresh token hợp lệ."""
    return refresh_access_token(
        session=session,
        raw_refresh_token=body.refresh_token,
    )


@router.delete("/sessions/current", response_model=Message)
def logout(session: SessionDep, body: LogoutRequest) -> Message:
    """Đăng xuất một phiên bằng cách weekday hồi refresh token hiện tại."""
    logout_refresh_token(session=session, raw_refresh_token=body.refresh_token)
    return Message(message="Logged out successfully")


@router.delete("/sessions", response_model=Message)
def logout_all(session: SessionDep, current_account: CurrentAccount) -> Message:
    """Đăng xuất khỏi tất cả thiết bị bằng cách weekday hồi mọi refresh token."""
    revoked_count = logout_all_refresh_tokens(
        session=session,
        account=current_account,
    )
    return Message(message=f"Logged out from {revoked_count} session(s)")


@router.get("/auth/token", response_model=AccountPublic)
def test_token(current_account: CurrentAccount) -> Any:
    return current_account


@router.post("/password-recovery/{email}", response_model=Message)
def recover_password(email: str, session: SessionDep) -> Message:
    """Password recovery endpoint."""
    account = crud.get_account_by_profile_google_email(
        session=session, google_email=email
    )
    if account:
        password_reset_token = generate_password_reset_token(email=email)
        email_data = generate_reset_password_email(
            email_to=email, email=email, token=password_reset_token
        )
        send_email(
            email_to=email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    return Message(message="Password recovery email sent")


@router.post("/password-resets")
def reset_password(session: SessionDep, body: NewPassword) -> Message:
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")

    account = crud.get_account_by_profile_google_email(
        session=session, google_email=email
    )
    if not account:
        raise HTTPException(status_code=400, detail="Invalid token")
    if not account.status:
        raise HTTPException(status_code=400, detail="Inactive account")

    crud.update_account(
        session=session,
        db_account=account,
        account_in=AccountUpdate(password=body.new_password),
    )
    return Message(message="Password updated successfully")
