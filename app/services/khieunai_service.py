"""
KhieuNai service.

Contains business logic for complaint metrics used by dashboard APIs.
"""

from datetime import datetime, timezone
from typing import Any

from app.core.exceptions import StaffNotFoundError, AppealNotFoundError, DuplicateAppealError, AppealTimeLimitExceededError, LessonNotFoundError, PermissionDeniedError, AppException
from sqlmodel import Session

from app.crud.canbo_crud import get_staff_member
from app.crud.khieunai_crud import (
    TRANG_THAI_CHO_XU_LY,
    TRANG_THAI_DA_CHAP_THUAN,
    TRANG_THAI_DA_TU_CHOI,
    count_khieu_nai_cho_xu_ly_by_can_bo,
    get_khieu_nai_can_xu_ly_by_can_bo,
    get_khieu_nai_can_xu_ly_detail_by_can_bo,
    get_khieu_nai_detail_context_by_can_bo,
    update_khieu_nai_xu_ly,
)
from app.models import (
    KhieuNai,
    KhieuNaiCreate,
    KhieuNaiPublic,
    KhieuNaisPublic,
    KhieuNaiCanXuLyDetail,
    KhieuNaiCanXuLysPublic,
    KhieuNaiChapThuanRequest,
    KhieuNaiChoXuLyMetric,
    KhieuNaiXuLyRequest,
    KhieuNaiXuLyResult,
)

TRANG_THAI_DIEM_DANH_HOP_LE = {"CO_MAT", "DI_MUON", "VANG", "VANG_MAT"}


def get_khieu_nai_cho_xu_ly_metric(
    *, session: Session, ma_can_bo: int
) -> KhieuNaiChoXuLyMetric:
    """
    Build pending complaint metric for a staff member.

    Args:
        session: Database session.
        ma_can_bo: Staff/teacher identifier.

    Returns:
        Metric containing pending complaints and generated timestamp.
    """
    return KhieuNaiChoXuLyMetric(
        so_luong_cho_xu_ly=count_khieu_nai_cho_xu_ly_by_can_bo(
            session=session,
            ma_can_bo=ma_can_bo,
        ),
        thoi_diem_thong_ke=datetime.now(timezone.utc),
    )


def ensure_can_bo_exists(*, session: Session, ma_can_bo: int) -> None:
    """Raise 404 when staff profile does not exist."""
    if not get_staff_member(session=session, ma_can_bo=ma_can_bo):
        raise StaffNotFoundError("Staff profile not found")


def list_khieu_nai_can_xu_ly(
    *,
    session: Session,
    ma_can_bo: int,
    skip: int = 0,
    limit: int = 100,
) -> KhieuNaiCanXuLysPublic:
    """Build pending complaint list for a staff member."""
    ensure_can_bo_exists(session=session, ma_can_bo=ma_can_bo)
    items, count = get_khieu_nai_can_xu_ly_by_can_bo(
        session=session,
        ma_can_bo=ma_can_bo,
        skip=skip,
        limit=limit,
    )
    return KhieuNaiCanXuLysPublic(data=items, count=count)


def get_khieu_nai_can_xu_ly_detail(
    *,
    session: Session,
    ma_can_bo: int,
    ma_khieu_nai: int,
) -> KhieuNaiCanXuLyDetail:
    """Build pending complaint detail for a staff member."""
    ensure_can_bo_exists(session=session, ma_can_bo=ma_can_bo)
    detail = get_khieu_nai_can_xu_ly_detail_by_can_bo(
        session=session,
        ma_can_bo=ma_can_bo,
        ma_khieu_nai=ma_khieu_nai,
    )
    if not detail:
        raise AppealNotFoundError("Pending complaint not found")
    return detail


def ensure_khieu_nai_can_xu_ly(
    *,
    session: Session,
    ma_can_bo: int,
    ma_khieu_nai: int,
):
    """Return complaint context and ensure it can still be processed."""
    ensure_can_bo_exists(session=session, ma_can_bo=ma_can_bo)
    context = get_khieu_nai_detail_context_by_can_bo(
        session=session,
        ma_can_bo=ma_can_bo,
        ma_khieu_nai=ma_khieu_nai,
    )
    if not context:
        raise AppealNotFoundError("Complaint not found")

    khieu_nai = context[0]
    if khieu_nai.trang_thai != TRANG_THAI_CHO_XU_LY or khieu_nai.ngay_xu_ly:
        raise AppException("Complaint has already been processed", status_code=409)
    return context


