from sqlmodel import Session, select, func
from app.models import DangKyHocPhan, DangKyHocPhanCreate, DangKyHocPhanUpdate

def get_dangkyhocphan(*, session: Session, ma_dang_ky: int) -> DangKyHocPhan | None:
    return session.get(DangKyHocPhan, ma_dang_ky)

def get_dangkyhocphans(*, session: Session, skip: int = 0, limit: int = 100) -> tuple[list[DangKyHocPhan], int]:
    count_statement = select(func.count()).select_from(DangKyHocPhan)
    count = session.exec(count_statement).one()
    statement = select(DangKyHocPhan).offset(skip).limit(limit)
    items = session.exec(statement).all()
    return list(items), count

def create_dangkyhocphan(*, session: Session, item_create: DangKyHocPhanCreate) -> DangKyHocPhan:
    db_item = DangKyHocPhan.model_validate(item_create)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

def update_dangkyhocphan(*, session: Session, db_item: DangKyHocPhan, item_update: DangKyHocPhanUpdate) -> DangKyHocPhan:
    item_data = item_update.model_dump(exclude_unset=True)
    for field, value in item_data.items():
        setattr(db_item, field, value)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

def delete_dangkyhocphan(*, session: Session, db_item: DangKyHocPhan) -> None:
    session.delete(db_item)
    session.commit()
