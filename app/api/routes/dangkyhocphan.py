"""Define course registration HTTP routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import (
    DangKyHocPhanCreate,
    DangKyHocPhanPublic,
    DangKyHocPhansPublic,
    DangKyHocPhanUpdate,
    Message,
)
from app.services import course_registration_service

router = APIRouter(prefix="/dangkyhocphan", tags=["dangkyhocphan"])


@router.get(
    "/",
    response_model=DangKyHocPhansPublic,
    status_code=status.HTTP_200_OK,
    summary="List course registrations",
    description="Return paginated course registrations.",
)
async def read_course_registrations(
    session: SessionDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
) -> DangKyHocPhansPublic:
    """Return paginated course registrations."""
    items, count = course_registration_service.list_course_registrations(
        session=session,
        skip=skip,
        limit=limit,
    )
    return DangKyHocPhansPublic(data=items, count=count)


@router.get(
    "/{ma_dang_ky}",
    response_model=DangKyHocPhanPublic,
    status_code=status.HTTP_200_OK,
    summary="Get a course registration",
    description="Return one course registration by its identifier.",
)
async def read_course_registration(
    session: SessionDep,
    ma_dang_ky: Annotated[int, Path(ge=1)],
) -> DangKyHocPhanPublic:
    """Return one course registration."""
    return course_registration_service.get_course_registration_or_404(
        session=session,
        ma_dang_ky=ma_dang_ky,
    )


@router.post(
    "/",
    response_model=DangKyHocPhanPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create a course registration",
    description="Create a new course registration.",
    dependencies=[Depends(get_current_active_superuser)],
)
async def create_course_registration(
    session: SessionDep,
    item_in: DangKyHocPhanCreate,
) -> DangKyHocPhanPublic:
    """Create a course registration."""
    return course_registration_service.create_course_registration(
        session=session,
        item_in=item_in,
    )


@router.patch(
    "/{ma_dang_ky}",
    response_model=DangKyHocPhanPublic,
    status_code=status.HTTP_200_OK,
    summary="Update a course registration",
    description="Update one course registration by its identifier.",
    dependencies=[Depends(get_current_active_superuser)],
)
async def update_course_registration(
    session: SessionDep,
    ma_dang_ky: Annotated[int, Path(ge=1)],
    item_in: DangKyHocPhanUpdate,
) -> DangKyHocPhanPublic:
    """Update a course registration."""
    return course_registration_service.update_course_registration(
        session=session,
        ma_dang_ky=ma_dang_ky,
        item_in=item_in,
    )


@router.delete(
    "/{ma_dang_ky}",
    response_model=Message,
    status_code=status.HTTP_200_OK,
    summary="Delete a course registration",
    description="Delete one course registration by its identifier.",
    dependencies=[Depends(get_current_active_superuser)],
)
async def delete_course_registration(
    session: SessionDep,
    ma_dang_ky: Annotated[int, Path(ge=1)],
) -> Message:
    """Delete a course registration."""
    return course_registration_service.delete_course_registration(
        session=session,
        ma_dang_ky=ma_dang_ky,
    )
