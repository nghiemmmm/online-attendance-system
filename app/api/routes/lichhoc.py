"""
Lich hoc router.

Defines APIs for student study schedules.
"""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.api.deps import SessionDep, get_current_active_sinhvien, CurrentAccount
from fastapi import APIRouter, Depends, Path, HTTPException
from sqlmodel import select
from app.models import LichHocHomNayPublic, SinhVien
from app.services.lichhoc_service import get_lich_hoc_hom_nay

router = APIRouter(prefix="/lich-hoc", tags=["lich-hoc"])


@router.get(
    "/sinh-vien/{ma_sinh_vien}/hom-nay",
    dependencies=[Depends(get_current_active_sinhvien)],
    response_model=LichHocHomNayPublic,
)
def read_lich_hoc_hom_nay_sinh_vien(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_sinh_vien: Annotated[int, Path(ge=1)],
    target_date: date | None = None,
) -> LichHocHomNayPublic:
    """Lay danh sach buoi hoc trong ngay cua sinh vien."""
    sinh_vien = session.exec(select(SinhVien).where(SinhVien.ma_sinh_vien == ma_sinh_vien)).first()
    if not sinh_vien or sinh_vien.ma_tai_khoan != current_account.ma_tai_khoan:
        raise HTTPException(status_code=403, detail="Not authorized to access this Sinh Vien's data")

    return get_lich_hoc_hom_nay(
        session=session,
        ma_sinh_vien=ma_sinh_vien,
        target_date=target_date or date.today(),
    )
