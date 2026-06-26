"""Provide course application services."""

from sqlmodel import Session

from app.crud import hocphan_crud
from app.models import HocPhan, HocPhanCreate, HocPhanUpdate, Message
from app.core.exceptions import CourseNotFoundError


def list_courses(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[HocPhan], int]:
    """Return paginated courses."""
    return hocphan_crud.get_courses(session=session, skip=skip, limit=limit)


def get_course_or_404(*, session: Session, ma_hoc_phan: int) -> HocPhan:
    """Return a course or raise a 404 error."""
    item = hocphan_crud.get_course(session=session, ma_hoc_phan=ma_hoc_phan)
    if not item:
        raise CourseNotFoundError()
    return item


def create_course(*, session: Session, item_in: HocPhanCreate) -> HocPhan:
    """Create a course."""
    return hocphan_crud.create_course(session=session, item_create=item_in)


def update_course(
    *,
    session: Session,
    ma_hoc_phan: int,
    item_in: HocPhanUpdate,
) -> HocPhan:
    """Update a course."""
    item = get_course_or_404(session=session, ma_hoc_phan=ma_hoc_phan)
    return hocphan_crud.update_course(
        session=session,
        db_item=item,
        item_update=item_in,
    )


def delete_course(*, session: Session, ma_hoc_phan: int) -> Message:
    """Delete a course."""
    item = get_course_or_404(session=session, ma_hoc_phan=ma_hoc_phan)
    hocphan_crud.delete_course(session=session, db_item=item)
    return Message(message="Course deleted successfully")
