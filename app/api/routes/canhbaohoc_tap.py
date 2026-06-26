"""
Canh bao hoc tap router.

Defines APIs for student academic warnings.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import CanhBaoVangPublic
from app.services.canhbaohoc_tap_service import get_absence_warnings_by_student

router = APIRouter(prefix="/canh-bao-hoc-tap", tags=["canh-bao-hoc-tap"])


@router.get(
    "/sinh-vien/{ma_sinh_vien}/vang",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=CanhBaoVangPublic,
)
def read_student_absence_warnings(
    session: SessionDep,
    ma_sinh_vien: Annotated[int, Path(ge=1)],
    warning_threshold: Annotated[float, Query(ge=0, le=100)] = 15.0,
    absence_limit: Annotated[float, Query(ge=0, le=100)] = 20.0,
    include_safe: bool = False,
) -> CanhBaoVangPublic:
    """Lay danh sach mon hoc gan vuot hoac da vuot nguong vang cua sinh vien."""
    return get_absence_warnings_by_student(
        session=session,
        ma_sinh_vien=ma_sinh_vien,
        warning_threshold=warning_threshold,
        absence_limit=absence_limit,
        include_safe=include_safe,
    )
