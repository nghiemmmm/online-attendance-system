"""Provide CRUD operations for courses."""

from sqlmodel import Session, func, select

from app.models import HocPhan, HocPhanCreate, HocPhanUpdate


def get_course(*, session: Session, ma_hoc_phan: int) -> HocPhan | None:
    """Return a course by ID."""
    return session.get(HocPhan, ma_hoc_phan)


def get_courses(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[HocPhan], int]:
    """Return paginated courses and their total count."""
    count_statement = select(func.count()).select_from(HocPhan)
    count = session.exec(count_statement).one()
    statement = select(HocPhan).offset(skip).limit(limit)
    items = session.exec(statement).all()
    return list(items), count


def create_course(*, session: Session, item_create: HocPhanCreate) -> HocPhan:
    """Create a course."""
    db_item = HocPhan.model_validate(item_create)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def update_course(
    *,
    session: Session,
    db_item: HocPhan,
    item_update: HocPhanUpdate,
) -> HocPhan:
    """Update a course."""
    item_data = item_update.model_dump(exclude_unset=True)
    for field, value in item_data.items():
        setattr(db_item, field, value)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def delete_course(*, session: Session, db_item: HocPhan) -> None:
    """Delete a course."""
    session.delete(db_item)
    session.commit()
