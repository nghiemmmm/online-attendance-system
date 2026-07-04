from sqlmodel import Session, func, select

from app.models import Timetable, TimetableCreate, TimetableUpdate


def get_timetable(*, session: Session, timetable_id: int) -> Timetable | None:
    return session.get(Timetable, timetable_id)


def get_timetables(
    *, session: Session, skip: int = 0, limit: int = 100
) -> tuple[list[Timetable], int]:
    count_statement = select(func.count()).select_from(Timetable)
    count = session.exec(count_statement).one()
    statement = select(Timetable).offset(skip).limit(limit)
    items = session.exec(statement).all()
    return list(items), count


def create_timetable(*, session: Session, item_create: TimetableCreate) -> Timetable:
    db_item = Timetable.model_validate(item_create)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def update_timetable(
    *, session: Session, db_item: Timetable, item_update: TimetableUpdate
) -> Timetable:
    item_data = item_update.model_dump(exclude_unset=True)
    for field, value in item_data.items():
        setattr(db_item, field, value)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def delete_timetable(*, session: Session, db_item: Timetable) -> None:
    session.delete(db_item)
    session.commit()
