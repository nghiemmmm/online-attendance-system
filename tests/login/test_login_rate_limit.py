import pytest
from app.api.deps import login_rate_limiter
from app.core.config import settings

@pytest.fixture(scope="session", autouse=True)
def db():
    """Override conftest.py global db fixture to avoid Render PG execution."""
    yield None

def test_login_rate_limiting(client):
    login_rate_limiter.history.clear()
    
    # 5 attempts should not return HTTP 429 (they should return 400 Bad Request due to incorrect username/password)
    for _ in range(5):
        response = client.post(
            f"{settings.API_V1_STR}/login/json",
            json={"username": "dummy_user_rate_limit_test", "password": "wrong_password"},
        )
        assert response.status_code == 400
        
    # The 6th attempt should be rate limited with HTTP 429
    response = client.post(
        f"{settings.API_V1_STR}/login/json",
        json={"username": "dummy_user_rate_limit_test", "password": "wrong_password"},
    )
    assert response.status_code == 429
    assert response.json()["detail"] == "Too many login attempts. Please try again later."
    
    # Clean up after test
    login_rate_limiter.history.clear()
