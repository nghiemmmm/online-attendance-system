from sqlmodel import Session, select, func
from app.models import HocPhan, HocPhanCreate, HocPhanUpdate

def get_hocphan(*, session: Session, ma_hoc_phan: int) -> HocPhan | None:
    return session.get(HocPhan, ma_hoc_phan)

def get_hocphans(*, session: Session, skip: int = 0, limit: int = 100) -> tuple[list[HocPhan], int]:
    count_statement = select(func.count()).select_from(HocPhan)
    count = session.exec(count_statement).one()
    statement = select(HocPhan).offset(skip).limit(limit)
    items = session.exec(statement).all()
    return list(items), count

def create_hocphan(*, session: Session, item_create: HocPhanCreate) -> HocPhan:
    db_item = HocPhan.model_validate(item_create)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

def update_hocphan(*, session: Session, db_item: HocPhan, item_update: HocPhanUpdate) -> HocPhan:
    item_data = item_update.model_dump(exclude_unset=True)
    for field, value in item_data.items():
        setattr(db_item, field, value)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

def delete_hocphan(*, session: Session, db_item: HocPhan) -> None:
    session.delete(db_item)
    session.commit()
