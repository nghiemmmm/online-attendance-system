"""
Lich hoc router.

Defines APIs for student study schedules.
"""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import LichHocHomNayPublic
from app.services.lichhoc_service import get_lich_hoc_hom_nay

router = APIRouter(prefix="/lich-hoc", tags=["lich-hoc"])


@router.get(
    "/sinh-vien/{ma_sinh_vien}/hom-nay",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=LichHocHomNayPublic,
)
def read_lich_hoc_hom_nay_sinh_vien(
    session: SessionDep,
    ma_sinh_vien: Annotated[int, Path(ge=1)],
    target_date: date | None = None,
) -> LichHocHomNayPublic:
    """Lay danh sach buoi hoc trong ngay cua sinh vien."""
    return get_lich_hoc_hom_nay(
        session=session,
        ma_sinh_vien=ma_sinh_vien,
        target_date=target_date or date.today(),
    )
