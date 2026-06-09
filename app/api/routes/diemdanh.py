"""
Diem danh router.

Defines APIs for attendance statistics.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import TongBuoiCoMatHocKyPublic
from app.services.diemdanh_summary_service import get_tong_buoi_co_mat_hoc_ky

router = APIRouter(prefix="/diem-danh", tags=["diem-danh"])


@router.get(
    "/sinh-vien/{ma_sinh_vien}/tong-buoi-co-mat",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=TongBuoiCoMatHocKyPublic,
)
def read_tong_buoi_co_mat_hoc_ky_sinh_vien(
    session: SessionDep,
    ma_sinh_vien: Annotated[int, Path(ge=1)],
    hoc_ky: Annotated[int, Query(ge=1, le=3)],
    nam_hoc: Annotated[str, Query(max_length=20)],
) -> TongBuoiCoMatHocKyPublic:
    """Lay tong so buoi co mat cua sinh vien trong hoc ky."""
    return get_tong_buoi_co_mat_hoc_ky(
        session=session,
        ma_sinh_vien=ma_sinh_vien,
        hoc_ky=hoc_ky,
        nam_hoc=nam_hoc,
    )
