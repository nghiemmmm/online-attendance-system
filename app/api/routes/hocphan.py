"""Define course HTTP routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import (
    HocPhanCreate,
    HocPhanPublic,
    HocPhansPublic,
    HocPhanUpdate,
    Message,
)
from app.services import course_service

router = APIRouter(prefix="/hocphan", tags=["hocphan"])


@router.get(
    "/",
    response_model=HocPhansPublic,
    status_code=status.HTTP_200_OK,
    summary="List courses",
    description="Return paginated courses.",
)
async def read_courses(
    session: SessionDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
) -> HocPhansPublic:
    """Return paginated courses."""
    items, count = course_service.list_courses(
        session=session,
        skip=skip,
        limit=limit,
    )
    return HocPhansPublic(data=items, count=count)


@router.get(
    "/{ma_hoc_phan}",
    response_model=HocPhanPublic,
    status_code=status.HTTP_200_OK,
    summary="Get a course",
    description="Return one course by its identifier.",
)
async def read_course(
    session: SessionDep,
    ma_hoc_phan: Annotated[int, Path(ge=1)],
) -> HocPhanPublic:
    """Return one course."""
    return course_service.get_course_or_404(
        session=session,
        ma_hoc_phan=ma_hoc_phan,
    )


@router.post(
    "/",
    response_model=HocPhanPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create a course",
    description="Create a new course.",
    dependencies=[Depends(get_current_active_superuser)],
)
async def create_course(
    session: SessionDep,
    item_in: HocPhanCreate,
) -> HocPhanPublic:
    """Create a course."""
    return course_service.create_course(session=session, item_in=item_in)


@router.patch(
    "/{ma_hoc_phan}",
    response_model=HocPhanPublic,
    status_code=status.HTTP_200_OK,
    summary="Update a course",
    description="Update one course by its identifier.",
    dependencies=[Depends(get_current_active_superuser)],
)
async def update_course(
    session: SessionDep,
    ma_hoc_phan: Annotated[int, Path(ge=1)],
    item_in: HocPhanUpdate,
) -> HocPhanPublic:
    """Update a course."""
    return course_service.update_course(
        session=session,
        ma_hoc_phan=ma_hoc_phan,
        item_in=item_in,
    )


@router.delete(
    "/{ma_hoc_phan}",
    response_model=Message,
    status_code=status.HTTP_200_OK,
    summary="Delete a course",
    description="Delete one course by its identifier.",
    dependencies=[Depends(get_current_active_superuser)],
)
async def delete_course(
    session: SessionDep,
    ma_hoc_phan: Annotated[int, Path(ge=1)],
) -> Message:
    """Delete a course."""
    return course_service.delete_course(session=session, ma_hoc_phan=ma_hoc_phan)
