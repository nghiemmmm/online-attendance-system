from sqlmodel import Field, SQLModel

class GoogleAuthPending(SQLModel):
    message: str
    status: str = "pending_approval"
    ma_tai_khoan: int

#Response dùng schema Token trong
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str | None = None
    expires_in: int | None = None


class LoginRequest(SQLModel):
    """Dữ liệu đăng nhập JSON, có hỗ trợ tùy chọn ghi nhớ đăng nhập."""

    username: str = Field(max_length=50)
    password: str = Field(min_length=5, max_length=128)
    remember_me: bool = False


class RefreshTokenRequest(SQLModel):
    """Request dùng refresh token để xin access token mới."""

    refresh_token: str = Field(min_length=20)


class LogoutRequest(SQLModel):
    """Request đăng xuất một phiên bằng refresh token."""

    refresh_token: str = Field(min_length=20)


class TokenPayload(SQLModel):
    sub: str | None = None
    role: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)
