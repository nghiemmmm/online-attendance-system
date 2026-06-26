"""Provide academic major application services."""

from sqlmodel import Session

from app.crud import nganh_crud
from app.models import Message, Nganh, NganhCreate, NganhUpdate
from app.core.exceptions import MajorNotFoundError


def list_majors(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Nganh], int]:
    """Return paginated academic majors."""
    return nganh_crud.get_majors(session=session, skip=skip, limit=limit)


def get_major_or_404(*, session: Session, ma_nganh: int) -> Nganh:
    """Return an academic major or raise a 404 error."""
    item = nganh_crud.get_major(session=session, ma_nganh=ma_nganh)
    if not item:
        raise MajorNotFoundError()
    return item


def create_major(*, session: Session, item_in: NganhCreate) -> Nganh:
    """Create an academic major."""
    return nganh_crud.create_major(session=session, item_create=item_in)


def update_major(
    *,
    session: Session,
    ma_nganh: int,
    item_in: NganhUpdate,
) -> Nganh:
    """Update an academic major."""
    item = get_major_or_404(session=session, ma_nganh=ma_nganh)
    return nganh_crud.update_major(
        session=session,
        db_item=item,
        item_update=item_in,
    )


def delete_major(*, session: Session, ma_nganh: int) -> Message:
    """Delete an academic major."""
    item = get_major_or_404(session=session, ma_nganh=ma_nganh)
    nganh_crud.delete_major(session=session, db_item=item)
    return Message(message="Major deleted successfully")
