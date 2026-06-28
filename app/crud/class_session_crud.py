from sqlmodel import Session, select, func
from app.models import ClassSession, ClassSessionCreate, ClassSessionUpdate

def get_class_session(*, session: Session, class_session_id: int) -> ClassSession | None:
    return session.get(ClassSession, class_session_id)

def get_class_sessions(*, session: Session, skip: int = 0, limit: int = 100) -> tuple[list[ClassSession], int]:
    count_statement = select(func.count()).select_from(ClassSession)
    count = session.exec(count_statement).one()
    statement = select(ClassSession).offset(skip).limit(limit)
    items = session.exec(statement).all()
    return list(items), count

def create_class_session(*, session: Session, item_create: ClassSessionCreate) -> ClassSession:
    db_item = ClassSession.model_validate(item_create)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

def update_class_session(*, session: Session, db_item: ClassSession, item_update: ClassSessionUpdate) -> ClassSession:
    item_data = item_update.model_dump(exclude_unset=True)
    for field, value in item_data.items():
        setattr(db_item, field, value)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

def delete_class_session(*, session: Session, db_item: ClassSession) -> None:
    session.delete(db_item)
    session.commit()
