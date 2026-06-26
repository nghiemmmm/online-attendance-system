"""Provide CRUD operations for class registrations."""

from sqlmodel import Session, func, select

from app.models import DangKyHocPhan, DangKyHocPhanCreate, DangKyHocPhanUpdate


def get_course_registration(
    *,
    session: Session,
    ma_dang_ky: int,
) -> DangKyHocPhan | None:
    """Return a class registration by ID."""
    return session.get(DangKyHocPhan, ma_dang_ky)


def get_course_registrations(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[DangKyHocPhan], int]:
    """Return paginated class registrations and their total count."""
    count_statement = select(func.count()).select_from(DangKyHocPhan)
    count = session.exec(count_statement).one()
    statement = select(DangKyHocPhan).offset(skip).limit(limit)
    items = session.exec(statement).all()
    return list(items), count


def create_course_registration(
    *,
    session: Session,
    item_create: DangKyHocPhanCreate,
) -> DangKyHocPhan:
    """Create a class registration."""
    db_item = DangKyHocPhan.model_validate(item_create)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def update_course_registration(
    *,
    session: Session,
    db_item: DangKyHocPhan,
    item_update: DangKyHocPhanUpdate,
) -> DangKyHocPhan:
    """Update a class registration."""
    item_data = item_update.model_dump(exclude_unset=True)
    for field, value in item_data.items():
        setattr(db_item, field, value)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def delete_course_registration(*, session: Session, db_item: DangKyHocPhan) -> None:
    """Delete a class registration."""
    session.delete(db_item)
    session.commit()
