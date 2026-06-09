"""
Khieu nai router.

Defines APIs for staff members to view and process pending attendance complaints.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import (
    KhieuNaiCanXuLyDetail,
    KhieuNaiCanXuLysPublic,
    KhieuNaiChapThuanRequest,
    KhieuNaiXuLyRequest,
    KhieuNaiXuLyResult,
)
from app.services.khieunai_service import (
    chap_thuan_khieu_nai,
    get_khieu_nai_can_xu_ly_detail,
    list_khieu_nai_can_xu_ly,
    tu_choi_khieu_nai,
)

router = APIRouter(prefix="/khieu-nai", tags=["khieu-nai"])


@router.get(
    "/can-bo/{ma_can_bo}/can-xu-ly",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=KhieuNaiCanXuLysPublic,
)
def read_khieu_nai_can_xu_ly(
    session: SessionDep,
    ma_can_bo: Annotated[int, Path(ge=1)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
) -> KhieuNaiCanXuLysPublic:
    """Lay danh sach khieu nai can xu ly cua can bo."""
    return list_khieu_nai_can_xu_ly(
        session=session,
        ma_can_bo=ma_can_bo,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/can-bo/{ma_can_bo}/can-xu-ly/{ma_khieu_nai}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=KhieuNaiCanXuLyDetail,
)
def read_khieu_nai_can_xu_ly_detail(
    session: SessionDep,
    ma_can_bo: Annotated[int, Path(ge=1)],
    ma_khieu_nai: Annotated[int, Path(ge=1)],
) -> KhieuNaiCanXuLyDetail:
    """Lay chi tiet mot khieu nai can xu ly cua can bo."""
    return get_khieu_nai_can_xu_ly_detail(
        session=session,
        ma_can_bo=ma_can_bo,
        ma_khieu_nai=ma_khieu_nai,
    )


@router.patch(
    "/can-bo/{ma_can_bo}/can-xu-ly/{ma_khieu_nai}/chap-thuan",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=KhieuNaiXuLyResult,
)
def approve_khieu_nai(
    session: SessionDep,
    ma_can_bo: Annotated[int, Path(ge=1)],
    ma_khieu_nai: Annotated[int, Path(ge=1)],
    payload: KhieuNaiChapThuanRequest,
) -> KhieuNaiXuLyResult:
    """Chap thuan khieu nai va cap nhat diem danh neu co."""
    return chap_thuan_khieu_nai(
        session=session,
        ma_can_bo=ma_can_bo,
        ma_khieu_nai=ma_khieu_nai,
        payload=payload,
    )


@router.patch(
    "/can-bo/{ma_can_bo}/can-xu-ly/{ma_khieu_nai}/tu-choi",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=KhieuNaiXuLyResult,
)
def reject_khieu_nai(
    session: SessionDep,
    ma_can_bo: Annotated[int, Path(ge=1)],
    ma_khieu_nai: Annotated[int, Path(ge=1)],
    payload: KhieuNaiXuLyRequest,
) -> KhieuNaiXuLyResult:
    """Tu choi khieu nai va ghi nhan thong tin xu ly."""
    return tu_choi_khieu_nai(
        session=session,
        ma_can_bo=ma_can_bo,
        ma_khieu_nai=ma_khieu_nai,
        payload=payload,
    )
