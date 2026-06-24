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


def seed_attendance_summary_data(session: Session):
    """Seed student semester attendance data for summary tests."""
    can_bo = CanBo(ho="Nguyen", ten="Giang", google_ten_dang_nhap="gv@example.edu")
    nganh = Nganh(ten_nganh="Cong nghe thong tin")
    hoc_phan = HocPhan(ma_hoc_phan=1001, ten_hoc_phan="Co so du lieu")
    other_hoc_phan = HocPhan(ma_hoc_phan=1002, ten_hoc_phan="Tri tue nhan tao")
    session.add_all([can_bo, nganh, hoc_phan, other_hoc_phan])
    session.commit()
    session.refresh(can_bo)
    session.refresh(nganh)

    sinh_vien = SinhVien(ho="Le", ten="An", ma_nganh=nganh.ma_nganh)
    session.add(sinh_vien)
    session.commit()
    session.refresh(sinh_vien)

    target_lop = LopHocPhan(
        ma_hoc_phan=hoc_phan.ma_hoc_phan,
        ma_can_bo=can_bo.ma_can_bo,
        hoc_ky=1,
        nam_hoc="2025-2026",
    )
    other_semester_lop = LopHocPhan(
        ma_hoc_phan=other_hoc_phan.ma_hoc_phan,
        ma_can_bo=can_bo.ma_can_bo,
        hoc_ky=2,
        nam_hoc="2025-2026",
    )
    session.add_all([target_lop, other_semester_lop])
    session.commit()
    session.refresh(target_lop)
    session.refresh(other_semester_lop)

    session.add_all(
        [
            DangKyHocPhan(
                ma_sinh_vien=sinh_vien.ma_sinh_vien,
                ma_lop_hoc_phan=target_lop.ma_lop_hoc_phan,
            ),
            DangKyHocPhan(
                ma_sinh_vien=sinh_vien.ma_sinh_vien,
                ma_lop_hoc_phan=other_semester_lop.ma_lop_hoc_phan,
            ),
        ]
    )
    session.commit()

    target_lessons = [
        BuoiHoc(
            ma_lop_hoc_phan=target_lop.ma_lop_hoc_phan,
            ngay_hoc=date(2025, 10, day),
        )
        for day in range(1, 5)
    ]
    other_lesson = BuoiHoc(
        ma_lop_hoc_phan=other_semester_lop.ma_lop_hoc_phan,
        ngay_hoc=date(2026, 3, 1),
    )
    session.add_all([*target_lessons, other_lesson])
    session.commit()
    for lesson in target_lessons:
        session.refresh(lesson)
    session.refresh(other_lesson)

    session.add_all(
        [
            DiemDanh(
                ma_sinh_vien=sinh_vien.ma_sinh_vien,
                ma_buoi_hoc=target_lessons[0].ma_buoi_hoc,
                trang_thai="CO_MAT",
            ),
            DiemDanh(
                ma_sinh_vien=sinh_vien.ma_sinh_vien,
                ma_buoi_hoc=target_lessons[1].ma_buoi_hoc,
                trang_thai="DI_MUON",
            ),
            DiemDanh(
                ma_sinh_vien=sinh_vien.ma_sinh_vien,
                ma_buoi_hoc=target_lessons[2].ma_buoi_hoc,
                trang_thai="VANG",
            ),
            DiemDanh(
                ma_sinh_vien=sinh_vien.ma_sinh_vien,
                ma_buoi_hoc=other_lesson.ma_buoi_hoc,
                trang_thai="CO_MAT",
            ),
        ]
    )
    session.commit()
    return sinh_vien


def test_read_tong_buoi_co_mat_hoc_ky_returns_summary() -> None:
    """Test semester attendance summary counts present and total lessons."""
    for client, session in make_test_client():
        sinh_vien = seed_attendance_summary_data(session)

        response = client.get(
            f"/diem-danh/sinh-vien/{sinh_vien.ma_sinh_vien}/tong-buoi-co-mat",
            params={"hoc_ky": 1, "nam_hoc": "2025-2026"},
        )
        body = response.json()

        assert response.status_code == 200
        assert body["ma_sinh_vien"] == sinh_vien.ma_sinh_vien
        assert body["hoc_ky"] == 1
        assert body["nam_hoc"] == "2025-2026"
        assert body["so_buoi_co_mat"] == 2
        assert body["tong_so_buoi_hoc"] == 4
        assert body["ty_le_co_mat"] == 50.0
        assert body["mo_ta"] == "2/4 buổi trong học kỳ"


def test_read_tong_buoi_co_mat_hoc_ky_returns_zero_without_data() -> None:
    """Test semester attendance summary returns zeros when no classes are found."""
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
            f"/diem-danh/sinh-vien/{sinh_vien.ma_sinh_vien}/tong-buoi-co-mat",
            params={"hoc_ky": 1, "nam_hoc": "2025-2026"},
        )
        body = response.json()

        assert response.status_code == 200
        assert body["so_buoi_co_mat"] == 0
        assert body["tong_so_buoi_hoc"] == 0
        assert body["ty_le_co_mat"] == 0.0
        assert body["mo_ta"] == "0/0 buổi trong học kỳ"


def test_read_tong_buoi_co_mat_hoc_ky_rejects_missing_student() -> None:
    """Test semester attendance summary returns 404 for missing student profile."""
    for client, _session in make_test_client():
        response = client.get(
            "/diem-danh/sinh-vien/999/tong-buoi-co-mat",
            params={"hoc_ky": 1, "nam_hoc": "2025-2026"},
        )

        assert response.status_code == 404
        assert response.json()["errors"][0]["developer_message"] == "Not found"
