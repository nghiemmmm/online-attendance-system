from sqlmodel import Field, SQLModel

class GoogleAuthPending(SQLModel):
    message: str
    status: str = "pending_approval"
    ma_tai_khoan: int

#Response dùng schema Token trong
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: str | None = None
    role: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)
