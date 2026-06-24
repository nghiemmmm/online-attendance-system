from collections.abc import Generator
from datetime import date, time

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.api.deps import get_current_active_superuser, get_db
from app.main import app
from app.models import (
    BuoiHoc,
    CanBo,
    DangKyHocPhan,
    HocPhan,
    LopHocPhan,
    Nganh,
    SinhVien,
    TaiKhoan,
)


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
            CanBo.__table__,
            Nganh.__table__,
            SinhVien.__table__,
            HocPhan.__table__,
            LopHocPhan.__table__,
            DangKyHocPhan.__table__,
            BuoiHoc.__table__,
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


def test_read_lich_hoc_hom_nay_returns_student_lessons() -> None:
    """Test today schedule API returns only active registered lessons."""
    for client, session in make_test_client():
        can_bo = CanBo(ho="Nguyen", ten="Giang", google_ten_dang_nhap="gv@example.edu")
        nganh = Nganh(ten_nganh="Cong nghe thong tin")
        hoc_phan_1 = HocPhan(
            ma_hoc_phan=801,
            ten_hoc_phan="Co so du lieu",
            so_tin_chi=3,
        )
        hoc_phan_2 = HocPhan(
            ma_hoc_phan=802,
            ten_hoc_phan="Mang may tinh",
            so_tin_chi=3,
        )
        session.add_all([can_bo, nganh, hoc_phan_1, hoc_phan_2])
        session.commit()
        session.refresh(can_bo)
        session.refresh(nganh)

        sinh_vien = SinhVien(
            ho="Le",
            ten="An",
            ma_nganh=nganh.ma_nganh,
            google_ten_dang_nhap="an@student.edu",
        )
        session.add(sinh_vien)
        session.commit()
        session.refresh(sinh_vien)

        active_lop = LopHocPhan(
            ma_hoc_phan=hoc_phan_1.ma_hoc_phan,
            ma_can_bo=can_bo.ma_can_bo,
            hoc_ky=1,
            nam_hoc="2025-2026",
            trang_thai=True,
        )
        inactive_registration_lop = LopHocPhan(
            ma_hoc_phan=hoc_phan_2.ma_hoc_phan,
            ma_can_bo=can_bo.ma_can_bo,
            hoc_ky=1,
            nam_hoc="2025-2026",
            trang_thai=True,
        )
        unregistered_lop = LopHocPhan(
            ma_hoc_phan=hoc_phan_2.ma_hoc_phan,
            ma_can_bo=can_bo.ma_can_bo,
            hoc_ky=1,
            nam_hoc="2025-2026",
            trang_thai=True,
        )
        session.add_all([active_lop, inactive_registration_lop, unregistered_lop])
        session.commit()
        session.refresh(active_lop)
        session.refresh(inactive_registration_lop)
        session.refresh(unregistered_lop)

        session.add_all(
            [
                DangKyHocPhan(
                    ma_sinh_vien=sinh_vien.ma_sinh_vien,
                    ma_lop_hoc_phan=active_lop.ma_lop_hoc_phan,
                    trang_thai=True,
                ),
                DangKyHocPhan(
                    ma_sinh_vien=sinh_vien.ma_sinh_vien,
                    ma_lop_hoc_phan=inactive_registration_lop.ma_lop_hoc_phan,
                    trang_thai=False,
                ),
            ]
        )
        session.add_all(
            [
                BuoiHoc(
                    ma_lop_hoc_phan=active_lop.ma_lop_hoc_phan,
                    ngay_hoc=date(2025, 10, 20),
                    gio_bat_dau=time(7, 0),
                    gio_ket_thuc=time(9, 30),
                ),
                BuoiHoc(
                    ma_lop_hoc_phan=inactive_registration_lop.ma_lop_hoc_phan,
                    ngay_hoc=date(2025, 10, 20),
                    gio_bat_dau=time(9, 40),
                    gio_ket_thuc=time(11, 10),
                ),
                BuoiHoc(
                    ma_lop_hoc_phan=unregistered_lop.ma_lop_hoc_phan,
                    ngay_hoc=date(2025, 10, 20),
                    gio_bat_dau=time(13, 0),
                    gio_ket_thuc=time(15, 0),
                ),
                BuoiHoc(
                    ma_lop_hoc_phan=active_lop.ma_lop_hoc_phan,
                    ngay_hoc=date(2025, 10, 21),
                    gio_bat_dau=time(7, 0),
                    gio_ket_thuc=time(9, 30),
                ),
            ]
        )
        session.commit()

        response = client.get(
            f"/lich-hoc/sinh-vien/{sinh_vien.ma_sinh_vien}/hom-nay",
            params={"target_date": "2025-10-20"},
        )
        body = response.json()

        assert response.status_code == 200
        assert body["ma_sinh_vien"] == sinh_vien.ma_sinh_vien
        assert body["ngay_hoc"] == "2025-10-20"
        assert body["count"] == 1
        assert body["data"][0]["ma_lop_hoc_phan"] == active_lop.ma_lop_hoc_phan
        assert body["data"][0]["ten_hoc_phan"] == "Co so du lieu"
        assert body["data"][0]["phong_hoc"] is None
        assert body["data"][0]["gio_bat_dau"] == "07:00:00"
        assert body["data"][0]["gio_ket_thuc"] == "09:30:00"


def test_read_lich_hoc_hom_nay_returns_empty_when_no_lessons() -> None:
    """Test today schedule API returns an empty list when the student has no lessons."""
    for client, session in make_test_client():
        nganh = Nganh(ten_nganh="He thong thong tin")
        session.add(nganh)
        session.commit()
        session.refresh(nganh)
        sinh_vien = SinhVien(ho="Tran", ten="Binh", ma_nganh=nganh.ma_nganh)
        session.add(sinh_vien)
        session.commit()
        session.refresh(sinh_vien)

        response = client.get(
            f"/lich-hoc/sinh-vien/{sinh_vien.ma_sinh_vien}/hom-nay",
            params={"target_date": "2025-10-20"},
        )
        body = response.json()

        assert response.status_code == 200
        assert body["data"] == []
        assert body["count"] == 0


def test_read_lich_hoc_hom_nay_rejects_missing_student() -> None:
    """Test today schedule API returns 404 when student profile is missing."""
    for client, _session in make_test_client():
        response = client.get(
            "/lich-hoc/sinh-vien/999/hom-nay",
            params={"target_date": "2025-10-20"},
        )

        assert response.status_code == 404
        assert response.json()["errors"][0]["developer_message"] == "Not found"
