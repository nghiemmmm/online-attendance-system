from sqlmodel import Session, select, func
from app.models import Nganh, NganhCreate, NganhUpdate

def get_nganh(*, session: Session, ma_nganh: int) -> Nganh | None:
    return session.get(Nganh, ma_nganh)

def get_nganhs(*, session: Session, skip: int = 0, limit: int = 100) -> tuple[list[Nganh], int]:
    count_statement = select(func.count()).select_from(Nganh)
    count = session.exec(count_statement).one()
    statement = select(Nganh).offset(skip).limit(limit)
    items = session.exec(statement).all()
    return list(items), count

def create_nganh(*, session: Session, item_create: NganhCreate) -> Nganh:
    db_item = Nganh.model_validate(item_create)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

def update_nganh(*, session: Session, db_item: Nganh, item_update: NganhUpdate) -> Nganh:
    item_data = item_update.model_dump(exclude_unset=True)
    for field, value in item_data.items():
        setattr(db_item, field, value)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

def delete_nganh(*, session: Session, db_item: Nganh) -> None:
    session.delete(db_item)
    session.commit()
