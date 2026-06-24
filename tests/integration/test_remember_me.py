from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.api.deps import get_db
from app.core.security import get_password_hash
from app.main import app
from app.models import RefreshToken, TaiKhoan


def make_test_client() -> Generator[tuple[TestClient, Session], None, None]:
    """Tạo TestClient dùng SQLite in-memory cho integration test Remember Me."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(
        engine,
        tables=[TaiKhoan.__table__, RefreshToken.__table__],
    )

    with Session(engine) as session:
        account = TaiKhoan(
            ten_dang_nhap="remember_user",
            mat_khau_hash=get_password_hash("secret123"),
            vai_tro="SINH_VIEN",
            trang_thai=True,
        )
        session.add(account)
        session.commit()

        def override_get_db():
            """Cung cấp session test thay cho database thật."""
            yield session

        app.dependency_overrides[get_db] = override_get_db
        with TestClient(app) as client:
            yield client, session
        app.dependency_overrides.clear()


def test_login_json_without_remember_me_returns_only_access_token() -> None:
    """Kiểm tra login JSON không remember chỉ trả access token."""
    for client, session in make_test_client():
        response = client.post(
            "/login/json",
            json={
                "username": "remember_user",
                "password": "secret123",
                "remember_me": False,
            },
        )

        body = response.json()
        tokens = session.exec(select(RefreshToken)).all()

        assert response.status_code == 200
        assert response.headers["X-Request-ID"]
        assert body["access_token"]
        assert body["refresh_token"] is None
        assert tokens == []


def test_login_refresh_and_logout_flow_with_remember_me() -> None:
    """Kiểm tra đủ luồng login remember, refresh token và logout một phiên."""
    for client, session in make_test_client():
        login_response = client.post(
            "/login/json",
            json={
                "username": "remember_user",
                "password": "secret123",
                "remember_me": True,
            },
        )
        login_body = login_response.json()
        refresh_token = login_body["refresh_token"]

        refresh_response = client.post(
            "/login/refresh",
            json={"refresh_token": refresh_token},
        )
        logout_response = client.post(
            "/login/logout",
            json={"refresh_token": refresh_token},
        )
        refresh_after_logout_response = client.post(
            "/login/refresh",
            json={"refresh_token": refresh_token},
        )
        db_token = session.exec(select(RefreshToken)).first()

        assert login_response.status_code == 200
        assert login_response.headers["X-Request-ID"]
        assert login_body["access_token"]
        assert refresh_token
        assert db_token is not None
        assert db_token.token_hash != refresh_token
        assert refresh_response.status_code == 200
        assert refresh_response.json()["access_token"]
        assert logout_response.status_code == 200
        assert refresh_after_logout_response.status_code == 401


def test_logout_all_revokes_every_refresh_token() -> None:
    """Kiểm tra logout-all thu hồi mọi refresh token của tài khoản đang đăng nhập."""
    for client, session in make_test_client():
        first_login = client.post(
            "/login/json",
            json={
                "username": "remember_user",
                "password": "secret123",
                "remember_me": True,
            },
        ).json()
        second_login = client.post(
            "/login/json",
            json={
                "username": "remember_user",
                "password": "secret123",
                "remember_me": True,
            },
        ).json()

        logout_all_response = client.post(
            "/login/logout-all",
            headers={"Authorization": f"Bearer {first_login['access_token']}"},
        )
        first_refresh = client.post(
            "/login/refresh",
            json={"refresh_token": first_login["refresh_token"]},
        )
        second_refresh = client.post(
            "/login/refresh",
            json={"refresh_token": second_login["refresh_token"]},
        )
        tokens = session.exec(select(RefreshToken)).all()

        assert logout_all_response.status_code == 200
        assert logout_all_response.headers["X-Request-ID"]
        assert first_refresh.status_code == 401
        assert second_refresh.status_code == 401
        assert all(token.revoked_at is not None for token in tokens)
