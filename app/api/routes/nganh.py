"""Define academic major HTTP routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import Message, NganhCreate, NganhPublic, NganhsPublic, NganhUpdate
from app.services import major_service

router = APIRouter(prefix="/nganh", tags=["nganh"])


@router.get(
    "/",
    response_model=NganhsPublic,
    status_code=status.HTTP_200_OK,
    summary="List majors",
    description="Return paginated academic majors.",
)
async def read_majors(
    session: SessionDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
) -> NganhsPublic:
    """Return paginated academic majors."""
    items, count = major_service.list_majors(
        session=session,
        skip=skip,
        limit=limit,
    )
    return NganhsPublic(data=items, count=count)


@router.get(
    "/{ma_nganh}",
    response_model=NganhPublic,
    status_code=status.HTTP_200_OK,
    summary="Get a major",
    description="Return one academic major by its identifier.",
)
async def read_major(
    session: SessionDep,
    ma_nganh: Annotated[int, Path(ge=1)],
) -> NganhPublic:
    """Return one academic major."""
    return major_service.get_major_or_404(session=session, ma_nganh=ma_nganh)


@router.post(
    "/",
    response_model=NganhPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create a major",
    description="Create a new academic major.",
    dependencies=[Depends(get_current_active_superuser)],
)
async def create_major(
    session: SessionDep,
    item_in: NganhCreate,
) -> NganhPublic:
    """Create an academic major."""
    return major_service.create_major(session=session, item_in=item_in)


@router.patch(
    "/{ma_nganh}",
    response_model=NganhPublic,
    status_code=status.HTTP_200_OK,
    summary="Update a major",
    description="Update one academic major by its identifier.",
    dependencies=[Depends(get_current_active_superuser)],
)
async def update_major(
    session: SessionDep,
    ma_nganh: Annotated[int, Path(ge=1)],
    item_in: NganhUpdate,
) -> NganhPublic:
    """Update an academic major."""
    return major_service.update_major(
        session=session,
        ma_nganh=ma_nganh,
        item_in=item_in,
    )


@router.delete(
    "/{ma_nganh}",
    response_model=Message,
    status_code=status.HTTP_200_OK,
    summary="Delete a major",
    description="Delete one academic major by its identifier.",
    dependencies=[Depends(get_current_active_superuser)],
)
async def delete_major(
    session: SessionDep,
    ma_nganh: Annotated[int, Path(ge=1)],
) -> Message:
    """Delete an academic major."""
    return major_service.delete_major(session=session, ma_nganh=ma_nganh)
