import pytest
from datetime import date, time, datetime, timedelta
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine
from app.core.exceptions import AppealTimeLimitExceededError, DuplicateAppealError, PermissionDeniedError

from app.models import (
    BuoiHoc,
    CanBo,
    DiemDanh,
    HocPhan,
    KhieuNai,
    KhieuNaiCreate,
    LopHocPhan,
    Nganh,
    SinhVien,
    TaiKhoan,
)
from app.services import khieunai_service


@pytest.fixture(scope="session", autouse=True)
def db():
    """Override conftest.py global db fixture to avoid Render PG execution."""
    yield None


def make_test_session():
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
    return Session(engine)


def seed_test_data(session: Session):
    can_bo = CanBo(ma_can_bo=1, ho="Nguyen", ten="Giang", google_ten_dang_nhap="giang@example.edu", ma_tai_khoan=10)
    nganh = Nganh(ma_nganh=1, ten_nganh="Cong nghe thong tin")
    hoc_phan = HocPhan(ma_hoc_phan=701, ten_hoc_phan="Nhap mon AI", so_tin_chi=3, trang_thai=True)
    session.add_all([can_bo, nganh, hoc_phan])
    session.commit()

    student_account = TaiKhoan(ma_tai_khoan=2, ten_dang_nhap="sv001", vai_tro="STUDENT", mat_khau_hash="hashed-password")
    sinh_vien = SinhVien(ma_sinh_vien=1, ho="Le", ten="An", ma_nganh=1, ma_tai_khoan=2)
    session.add_all([student_account, sinh_vien])
    session.commit()

    lop = LopHocPhan(ma_lop_hoc_phan=1, ma_hoc_phan=701, ma_can_bo=1, hoc_ky=1, nam_hoc="2025-2026")
    session.add(lop)
    session.commit()

    # 1. Buoi hoc hop le (ngay_hoc hom nay, ket thuc 10:00)
    buoi_hoc_ok = BuoiHoc(ma_buoi_hoc=1, ma_lop_hoc_phan=1, ngay_hoc=date.today(), gio_bat_dau=time(8, 0), gio_ket_thuc=time(10, 0))
    # 2. Buoi hoc qua han 48 gio
    buoi_hoc_expired = BuoiHoc(ma_buoi_hoc=2, ma_lop_hoc_phan=1, ngay_hoc=date.today() - timedelta(days=3), gio_bat_dau=time(8, 0), gio_ket_thuc=time(10, 0))
    session.add_all([buoi_hoc_ok, buoi_hoc_expired])
    session.commit()

    diem_danh_ok = DiemDanh(ma_diem_danh=1, ma_sinh_vien=1, ma_buoi_hoc=1, trang_thai="VANG")
    diem_danh_expired = DiemDanh(ma_diem_danh=2, ma_sinh_vien=1, ma_buoi_hoc=2, trang_thai="VANG")
    session.add_all([diem_danh_ok, diem_danh_expired])
    session.commit()

    return student_account, sinh_vien


def test_create_appeal_success():
    session = make_test_session()
    student_account, sinh_vien = seed_test_data(session)

    payload = KhieuNaiCreate(
        ma_sinh_vien=1,
        ma_diem_danh=1,
        ly_do="Em co di hoc",
        minh_chung="anh.jpg"
    )
    appeal = khieunai_service.create_appeal(
        session=session,
        payload=payload,
        current_account=student_account
    )
    assert appeal.ma_khieu_nai is not None
    assert appeal.ma_diem_danh == 1
    assert appeal.trang_thai == "CHO_XU_LY"


def test_create_appeal_expired():
    session = make_test_session()
    student_account, sinh_vien = seed_test_data(session)

    payload = KhieuNaiCreate(
        ma_sinh_vien=1,
        ma_diem_danh=2,
        ly_do="Em co di hoc tre",
        minh_chung="anh.jpg"
    )
    with pytest.raises(AppealTimeLimitExceededError) as excinfo:
        khieunai_service.create_appeal(
            session=session,
            payload=payload,
            current_account=student_account
        )
    assert excinfo.value.status_code == 400
    assert "Đã quá thời hạn 48 giờ" in excinfo.value.detail


def test_create_appeal_duplicate():
    session = make_test_session()
    student_account, sinh_vien = seed_test_data(session)

    payload = KhieuNaiCreate(
        ma_sinh_vien=1,
        ma_diem_danh=1,
        ly_do="Ly do 1",
        minh_chung="anh.jpg"
    )
    khieunai_service.create_appeal(
        session=session,
        payload=payload,
        current_account=student_account
    )

    with pytest.raises(DuplicateAppealError) as excinfo:
        khieunai_service.create_appeal(
            session=session,
            payload=payload,
            current_account=student_account
        )
    assert excinfo.value.status_code == 400
    assert "Đã tồn tại khiếu nại" in excinfo.value.detail


def test_create_appeal_unauthorized_student():
    session = make_test_session()
    student_account, sinh_vien = seed_test_data(session)

    payload = KhieuNaiCreate(
        ma_sinh_vien=999,
        ma_diem_danh=1,
        ly_do="Em co di hoc",
        minh_chung="anh.jpg"
    )
    with pytest.raises(PermissionDeniedError) as excinfo:
        khieunai_service.create_appeal(
            session=session,
            payload=payload,
            current_account=student_account
        )
    assert excinfo.value.status_code == 403
    assert "Cannot submit claim for another student" in excinfo.value.detail
