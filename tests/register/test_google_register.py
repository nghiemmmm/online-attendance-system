import pytest
from fastapi import HTTPException

from app.api.routes import google_auth_router as google_auth
from app.models import GoogleAuthPending, OAuthIdentity, TaiKhoan


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


def make_account(*, ma_tai_khoan: int = 1, trang_thai: bool = True) -> TaiKhoan:
    """Tạo tài khoản giả để dùng trong các nhánh đăng ký Google."""
    return TaiKhoan(
        ma_tai_khoan=ma_tai_khoan,
        ten_dang_nhap=f"google_user_{ma_tai_khoan}",
        mat_khau_hash="hashed-password",
        vai_tro="SINH_VIEN",
        trang_thai=trang_thai,
    )


def make_identity(*, ma_tai_khoan: int = 1) -> OAuthIdentity:
    """Tạo bản ghi OAuth giả liên kết Google với tài khoản nội bộ."""
    return OAuthIdentity(
        ma_oauth_identity=10,
        provider=google_auth.GOOGLE_PROVIDER,
        provider_subject="google-subject",
        email="student@example.edu",
        ma_tai_khoan=ma_tai_khoan,
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
        return make_account(ma_tai_khoan=42, trang_thai=account_create.trang_thai)

    def fake_create_oauth_identity(
        *, session, provider, provider_subject, email, ma_tai_khoan
    ):
        """Ghi lại dữ liệu liên kết OAuth để kiểm tra provider và email."""
        created["identity"] = {
            "provider": provider,
            "provider_subject": provider_subject,
            "email": email,
            "ma_tai_khoan": ma_tai_khoan,
        }
        return make_identity(ma_tai_khoan=ma_tai_khoan)

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
    assert result.ma_tai_khoan == 42
    assert created["account_create"].vai_tro == "SINH_VIEN"
    assert created["account_create"].trang_thai is False
    assert created["account_create"].ten_dang_nhap.startswith("google_")
    assert created["identity"] == {
        "provider": "google",
        "provider_subject": "google-subject",
        "email": "new-student@example.edu",
        "ma_tai_khoan": 42,
    }


def test_auto_register_links_existing_profile_account_and_returns_token(
    monkeypatch,
) -> None:
    """Kiểm tra Google email đã có hồ sơ thì liên kết OAuth và trả token."""
    session = FakeSession()
    account = make_account(ma_tai_khoan=7, trang_thai=True)
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
        lambda *, session, provider, provider_subject, email, ma_tai_khoan: make_identity(
            ma_tai_khoan=ma_tai_khoan
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
    assert account.lan_dang_nhap_cuoi is not None
    assert session.commits == 1
    assert len(updated_identities) == 1


def test_auto_register_blocks_existing_inactive_profile_account(monkeypatch) -> None:
    """Kiểm tra tài khoản đã có nhưng đang inactive thì không được đăng nhập."""
    session = FakeSession()
    account = make_account(ma_tai_khoan=8, trang_thai=False)

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
        lambda *, session, provider, provider_subject, email, ma_tai_khoan: make_identity(
            ma_tai_khoan=ma_tai_khoan
        ),
    )

    with pytest.raises(HTTPException) as exc_info:
        google_auth.handle_auto_register_login(
            session=session,
            provider_subject="google-subject",
            email="student@example.edu",
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Inactive account or waiting for approval"
