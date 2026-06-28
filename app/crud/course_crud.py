"""Provide CRUD operations for courses."""

from sqlmodel import Session, func, select

from app.models import Course, CourseCreate, CourseUpdate


def get_course(*, session: Session, course_id: int) -> Course | None:
    """Return a course by ID."""
    return session.get(Course, course_id)


def get_courses(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Course], int]:
    """Return paginated courses and their total count."""
    count_statement = select(func.count()).select_from(Course)
    count = session.exec(count_statement).one()
    statement = select(Course).offset(skip).limit(limit)
    items = session.exec(statement).all()
    return list(items), count


def create_course(*, session: Session, item_create: CourseCreate) -> Course:
    """Create a course."""
    db_item = Course.model_validate(item_create)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def update_course(
    *,
    session: Session,
    db_item: Course,
    item_update: CourseUpdate,
) -> Course:
    """Update a course."""
    item_data = item_update.model_dump(exclude_unset=True)
    for field, value in item_data.items():
        setattr(db_item, field, value)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def delete_course(*, session: Session, db_item: Course) -> None:
    """Delete a course."""
    session.delete(db_item)
    session.commit()
