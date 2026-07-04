import pytest
from fastapi import HTTPException

from app.api.routes import google_auth_router as google_auth
from app.core.exceptions import AccountInactiveError
from app.models import OAuthIdentity, RefreshToken, Account


class FakeSession:
    """Session giả dùng để mô phỏng đọc/ghi database trong test đăng nhập."""

    def __init__(self, account: Account | None = None) -> None:
        self.account = account
        self.added = []
        self.commits = 0
        self.refreshed = []

    def get(self, model, object_id):
        """Trả về tài khoản giả khi callback cần lấy Account từ account_id."""
        if model is Account and self.account and self.account.account_id == object_id:
            return self.account
        return None

    def add(self, obj):
        """Ghi nhận object được thêm vào session."""
        self.added.append(obj)

    def commit(self):
        """Ghi nhận số lần commit khi cập nhật lần đăng nhập cuối."""
        self.commits += 1

    def refresh(self, obj):
        """Ghi nhận object được refresh sau commit."""
        self.refreshed.append(obj)


class FakeRequest:
    """Request giả chỉ chứa session để callback đọc mode đăng nhập Google."""

    def __init__(self, mode: str = "existing") -> None:
        self.session = {"google_auth_mode": mode}


def make_account(*, account_id: int = 1, status: bool = True) -> Account:
    """Tạo tài khoản giả dùng trong luồng đăng nhập Google."""
    return Account(
        account_id=account_id,
        username=f"google_user_{account_id}",
        password_hash="hashed-password",
        role="SINH_VIEN",
        status=status,
    )


def make_identity(*, account_id: int = 1) -> OAuthIdentity:
    """Tạo OAuth identity giả cho tài khoản Google đã liên kết."""
    return OAuthIdentity(
        oauth_identity_id=99,
        provider=google_auth.GOOGLE_PROVIDER,
        provider_subject="google-subject",
        username="student@example.edu",
        account_id=account_id,
    )


def patch_token_creation(monkeypatch, token: str = "jwt-token") -> None:
    """Mock hàm tạo JWT để test không phụ thuộc signing thật."""
    monkeypatch.setattr(
        google_auth.settings,
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        30,
    )
    monkeypatch.setattr(
        google_auth.security,
        "create_access_token",
        lambda subject, data, expires_delta: token,
    )


def test_existing_google_login_links_profile_account_and_returns_token(
    monkeypatch,
) -> None:
    """Kiểm tra đăng nhập Google bằng email đã có hồ sơ thì trả token."""
    session = FakeSession()
    account = make_account(account_id=11, status=True)
    created_identity = make_identity(account_id=account.account_id)
    updated_identities = []

    # Giả lập email Google đã được khai báo trong hồ sơ sinh viên/cán bộ.
    monkeypatch.setattr(
        google_auth.crud,
        "get_account_by_profile_google_email",
        lambda *, session, google_email: account,
    )
    # Giả lập lần đăng nhập đầu tiên sẽ tạo liên kết OAuth identity.
    monkeypatch.setattr(
        google_auth.crud,
        "create_oauth_identity",
        lambda *, session, provider, provider_subject, email, account_id: created_identity,
    )
    monkeypatch.setattr(
        google_auth.crud,
        "update_oauth_identity_last_login",
        lambda *, session, identity: updated_identities.append(identity) or identity,
    )
    patch_token_creation(monkeypatch)

    result = google_auth.handle_existing_account_login(
        session=session,
        provider_subject="google-subject",
        email="student@example.edu",
    )

    assert result.access_token == "jwt-token"
    assert result.token_type == "bearer"
    assert account.last_login_at is not None
    assert session.commits == 1
    assert updated_identities == [created_identity]


