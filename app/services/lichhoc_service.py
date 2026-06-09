"""
Lich hoc service.

Contains business logic for student study schedules.
"""

from datetime import date

from fastapi import HTTPException, status
from sqlmodel import Session

from app.crud.lichhoc_crud import get_lich_hoc_hom_nay_by_sinh_vien
from app.crud.sinhvien_crud import get_sinh_vien
from app.models import LichHocHomNayPublic


def get_lich_hoc_hom_nay(
    *,
    session: Session,
    ma_sinh_vien: int,
    target_date: date,
) -> LichHocHomNayPublic:
    """Lay lich hoc trong ngay cua sinh vien."""
    if not get_sinh_vien(session=session, ma_sinh_vien=ma_sinh_vien):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    items, count = get_lich_hoc_hom_nay_by_sinh_vien(
        session=session,
        ma_sinh_vien=ma_sinh_vien,
        target_date=target_date,
    )
    return LichHocHomNayPublic(
        ma_sinh_vien=ma_sinh_vien,
        ngay_hoc=target_date,
        data=items,
        count=count,
    )
