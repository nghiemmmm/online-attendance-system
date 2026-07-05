from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.api.deps import get_current_active_superuser, get_db
from app.main import app
from app.models import Account, Major, Student


def make_test_client() -> Generator[tuple[TestClient, Session], None, None]:
    """Create a test client backed by an in-memory SQLite database."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(
        engine,
        tables=[
            Account.__table__,
            Major.__table__,
            Student.__table__,
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
            """Yield the test database session."""
            yield session

        def override_superuser():
            """Bypass authentication for router tests."""
            return superuser

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_superuser] = override_superuser
        with TestClient(app) as client:
            yield client, session
        app.dependency_overrides.clear()


def test_student_crud_flow() -> None:
    """Test create, search, read, update and delete APIs for student profiles."""
    for client, session in make_test_client():
        major = Major(major_name="Cong nghe thong tin")
        session.add(major)
        session.commit()
        session.refresh(major)

        create_response = client.post(
            "/api/students/",
            json={
                "last_name": "Nguyen",
                "first_name": "An",
                "google_email": "an@student.edu",
                "phone": "0900000001",
                "major_id": major.major_id,
            },
        )
        created = create_response.json()

        list_response = client.get("/api/students/", params={"q": "An"})
        detail_response = client.get(f"/api/students/{created['student_id']}")
        update_response = client.patch(
            f"/api/students/{created['student_id']}",
            json={"phone": "0911111111", "academic_status": False},
        )
        delete_response = client.delete(f"/api/students/{created['student_id']}")
        after_delete_response = client.get(f"/api/students/{created['student_id']}")

        assert create_response.status_code == 201
        assert created["last_name"] == "Nguyen"
        assert created["first_name"] == "An"
        assert created["major_id"] == major.major_id
        assert list_response.status_code == 200
        assert list_response.json()["count"] == 1
        assert detail_response.status_code == 200
        assert update_response.status_code == 200
        assert update_response.json()["phone"] == "0911111111"
        assert update_response.json()["academic_status"] is False
        assert delete_response.status_code == 200
        assert after_delete_response.status_code == 404


def test_create_student_rejects_duplicate_google_email() -> None:
    """Test create API rejects duplicate student Google email."""
    for client, session in make_test_client():
        major = Major(major_name="He thong thong tin")
        session.add(major)
        session.commit()
        session.refresh(major)

        payload = {
            "last_name": "Tran",
            "first_name": "Binh",
            "google_email": "binh@student.edu",
            "major_id": major.major_id,
        }

        first_response = client.post("/api/students/", json=payload)
        second_response = client.post(
            "/api/students/",
            json={**payload, "first_name": "Binh 2"},
        )

        assert first_response.status_code == 201
        assert second_response.status_code == 409
        assert second_response.json()["message"] == "Google email already exists"


def test_create_student_rejects_missing_major() -> None:
    """Test create API rejects student payload with missing major."""
    for client, _session in make_test_client():
        response = client.post(
            "/api/students/",
            json={
                "last_name": "Le",
                "first_name": "Chi",
                "google_email": "chi@student.edu",
                "major_id": 999,
            },
        )

        assert response.status_code == 404
        assert response.json()["message"] == "Major not found"
