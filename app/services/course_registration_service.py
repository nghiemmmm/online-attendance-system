"""Provide course registration application services."""

from sqlmodel import Session

from app.crud import course_registration_crud
from app.models import (
    CourseRegistration,
    CourseRegistrationCreate,
    CourseRegistrationUpdate,
    Message,
)
from app.core.exceptions import CourseRegistrationNotFoundError


def list_course_registrations(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[CourseRegistration], int]:
    """Return paginated course registrations."""
    return course_registration_crud.get_course_registrations(
        session=session,
        skip=skip,
        limit=limit,
    )


def get_course_registration_or_404(
    *,
    session: Session,
    registration_id: int,
) -> CourseRegistration:
    """Return a course registration or raise a 404 error."""
    item = course_registration_crud.get_course_registration(
        session=session,
        registration_id=registration_id,
    )
    if not item:
        raise CourseRegistrationNotFoundError()
    return item


def create_course_registration(
    *,
    session: Session,
    item_in: CourseRegistrationCreate,
) -> CourseRegistration:
    """Create a course registration."""
    return course_registration_crud.create_course_registration(
        session=session,
        item_create=item_in,
    )


def update_course_registration(
    *,
    session: Session,
    registration_id: int,
    item_in: CourseRegistrationUpdate,
) -> CourseRegistration:
    """Update a course registration."""
    item = get_course_registration_or_404(
        session=session,
        registration_id=registration_id,
    )
    return course_registration_crud.update_course_registration(
        session=session,
        db_item=item,
        item_update=item_in,
    )


def delete_course_registration(*, session: Session, registration_id: int) -> Message:
    """Delete a course registration."""
    item = get_course_registration_or_404(
        session=session,
        registration_id=registration_id,
    )
    course_registration_crud.delete_course_registration(session=session, db_item=item)
    return Message(message="Course registration deleted successfully")
