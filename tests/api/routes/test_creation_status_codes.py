import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.api.deps import get_current_active_superuser, get_db
from app.main import app
from app.models import Account, Student, Staff, Major
from app.core.config import settings

@pytest.fixture(scope="session", autouse=True)
def db():
    """Override conftest.py global db fixture to avoid Render PG execution."""
    yield None

def make_test_client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(
        engine,
        tables=[
            Account.__table__,
            Student.__table__,
            Staff.__table__,
            Major.__table__,
        ],
    )
    with Session(engine) as session:
        superuser = Account(
            account_id=1,
            username="admin",
            password_hash="hashed-password",
            role="ADMIN",
            status=True,
        )

        def override_get_db():
            yield session

        def override_superuser():
            return superuser

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_superuser] = override_superuser
        with TestClient(app) as client:
            yield client, session
        app.dependency_overrides.clear()

def test_create_user_returns_201() -> None:
    for client, session in make_test_client():
        username = "new_user_201@example.com"
        password = "testpassword123"
        data = {"username": username, "password": password}
        response = client.post(
            f"{settings.API_V1_STR}/users/",
            json=data,
        )
        assert response.status_code == 201
        created_user = response.json()
        assert created_user["username"] == username
