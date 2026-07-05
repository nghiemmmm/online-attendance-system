import pytest

import app.core.redis as redis_module
from app.api.deps import login_rate_limiter
from app.core.config import settings
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def db():
    """Override conftest.py global db fixture to avoid Render PG execution."""
    yield None


def test_login_rate_limiting(client):
    # Remove the conftest bypass so the real rate limiter runs
    app.dependency_overrides.pop(login_rate_limiter, None)
    login_rate_limiter.history.clear()

    # Force in-memory path: mock Redis is unreliable in tests (always returns count=1)
    original_redis = redis_module.redis_client
    redis_module.redis_client = None

    try:
        # 5 attempts should not return HTTP 429 (they return 400 due to incorrect credentials)
        for _ in range(5):
            response = client.post(
                f"{settings.API_V1_STR}/auth/tokens",
                json={
                    "username": "dummy_user_rate_limit_test",
                    "password": "wrong_password",
                },
            )
            assert response.status_code == 400

        # The 6th attempt should be rate limited with HTTP 429
        response = client.post(
            f"{settings.API_V1_STR}/auth/tokens",
            json={
                "username": "dummy_user_rate_limit_test",
                "password": "wrong_password",
            },
        )
        assert response.status_code == 429
        assert "Too many requests" in response.json()["detail"]
    finally:
        # Restore everything so other tests are not affected
        redis_module.redis_client = original_redis
        app.dependency_overrides[login_rate_limiter] = lambda: None
        login_rate_limiter.history.clear()
