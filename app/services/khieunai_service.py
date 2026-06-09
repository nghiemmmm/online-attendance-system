"""
KhieuNai service.

Contains business logic for complaint metrics used by dashboard APIs.
"""

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlmodel import Session

from app.crud.canbo_crud import get_can_bo
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
    if not get_can_bo(session=session, ma_can_bo=ma_can_bo):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff profile not found",
        )


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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pending complaint not found",
        )
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found",
        )

    khieu_nai = context[0]
    if khieu_nai.trang_thai != TRANG_THAI_CHO_XU_LY or khieu_nai.ngay_xu_ly:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Complaint has already been processed",
        )
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid attendance status",
        )

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
