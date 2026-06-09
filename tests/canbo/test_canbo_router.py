from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.api.deps import get_current_active_superuser, get_db
from app.main import app
from datetime import date, datetime, time

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
    ThoiKhoaBieu,
)


def make_test_client() -> Generator[tuple[TestClient, Session], None, None]:
    """Tạo TestClient dùng SQLite in-memory để kiểm tra router cán bộ."""
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
            ThoiKhoaBieu.__table__,
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
            """Cung cấp session test thay cho database thật."""
            yield session

        def override_superuser():
            """Bỏ qua xác thực thật và giả lập admin cho test router."""
            return superuser

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_superuser] = override_superuser
        with TestClient(app) as client:
            yield client, session
        app.dependency_overrides.clear()


def test_canbo_crud_flow() -> None:
    """Kiểm tra đủ luồng thêm, tìm kiếm, sửa và xóa cán bộ."""
    for client, _session in make_test_client():
        create_response = client.post(
            "/canbo/",
            json={
                "ho": "Nguyen",
                "ten": "An",
                "google_email": "an@example.edu",
                "dien_thoai": "0900000000",
                "chuc_vu": "Giang vien",
            },
        )
        created = create_response.json()

        list_response = client.get("/canbo/", params={"q": "An"})
        detail_response = client.get(f"/canbo/{created['ma_can_bo']}")
        update_response = client.patch(
            f"/canbo/{created['ma_can_bo']}",
            json={"chuc_vu": "Truong bo mon"},
        )
        delete_response = client.delete(f"/canbo/{created['ma_can_bo']}")
        after_delete_response = client.get(f"/canbo/{created['ma_can_bo']}")

        assert create_response.status_code == 201
        assert created["ho"] == "Nguyen"
        assert created["ten"] == "An"
        assert list_response.status_code == 200
        assert list_response.json()["count"] == 1
        assert detail_response.status_code == 200
        assert update_response.status_code == 200
        assert update_response.json()["chuc_vu"] == "Truong bo mon"
        assert delete_response.status_code == 200
        assert after_delete_response.status_code == 404


def test_create_canbo_rejects_duplicate_google_email() -> None:
    """Kiểm tra không cho tạo hai cán bộ cùng Google email."""
    for client, _session in make_test_client():
        payload = {
            "ho": "Tran",
            "ten": "Binh",
            "google_email": "binh@example.edu",
        }

        first_response = client.post("/canbo/", json=payload)
        second_response = client.post(
            "/canbo/",
            json={**payload, "ten": "Binh 2"},
        )

        assert first_response.status_code == 201
        assert second_response.status_code == 409
        assert second_response.json()["detail"] == "Google email already exists"


