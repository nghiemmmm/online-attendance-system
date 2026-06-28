"""Provide CRUD operations for academic majors."""

from sqlmodel import Session, func, select

from app.models import Major, MajorCreate, MajorUpdate


def get_major(*, session: Session, major_id: int) -> Major | None:
    """Return an academic major by ID."""
    return session.get(Major, major_id)


def get_majors(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Major], int]:
    """Return paginated academic majors and their total count."""
    count_statement = select(func.count()).select_from(Major)
    count = session.exec(count_statement).one()
    statement = select(Major).offset(skip).limit(limit)
    items = session.exec(statement).all()
    return list(items), count


def create_major(*, session: Session, item_create: MajorCreate) -> Major:
    """Create an academic major."""
    db_item = Major.model_validate(item_create)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def update_major(
    *,
    session: Session,
    db_item: Major,
    item_update: MajorUpdate,
) -> Major:
    """Update an academic major."""
    item_data = item_update.model_dump(exclude_unset=True)
    for field, value in item_data.items():
        setattr(db_item, field, value)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def delete_major(*, session: Session, db_item: Major) -> None:
    """Delete an academic major."""
    session.delete(db_item)
    session.commit()
