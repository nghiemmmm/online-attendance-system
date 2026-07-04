import pytest
from fastapi import HTTPException

from app.api.routes import google_auth_router as google_auth
from app.core.exceptions import AccountInactiveError
from app.models import GoogleAuthPending, OAuthIdentity, Account


class FakeSession:
    """Session giả dùng để ghi nhận các thao tác database trong test."""

    def __init__(self) -> None:
        self.added = []
        self.commits = 0
        self.refreshed = []

    def add(self, obj):
        """Ghi nhận object được thêm vào session."""
        self.added.append(obj)

    def commit(self):
        """Ghi nhận số lần commit database."""
        self.commits += 1

    def refresh(self, obj):
        """Ghi nhận object được refresh sau khi commit."""
        self.refreshed.append(obj)


def make_account(*, account_id: int = 1, status: bool = True) -> Account:
    """Tạo tài khoản giả để dùng trong các nhánh đăng ký Google."""
    return Account(
        account_id=account_id,
        username=f"google_user_{account_id}",
        password_hash="hashed-password",
        role="SINH_VIEN",
        status=status,
    )


def make_identity(*, account_id: int = 1) -> OAuthIdentity:
    """Tạo bản ghi OAuth giả liên kết Google với tài khoản nội bộ."""
    return OAuthIdentity(
        oauth_identity_id=10,
        provider=google_auth.GOOGLE_PROVIDER,
        provider_subject="google-subject",
        username="student@example.edu",
        account_id=account_id,
    )


def test_validate_google_user_info_accepts_verified_email() -> None:
    """Kiểm tra Google user info hợp lệ được chấp nhận."""
    provider_subject, email = google_auth.validate_google_user_info(
        {
            "sub": "google-subject",
            "email": "student@example.edu",
            "email_verified": True,
        }
    )

    assert provider_subject == "google-subject"
    assert email == "student@example.edu"


def test_validate_google_user_info_rejects_unverified_email() -> None:
    """Kiểm tra hệ thống từ chối email Google chưa xác thực."""
    with pytest.raises(HTTPException) as exc_info:
        google_auth.validate_google_user_info(
            {
                "sub": "google-subject",
                "email": "student@example.edu",
                "email_verified": False,
            }
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Google email is not verified"


def test_validate_allowed_email_domain_rejects_wrong_domain(monkeypatch) -> None:
    """Kiểm tra chỉ cho phép đăng ký Google bằng domain email được cấu hình."""
    monkeypatch.setattr(
        google_auth.settings,
        "GOOGLE_ALLOWED_EMAIL_DOMAIN",
        "@school.edu",
    )

    google_auth.validate_allowed_email_domain("student@school.edu")

    with pytest.raises(HTTPException) as exc_info:
        google_auth.validate_allowed_email_domain("student@gmail.com")

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Email domain is not allowed"


def test_auto_register_creates_pending_account_and_google_identity(monkeypatch) -> None:
    """Kiểm tra đăng ký Google mới tạo tài khoản chờ duyệt và OAuth identity."""
    session = FakeSession()
    created = {}

    # Không giới hạn domain để test tập trung vào nhánh tạo tài khoản mới.
    monkeypatch.setattr(
        google_auth.settings,
        "GOOGLE_ALLOWED_EMAIL_DOMAIN",
        "",
    )
    # Giả lập email Google chưa khớp với hồ sơ sinh viên/cán bộ nào.
    monkeypatch.setattr(
        google_auth.crud,
        "get_account_by_profile_google_email",
        lambda *, session, google_email: None,
    )

    def fake_create_account(*, session, account_create):
        """Ghi lại dữ liệu tạo tài khoản để assert sau khi gọi use case."""
        created["account_create"] = account_create
        return make_account(account_id=42, status=account_create.status)

    def fake_create_oauth_identity(
        *, session, provider, provider_subject, email, account_id
    ):
        """Ghi lại dữ liệu liên kết OAuth để kiểm tra provider và email."""
        created["identity"] = {
            "provider": provider,
            "provider_subject": provider_subject,
            "username": email,
            "account_id": account_id,
        }
        return make_identity(account_id=account_id)

    monkeypatch.setattr(google_auth.crud, "create_account", fake_create_account)
    monkeypatch.setattr(
        google_auth.crud,
        "create_oauth_identity",
        fake_create_oauth_identity,
    )

    result = google_auth.handle_auto_register_login(
        session=session,
        provider_subject="google-subject",
        email="new-student@example.edu",
    )

    assert isinstance(result, GoogleAuthPending)
    assert result.status == "pending_approval"
    assert result.account_id == 42
    assert created["account_create"].role == "SINH_VIEN"
    assert created["account_create"].status is False
    assert created["account_create"].username.startswith("google_")
    assert created["identity"] == {
        "provider": "google",
        "provider_subject": "google-subject",
        "username": "new-student@example.edu",
        "account_id": 42,
    }


def test_auto_register_links_existing_profile_account_and_returns_token(
    monkeypatch,
) -> None:
    """Kiểm tra Google email đã có hồ sơ thì liên kết OAuth và trả token."""
    session = FakeSession()
    account = make_account(account_id=7, status=True)
    updated_identities = []

    monkeypatch.setattr(
        google_auth.settings,
        "GOOGLE_ALLOWED_EMAIL_DOMAIN",
        "",
    )
    monkeypatch.setattr(
        google_auth.settings,
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        30,
    )
    # Giả lập Google email đã tồn tại trong profile và có tài khoản active.
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
    # Ghi nhận việc cập nhật thời điểm đăng nhập cuối của OAuth identity.
    monkeypatch.setattr(
        google_auth.crud,
        "update_oauth_identity_last_login",
        lambda *, session, identity: updated_identities.append(identity) or identity,
    )
    monkeypatch.setattr(
        google_auth.security,
        "create_access_token",
        lambda subject, data, expires_delta: "jwt-token",
    )

    result = google_auth.handle_auto_register_login(
        session=session,
        provider_subject="google-subject",
        email="student@example.edu",
    )

    assert result.access_token == "jwt-token"
    assert result.token_type == "bearer"
    assert account.last_login_at is not None
    assert session.commits == 1
    assert len(updated_identities) == 1


def test_auto_register_blocks_existing_inactive_profile_account(monkeypatch) -> None:
    """Kiểm tra tài khoản đã có nhưng đang inactive thì không được đăng nhập."""
    session = FakeSession()
    account = make_account(account_id=8, status=False)

    monkeypatch.setattr(
        google_auth.settings,
        "GOOGLE_ALLOWED_EMAIL_DOMAIN",
        "",
    )
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
        google_auth.handle_auto_register_login(
            session=session,
            provider_subject="google-subject",
            email="student@example.edu",
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Inactive account or waiting for approval"
