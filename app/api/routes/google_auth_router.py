import hashlib
import logging
import secrets
from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Depends, Request
from sqlmodel import Session

from app import crud
from app.api.deps import SessionDep
from app.core import security
from app.core.config import settings
from app.core.security.auth.google_oauth import oauth
from app.models import GoogleAuthPending, OAuthIdentity, TaiKhoan, TaiKhoanCreate, Token
from app.services.auth_token_service import issue_login_tokens

router = APIRouter(prefix="/auth/google", tags=["google-auth"])
logger = logging.getLogger("app.auth.google")

GoogleAuthMode = Literal["existing", "auto_register"]
GOOGLE_PROVIDER = "google"


def get_email_domain(email: str) -> str:
    """Lấy domain email để log mà không ghi đầy đủ địa chỉ email."""
    if "@" not in email:
        return "-"
    return email.rsplit("@", 1)[1]


@router.get("/login")
async def google_login(
    request: Request,
    mode: GoogleAuthMode = "existing",
    remember_me: bool = False,
):
    request.session["google_auth_mode"] = mode
    request.session["remember_me"] = remember_me
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/login/existing")
async def google_login_existing(request: Request, remember_me: bool = False):
    request.session["google_auth_mode"] = "existing"
    request.session["remember_me"] = remember_me
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/login/register")
async def google_login_register(request: Request, remember_me: bool = False):
    request.session["google_auth_mode"] = "auto_register"
    request.session["remember_me"] = remember_me
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback", name="google_callback")
async def google_callback(
    request: Request, session: SessionDep
) -> Token | GoogleAuthPending:
    google_token = await oauth.google.authorize_access_token(request)
    user_info = await oauth.google.userinfo(token=google_token)
    provider_subject, email = validate_google_user_info(user_info)
    mode: GoogleAuthMode = request.session.pop("google_auth_mode", "existing")
    remember_me = request.session.pop("remember_me", False)

    identity = crud.get_oauth_identity_by_provider_subject(
        session=session,
        provider=GOOGLE_PROVIDER,
        provider_subject=provider_subject,
    )
    if identity:
        account = session.get(TaiKhoan, identity.ma_tai_khoan)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        token = create_login_token_for_account(
            session=session,
            account=account,
            remember_me=remember_me,
            request=request,
        )
        crud.update_oauth_identity_last_login(session=session, identity=identity)
        logger.info(
            "google_login_existing_identity account_id=%s identity_id=%s remember_me=%s",
            account.ma_tai_khoan,
            identity.ma_oauth_identity,
            remember_me,
        )
        return token

    if mode == "auto_register":
        return handle_auto_register_login(
            session=session,
            provider_subject=provider_subject,
            email=email,
            remember_me=remember_me,
            request=request,
        )

    return handle_existing_account_login(
        session=session,
        provider_subject=provider_subject,
        email=email,
        remember_me=remember_me,
        request=request,
    )


def validate_google_user_info(user_info: dict[str, Any]) -> tuple[str, str]:
    provider_subject = user_info.get("sub")
    email = user_info.get("email")
    email_verified = user_info.get("email_verified")

    if not provider_subject:
        raise HTTPException(
            status_code=400,
            detail="Google account does not provide a subject",
        )
    if not email:
        raise HTTPException(
            status_code=400,
            detail="Google account does not provide an email",
        )
    if not email_verified:
        raise HTTPException(
            status_code=400,
            detail="Google email is not verified",
        )

    return provider_subject, email


def handle_existing_account_login(
    *,
    session: Session,
    provider_subject: str,
    email: str,
    remember_me: bool = False,
    request: Request | None = None,
) -> Token:
    account = crud.get_account_by_profile_google_email(
        session=session, google_email=email
    )
    if not account:
        raise HTTPException(
            status_code=404,
            detail="Google email is not registered in the system",
        )

    identity = create_google_identity_for_account(
        session=session,
        provider_subject=provider_subject,
        email=email,
        account=account,
    )
    logger.info(
        "google_identity_linked account_id=%s email_domain=%s",
        account.ma_tai_khoan,
        get_email_domain(email),
    )
    token = create_login_token_for_account(
        session=session,
        account=account,
        remember_me=remember_me,
        request=request,
    )
    crud.update_oauth_identity_last_login(session=session, identity=identity)
    return token


def handle_auto_register_login(
    *,
    session: Session,
    provider_subject: str,
    email: str,
    remember_me: bool = False,
    request: Request | None = None,
) -> Token | GoogleAuthPending:
    validate_allowed_email_domain(email)

    account = crud.get_account_by_profile_google_email(
        session=session, google_email=email
    )

    if account:
        identity = create_google_identity_for_account(
            session=session,
            provider_subject=provider_subject,
            email=email,
            account=account,
        )
        token = create_login_token_for_account(
            session=session,
            account=account,
            remember_me=remember_me,
            request=request,
        )
        crud.update_oauth_identity_last_login(session=session, identity=identity)
        logger.info(
            "google_auto_register_existing_profile account_id=%s email_domain=%s remember_me=%s",
            account.ma_tai_khoan,
            get_email_domain(email),
            remember_me,
        )
        return token

    account_create = TaiKhoanCreate(
        ten_dang_nhap=build_google_username(provider_subject),
        password=secrets.token_urlsafe(32),
        vai_tro="SINH_VIEN",
        trang_thai=False,
    )
    account = crud.create_account(session=session, account_create=account_create)
    create_google_identity_for_account(
        session=session,
        provider_subject=provider_subject,
        email=email,
        account=account,
    )
    logger.info(
        "google_auto_register_pending account_id=%s email_domain=%s",
        account.ma_tai_khoan,
        get_email_domain(email),
    )

    return GoogleAuthPending(
        message="Account created and waiting for approval",
        ma_tai_khoan=account.ma_tai_khoan,
    )


def validate_allowed_email_domain(email: str) -> None:
    allowed_domain = getattr(settings, "GOOGLE_ALLOWED_EMAIL_DOMAIN", "")
    if allowed_domain and not email.endswith(allowed_domain):
        raise HTTPException(
            status_code=403,
            detail="Email domain is not allowed",
        )


def build_google_username(provider_subject: str) -> str:
    subject_hash = hashlib.sha256(
        provider_subject.encode("utf-8")
    ).hexdigest()[:32]
    return f"google_{subject_hash}"


def create_google_identity_for_account(
    *, session: Session, provider_subject: str, email: str, account: TaiKhoan
) -> OAuthIdentity:
    if account.ma_tai_khoan is None:
        raise HTTPException(status_code=400, detail="Account has no id")

    return crud.create_oauth_identity(
        session=session,
        provider=GOOGLE_PROVIDER,
        provider_subject=provider_subject,
        email=email,
        ma_tai_khoan=account.ma_tai_khoan,
    )


def create_login_token_for_account(
    *,
    session: Session,
    account: TaiKhoan,
    remember_me: bool = False,
    request: Request | None = None,
) -> Token:
    """Cấp token đăng nhập cho tài khoản Google đã xác thực."""
    headers = getattr(request, "headers", None)
    client = getattr(request, "client", None)
    return issue_login_tokens(
        session=session,
        account=account,
        remember_me=remember_me,
        user_agent=headers.get("user-agent") if headers else None,
        ip_address=client.host if client else None,
    )
