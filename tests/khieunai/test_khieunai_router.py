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
    DiemDanh,
    HocPhan,
    KhieuNai,
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
            HocPhan.__table__,
            LopHocPhan.__table__,
            BuoiHoc.__table__,
            Nganh.__table__,
            SinhVien.__table__,
            DiemDanh.__table__,
            KhieuNai.__table__,
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


def seed_khieu_nai_data(session: Session):
    """Seed staff, class, attendance and complaints for complaint router tests."""
    can_bo = CanBo(ho="Nguyen", ten="Giang", google_email="giang@example.edu")
    other_can_bo = CanBo(ho="Tran", ten="Khac", google_email="khac@example.edu")
    nganh = Nganh(ten_nganh="Cong nghe thong tin")
    hoc_phan = HocPhan(
        ma_hoc_phan=701,
        ten_hoc_phan="Nhap mon AI",
        so_tin_chi=3,
        trang_thai=True,
    )
    session.add_all([can_bo, other_can_bo, nganh, hoc_phan])
    session.commit()
    session.refresh(can_bo)
    session.refresh(other_can_bo)
    session.refresh(nganh)

    sinh_vien_1 = SinhVien(ho="Le", ten="An", ma_nganh=nganh.ma_nganh)
    sinh_vien_2 = SinhVien(ho="Pham", ten="Binh", ma_nganh=nganh.ma_nganh)
    sinh_vien_3 = SinhVien(ho="Do", ten="Chi", ma_nganh=nganh.ma_nganh)
    session.add_all([sinh_vien_1, sinh_vien_2, sinh_vien_3])
    session.commit()
    session.refresh(sinh_vien_1)
    session.refresh(sinh_vien_2)
    session.refresh(sinh_vien_3)

    target_lop = LopHocPhan(
        ma_hoc_phan=hoc_phan.ma_hoc_phan,
        ma_can_bo=can_bo.ma_can_bo,
        hoc_ky=1,
        nam_hoc="2025-2026",
    )
    other_lop = LopHocPhan(
        ma_hoc_phan=hoc_phan.ma_hoc_phan,
        ma_can_bo=other_can_bo.ma_can_bo,
        hoc_ky=1,
        nam_hoc="2025-2026",
    )
    session.add_all([target_lop, other_lop])
    session.commit()
    session.refresh(target_lop)
    session.refresh(other_lop)

    target_buoi = BuoiHoc(
        ma_lop_hoc_phan=target_lop.ma_lop_hoc_phan,
        ngay_hoc=date(2025, 10, 15),
    )
    other_buoi = BuoiHoc(
        ma_lop_hoc_phan=other_lop.ma_lop_hoc_phan,
        ngay_hoc=date(2025, 10, 15),
    )
    session.add_all([target_buoi, other_buoi])
    session.commit()
    session.refresh(target_buoi)
    session.refresh(other_buoi)

    diem_danh_1 = DiemDanh(
        ma_sinh_vien=sinh_vien_1.ma_sinh_vien,
        ma_buoi_hoc=target_buoi.ma_buoi_hoc,
        trang_thai="VANG",
    )
    diem_danh_2 = DiemDanh(
        ma_sinh_vien=sinh_vien_2.ma_sinh_vien,
        ma_buoi_hoc=target_buoi.ma_buoi_hoc,
        trang_thai="VANG",
    )
    other_diem_danh = DiemDanh(
        ma_sinh_vien=sinh_vien_3.ma_sinh_vien,
        ma_buoi_hoc=other_buoi.ma_buoi_hoc,
        trang_thai="VANG",
    )
    session.add_all([diem_danh_1, diem_danh_2, other_diem_danh])
    session.commit()
    session.refresh(diem_danh_1)
    session.refresh(diem_danh_2)
    session.refresh(other_diem_danh)

    khieu_nai_1 = KhieuNai(
        ma_diem_danh=diem_danh_1.ma_diem_danh,
        ma_sinh_vien=sinh_vien_1.ma_sinh_vien,
        ly_do="Em co mat trong lop",
        trang_thai="CHO_XU_LY",
    )
    khieu_nai_2 = KhieuNai(
        ma_diem_danh=diem_danh_2.ma_diem_danh,
        ma_sinh_vien=sinh_vien_2.ma_sinh_vien,
        ly_do="Em den muon",
        trang_thai="CHO_XU_LY",
    )
    other_khieu_nai = KhieuNai(
        ma_diem_danh=other_diem_danh.ma_diem_danh,
        ma_sinh_vien=sinh_vien_3.ma_sinh_vien,
        ly_do="Lop khac",
        trang_thai="CHO_XU_LY",
    )
    session.add_all([khieu_nai_1, khieu_nai_2, other_khieu_nai])
    session.commit()
    session.refresh(khieu_nai_1)
    session.refresh(khieu_nai_2)
    session.refresh(other_khieu_nai)

    return can_bo, other_can_bo, khieu_nai_1, khieu_nai_2, other_khieu_nai


