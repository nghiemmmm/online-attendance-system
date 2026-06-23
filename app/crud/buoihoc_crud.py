from sqlmodel import Session, select, func
from app.models import BuoiHoc, BuoiHocCreate, BuoiHocUpdate

def get_buoihoc(*, session: Session, ma_buoi_hoc: int) -> BuoiHoc | None:
    return session.get(BuoiHoc, ma_buoi_hoc)

def get_buoihocs(*, session: Session, skip: int = 0, limit: int = 100) -> tuple[list[BuoiHoc], int]:
    count_statement = select(func.count()).select_from(BuoiHoc)
    count = session.exec(count_statement).one()
    statement = select(BuoiHoc).offset(skip).limit(limit)
    items = session.exec(statement).all()
    return list(items), count

def create_buoihoc(*, session: Session, item_create: BuoiHocCreate) -> BuoiHoc:
    db_item = BuoiHoc.model_validate(item_create)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

def update_buoihoc(*, session: Session, db_item: BuoiHoc, item_update: BuoiHocUpdate) -> BuoiHoc:
    item_data = item_update.model_dump(exclude_unset=True)
    for field, value in item_data.items():
        setattr(db_item, field, value)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

def delete_buoihoc(*, session: Session, db_item: BuoiHoc) -> None:
    session.delete(db_item)
    session.commit()