def build_khieu_nai_xu_ly_result(
    *,
    ma_khieu_nai: int,
    trang_thai: str,
    ma_can_bo_xu_ly: int,
    ghi_chu_xu_ly: str | None,
    ngay_xu_ly: datetime,
    trang_thai_diem_danh: str,
) -> KhieuNaiXuLyResult:
    """Build complaint processing result response."""
    return KhieuNaiXuLyResult(
        ma_khieu_nai=ma_khieu_nai,
        trang_thai=trang_thai,
        ma_can_bo_xu_ly=ma_can_bo_xu_ly,
        ghi_chu_xu_ly=ghi_chu_xu_ly,
        ngay_xu_ly=ngay_xu_ly,
        trang_thai_diem_danh=trang_thai_diem_danh,
    )


def chap_thuan_khieu_nai(
    *,
    session: Session,
    ma_can_bo: int,
    ma_khieu_nai: int,
    payload: KhieuNaiChapThuanRequest,
) -> KhieuNaiXuLyResult:
    """Approve a pending complaint and optionally update attendance status."""
    if (
        payload.trang_thai_diem_danh_moi
        and payload.trang_thai_diem_danh_moi not in TRANG_THAI_DIEM_DANH_HOP_LE
    ):
        raise AppException("Invalid attendance status", status_code=400)

    khieu_nai, diem_danh, *_ = ensure_khieu_nai_can_xu_ly(
        session=session,
        ma_can_bo=ma_can_bo,
        ma_khieu_nai=ma_khieu_nai,
    )
    ngay_xu_ly = datetime.now(timezone.utc)
    update_khieu_nai_xu_ly(
        session=session,
        khieu_nai=khieu_nai,
        diem_danh=diem_danh,
        trang_thai_khieu_nai=TRANG_THAI_DA_CHAP_THUAN,
        ma_can_bo_xu_ly=ma_can_bo,
        ngay_xu_ly=ngay_xu_ly,
        ghi_chu_xu_ly=payload.ghi_chu_xu_ly,
        trang_thai_diem_danh_moi=payload.trang_thai_diem_danh_moi,
    )
    return build_khieu_nai_xu_ly_result(
        ma_khieu_nai=khieu_nai.ma_khieu_nai,
        trang_thai=khieu_nai.trang_thai,
        ma_can_bo_xu_ly=ma_can_bo,
        ghi_chu_xu_ly=khieu_nai.ghi_chu_xu_ly,
        ngay_xu_ly=khieu_nai.ngay_xu_ly,
        trang_thai_diem_danh=diem_danh.trang_thai,
    )


def tu_choi_khieu_nai(
    *,
    session: Session,
    ma_can_bo: int,
    ma_khieu_nai: int,
    payload: KhieuNaiXuLyRequest,
) -> KhieuNaiXuLyResult:
    """Reject a pending complaint and keep attendance status unchanged."""
    khieu_nai, diem_danh, *_ = ensure_khieu_nai_can_xu_ly(
        session=session,
        ma_can_bo=ma_can_bo,
        ma_khieu_nai=ma_khieu_nai,
    )
    ngay_xu_ly = datetime.now(timezone.utc)
    update_khieu_nai_xu_ly(
        session=session,
        khieu_nai=khieu_nai,
        diem_danh=diem_danh,
        trang_thai_khieu_nai=TRANG_THAI_DA_TU_CHOI,
        ma_can_bo_xu_ly=ma_can_bo,
        ngay_xu_ly=ngay_xu_ly,
        ghi_chu_xu_ly=payload.ghi_chu_xu_ly,
    )
    return build_khieu_nai_xu_ly_result(
        ma_khieu_nai=khieu_nai.ma_khieu_nai,
        trang_thai=khieu_nai.trang_thai,
        ma_can_bo_xu_ly=ma_can_bo,
        ghi_chu_xu_ly=khieu_nai.ghi_chu_xu_ly,
        ngay_xu_ly=khieu_nai.ngay_xu_ly,
        trang_thai_diem_danh=diem_danh.trang_thai,
    )


