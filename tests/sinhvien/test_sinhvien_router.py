from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.api.deps import get_current_active_superuser, get_db
from app.main import app
from app.models import Nganh, SinhVien, TaiKhoan


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
            TaiKhoan.__table__,
            Nganh.__table__,
            SinhVien.__table__,
        ],
    )

    with Session(engine) as session:
        superuser = TaiKhoan(
            ma_tai_khoan=1,
            ten_dang_nhap="admin",
            mat_khau_hash="hashed-password",
            vai_tro="ADMIN",
            trang_thai=True,
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


def test_sinh_vien_crud_flow() -> None:
    """Test create, search, read, update and delete APIs for student profiles."""
    for client, session in make_test_client():
        nganh = Nganh(ten_nganh="Cong nghe thong tin")
        session.add(nganh)
        session.commit()
        session.refresh(nganh)

        create_response = client.post(
            "/sinh-vien/",
            json={
                "ho": "Nguyen",
                "ten": "An",
                "google_email": "an@student.edu",
                "dien_thoai": "0900000001",
                "ma_nganh": nganh.ma_nganh,
            },
        )
        created = create_response.json()

        list_response = client.get("/sinh-vien/", params={"q": "An"})
        detail_response = client.get(f"/sinh-vien/{created['ma_sinh_vien']}")
        update_response = client.patch(
            f"/sinh-vien/{created['ma_sinh_vien']}",
            json={"dien_thoai": "0911111111", "trang_thai_hoc": False},
        )
        delete_response = client.delete(f"/sinh-vien/{created['ma_sinh_vien']}")
        after_delete_response = client.get(f"/sinh-vien/{created['ma_sinh_vien']}")

        assert create_response.status_code == 201
        assert created["ho"] == "Nguyen"
        assert created["ten"] == "An"
        assert created["ma_nganh"] == nganh.ma_nganh
        assert list_response.status_code == 200
        assert list_response.json()["count"] == 1
        assert detail_response.status_code == 200
        assert update_response.status_code == 200
        assert update_response.json()["dien_thoai"] == "0911111111"
        assert update_response.json()["trang_thai_hoc"] is False
        assert delete_response.status_code == 200
        assert after_delete_response.status_code == 404


def test_create_sinh_vien_rejects_duplicate_google_email() -> None:
    """Test create API rejects duplicate student Google email."""
    for client, session in make_test_client():
        nganh = Nganh(ten_nganh="He thong thong tin")
        session.add(nganh)
        session.commit()
        session.refresh(nganh)

        payload = {
            "ho": "Tran",
            "ten": "Binh",
            "google_email": "binh@student.edu",
            "ma_nganh": nganh.ma_nganh,
        }

        first_response = client.post("/sinh-vien/", json=payload)
        second_response = client.post(
            "/sinh-vien/",
            json={**payload, "ten": "Binh 2"},
        )

        assert first_response.status_code == 201
        assert second_response.status_code == 409
        assert second_response.json()["detail"] == "Google email already exists"


def test_create_sinh_vien_rejects_missing_nganh() -> None:
    """Test create API rejects student payload with missing major."""
    for client, _session in make_test_client():
        response = client.post(
            "/sinh-vien/",
            json={
                "ho": "Le",
                "ten": "Chi",
                "google_email": "chi@student.edu",
                "ma_nganh": 999,
            },
        )

        assert response.status_code == 404
        assert response.json()["errors"][0]["developer_message"] == "Not found"
