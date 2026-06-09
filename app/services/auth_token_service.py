from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import logging
import secrets

from fastapi import HTTPException, status
from sqlmodel import Session

from app import crud
from app.core import security
from app.core.config import settings
from app.models import RefreshToken, TaiKhoan, Token

logger = logging.getLogger("app.auth")


def hash_refresh_token(raw_token: str) -> str:
    """Hash refresh token bằng SECRET_KEY để không lưu token gốc trong database."""
    return hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        raw_token.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def create_raw_refresh_token() -> str:
    """Sinh refresh token ngẫu nhiên dùng cho Remember Me."""
    return secrets.token_urlsafe(64)


def normalize_datetime_utc(value: datetime) -> datetime:
    """Chuẩn hóa datetime từ DB về dạng có timezone UTC để so sánh an toàn."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def create_access_token_for_account(*, account: TaiKhoan) -> Token:
    """Tạo access token JWT ngắn hạn cho tài khoản đã xác thực."""
    if account.ma_tai_khoan is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account has no id",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            account.ma_tai_khoan,
            data={"role": account.vai_tro},
            expires_delta=access_token_expires,
        ),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


def create_refresh_token_for_account(
    *,
    session: Session,
    account: TaiKhoan,
    user_agent: str | None = None,
    ip_address: str | None = None,
) -> str:
    """Tạo refresh token raw, lưu hash vào database và trả token raw cho client."""
    if account.ma_tai_khoan is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account has no id",
        )

    raw_token = create_raw_refresh_token()
    token_hash = hash_refresh_token(raw_token)
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    crud.create_refresh_token(
        session=session,
        ma_tai_khoan=account.ma_tai_khoan,
        token_hash=token_hash,
        expires_at=expires_at,
        user_agent=user_agent,
        ip_address=ip_address,
    )
    logger.info(
        "refresh_token_created account_id=%s expires_at=%s",
        account.ma_tai_khoan,
        expires_at.isoformat(),
    )
    return raw_token


def issue_login_tokens(
    *,
    session: Session,
    account: TaiKhoan,
    remember_me: bool = False,
    user_agent: str | None = None,
    ip_address: str | None = None,
) -> Token:
    """Cấp token đăng nhập, kèm refresh token nếu người dùng chọn Remember Me."""
    if not account.trang_thai:
        logger.warning(
            "login_token_rejected_inactive account_id=%s username=%s",
            account.ma_tai_khoan,
            account.ten_dang_nhap,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive account or waiting for approval",
        )

    account.lan_dang_nhap_cuoi = datetime.now(timezone.utc)
    session.add(account)
    session.commit()
    session.refresh(account)

    token = create_access_token_for_account(account=account)
    if remember_me:
        token.refresh_token = create_refresh_token_for_account(
            session=session,
            account=account,
            user_agent=user_agent,
            ip_address=ip_address,
        )
    logger.info(
        "login_tokens_issued account_id=%s username=%s remember_me=%s",
        account.ma_tai_khoan,
        account.ten_dang_nhap,
        remember_me,
    )
    return token


def _get_valid_refresh_token(
    *, session: Session, raw_refresh_token: str
) -> RefreshToken:
    """Kiểm tra refresh token còn tồn tại, chưa hết hạn và chưa bị thu hồi."""
    token_hash = hash_refresh_token(raw_refresh_token)
    db_token = crud.get_refresh_token_by_hash(
        session=session,
        token_hash=token_hash,
    )
    if not db_token:
        logger.warning("refresh_token_invalid")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    if db_token.revoked_at is not None:
        logger.warning(
            "refresh_token_revoked token_id=%s account_id=%s",
            db_token.ma_refresh_token,
            db_token.ma_tai_khoan,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
        )
    if normalize_datetime_utc(db_token.expires_at) <= datetime.now(timezone.utc):
        logger.warning(
            "refresh_token_expired token_id=%s account_id=%s",
            db_token.ma_refresh_token,
            db_token.ma_tai_khoan,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
        )
    return db_token


def refresh_access_token(*, session: Session, raw_refresh_token: str) -> Token:
    """Dùng refresh token hợp lệ để cấp access token mới."""
    db_token = _get_valid_refresh_token(
        session=session,
        raw_refresh_token=raw_refresh_token,
    )
    account = session.get(TaiKhoan, db_token.ma_tai_khoan)
    if not account:
        logger.warning(
            "refresh_token_account_missing token_id=%s account_id=%s",
            db_token.ma_refresh_token,
            db_token.ma_tai_khoan,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )
    if not account.trang_thai:
        logger.warning(
            "refresh_token_rejected_inactive account_id=%s",
            account.ma_tai_khoan,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive account",
        )

    crud.update_refresh_token_last_used(
        session=session,
        refresh_token=db_token,
    )
    logger.info(
        "access_token_refreshed account_id=%s token_id=%s",
        account.ma_tai_khoan,
        db_token.ma_refresh_token,
    )
    return create_access_token_for_account(account=account)


def logout_refresh_token(*, session: Session, raw_refresh_token: str) -> None:
    """Đăng xuất một phiên bằng cách thu hồi refresh token tương ứng."""
    db_token = _get_valid_refresh_token(
        session=session,
        raw_refresh_token=raw_refresh_token,
    )
    crud.revoke_refresh_token(session=session, refresh_token=db_token)
    logger.info(
        "refresh_token_logged_out token_id=%s account_id=%s",
        db_token.ma_refresh_token,
        db_token.ma_tai_khoan,
    )


def logout_all_refresh_tokens(*, session: Session, account: TaiKhoan) -> int:
    """Đăng xuất khỏi mọi thiết bị bằng cách thu hồi toàn bộ refresh token."""
    if account.ma_tai_khoan is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account has no id",
        )
    revoked_count = crud.revoke_all_refresh_tokens_for_account(
        session=session,
        ma_tai_khoan=account.ma_tai_khoan,
    )
    logger.info(
        "all_refresh_tokens_logged_out account_id=%s revoked_count=%s",
        account.ma_tai_khoan,
        revoked_count,
    )
    return revoked_count
