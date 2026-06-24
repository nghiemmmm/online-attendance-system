from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from app.models import RefreshToken, TaiKhoan
from app.services import auth_token_service


class FakeSession:
    """Session giả phục vụ unit test service token mà không cần database thật."""

    def __init__(self, account: TaiKhoan | None = None) -> None:
        self.account = account
        self.added = []
        self.commits = 0
        self.refreshed = []

    def get(self, model, object_id):
        """Trả về tài khoản giả khi service cần kiểm tra chủ refresh token."""
        if model is TaiKhoan and self.account and self.account.ma_tai_khoan == object_id:
            return self.account
        return None

    def add(self, obj):
        """Ghi nhận object được add vào session."""
        self.added.append(obj)

    def commit(self):
        """Ghi nhận số lần commit."""
        self.commits += 1

    def refresh(self, obj):
        """Ghi nhận object được refresh."""
        self.refreshed.append(obj)


def make_account(*, ma_tai_khoan: int = 1, trang_thai: bool = True) -> TaiKhoan:
    """Tạo tài khoản giả cho các test Remember Me."""
    return TaiKhoan(
        ma_tai_khoan=ma_tai_khoan,
        ten_dang_nhap=f"user_{ma_tai_khoan}",
        mat_khau_hash="hashed-password",
        vai_tro="SINH_VIEN",
        trang_thai=trang_thai,
    )


def make_refresh_token(*, raw_token: str, account_id: int = 1) -> RefreshToken:
    """Tạo refresh token còn hạn với hash tương ứng token raw."""
    return RefreshToken(
        ma_refresh_token=1,
        ma_tai_khoan=account_id,
        token_hash=auth_token_service.hash_refresh_token(raw_token),
        expires_at=datetime.now(timezone.utc) + timedelta(days=1),
    )


def test_hash_refresh_token_does_not_return_raw_token() -> None:
    """Kiểm tra refresh token được hash và không lưu nguyên bản token."""
    raw_token = "raw-refresh-token"

    token_hash = auth_token_service.hash_refresh_token(raw_token)

    assert token_hash != raw_token
    assert token_hash == auth_token_service.hash_refresh_token(raw_token)


def test_issue_login_tokens_without_remember_me_does_not_create_refresh_token(
    monkeypatch,
) -> None:
    """Kiểm tra đăng nhập thường không tạo refresh token khi remember_me=False."""
    session = FakeSession()
    account = make_account()

    monkeypatch.setattr(
        auth_token_service.security,
        "create_access_token",
        lambda subject, data, expires_delta: "access-token",
    )
    monkeypatch.setattr(
        auth_token_service.crud,
        "create_refresh_token",
        lambda **kwargs: pytest.fail("Không được tạo refresh token"),
    )

    result = auth_token_service.issue_login_tokens(
        session=session,
        account=account,
        remember_me=False,
    )

    assert result.access_token == "access-token"
    assert result.refresh_token is None
    assert session.commits == 1


def test_issue_login_tokens_with_remember_me_creates_refresh_token(monkeypatch) -> None:
    """Kiểm tra remember_me=True tạo refresh token và chỉ lưu hash vào CRUD."""
    session = FakeSession()
    account = make_account(ma_tai_khoan=2)
    created = {}

    monkeypatch.setattr(
        auth_token_service.security,
        "create_access_token",
        lambda subject, data, expires_delta: "access-token",
    )

    def fake_create_refresh_token(**kwargs):
        """Ghi nhận dữ liệu refresh token được lưu xuống database."""
        created.update(kwargs)
        return RefreshToken(
            ma_refresh_token=1,
            ma_tai_khoan=kwargs["ma_tai_khoan"],
            token_hash=kwargs["token_hash"],
            expires_at=kwargs["expires_at"],
        )

    monkeypatch.setattr(
        auth_token_service.crud,
        "create_refresh_token",
        fake_create_refresh_token,
    )

    result = auth_token_service.issue_login_tokens(
        session=session,
        account=account,
        remember_me=True,
        user_agent="pytest",
        ip_address="127.0.0.1",
    )

    assert result.access_token == "access-token"
    assert result.refresh_token
    assert created["ma_tai_khoan"] == 2
    assert created["token_hash"] != result.refresh_token
    assert created["token_hash"] == auth_token_service.hash_refresh_token(
        result.refresh_token
    )
    assert created["user_agent"] == "pytest"
    assert created["ip_address"] == "127.0.0.1"


def test_refresh_access_token_rejects_revoked_token(monkeypatch) -> None:
    """Kiểm tra refresh token đã revoke không được cấp access token mới."""
    raw_token = "refresh-token"
    db_token = make_refresh_token(raw_token=raw_token)
    db_token.revoked_at = datetime.now(timezone.utc)
    session = FakeSession(account=make_account())

    monkeypatch.setattr(
        auth_token_service.crud,
        "get_refresh_token_by_hash",
        lambda *, session, token_hash: db_token,
    )

    with pytest.raises(HTTPException) as exc_info:
        auth_token_service.refresh_access_token(
            session=session,
            raw_refresh_token=raw_token,
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Refresh token has been revoked"


def test_logout_all_refresh_tokens_calls_crud(monkeypatch) -> None:
    """Kiểm tra logout-all thu hồi toàn bộ refresh token của tài khoản."""
    session = FakeSession()
    account = make_account(ma_tai_khoan=3)
    called = {}

    monkeypatch.setattr(
        auth_token_service.crud,
        "revoke_all_refresh_tokens_for_account",
        lambda *, session, ma_tai_khoan: called.setdefault(
            "ma_tai_khoan", ma_tai_khoan
        )
        or 2,
    )

    result = auth_token_service.logout_all_refresh_tokens(
        session=session,
        account=account,
    )

    assert result == 3
    assert called["ma_tai_khoan"] == 3
