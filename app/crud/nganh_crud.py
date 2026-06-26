"""Provide CRUD operations for academic majors."""

from sqlmodel import Session, func, select

from app.models import Nganh, NganhCreate, NganhUpdate


def get_major(*, session: Session, ma_nganh: int) -> Nganh | None:
    """Return an academic major by ID."""
    return session.get(Nganh, ma_nganh)


def get_majors(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Nganh], int]:
    """Return paginated academic majors and their total count."""
    count_statement = select(func.count()).select_from(Nganh)
    count = session.exec(count_statement).one()
    statement = select(Nganh).offset(skip).limit(limit)
    items = session.exec(statement).all()
    return list(items), count


def create_major(*, session: Session, item_create: NganhCreate) -> Nganh:
    """Create an academic major."""
    db_item = Nganh.model_validate(item_create)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def update_major(
    *,
    session: Session,
    db_item: Nganh,
    item_update: NganhUpdate,
) -> Nganh:
    """Update an academic major."""
    item_data = item_update.model_dump(exclude_unset=True)
    for field, value in item_data.items():
        setattr(db_item, field, value)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def delete_major(*, session: Session, db_item: Nganh) -> None:
    """Delete an academic major."""
    session.delete(db_item)
    session.commit()
