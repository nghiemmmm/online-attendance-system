"""
Khieu nai router.

Defines APIs for staff members to view and process pending attendance complaints.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, HTTPException, Request, status
from pydantic import Field

from app.api.deps import SessionDep, get_current_active_superuser, CurrentAccount, get_current_active_student, get_current_active_lecturer
from app.models import (
    AppealCreate,
    AppealPublic,
    AppealsPublic,
    PendingAppealDetail,
    PendingAppealsPublic,
    AppealApprovalRequest,
    AppealResolutionRequest,
    AppealResolutionResult,
)
from app.services.appeal_service import (
    approve_appeal,
    get_actionable_appeal_detail,
    list_actionable_appeals,
    reject_appeal,
    create_appeal,
    list_my_appeals,
)
from app.services.staff_service import ensure_staff_owns_profile
from app.services.audit_log_service import write_audit_log
from app.models.base import AppBaseModel

router = APIRouter(prefix="/appeals", tags=["appeals"])


class AppealReviewRequest(AppBaseModel):
    """Represent staff review data for a complaint resource."""

    status: str = Field(min_length=1, max_length=30)
    resolution_note: str | None = Field(default=None, max_length=255)
    new_attendance_status: str | None = Field(default=None, max_length=30)

@router.post(
    "",
    dependencies=[Depends(get_current_active_student)],
    response_model=AppealPublic,
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
def create_appeal_route(
    request: Request,
    session: SessionDep,
    payload: AppealCreate,
    current_account: CurrentAccount,
) -> AppealPublic:
    db_appeal = create_appeal(
        session=session,
        payload=payload,
        current_account=current_account,
    )
    write_audit_log(
        session=session,
        account=current_account,
        action="GUI_KHIEU_NAI",
        target_type="Appeal",
        target_id=db_appeal.appeal_id,
        after_data=db_appeal.model_dump(mode="json"),
        request=request,
    )
    return db_appeal


@router.get(
    "",
    dependencies=[Depends(get_current_active_student)],
    response_model=AppealsPublic,
)
def read_my_appeals(
    session: SessionDep,
    current_account: CurrentAccount,
    skip: int = 0,
    limit: int = 100,
) -> AppealsPublic:
    return list_my_appeals(
        session=session,
        current_account=current_account,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/staff/{staff_id}",
    dependencies=[Depends(get_current_active_lecturer)],
    response_model=PendingAppealsPublic,
)
def read_actionable_appeals(
    session: SessionDep,
    current_account: CurrentAccount,
    staff_id: Annotated[int, Path(ge=1)],
    status_filter: Annotated[str, Query(alias="status", max_length=30)] = "pending",
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
) -> PendingAppealsPublic:
    """Lay danh sach khieu nai can xu ly cua can bo."""
    ensure_staff_owns_profile(
        session=session,
        staff_id=staff_id,
        account_id=current_account.account_id,
    )

    if status_filter not in {"pending", "CHO_XU_LY"}:
        raise HTTPException(status_code=400, detail="Only pending appeals are actionable")

    return list_actionable_appeals(
        session=session,
        staff_id=staff_id,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{appeal_id}",
    dependencies=[Depends(get_current_active_lecturer)],
    response_model=PendingAppealDetail,
)
def read_actionable_appeal_detail(
    session: SessionDep,
    current_account: CurrentAccount,
    appeal_id: Annotated[int, Path(ge=1)],
    staff_id: Annotated[int, Query(ge=1)],
) -> PendingAppealDetail:
    """Lay chi tiet mot khieu nai can xu ly cua can bo."""
    ensure_staff_owns_profile(
        session=session,
        staff_id=staff_id,
        account_id=current_account.account_id,
    )

    return get_actionable_appeal_detail(
        session=session,
        staff_id=staff_id,
        appeal_id=appeal_id,
    )


@router.patch(
    "/{appeal_id}",
    dependencies=[Depends(get_current_active_lecturer)],
    response_model=AppealResolutionResult,
)
def review_appeal_route(
    request: Request,
    session: SessionDep,
    current_account: CurrentAccount,
    appeal_id: Annotated[int, Path(ge=1)],
    staff_id: Annotated[int, Query(ge=1)],
    payload: AppealReviewRequest,
) -> AppealResolutionResult:
    """Update complaint review status and attendance if needed."""
    ensure_staff_owns_profile(
        session=session,
        staff_id=staff_id,
        account_id=current_account.account_id,
    )
    normalized_status = payload.status.strip().lower()
    if normalized_status in {"approved", "da_duyet", "da-duyet"}:
        result = approve_appeal(
            session=session,
            staff_id=staff_id,
            appeal_id=appeal_id,
            payload=AppealApprovalRequest(
                resolution_note=payload.resolution_note,
                new_attendance_status=payload.new_attendance_status,
            ),
        )
        audit_action = "DUYET_KHIEU_NAI"
    elif normalized_status in {"rejected", "tu_choi", "tu-choi"}:
        result = reject_appeal(
            session=session,
            staff_id=staff_id,
            appeal_id=appeal_id,
            payload=AppealResolutionRequest(
                resolution_note=payload.resolution_note,
            ),
        )
        audit_action = "TU_CHOI_KHIEU_NAI"
    else:
        raise HTTPException(status_code=400, detail="Unsupported appeal status")

    write_audit_log(
        session=session,
        account=current_account,
        action=audit_action,
        target_type="Appeal",
        target_id=appeal_id,
        after_data=result.model_dump(mode="json") if hasattr(result, "model_dump") else None,
        request=request,
    )
    return result
