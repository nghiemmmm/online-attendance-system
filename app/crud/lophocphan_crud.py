from sqlmodel import Session, select, func
from app.models import LopHocPhan, LopHocPhanCreate, LopHocPhanUpdate

def get_lophocphan(*, session: Session, ma_lop_hoc_phan: int) -> LopHocPhan | None:
    return session.get(LopHocPhan, ma_lop_hoc_phan)

def get_lophocphans(*, session: Session, skip: int = 0, limit: int = 100) -> tuple[list[LopHocPhan], int]:
    count_statement = select(func.count()).select_from(LopHocPhan)
    count = session.exec(count_statement).one()
    statement = select(LopHocPhan).offset(skip).limit(limit)
    items = session.exec(statement).all()
    return list(items), count

def create_lophocphan(*, session: Session, item_create: LopHocPhanCreate) -> LopHocPhan:
    db_item = LopHocPhan.model_validate(item_create)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

def update_lophocphan(*, session: Session, db_item: LopHocPhan, item_update: LopHocPhanUpdate) -> LopHocPhan:
    item_data = item_update.model_dump(exclude_unset=True)
    for field, value in item_data.items():
        setattr(db_item, field, value)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

def delete_lophocphan(*, session: Session, db_item: LopHocPhan) -> None:
    session.delete(db_item)
    session.commit()
