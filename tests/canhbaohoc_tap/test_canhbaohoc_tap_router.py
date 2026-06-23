from collections.abc import Generator
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.api.deps import get_current_active_superuser, get_db
from app.main import app
from app.models import (
    BuoiHoc,
    CanBo,
    DangKyHocPhan,
    DiemDanh,
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
            DiemDanh.__table__,
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


def seed_warning_data(session: Session):
    """Seed student, classes, lessons and attendance records for warning tests."""
    can_bo = CanBo(ho="Nguyen", ten="Giang", google_ten_dang_nhap="gv@example.edu")
    nganh = Nganh(ten_nganh="Cong nghe thong tin")
    hoc_phan_1 = HocPhan(ma_hoc_phan=901, ten_hoc_phan="Co so du lieu")
    hoc_phan_2 = HocPhan(ma_hoc_phan=902, ten_hoc_phan="Lap trinh web")
    session.add_all([can_bo, nganh, hoc_phan_1, hoc_phan_2])
    session.commit()
    session.refresh(can_bo)
    session.refresh(nganh)

    sinh_vien = SinhVien(ho="Le", ten="An", ma_nganh=nganh.ma_nganh)
    session.add(sinh_vien)
    session.commit()
    session.refresh(sinh_vien)

    warning_lop = LopHocPhan(
        ma_hoc_phan=hoc_phan_1.ma_hoc_phan,
        ma_can_bo=can_bo.ma_can_bo,
        hoc_ky=1,
        nam_hoc="2025-2026",
    )
    safe_lop = LopHocPhan(
        ma_hoc_phan=hoc_phan_2.ma_hoc_phan,
        ma_can_bo=can_bo.ma_can_bo,
        hoc_ky=1,
        nam_hoc="2025-2026",
    )
    session.add_all([warning_lop, safe_lop])
    session.commit()
    session.refresh(warning_lop)
    session.refresh(safe_lop)

    session.add_all(
        [
            DangKyHocPhan(
                ma_sinh_vien=sinh_vien.ma_sinh_vien,
                ma_lop_hoc_phan=warning_lop.ma_lop_hoc_phan,
            ),
            DangKyHocPhan(
                ma_sinh_vien=sinh_vien.ma_sinh_vien,
                ma_lop_hoc_phan=safe_lop.ma_lop_hoc_phan,
            ),
        ]
    )
    session.commit()

    warning_lessons = [
        BuoiHoc(
            ma_lop_hoc_phan=warning_lop.ma_lop_hoc_phan,
            ngay_hoc=date(2025, 10, day),
        )
        for day in range(1, 6)
    ]
    safe_lessons = [
        BuoiHoc(
            ma_lop_hoc_phan=safe_lop.ma_lop_hoc_phan,
            ngay_hoc=date(2025, 10, day),
        )
        for day in range(1, 6)
    ]
    session.add_all(warning_lessons + safe_lessons)
    session.commit()
    for lesson in warning_lessons + safe_lessons:
        session.refresh(lesson)

    session.add_all(
        [
            DiemDanh(
                ma_sinh_vien=sinh_vien.ma_sinh_vien,
                ma_buoi_hoc=warning_lessons[0].ma_buoi_hoc,
                trang_thai="VANG",
            ),
            DiemDanh(
                ma_sinh_vien=sinh_vien.ma_sinh_vien,
                ma_buoi_hoc=warning_lessons[1].ma_buoi_hoc,
                trang_thai="VANG_MAT",
            ),
            DiemDanh(
                ma_sinh_vien=sinh_vien.ma_sinh_vien,
                ma_buoi_hoc=safe_lessons[0].ma_buoi_hoc,
                trang_thai="CO_MAT",
            ),
        ]
    )
    session.commit()
    return sinh_vien, warning_lop, safe_lop


def test_read_canh_bao_vang_returns_warning_classes() -> None:
    """Test absence warning API returns classes near or over absence limit."""
    for client, session in make_test_client():
        sinh_vien, warning_lop, _safe_lop = seed_warning_data(session)

        response = client.get(
            f"/canh-bao-hoc-tap/sinh-vien/{sinh_vien.ma_sinh_vien}/vang"
        )
        body = response.json()

        assert response.status_code == 200
        assert body["ma_sinh_vien"] == sinh_vien.ma_sinh_vien
        assert body["count"] == 1
        assert body["data"][0]["ma_lop_hoc_phan"] == warning_lop.ma_lop_hoc_phan
        assert body["data"][0]["ten_hoc_phan"] == "Co so du lieu"
        assert body["data"][0]["tong_so_buoi_hoc"] == 5
        assert body["data"][0]["so_buoi_vang"] == 2
        assert body["data"][0]["ty_le_vang"] == 40.0
        assert body["data"][0]["nguong_canh_bao"] == 20.0
        assert body["data"][0]["trang_thai_canh_bao"] == "VUOT_NGUONG"


def test_read_canh_bao_vang_can_include_safe_classes() -> None:
    """Test absence warning API can include safe classes when requested."""
    for client, session in make_test_client():
        sinh_vien, _warning_lop, safe_lop = seed_warning_data(session)

        response = client.get(
            f"/canh-bao-hoc-tap/sinh-vien/{sinh_vien.ma_sinh_vien}/vang",
            params={"include_safe": True},
        )
        body = response.json()
        safe_item = next(
            item
            for item in body["data"]
            if item["ma_lop_hoc_phan"] == safe_lop.ma_lop_hoc_phan
        )

        assert response.status_code == 200
        assert body["count"] == 2
        assert safe_item["ty_le_vang"] == 0.0
        assert safe_item["trang_thai_canh_bao"] == "AN_TOAN"


def test_read_canh_bao_vang_returns_empty_when_no_warnings() -> None:
    """Test absence warning API returns empty response when there are no warnings."""
    for client, session in make_test_client():
        can_bo = CanBo(ho="Tran", ten="Giang", google_ten_dang_nhap="gv2@example.edu")
        nganh = Nganh(ten_nganh="He thong thong tin")
        hoc_phan = HocPhan(ma_hoc_phan=903, ten_hoc_phan="Kiem thu phan mem")
        session.add_all([can_bo, nganh, hoc_phan])
        session.commit()
        session.refresh(can_bo)
        session.refresh(nganh)
        sinh_vien = SinhVien(ho="Pham", ten="Binh", ma_nganh=nganh.ma_nganh)
        session.add(sinh_vien)
        session.commit()
        session.refresh(sinh_vien)

        lop_hoc_phan = LopHocPhan(
            ma_hoc_phan=hoc_phan.ma_hoc_phan,
            ma_can_bo=can_bo.ma_can_bo,
        )
        session.add(lop_hoc_phan)
        session.commit()
        session.refresh(lop_hoc_phan)
        session.add(
            DangKyHocPhan(
                ma_sinh_vien=sinh_vien.ma_sinh_vien,
                ma_lop_hoc_phan=lop_hoc_phan.ma_lop_hoc_phan,
            )
        )
        session.commit()

        response = client.get(
            f"/canh-bao-hoc-tap/sinh-vien/{sinh_vien.ma_sinh_vien}/vang"
        )
        body = response.json()

        assert response.status_code == 200
        assert body["data"] == []
        assert body["count"] == 0


def test_read_canh_bao_vang_rejects_invalid_threshold_order() -> None:
    """Test absence warning API rejects warning threshold greater than absence limit."""
    for client, session in make_test_client():
        sinh_vien, _warning_lop, _safe_lop = seed_warning_data(session)

        response = client.get(
            f"/canh-bao-hoc-tap/sinh-vien/{sinh_vien.ma_sinh_vien}/vang",
            params={"warning_threshold": 30, "absence_limit": 20},
        )

        assert response.status_code == 400
        assert response.json()["detail"] == (
            "warning_threshold must be less than or equal to absence_limit"
        )
