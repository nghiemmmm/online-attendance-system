"""Define timetable HTTP routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import (
    Message,
    TimetableCreate,
    TimetablePublic,
    TimetablesPublic,
    TimetableUpdate,
)
from app.services import timetable_service

router = APIRouter(prefix="/timetables", tags=["timetables"])


@router.get(
    "/",
    response_model=TimetablesPublic,
    status_code=status.HTTP_200_OK,
    summary="List timetables",
    description="Return paginated timetables.",
)
async def read_timetables(
    session: SessionDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
) -> TimetablesPublic:
    """Return paginated timetables."""
    items, count = timetable_service.list_timetables(
        session=session,
        skip=skip,
        limit=limit,
    )
    return TimetablesPublic(data=items, count=count)


@router.get(
    "/{timetable_id}",
    response_model=TimetablePublic,
    status_code=status.HTTP_200_OK,
    summary="Get a timetable",
    description="Return one timetable by its identifier.",
)
async def read_timetable(
    session: SessionDep,
    timetable_id: Annotated[int, Path(ge=1)],
) -> TimetablePublic:
    """Return one timetable."""
    return timetable_service.get_timetable_or_404(
        session=session,
        timetable_id=timetable_id,
    )


@router.post(
    "/",
    response_model=TimetablePublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create a timetable",
    description="Create a new timetable.",
    dependencies=[Depends(get_current_active_superuser)],
)
async def create_timetable(
    session: SessionDep,
    item_in: TimetableCreate,
) -> TimetablePublic:
    """Create a timetable."""
    return timetable_service.create_timetable(session=session, item_in=item_in)


@router.patch(
    "/{timetable_id}",
    response_model=TimetablePublic,
    status_code=status.HTTP_200_OK,
    summary="Update a timetable",
    description="Update one timetable by its identifier.",
    dependencies=[Depends(get_current_active_superuser)],
)
async def update_timetable(
    session: SessionDep,
    timetable_id: Annotated[int, Path(ge=1)],
    item_in: TimetableUpdate,
) -> TimetablePublic:
    """Update a timetable."""
    return timetable_service.update_timetable(
        session=session,
        timetable_id=timetable_id,
        item_in=item_in,
    )


@router.delete(
    "/{timetable_id}",
    response_model=Message,
    status_code=status.HTTP_200_OK,
    summary="Delete a timetable",
    description="Delete one timetable by its identifier.",
    dependencies=[Depends(get_current_active_superuser)],
)
async def delete_timetable(
    session: SessionDep,
    timetable_id: Annotated[int, Path(ge=1)],
) -> Message:
    """Delete a timetable."""
    return timetable_service.delete_timetable(
        session=session,
        timetable_id=timetable_id,
    )