def test_read_lich_day_can_bo_returns_teaching_schedule() -> None:
    """Kiểm tra API lịch dạy trả về buổi học của giảng viên theo mã cán bộ."""
    for client, session in make_test_client():
        can_bo = CanBo(ho="Le", ten="Cuong", google_email="cuong@example.edu")
        hoc_phan = HocPhan(
            ma_hoc_phan=101,
            ten_hoc_phan="Co so du lieu",
            so_tin_chi=3,
            trang_thai=True,
        )
        session.add(can_bo)
        session.add(hoc_phan)
        session.commit()
        session.refresh(can_bo)

        lop_hoc_phan = LopHocPhan(
            ma_hoc_phan=hoc_phan.ma_hoc_phan,
            ma_can_bo=can_bo.ma_can_bo,
            hoc_ky=1,
            nam_hoc="2025-2026",
            trang_thai=True,
        )
        session.add(lop_hoc_phan)
        session.commit()
        session.refresh(lop_hoc_phan)

        thoi_khoa_bieu = ThoiKhoaBieu(
            ma_lop_hoc_phan=lop_hoc_phan.ma_lop_hoc_phan,
            thu=2,
            tiet_bat_dau=1,
            tiet_ket_thuc=3,
            gio_bat_dau=time(7, 0),
            gio_ket_thuc=time(9, 30),
            ngay_bat_dau=date(2025, 9, 1),
            ngay_ket_thuc=date(2025, 12, 31),
        )
        buoi_hoc = BuoiHoc(
            ma_lop_hoc_phan=lop_hoc_phan.ma_lop_hoc_phan,
            ngay_hoc=date(2025, 9, 8),
            gio_bat_dau=time(7, 0),
            gio_ket_thuc=time(9, 30),
            so_buoi=1,
            trang_thai="DA_KET_THUC",
            ghi_chu="Buoi hoc dau tien",
        )
        session.add(thoi_khoa_bieu)
        session.add(buoi_hoc)
        session.commit()

        response = client.get(
            f"/canbo/{can_bo.ma_can_bo}/lich-day",
            params={
                "from_date": "2025-09-01",
                "to_date": "2025-09-30",
                "hoc_ky": 1,
                "nam_hoc": "2025-2026",
            },
        )
        body = response.json()

        assert response.status_code == 200
        assert body["count"] == 1
        assert body["data"][0]["ma_can_bo"] == can_bo.ma_can_bo
        assert body["data"][0]["ma_lop_hoc_phan"] == lop_hoc_phan.ma_lop_hoc_phan
        assert body["data"][0]["ten_hoc_phan"] == "Co so du lieu"
        assert body["data"][0]["ma_buoi_hoc"] is not None
        assert body["data"][0]["ma_thoi_khoa_bieu"] is not None
        assert body["data"][0]["ngay_hoc"] == "2025-09-08"
        assert body["data"][0]["trang_thai_buoi_hoc"] == "DA_KET_THUC"