def test_khieu_nai_can_xu_ly_flow() -> None:
    """Test list, detail, approve and reject APIs for staff pending complaints."""
    for client, session in make_test_client():
        can_bo, other_can_bo, khieu_nai_1, khieu_nai_2, other_khieu_nai = (
            seed_khieu_nai_data(session)
        )

        list_response = client.get(
            f"/khieu-nai/can-bo/{can_bo.ma_can_bo}/can-xu-ly"
        )
        list_body = list_response.json()

        detail_response = client.get(
            f"/khieu-nai/can-bo/{can_bo.ma_can_bo}/can-xu-ly/"
            f"{khieu_nai_1.ma_khieu_nai}"
        )
        approve_response = client.patch(
            f"/khieu-nai/can-bo/{can_bo.ma_can_bo}/can-xu-ly/"
            f"{khieu_nai_1.ma_khieu_nai}/chap-thuan",
            json={
                "ghi_chu_xu_ly": "Dong y cap nhat",
                "trang_thai_diem_danh_moi": "CO_MAT",
            },
        )
        approve_again_response = client.patch(
            f"/khieu-nai/can-bo/{can_bo.ma_can_bo}/can-xu-ly/"
            f"{khieu_nai_1.ma_khieu_nai}/chap-thuan",
            json={"trang_thai_diem_danh_moi": "CO_MAT"},
        )
        reject_response = client.patch(
            f"/khieu-nai/can-bo/{can_bo.ma_can_bo}/can-xu-ly/"
            f"{khieu_nai_2.ma_khieu_nai}/tu-choi",
            json={"ghi_chu_xu_ly": "Khong du bang chung"},
        )
        other_response = client.get(
            f"/khieu-nai/can-bo/{can_bo.ma_can_bo}/can-xu-ly/"
            f"{other_khieu_nai.ma_khieu_nai}"
        )
        wrong_staff_response = client.get(
            f"/khieu-nai/can-bo/{other_can_bo.ma_can_bo}/can-xu-ly/"
            f"{khieu_nai_1.ma_khieu_nai}"
        )

        assert list_response.status_code == 200
        assert list_body["count"] == 2
        assert list_body["data"][0]["ten_hoc_phan"] == "Nhap mon AI"
        assert detail_response.status_code == 200
        assert detail_response.json()["ma_khieu_nai"] == khieu_nai_1.ma_khieu_nai
        assert approve_response.status_code == 200
        assert approve_response.json()["trang_thai"] == "DA_CHAP_THUAN"
        assert approve_response.json()["trang_thai_diem_danh"] == "CO_MAT"
        assert approve_again_response.status_code == 409
        assert reject_response.status_code == 200
        assert reject_response.json()["trang_thai"] == "DA_TU_CHOI"
        assert other_response.status_code == 404
        assert wrong_staff_response.status_code == 404


def test_approve_khieu_nai_rejects_invalid_attendance_status() -> None:
    """Test approve API rejects unsupported attendance status values."""
    for client, session in make_test_client():
        can_bo, _other_can_bo, khieu_nai_1, _khieu_nai_2, _other_khieu_nai = (
            seed_khieu_nai_data(session)
        )

        response = client.patch(
            f"/khieu-nai/can-bo/{can_bo.ma_can_bo}/can-xu-ly/"
            f"{khieu_nai_1.ma_khieu_nai}/chap-thuan",
            json={"trang_thai_diem_danh_moi": "SAI_TRANG_THAI"},
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid attendance status"
