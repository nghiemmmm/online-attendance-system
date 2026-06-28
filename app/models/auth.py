"""Define authentication request and response models."""

from pydantic import Field, field_validator

from app.models.base import AppBaseModel


class GoogleAuthPending(AppBaseModel):
    """Represent a Google authentication request pending approval."""

    message: str
    status: str = "pending_approval"
    account_id: int


class Token(AppBaseModel):
    """Represent access and optional refresh token data."""

    access_token: str
    token_type: str = "bearer"
    refresh_token: str | None = None
    expires_in: int | None = None


class LoginRequest(AppBaseModel):
    """Represent JSON login credentials."""

    username: str = Field(max_length=50)
    password: str = Field(min_length=5, max_length=128)
    remember_me: bool = False

    @field_validator("username")
    @classmethod
    def _normalize_username(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError("username cannot be empty")
        return normalized


class RefreshTokenRequest(AppBaseModel):
    """Represent a request to refresh an access token."""

    refresh_token: str = Field(min_length=20)

    @field_validator("refresh_token")
    @classmethod
    def _normalize_refresh_token(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("refresh_token cannot be empty")
        return normalized


class LogoutRequest(AppBaseModel):
    """Represent a request to log out one refresh-token session."""

    refresh_token: str = Field(min_length=20)

    @field_validator("refresh_token")
    @classmethod
    def _normalize_logout_token(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("refresh_token cannot be empty")
        return normalized


class TokenPayload(AppBaseModel):
    """Represent JWT token payload claims."""

    sub: str | None = None
    role: str | None = None


class NewPassword(AppBaseModel):
    """Represent data required to reset a password."""

    token: str
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("token")
    @classmethod
    def _normalize_token(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("token cannot be empty")
        return normalized


class UpdatePassword(AppBaseModel):
    """Represent data required to update a password."""

    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)