def test_existing_google_login_rejects_unregistered_email(monkeypatch) -> None:
    """Kiểm tra đăng nhập Google bị từ chối khi email chưa có trong hệ thống."""
    session = FakeSession()

    monkeypatch.setattr(
        google_auth.crud,
        "get_account_by_profile_google_email",
        lambda *, session, google_email: None,
    )

    with pytest.raises(HTTPException) as exc_info:
        google_auth.handle_existing_account_login(
            session=session,
            provider_subject="google-subject",
            email="unknown@example.edu",
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Google email is not registered in the system"


def test_existing_google_login_with_remember_me_returns_refresh_token(
    monkeypatch,
) -> None:
    """Kiểm tra đăng nhập Google remember_me=True trả thêm refresh token."""
    session = FakeSession()
    account = make_account(account_id=14, status=True)

    monkeypatch.setattr(
        google_auth.crud,
        "get_account_by_profile_google_email",
        lambda *, session, google_email: account,
    )
    monkeypatch.setattr(
        google_auth.crud,
        "create_oauth_identity",
        lambda *, session, provider, provider_subject, email, account_id: make_identity(
            account_id=account_id
        ),
    )
    monkeypatch.setattr(
        google_auth.crud,
        "update_oauth_identity_last_login",
        lambda *, session, identity: identity,
    )
    monkeypatch.setattr(
        google_auth.crud,
        "create_refresh_token",
        lambda **kwargs: RefreshToken(
            refresh_token_id=1,
            account_id=kwargs["account_id"],
            token_hash=kwargs["token_hash"],
            expires_at=kwargs["expires_at"],
        ),
    )
    patch_token_creation(monkeypatch)

    result = google_auth.handle_existing_account_login(
        session=session,
        provider_subject="google-subject",
        email="student@example.edu",
        remember_me=True,
    )

    assert result.access_token == "jwt-token"
    assert result.refresh_token


def test_existing_google_login_rejects_inactive_account(monkeypatch) -> None:
    """Kiểm tra tài khoản inactive hoặc chờ duyệt không được nhận token."""
    session = FakeSession()
    account = make_account(account_id=12, status=False)

    monkeypatch.setattr(
        google_auth.crud,
        "get_account_by_profile_google_email",
        lambda *, session, google_email: account,
    )
    monkeypatch.setattr(
        google_auth.crud,
        "create_oauth_identity",
        lambda *, session, provider, provider_subject, email, account_id: make_identity(
            account_id=account_id
        ),
    )

    with pytest.raises(AccountInactiveError) as exc_info:
        google_auth.handle_existing_account_login(
            session=session,
            provider_subject="google-subject",
            email="student@example.edu",
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Inactive account or waiting for approval"


@pytest.mark.asyncio
async def test_google_callback_logs_in_with_existing_oauth_identity(
    monkeypatch,
) -> None:
    """Kiểm tra callback đăng nhập lại khi Google account đã được liên kết."""
    account = make_account(account_id=13, status=True)
    identity = make_identity(account_id=account.account_id)
    session = FakeSession(account=account)
    request = FakeRequest(mode="existing")
    updated_identities = []

    async def fake_authorize_access_token(request):
        """Giả lập Authlib đổi authorization code lấy Google token."""
        return {"access_token": "google-access-token"}

    async def fake_userinfo(token):
        """Giả lập Google trả về user info đã xác thực."""
        return {
            "sub": "google-subject",
            "email": "student@example.edu",
            "email_verified": True,
        }

    monkeypatch.setattr(
        google_auth.oauth.google,
        "authorize_access_token",
        fake_authorize_access_token,
    )
    monkeypatch.setattr(google_auth.oauth.google, "userinfo", fake_userinfo)
    monkeypatch.setattr(
        google_auth.crud,
        "get_oauth_identity_by_provider_subject",
        lambda *, session, provider, provider_subject: identity,
    )
    monkeypatch.setattr(
        google_auth.crud,
        "update_oauth_identity_last_login",
        lambda *, session, identity: updated_identities.append(identity) or identity,
    )
    patch_token_creation(monkeypatch, token="callback-jwt-token")

    result = await google_auth.google_callback(request=request, session=session)

    from fastapi.responses import RedirectResponse
    assert isinstance(result, RedirectResponse)
    assert "token=" in result.headers["location"]
    assert account.last_login_at is not None
    assert session.commits == 1
    assert updated_identities == [identity]
    assert "google_auth_mode" not in request.session


@pytest.mark.asyncio
async def test_google_callback_rejects_missing_linked_account(monkeypatch) -> None:
    """Kiểm tra callback báo lỗi khi OAuth identity trỏ tới tài khoản không tồn tại."""
    identity = make_identity(account_id=404)
    session = FakeSession(account=None)
    request = FakeRequest(mode="existing")

    async def fake_authorize_access_token(request):
        """Giả lập lấy token Google thành công."""
        return {"access_token": "google-access-token"}

    async def fake_userinfo(token):
        """Giả lập Google user info hợp lệ."""
        return {
            "sub": "google-subject",
            "email": "student@example.edu",
            "email_verified": True,
        }

    monkeypatch.setattr(
        google_auth.oauth.google,
        "authorize_access_token",
        fake_authorize_access_token,
    )
    monkeypatch.setattr(google_auth.oauth.google, "userinfo", fake_userinfo)
    monkeypatch.setattr(
        google_auth.crud,
        "get_oauth_identity_by_provider_subject",
        lambda *, session, provider, provider_subject: identity,
    )

    from fastapi.responses import RedirectResponse
    result = await google_auth.google_callback(request=request, session=session)
    assert isinstance(result, RedirectResponse)
    location = result.headers["location"]
    assert "error=" in location
    assert "Account" in location



