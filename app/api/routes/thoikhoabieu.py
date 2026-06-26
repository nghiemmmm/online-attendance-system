"""Define timetable HTTP routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import (
    Message,
    ThoiKhoaBieuCreate,
    ThoiKhoaBieuPublic,
    ThoiKhoaBieusPublic,
    ThoiKhoaBieuUpdate,
)
from app.services import timetable_service

router = APIRouter(prefix="/thoikhoabieu", tags=["thoikhoabieu"])


@router.get(
    "/",
    response_model=ThoiKhoaBieusPublic,
    status_code=status.HTTP_200_OK,
    summary="List timetables",
    description="Return paginated timetables.",
)
async def read_timetables(
    session: SessionDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
) -> ThoiKhoaBieusPublic:
    """Return paginated timetables."""
    items, count = timetable_service.list_timetables(
        session=session,
        skip=skip,
        limit=limit,
    )
    return ThoiKhoaBieusPublic(data=items, count=count)


@router.get(
    "/{ma_thoi_khoa_bieu}",
    response_model=ThoiKhoaBieuPublic,
    status_code=status.HTTP_200_OK,
    summary="Get a timetable",
    description="Return one timetable by its identifier.",
)
async def read_timetable(
    session: SessionDep,
    ma_thoi_khoa_bieu: Annotated[int, Path(ge=1)],
) -> ThoiKhoaBieuPublic:
    """Return one timetable."""
    return timetable_service.get_timetable_or_404(
        session=session,
        ma_thoi_khoa_bieu=ma_thoi_khoa_bieu,
    )


@router.post(
    "/",
    response_model=ThoiKhoaBieuPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create a timetable",
    description="Create a new timetable.",
    dependencies=[Depends(get_current_active_superuser)],
)
async def create_timetable(
    session: SessionDep,
    item_in: ThoiKhoaBieuCreate,
) -> ThoiKhoaBieuPublic:
    """Create a timetable."""
    return timetable_service.create_timetable(session=session, item_in=item_in)


@router.patch(
    "/{ma_thoi_khoa_bieu}",
    response_model=ThoiKhoaBieuPublic,
    status_code=status.HTTP_200_OK,
    summary="Update a timetable",
    description="Update one timetable by its identifier.",
    dependencies=[Depends(get_current_active_superuser)],
)
async def update_timetable(
    session: SessionDep,
    ma_thoi_khoa_bieu: Annotated[int, Path(ge=1)],
    item_in: ThoiKhoaBieuUpdate,
) -> ThoiKhoaBieuPublic:
    """Update a timetable."""
    return timetable_service.update_timetable(
        session=session,
        ma_thoi_khoa_bieu=ma_thoi_khoa_bieu,
        item_in=item_in,
    )


@router.delete(
    "/{ma_thoi_khoa_bieu}",
    response_model=Message,
    status_code=status.HTTP_200_OK,
    summary="Delete a timetable",
    description="Delete one timetable by its identifier.",
    dependencies=[Depends(get_current_active_superuser)],
)
async def delete_timetable(
    session: SessionDep,
    ma_thoi_khoa_bieu: Annotated[int, Path(ge=1)],
) -> Message:
    """Delete a timetable."""
    return timetable_service.delete_timetable(
        session=session,
        ma_thoi_khoa_bieu=ma_thoi_khoa_bieu,
    )
