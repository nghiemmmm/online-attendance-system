"""Provide CRUD operations for class registrations."""

from sqlmodel import Session, func, select

from app.models import (
    CourseRegistration,
    CourseRegistrationCreate,
    CourseRegistrationUpdate,
)


def get_course_registration(
    *,
    session: Session,
    registration_id: int,
) -> CourseRegistration | None:
    """Return a class registration by ID."""
    return session.get(CourseRegistration, registration_id)


def get_course_registrations(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[CourseRegistration], int]:
    """Return paginated class registrations and their total count."""
    count_statement = select(func.count()).select_from(CourseRegistration)
    count = session.exec(count_statement).one()
    statement = select(CourseRegistration).offset(skip).limit(limit)
    items = session.exec(statement).all()
    return list(items), count


def create_course_registration(
    *,
    session: Session,
    item_create: CourseRegistrationCreate,
) -> CourseRegistration:
    """Create a class registration."""
    db_item = CourseRegistration.model_validate(item_create)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def update_course_registration(
    *,
    session: Session,
    db_item: CourseRegistration,
    item_update: CourseRegistrationUpdate,
) -> CourseRegistration:
    """Update a class registration."""
    item_data = item_update.model_dump(exclude_unset=True)
    for field, value in item_data.items():
        setattr(db_item, field, value)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def delete_course_registration(
    *, session: Session, db_item: CourseRegistration
) -> None:
    """Delete a class registration."""
    session.delete(db_item)
    session.commit()
