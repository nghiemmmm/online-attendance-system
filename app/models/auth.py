"""Define authentication request and response models."""

from sqlmodel import Field, SQLModel


class GoogleAuthPending(SQLModel):
    """Represent a Google authentication request pending approval."""

    message: str
    status: str = "pending_approval"
    ma_tai_khoan: int


class Token(SQLModel):
    """Represent access and optional refresh token data."""

    access_token: str
    token_type: str = "bearer"
    refresh_token: str | None = None
    expires_in: int | None = None


class LoginRequest(SQLModel):
    """Represent JSON login credentials."""

    username: str = Field(max_length=50)
    password: str = Field(min_length=5, max_length=128)
    remember_me: bool = False


class RefreshTokenRequest(SQLModel):
    """Represent a request to refresh an access token."""

    refresh_token: str = Field(min_length=20)


class LogoutRequest(SQLModel):
    """Represent a request to log out one refresh-token session."""

    refresh_token: str = Field(min_length=20)


class TokenPayload(SQLModel):
    """Represent JWT token payload claims."""

    sub: str | None = None
    role: str | None = None


class NewPassword(SQLModel):
    """Represent data required to reset a password."""

    token: str
    new_password: str = Field(min_length=8, max_length=128)


class UpdatePassword(SQLModel):
    """Represent data required to update a password."""

    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)
