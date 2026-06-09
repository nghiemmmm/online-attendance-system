from datetime import datetime, timezone

from sqlmodel import Session, select

from app.models import RefreshToken


def create_refresh_token(
    *,
    session: Session,
    ma_tai_khoan: int,
    token_hash: str,
    expires_at: datetime,
    user_agent: str | None = None,
    ip_address: str | None = None,
) -> RefreshToken:
    """Tạo bản ghi refresh token đã hash cho một phiên đăng nhập."""
    db_token = RefreshToken(
        ma_tai_khoan=ma_tai_khoan,
        token_hash=token_hash,
        expires_at=expires_at,
        user_agent=user_agent,
        ip_address=ip_address,
    )
    session.add(db_token)
    session.commit()
    session.refresh(db_token)
    return db_token


def get_refresh_token_by_hash(
    *, session: Session, token_hash: str
) -> RefreshToken | None:
    """Tìm refresh token theo hash đã lưu trong database."""
    statement = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    return session.exec(statement).first()


def update_refresh_token_last_used(
    *, session: Session, refresh_token: RefreshToken
) -> RefreshToken:
    """Cập nhật thời điểm refresh token được dùng gần nhất."""
    refresh_token.last_used_at = datetime.now(timezone.utc)
    session.add(refresh_token)
    session.commit()
    session.refresh(refresh_token)
    return refresh_token


def revoke_refresh_token(
    *, session: Session, refresh_token: RefreshToken
) -> RefreshToken:
    """Thu hồi một refresh token để phiên đăng nhập đó không dùng lại được."""
    refresh_token.revoked_at = datetime.now(timezone.utc)
    session.add(refresh_token)
    session.commit()
    session.refresh(refresh_token)
    return refresh_token


def revoke_all_refresh_tokens_for_account(
    *, session: Session, ma_tai_khoan: int
) -> int:
    """Thu hồi toàn bộ refresh token còn hiệu lực của một tài khoản."""
    statement = select(RefreshToken).where(
        RefreshToken.ma_tai_khoan == ma_tai_khoan,
        RefreshToken.revoked_at.is_(None),
    )
    tokens = session.exec(statement).all()
    now = datetime.now(timezone.utc)
    for token in tokens:
        token.revoked_at = now
        session.add(token)
    session.commit()
    return len(tokens)
