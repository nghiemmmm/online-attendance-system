import os
from unittest.mock import AsyncMock, MagicMock

os.environ["DATABASE_URL"] = "sqlite:///test.db"

# Mock Redis globally to isolate tests from local Redis daemon dependency
mock_redis = MagicMock()
mock_redis.ping = AsyncMock(return_value=True)
mock_redis.aclose = AsyncMock()
mock_redis.pipeline = MagicMock(return_value=mock_redis)
mock_redis.zremrangebyscore = AsyncMock()
mock_redis.zadd = AsyncMock()
mock_redis.zcard = AsyncMock()
mock_redis.expire = AsyncMock()
mock_redis.execute = AsyncMock(return_value=(0, 0, 1, 0))

mock_redis_asyncio = MagicMock()
mock_redis_asyncio.from_url = MagicMock(return_value=mock_redis)

import app.core.redis
app.core.redis.aioredis = mock_redis_asyncio

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel

from app.core.config import settings
from app.core.db import engine, init_db
import app.models  # Ensure all models are loaded and registered
from app.models import Account
from app.main import app
from app.api.deps import login_rate_limiter
app.dependency_overrides[login_rate_limiter] = lambda: None


@pytest.fixture(autouse=True)
def bypass_rate_limiter():
    app.dependency_overrides[login_rate_limiter] = lambda: None

from tests.utils.user import authentication_token_from_email
from tests.utils.utils import get_superuser_token_headers


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    # Enable foreign keys for SQLite
    from sqlalchemy import event
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Set up SQLite test database tables
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        init_db(session)
        yield session
        # Clean up database after the session
        SQLModel.metadata.drop_all(engine)
    
    # Remove test database file
    if os.path.exists("test.db"):
        try:
            os.remove("test.db")
        except OSError:
            pass


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )
