from datetime import datetime, timezone

from sqlmodel import Session, select

from app.models import OAuthIdentity


def get_oauth_identity_by_provider_subject(
    *, session: Session, provider: str, provider_subject: str
) -> OAuthIdentity | None:
    statement = select(OAuthIdentity).where(
        OAuthIdentity.provider == provider,
        OAuthIdentity.provider_subject == provider_subject,
    )
    return session.exec(statement).first()


def create_oauth_identity(
    *,
    session: Session,
    provider: str,
    provider_subject: str,
    email: str,
    ma_tai_khoan: int,
) -> OAuthIdentity:
    identity = OAuthIdentity(
        provider=provider,
        provider_subject=provider_subject,
        email=email,
        ma_tai_khoan=ma_tai_khoan,
    )
    session.add(identity)
    session.commit()
    session.refresh(identity)
    return identity


def update_oauth_identity_last_login(
    *, session: Session, identity: OAuthIdentity
) -> OAuthIdentity:
    identity.last_login_at = datetime.now(timezone.utc)
    session.add(identity)
    session.commit()
    session.refresh(identity)
    return identity
