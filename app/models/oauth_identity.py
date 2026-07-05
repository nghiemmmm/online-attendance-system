"""Define OAuth identity database models."""

from datetime import UTC, datetime

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel

from app.core.email_compat import EmailStr


def get_datetime_utc() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(UTC)


class OAuthIdentity(SQLModel, table=True):
    """Represent an external OAuth identity linked to an account."""

    __tablename__ = "oauth_identity"
    __table_args__ = (
        UniqueConstraint(
            "provider",
            "provider_subject",
            name="uq_oauth_identity_provider_subject",
        ),
    )

    oauth_identity_id: int | None = Field(default=None, primary_key=True)
    provider: str = Field(max_length=30, index=True)
    provider_subject: str = Field(max_length=255, index=True)
    email: EmailStr = Field(max_length=255, index=True)
    account_id: int = Field(foreign_key="accounts.account_id", index=True)
    created_at: datetime = Field(default_factory=get_datetime_utc)
    last_login_at: datetime | None = None
