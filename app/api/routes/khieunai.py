"""
Khieu nai router.

Defines APIs for staff members to view and process pending attendance complaints.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, HTTPException, Request, status

from app.api.deps import SessionDep, get_current_active_superuser, CurrentAccount, get_current_active_student, get_current_active_lecturer
from app.models import (
    KhieuNaiCreate,
    KhieuNaiPublic,
    KhieuNaisPublic,
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
    create_appeal,
    list_my_appeals,
)
from app.services.staff_service import ensure_staff_owns_profile
from app.services.audit_log_service import write_audit_log

router = APIRouter(prefix="/khieu-nai", tags=["khieu-nai"])

@router.post(
    "",
    dependencies=[Depends(get_current_active_student)],
    response_model=KhieuNaiPublic,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Lỗi quá hạn 48 giờ để khiếu nại hoặc đã tồn tại khiếu nại cho bản ghi điểm danh này"
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Tài khoản không phải sinh viên hoặc gửi khiếu nại hộ sinh viên khác"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Bản ghi điểm danh hoặc buổi học không tồn tại"
        }
    }
)
def create_khieu_nai(
    request: Request,
    session: SessionDep,
    payload: KhieuNaiCreate,
    current_account: CurrentAccount,
) -> KhieuNaiPublic:
    db_khieu_nai = create_appeal(
        session=session,
        payload=payload,
        current_account=current_account,
    )
    write_audit_log(
        session=session,
        account=current_account,
        hanh_dong="GUI_KHIEU_NAI",
        doi_tuong="KhieuNai",
        doi_tuong_id=db_khieu_nai.ma_khieu_nai,
        du_lieu_sau=db_khieu_nai.model_dump(mode="json"),
        request=request,
    )
    return db_khieu_nai


@router.get(
    "",
    dependencies=[Depends(get_current_active_student)],
    response_model=KhieuNaisPublic,
)
def read_my_khieu_nai(
    session: SessionDep,
    current_account: CurrentAccount,
    skip: int = 0,
    limit: int = 100,
) -> KhieuNaisPublic:
    return list_my_appeals(
        session=session,
        current_account=current_account,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/can-bo/{ma_can_bo}/can-xu-ly",
    dependencies=[Depends(get_current_active_lecturer)],
    response_model=KhieuNaiCanXuLysPublic,
)
def read_khieu_nai_can_xu_ly(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_can_bo: Annotated[int, Path(ge=1)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
) -> KhieuNaiCanXuLysPublic:
    """Lay danh sach khieu nai can xu ly cua can bo."""
    ensure_staff_owns_profile(
        session=session,
        ma_can_bo=ma_can_bo,
        ma_tai_khoan=current_account.ma_tai_khoan,
    )

    return list_khieu_nai_can_xu_ly(
        session=session,
        ma_can_bo=ma_can_bo,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/can-bo/{ma_can_bo}/can-xu-ly/{ma_khieu_nai}",
    dependencies=[Depends(get_current_active_lecturer)],
    response_model=KhieuNaiCanXuLyDetail,
)
def read_khieu_nai_can_xu_ly_detail(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_can_bo: Annotated[int, Path(ge=1)],
    ma_khieu_nai: Annotated[int, Path(ge=1)],
) -> KhieuNaiCanXuLyDetail:
    """Lay chi tiet mot khieu nai can xu ly cua can bo."""
    ensure_staff_owns_profile(
        session=session,
        ma_can_bo=ma_can_bo,
        ma_tai_khoan=current_account.ma_tai_khoan,
    )

    return get_khieu_nai_can_xu_ly_detail(
        session=session,
        ma_can_bo=ma_can_bo,
        ma_khieu_nai=ma_khieu_nai,
    )


@router.patch(
    "/can-bo/{ma_can_bo}/can-xu-ly/{ma_khieu_nai}/chap-thuan",
    dependencies=[Depends(get_current_active_lecturer)],
    response_model=KhieuNaiXuLyResult,
)
def approve_khieu_nai(
    request: Request,
    session: SessionDep,
    current_account: CurrentAccount,
    ma_can_bo: Annotated[int, Path(ge=1)],
    ma_khieu_nai: Annotated[int, Path(ge=1)],
    payload: KhieuNaiChapThuanRequest,
) -> KhieuNaiXuLyResult:
    """Chap thuan khieu nai va cap nhat diem danh neu co."""
    ensure_staff_owns_profile(
        session=session,
        ma_can_bo=ma_can_bo,
        ma_tai_khoan=current_account.ma_tai_khoan,
    )
    result = chap_thuan_khieu_nai(
        session=session,
        ma_can_bo=ma_can_bo,
        ma_khieu_nai=ma_khieu_nai,
        payload=payload,
    )
    write_audit_log(
        session=session,
        account=current_account,
        hanh_dong="DUYET_KHIEU_NAI",
        doi_tuong="KhieuNai",
        doi_tuong_id=ma_khieu_nai,
        du_lieu_sau=result.model_dump(mode="json") if hasattr(result, "model_dump") else None,
        request=request,
    )
    return result


@router.patch(
    "/can-bo/{ma_can_bo}/can-xu-ly/{ma_khieu_nai}/tu-choi",
    dependencies=[Depends(get_current_active_lecturer)],
    response_model=KhieuNaiXuLyResult,
)
def reject_khieu_nai(
    request: Request,
    session: SessionDep,
    current_account: CurrentAccount,
    ma_can_bo: Annotated[int, Path(ge=1)],
    ma_khieu_nai: Annotated[int, Path(ge=1)],
    payload: KhieuNaiXuLyRequest,
) -> KhieuNaiXuLyResult:
    """Tu choi khieu nai va ghi nhan thong tin xu ly."""
    ensure_staff_owns_profile(
        session=session,
        ma_can_bo=ma_can_bo,
        ma_tai_khoan=current_account.ma_tai_khoan,
    )

    result = tu_choi_khieu_nai(
        session=session,
        ma_can_bo=ma_can_bo,
        ma_khieu_nai=ma_khieu_nai,
        payload=payload,
    )
    write_audit_log(
        session=session,
        account=current_account,
        hanh_dong="TU_CHOI_KHIEU_NAI",
        doi_tuong="KhieuNai",
        doi_tuong_id=ma_khieu_nai,
        du_lieu_sau=result.model_dump(mode="json") if hasattr(result, "model_dump") else None,
        request=request,
    )
    return result
