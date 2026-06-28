"""Provide academic major application services."""

from sqlmodel import Session

from app.crud import major_crud
from app.models import Message, Major, MajorCreate, MajorUpdate
from app.core.exceptions import MajorNotFoundError


def list_majors(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Major], int]:
    """Return paginated academic majors."""
    return major_crud.get_majors(session=session, skip=skip, limit=limit)


def get_major_or_404(*, session: Session, major_id: int) -> Major:
    """Return an academic major or raise a 404 error."""
    item = major_crud.get_major(session=session, major_id=major_id)
    if not item:
        raise MajorNotFoundError()
    return item


def create_major(*, session: Session, item_in: MajorCreate) -> Major:
    """Create an academic major."""
    return major_crud.create_major(session=session, item_create=item_in)


def update_major(
    *,
    session: Session,
    major_id: int,
    item_in: MajorUpdate,
) -> Major:
    """Update an academic major."""
    item = get_major_or_404(session=session, major_id=major_id)
    return major_crud.update_major(
        session=session,
        db_item=item,
        item_update=item_in,
    )


def delete_major(*, session: Session, major_id: int) -> Message:
    """Delete an academic major."""
    item = get_major_or_404(session=session, major_id=major_id)
    major_crud.delete_major(session=session, db_item=item)
    return Message(message="Major deleted successfully")