def create_appeal(
    *,
    session: Session,
    payload: KhieuNaiCreate,
    current_account: Any,
) -> KhieuNai:
    """Create a new complaint for attendance records."""
    from datetime import timedelta
    from sqlmodel import select
    from app.models import SinhVien, DiemDanh, BuoiHoc

    sinh_vien = session.exec(select(SinhVien).where(SinhVien.ma_tai_khoan == current_account.ma_tai_khoan)).first()
    if not sinh_vien:
        raise PermissionDeniedError("Not a student")
    if payload.ma_sinh_vien != sinh_vien.ma_sinh_vien:
        raise PermissionDeniedError("Cannot submit claim for another student")

    existing_khieu_nai = session.exec(select(KhieuNai).where(KhieuNai.ma_diem_danh == payload.ma_diem_danh)).first()
    if existing_khieu_nai:
        raise DuplicateAppealError("Đã tồn tại khiếu nại cho bản ghi điểm danh này")

    diem_danh = session.get(DiemDanh, payload.ma_diem_danh)
    if not diem_danh:
        raise AppealNotFoundError("Bản ghi điểm danh không tồn tại")
    
    buoi_hoc = session.get(BuoiHoc, diem_danh.ma_buoi_hoc)
    if not buoi_hoc:
        raise LessonNotFoundError("Buổi học không tồn tại")
        
    if buoi_hoc.gio_ket_thuc:
        thoi_gian_ket_thuc = datetime.combine(buoi_hoc.ngay_hoc, buoi_hoc.gio_ket_thuc)
    else:
        thoi_gian_ket_thuc = datetime.combine(buoi_hoc.ngay_hoc, datetime.max.time())
        
    if datetime.now() > thoi_gian_ket_thuc + timedelta(hours=48):
        raise AppealTimeLimitExceededError("Đã quá thời hạn 48 giờ để gửi khiếu nại cho buổi học này")

    db_khieu_nai = KhieuNai.model_validate(payload)
    session.add(db_khieu_nai)
    session.commit()
    session.refresh(db_khieu_nai)
    return db_khieu_nai


def list_my_appeals(
    *,
    session: Session,
    current_account: Any,
    skip: int = 0,
    limit: int = 100,
) -> KhieuNaisPublic:
    """List appeals submitted by the current student."""
    from sqlmodel import select, func, col
    from app.models import SinhVien, DiemDanh, BuoiHoc, LopHocPhan, HocPhan

    sinh_vien = session.exec(select(SinhVien).where(SinhVien.ma_tai_khoan == current_account.ma_tai_khoan)).first()
    if not sinh_vien:
        raise PermissionDeniedError("Not a student")

    count_statement = select(func.count()).select_from(KhieuNai).where(KhieuNai.ma_sinh_vien == sinh_vien.ma_sinh_vien)
    count = session.exec(count_statement).one()

    statement = (
        select(KhieuNai, DiemDanh, BuoiHoc, LopHocPhan, HocPhan)
        .join(DiemDanh, KhieuNai.ma_diem_danh == DiemDanh.ma_diem_danh)
        .join(BuoiHoc, DiemDanh.ma_buoi_hoc == BuoiHoc.ma_buoi_hoc)
        .join(LopHocPhan, BuoiHoc.ma_lop_hoc_phan == LopHocPhan.ma_lop_lop_hoc_phan if hasattr(LopHocPhan, 'ma_lop_lop_hoc_phan') else LopHocPhan.ma_lop_hoc_phan)
        .join(HocPhan, LopHocPhan.ma_hoc_phan == HocPhan.ma_hoc_phan)
        .where(KhieuNai.ma_sinh_vien == sinh_vien.ma_sinh_vien)
        .order_by(col(KhieuNai.ngay_gui).desc())
        .offset(skip)
        .limit(limit)
    )
    # Wait, let's verify if LopHocPhan.ma_lop_hoc_phan is correct. Yes, we saw it in khieunai.py.
    # So we can just join(LopHocPhan, BuoiHoc.ma_lop_hoc_phan == LopHocPhan.ma_lop_hoc_phan)
    statement = (
        select(KhieuNai, DiemDanh, BuoiHoc, LopHocPhan, HocPhan)
        .join(DiemDanh, KhieuNai.ma_diem_danh == DiemDanh.ma_diem_danh)
        .join(BuoiHoc, DiemDanh.ma_buoi_hoc == BuoiHoc.ma_buoi_hoc)
        .join(LopHocPhan, BuoiHoc.ma_lop_hoc_phan == LopHocPhan.ma_lop_hoc_phan)
        .join(HocPhan, LopHocPhan.ma_hoc_phan == HocPhan.ma_hoc_phan)
        .where(KhieuNai.ma_sinh_vien == sinh_vien.ma_sinh_vien)
        .order_by(col(KhieuNai.ngay_gui).desc())
        .offset(skip)
        .limit(limit)
    )

    rows = session.exec(statement).all()
    khieu_nais = [
        KhieuNaiPublic(
            **khieu_nai.model_dump(),
            ma_lop_hoc_phan=lop_hoc_phan.ma_lop_hoc_phan,
            ma_hoc_phan=hoc_phan.ma_hoc_phan,
            ten_hoc_phan=hoc_phan.ten_hoc_phan,
            ngay_hoc=buoi_hoc.ngay_hoc,
            so_buoi=buoi_hoc.so_buoi,
            trang_thai_diem_danh=diem_danh.trang_thai,
        )
        for khieu_nai, diem_danh, buoi_hoc, lop_hoc_phan, hoc_phan in rows
    ]
    return KhieuNaisPublic(data=khieu_nais, count=count)
