from sqlmodel import Session, select, func
from app.models import ThoiKhoaBieu, ThoiKhoaBieuCreate, ThoiKhoaBieuUpdate

def get_thoikhoabieu(*, session: Session, ma_thoi_khoa_bieu: int) -> ThoiKhoaBieu | None:
    return session.get(ThoiKhoaBieu, ma_thoi_khoa_bieu)

def get_thoikhoabieus(*, session: Session, skip: int = 0, limit: int = 100) -> tuple[list[ThoiKhoaBieu], int]:
    count_statement = select(func.count()).select_from(ThoiKhoaBieu)
    count = session.exec(count_statement).one()
    statement = select(ThoiKhoaBieu).offset(skip).limit(limit)
    items = session.exec(statement).all()
    return list(items), count

def create_thoikhoabieu(*, session: Session, item_create: ThoiKhoaBieuCreate) -> ThoiKhoaBieu:
    db_item = ThoiKhoaBieu.model_validate(item_create)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

def update_thoikhoabieu(*, session: Session, db_item: ThoiKhoaBieu, item_update: ThoiKhoaBieuUpdate) -> ThoiKhoaBieu:
    item_data = item_update.model_dump(exclude_unset=True)
    for field, value in item_data.items():
        setattr(db_item, field, value)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

def delete_thoikhoabieu(*, session: Session, db_item: ThoiKhoaBieu) -> None:
    session.delete(db_item)
    session.commit()
