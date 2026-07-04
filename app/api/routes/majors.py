"""Define academic major HTTP routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import MajorCreate, MajorPublic, MajorsPublic, MajorUpdate, Message
from app.services import major_service

router = APIRouter(prefix="/majors", tags=["majors"])


@router.get(
    "/",
    response_model=MajorsPublic,
    status_code=status.HTTP_200_OK,
    summary="List majors",
    description="Return paginated academic majors.",
)
async def read_majors(
    session: SessionDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
) -> MajorsPublic:
    """Return paginated academic majors."""
    items, count = major_service.list_majors(
        session=session,
        skip=skip,
        limit=limit,
    )
    return MajorsPublic(data=items, count=count)


@router.get(
    "/{major_id}",
    response_model=MajorPublic,
    status_code=status.HTTP_200_OK,
    summary="Get a major",
    description="Return one academic major by its identifier.",
)
async def read_major(
    session: SessionDep,
    major_id: Annotated[int, Path(ge=1)],
) -> MajorPublic:
    """Return one academic major."""
    return major_service.get_major_or_404(session=session, major_id=major_id)


@router.post(
    "/",
    response_model=MajorPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create a major",
    description="Create a new academic major.",
    dependencies=[Depends(get_current_active_superuser)],
)
async def create_major(
    session: SessionDep,
    item_in: MajorCreate,
) -> MajorPublic:
    """Create an academic major."""
    return major_service.create_major(session=session, item_in=item_in)


@router.patch(
    "/{major_id}",
    response_model=MajorPublic,
    status_code=status.HTTP_200_OK,
    summary="Update a major",
    description="Update one academic major by its identifier.",
    dependencies=[Depends(get_current_active_superuser)],
)
async def update_major(
    session: SessionDep,
    major_id: Annotated[int, Path(ge=1)],
    item_in: MajorUpdate,
) -> MajorPublic:
    """Update an academic major."""
    return major_service.update_major(
        session=session,
        major_id=major_id,
        item_in=item_in,
    )


@router.delete(
    "/{major_id}",
    response_model=Message,
    status_code=status.HTTP_200_OK,
    summary="Delete a major",
    description="Delete one academic major by its identifier.",
    dependencies=[Depends(get_current_active_superuser)],
)
async def delete_major(
    session: SessionDep,
    major_id: Annotated[int, Path(ge=1)],
) -> Message:
    """Delete an academic major."""
    return major_service.delete_major(session=session, major_id=major_id)
