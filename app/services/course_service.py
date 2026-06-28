"""Provide course application services."""

from sqlmodel import Session

from app.crud import course_crud
from app.models import Course, CourseCreate, CourseUpdate, Message
from app.core.exceptions import CourseNotFoundError


def list_courses(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Course], int]:
    """Return paginated courses."""
    return course_crud.get_courses(session=session, skip=skip, limit=limit)


def get_course_or_404(*, session: Session, course_id: int) -> Course:
    """Return a course or raise a 404 error."""
    item = course_crud.get_course(session=session, course_id=course_id)
    if not item:
        raise CourseNotFoundError()
    return item


def create_course(*, session: Session, item_in: CourseCreate) -> Course:
    """Create a course."""
    return course_crud.create_course(session=session, item_create=item_in)


def update_course(
    *,
    session: Session,
    course_id: int,
    item_in: CourseUpdate,
) -> Course:
    """Update a course."""
    item = get_course_or_404(session=session, course_id=course_id)
    return course_crud.update_course(
        session=session,
        db_item=item,
        item_update=item_in,
    )


def delete_course(*, session: Session, course_id: int) -> Message:
    """Delete a course."""
    item = get_course_or_404(session=session, course_id=course_id)
    course_crud.delete_course(session=session, db_item=item)
    return Message(message="Course deleted successfully")