def test_read_lich_day_can_bo_rejects_invalid_date_range() -> None:
    """Kiểm tra API lịch dạy từ chối khoảng ngày không hợp lệ."""
    for client, _session in make_test_client():
        response = client.get(
            "/canbo/1/lich-day",
            params={"from_date": "2025-10-01", "to_date": "2025-09-01"},
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "from_date must be before or equal to to_date"


def test_read_buoi_hoc_gan_day_can_bo_returns_recent_lessons() -> None:
    """Kiem tra API buoi hoc gan day tra ve thong ke diem danh cua can bo."""
    for client, session in make_test_client():
        can_bo = CanBo(ho="Mai", ten="Lan", google_email="lan@example.edu")
        other_can_bo = CanBo(ho="Mai", ten="Khac", google_email="khac@example.edu")
        nganh = Nganh(ten_nganh="Khoa hoc may tinh")
        hoc_phan = HocPhan(
            ma_hoc_phan=151,
            ten_hoc_phan="Tri tue nhan tao",
            so_tin_chi=3,
            trang_thai=True,
        )
        session.add_all([can_bo, other_can_bo, nganh, hoc_phan])
        session.commit()
        session.refresh(can_bo)
        session.refresh(other_can_bo)
        session.refresh(nganh)

        sinh_vien_1 = SinhVien(ho="Nguyen", ten="A", ma_nganh=nganh.ma_nganh)
        sinh_vien_2 = SinhVien(ho="Tran", ten="B", ma_nganh=nganh.ma_nganh)
        sinh_vien_3 = SinhVien(ho="Le", ten="C", ma_nganh=nganh.ma_nganh)
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

        old_lesson = BuoiHoc(
            ma_lop_hoc_phan=target_lop.ma_lop_hoc_phan,
            ngay_hoc=date(2025, 10, 1),
        )
        recent_lesson = BuoiHoc(
            ma_lop_hoc_phan=target_lop.ma_lop_hoc_phan,
            ngay_hoc=date(2025, 10, 8),
        )
        other_lesson = BuoiHoc(
            ma_lop_hoc_phan=other_lop.ma_lop_hoc_phan,
            ngay_hoc=date(2025, 10, 9),
        )
        session.add_all([old_lesson, recent_lesson, other_lesson])
        session.commit()
        session.refresh(recent_lesson)
        session.refresh(other_lesson)

        session.add_all(
            [
                DiemDanh(
                    ma_sinh_vien=sinh_vien_1.ma_sinh_vien,
                    ma_buoi_hoc=recent_lesson.ma_buoi_hoc,
                    trang_thai="CO_MAT",
                ),
                DiemDanh(
                    ma_sinh_vien=sinh_vien_2.ma_sinh_vien,
                    ma_buoi_hoc=recent_lesson.ma_buoi_hoc,
                    trang_thai="DI_MUON",
                ),
                DiemDanh(
                    ma_sinh_vien=sinh_vien_3.ma_sinh_vien,
                    ma_buoi_hoc=recent_lesson.ma_buoi_hoc,
                    trang_thai="VANG",
                ),
                DiemDanh(
                    ma_sinh_vien=sinh_vien_1.ma_sinh_vien,
                    ma_buoi_hoc=other_lesson.ma_buoi_hoc,
                    trang_thai="CO_MAT",
                ),
            ]
        )
        session.commit()

        response = client.get(
            f"/canbo/{can_bo.ma_can_bo}/buoi-hoc/gan-day",
            params={"limit": 1},
        )
        body = response.json()

        assert response.status_code == 200
        assert body["count"] == 1
        assert body["data"][0]["ma_lop_hoc_phan"] == target_lop.ma_lop_hoc_phan
        assert body["data"][0]["ten_hoc_phan"] == "Tri tue nhan tao"
        assert body["data"][0]["ngay_hoc"] == "2025-10-08"
        assert body["data"][0]["so_sinh_vien_co_mat"] == 1
        assert body["data"][0]["so_sinh_vien_di_muon"] == 1
        assert body["data"][0]["so_sinh_vien_vang_mat"] == 1


def test_count_lop_hoc_phan_dang_day_returns_current_semester_count() -> None:
    """Kiểm tra API đếm số lớp học phần đang giảng dạy trong học kỳ hiện tại."""
    for client, session in make_test_client():
        can_bo = CanBo(ho="Pham", ten="Dung", google_email="dung@example.edu")
        hoc_phan = HocPhan(
            ma_hoc_phan=201,
            ten_hoc_phan="Lap trinh Python",
            so_tin_chi=3,
            trang_thai=True,
        )
        session.add(can_bo)
        session.add(hoc_phan)
        session.commit()
        session.refresh(can_bo)

        active_lop = LopHocPhan(
            ma_hoc_phan=hoc_phan.ma_hoc_phan,
            ma_can_bo=can_bo.ma_can_bo,
            hoc_ky=1,
            nam_hoc="2025-2026",
            trang_thai=True,
        )
        inactive_lop = LopHocPhan(
            ma_hoc_phan=hoc_phan.ma_hoc_phan,
            ma_can_bo=can_bo.ma_can_bo,
            hoc_ky=1,
            nam_hoc="2025-2026",
            trang_thai=True,
        )
        session.add(active_lop)
        session.add(inactive_lop)
        session.commit()
        session.refresh(active_lop)
        session.refresh(inactive_lop)

        session.add(
            ThoiKhoaBieu(
                ma_lop_hoc_phan=active_lop.ma_lop_hoc_phan,
                thu=2,
                ngay_bat_dau=date(2025, 9, 1),
                ngay_ket_thuc=date(2025, 12, 31),
            )
        )
        session.add(
            ThoiKhoaBieu(
                ma_lop_hoc_phan=inactive_lop.ma_lop_hoc_phan,
                thu=2,
                ngay_bat_dau=date(2025, 9, 1),
                ngay_ket_thuc=date(2025, 9, 30),
            )
        )
        session.commit()

        response = client.get(
            f"/canbo/{can_bo.ma_can_bo}/lop-hoc-phan/dang-day/count",
            params={"as_of_date": "2025-10-06"},
        )
        body = response.json()

        assert response.status_code == 200
        assert body["ma_can_bo"] == can_bo.ma_can_bo
        assert body["hoc_ky"] == 1
        assert body["nam_hoc"] == "2025-2026"
        assert body["as_of_date"] == "2025-10-06"
        assert body["count"] == 1


def test_read_monthly_attendance_summary_returns_change_from_previous_month() -> None:
    """Kiểm tra API thống kê tỷ lệ có mặt tháng hiện tại so với tháng trước."""
    for client, session in make_test_client():
        can_bo = CanBo(ho="Do", ten="Hoa", google_email="hoa@example.edu")
        nganh = Nganh(ten_nganh="Cong nghe thong tin")
        hoc_phan = HocPhan(
            ma_hoc_phan=301,
            ten_hoc_phan="Kien truc phan mem",
            so_tin_chi=3,
            trang_thai=True,
        )
        session.add(can_bo)
        session.add(nganh)
        session.add(hoc_phan)
        session.commit()
        session.refresh(can_bo)
        session.refresh(nganh)

        sinh_vien_1 = SinhVien(ho="Nguyen", ten="A", ma_nganh=nganh.ma_nganh)
        sinh_vien_2 = SinhVien(ho="Tran", ten="B", ma_nganh=nganh.ma_nganh)
        session.add(sinh_vien_1)
        session.add(sinh_vien_2)
        session.commit()
        session.refresh(sinh_vien_1)
        session.refresh(sinh_vien_2)

        lop_hoc_phan = LopHocPhan(
            ma_hoc_phan=hoc_phan.ma_hoc_phan,
            ma_can_bo=can_bo.ma_can_bo,
            hoc_ky=1,
            nam_hoc="2025-2026",
            trang_thai=True,
        )
        session.add(lop_hoc_phan)
        session.commit()
        session.refresh(lop_hoc_phan)

        previous_month_lesson = BuoiHoc(
            ma_lop_hoc_phan=lop_hoc_phan.ma_lop_hoc_phan,
            ngay_hoc=date(2025, 9, 15),
        )
        current_month_lesson_1 = BuoiHoc(
            ma_lop_hoc_phan=lop_hoc_phan.ma_lop_hoc_phan,
            ngay_hoc=date(2025, 10, 6),
        )
        current_month_lesson_2 = BuoiHoc(
            ma_lop_hoc_phan=lop_hoc_phan.ma_lop_hoc_phan,
            ngay_hoc=date(2025, 10, 13),
        )
        session.add(previous_month_lesson)
        session.add(current_month_lesson_1)
        session.add(current_month_lesson_2)
        session.commit()
        session.refresh(previous_month_lesson)
        session.refresh(current_month_lesson_1)
        session.refresh(current_month_lesson_2)

        session.add_all(
            [
                DiemDanh(
                    ma_sinh_vien=sinh_vien_1.ma_sinh_vien,
                    ma_buoi_hoc=previous_month_lesson.ma_buoi_hoc,
                    trang_thai="CO_MAT",
                ),
                DiemDanh(
                    ma_sinh_vien=sinh_vien_2.ma_sinh_vien,
                    ma_buoi_hoc=previous_month_lesson.ma_buoi_hoc,
                    trang_thai="VANG",
                ),
                DiemDanh(
                    ma_sinh_vien=sinh_vien_1.ma_sinh_vien,
                    ma_buoi_hoc=current_month_lesson_1.ma_buoi_hoc,
                    trang_thai="CO_MAT",
                ),
                DiemDanh(
                    ma_sinh_vien=sinh_vien_2.ma_sinh_vien,
                    ma_buoi_hoc=current_month_lesson_1.ma_buoi_hoc,
                    trang_thai="CO_MAT",
                ),
                DiemDanh(
                    ma_sinh_vien=sinh_vien_1.ma_sinh_vien,
                    ma_buoi_hoc=current_month_lesson_2.ma_buoi_hoc,
                    trang_thai="DI_MUON",
                ),
                DiemDanh(
                    ma_sinh_vien=sinh_vien_2.ma_sinh_vien,
                    ma_buoi_hoc=current_month_lesson_2.ma_buoi_hoc,
                    trang_thai="VANG",
                ),
            ]
        )
        session.commit()

        response = client.get(
            f"/canbo/{can_bo.ma_can_bo}/attendance/monthly-summary",
            params={"reference_date": "2025-10-20"},
        )
        body = response.json()

        assert response.status_code == 200
        assert body["current_month"] == "2025-10"
        assert body["previous_month"] == "2025-09"
        assert body["current_month_present_count"] == 3
        assert body["current_month_total_count"] == 4
        assert body["previous_month_present_count"] == 1
        assert body["previous_month_total_count"] == 2
        assert body["current_month_attendance_rate"] == 75.0
        assert body["previous_month_attendance_rate"] == 50.0
        assert body["change_percentage"] == 25.0
        assert body["description"] == "+25.0% so với tháng trước"


def test_count_khieu_nai_cho_xu_ly_returns_staff_owned_pending_count() -> None:
    """Kiểm tra API chỉ đếm khiếu nại chờ xử lý thuộc lớp cán bộ phụ trách."""
    for client, session in make_test_client():
        can_bo = CanBo(ho="Vu", ten="Minh", google_email="minh@example.edu")
        other_can_bo = CanBo(ho="Hoang", ten="Nam", google_email="nam@example.edu")
        nganh = Nganh(ten_nganh="He thong thong tin")
        hoc_phan = HocPhan(
            ma_hoc_phan=401,
            ten_hoc_phan="Phan tich thiet ke",
            so_tin_chi=3,
            trang_thai=True,
        )
        session.add_all([can_bo, other_can_bo, nganh, hoc_phan])
        session.commit()
        session.refresh(can_bo)
        session.refresh(other_can_bo)
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
            ngay_hoc=date(2025, 10, 7),
        )
        other_buoi = BuoiHoc(
            ma_lop_hoc_phan=other_lop.ma_lop_hoc_phan,
            ngay_hoc=date(2025, 10, 7),
        )
        session.add_all([target_buoi, other_buoi])
        session.commit()
        session.refresh(target_buoi)
        session.refresh(other_buoi)

        target_diem_danh_1 = DiemDanh(
            ma_sinh_vien=sinh_vien.ma_sinh_vien,
            ma_buoi_hoc=target_buoi.ma_buoi_hoc,
            trang_thai="VANG",
        )
        target_diem_danh_2 = DiemDanh(
            ma_sinh_vien=sinh_vien.ma_sinh_vien + 100,
            ma_buoi_hoc=target_buoi.ma_buoi_hoc,
            trang_thai="VANG",
        )
        other_diem_danh = DiemDanh(
            ma_sinh_vien=sinh_vien.ma_sinh_vien + 200,
            ma_buoi_hoc=other_buoi.ma_buoi_hoc,
            trang_thai="VANG",
        )
        session.add_all([target_diem_danh_1, target_diem_danh_2, other_diem_danh])
        session.commit()
        session.refresh(target_diem_danh_1)
        session.refresh(target_diem_danh_2)
        session.refresh(other_diem_danh)

        session.add_all(
            [
                KhieuNai(
                    ma_diem_danh=target_diem_danh_1.ma_diem_danh,
                    ma_sinh_vien=target_diem_danh_1.ma_sinh_vien,
                    ly_do="Can xem lai",
                    trang_thai="CHO_XU_LY",
                    ngay_xu_ly=None,
                ),
                KhieuNai(
                    ma_diem_danh=target_diem_danh_2.ma_diem_danh,
                    ma_sinh_vien=target_diem_danh_2.ma_sinh_vien,
                    ly_do="Da xu ly",
                    trang_thai="CHO_XU_LY",
                    ngay_xu_ly=datetime(2025, 10, 8),
                ),
                KhieuNai(
                    ma_diem_danh=other_diem_danh.ma_diem_danh,
                    ma_sinh_vien=other_diem_danh.ma_sinh_vien,
                    ly_do="Lop khac",
                    trang_thai="CHO_XU_LY",
                    ngay_xu_ly=None,
                ),
            ]
        )
        session.commit()

        response = client.get(
            f"/canbo/{can_bo.ma_can_bo}/khieu-nai/cho-xu-ly/count"
        )
        body = response.json()

        assert response.status_code == 200
        assert body["so_luong_cho_xu_ly"] == 1
        assert body["thoi_diem_thong_ke"]
