"""
Canh bao hoc tap service.

Contains business logic for student academic warnings.
"""

from fastapi import HTTPException, status
from sqlmodel import Session

from app.crud.canhbaohoc_tap_crud import get_absence_warning_sources_by_sinh_vien
from app.crud.sinhvien_crud import get_sinh_vien
from app.models import CanhBaoVangItem, CanhBaoVangPublic

TRANG_THAI_AN_TOAN = "AN_TOAN"
TRANG_THAI_CANH_BAO = "CANH_BAO"
TRANG_THAI_VUOT_NGUONG = "VUOT_NGUONG"


def validate_warning_thresholds(
    *, warning_threshold: float, absence_limit: float
) -> None:
    """Validate warning and absence limit values."""
    if warning_threshold > absence_limit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="warning_threshold must be less than or equal to absence_limit",
        )


def classify_absence_warning(
    *,
    ty_le_vang: float,
    warning_threshold: float,
    absence_limit: float,
) -> str:
    """Classify absence warning status from absence rate."""
    if ty_le_vang >= absence_limit:
        return TRANG_THAI_VUOT_NGUONG
    if ty_le_vang >= warning_threshold:
        return TRANG_THAI_CANH_BAO
    return TRANG_THAI_AN_TOAN


def get_canh_bao_vang_by_sinh_vien(
    *,
    session: Session,
    ma_sinh_vien: int,
    warning_threshold: float = 15.0,
    absence_limit: float = 20.0,
    include_safe: bool = False,
) -> CanhBaoVangPublic:
    """Lay danh sach mon hoc gan vuot hoac da vuot nguong vang cua sinh vien."""
    validate_warning_thresholds(
        warning_threshold=warning_threshold,
        absence_limit=absence_limit,
    )
    if not get_sinh_vien(session=session, ma_sinh_vien=ma_sinh_vien):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    items: list[CanhBaoVangItem] = []
    for source in get_absence_warning_sources_by_sinh_vien(
        session=session,
        ma_sinh_vien=ma_sinh_vien,
    ):
        ty_le_vang = (
            0.0
            if source.tong_so_buoi_hoc == 0
            else round(source.so_buoi_vang / source.tong_so_buoi_hoc * 100, 2)
        )
        trang_thai = classify_absence_warning(
            ty_le_vang=ty_le_vang,
            warning_threshold=warning_threshold,
            absence_limit=absence_limit,
        )
        if not include_safe and trang_thai == TRANG_THAI_AN_TOAN:
            continue

        items.append(
            CanhBaoVangItem(
                ma_lop_hoc_phan=source.ma_lop_hoc_phan,
                ten_hoc_phan=source.ten_hoc_phan,
                tong_so_buoi_hoc=source.tong_so_buoi_hoc,
                so_buoi_vang=source.so_buoi_vang,
                ty_le_vang=ty_le_vang,
                nguong_canh_bao=absence_limit,
                trang_thai_canh_bao=trang_thai,
            )
        )

    return CanhBaoVangPublic(
        ma_sinh_vien=ma_sinh_vien,
        data=items,
        count=len(items),
    )
