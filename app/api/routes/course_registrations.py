"""Define course registration HTTP routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import (
    CourseRegistrationCreate,
    CourseRegistrationPublic,
    CourseRegistrationsPublic,
    CourseRegistrationUpdate,
    Message,
)
from app.services import course_registration_service

router = APIRouter(prefix="/course-registrations", tags=["course-registrations"])


@router.get(
    "/",
    response_model=CourseRegistrationsPublic,
    status_code=status.HTTP_200_OK,
    summary="List course registrations",
    description="Return paginated course registrations.",
)
async def read_course_registrations(
    session: SessionDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
) -> CourseRegistrationsPublic:
    """Return paginated course registrations."""
    items, count = course_registration_service.list_course_registrations(
        session=session,
        skip=skip,
        limit=limit,
    )
    return CourseRegistrationsPublic(data=items, count=count)


@router.get(
    "/{registration_id}",
    response_model=CourseRegistrationPublic,
    status_code=status.HTTP_200_OK,
    summary="Get a course registration",
    description="Return one course registration by its identifier.",
)
async def read_course_registration(
    session: SessionDep,
    registration_id: Annotated[int, Path(ge=1)],
) -> CourseRegistrationPublic:
    """Return one course registration."""
    return course_registration_service.get_course_registration_or_404(
        session=session,
        registration_id=registration_id,
    )


@router.post(
    "/",
    response_model=CourseRegistrationPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create a course registration",
    description="Create a new course registration.",
    dependencies=[Depends(get_current_active_superuser)],
)
async def create_course_registration(
    session: SessionDep,
    item_in: CourseRegistrationCreate,
) -> CourseRegistrationPublic:
    """Create a course registration."""
    return course_registration_service.create_course_registration(
        session=session,
        item_in=item_in,
    )


@router.patch(
    "/{registration_id}",
    response_model=CourseRegistrationPublic,
    status_code=status.HTTP_200_OK,
    summary="Update a course registration",
    description="Update one course registration by its identifier.",
    dependencies=[Depends(get_current_active_superuser)],
)
async def update_course_registration(
    session: SessionDep,
    registration_id: Annotated[int, Path(ge=1)],
    item_in: CourseRegistrationUpdate,
) -> CourseRegistrationPublic:
    """Update a course registration."""
    return course_registration_service.update_course_registration(
        session=session,
        registration_id=registration_id,
        item_in=item_in,
    )


@router.delete(
    "/{registration_id}",
    response_model=Message,
    status_code=status.HTTP_200_OK,
    summary="Delete a course registration",
    description="Delete one course registration by its identifier.",
    dependencies=[Depends(get_current_active_superuser)],
)
async def delete_course_registration(
    session: SessionDep,
    registration_id: Annotated[int, Path(ge=1)],
) -> Message:
    """Delete a course registration."""
    return course_registration_service.delete_course_registration(
        session=session,
        registration_id=registration_id,
    )
