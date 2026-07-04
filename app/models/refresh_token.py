"""Define refresh token database models."""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


def get_datetime_utc() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(UTC)


class RefreshToken(SQLModel, table=True):
    """Represent a hashed refresh token for session management."""

    __tablename__ = "refresh_token"

    refresh_token_id: int | None = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="accounts.account_id", index=True)
    token_hash: str = Field(max_length=255, unique=True, index=True)
    expires_at: datetime = Field(index=True)
    created_at: datetime = Field(default_factory=get_datetime_utc)
    last_used_at: datetime | None = None
    revoked_at: datetime | None = Field(default=None, index=True)
    user_agent: str | None = Field(default=None, max_length=255)
    ip_address: str | None = Field(default=None, max_length=45)
