from sqlmodel import Session, select, func
from app.models import ClassSection, ClassSectionCreate, ClassSectionUpdate

def get_class_section(*, session: Session, class_section_id: int) -> ClassSection | None:
    return session.get(ClassSection, class_section_id)

def get_class_sections(*, session: Session, skip: int = 0, limit: int = 100) -> tuple[list[ClassSection], int]:
    count_statement = select(func.count()).select_from(ClassSection)
    count = session.exec(count_statement).one()
    statement = select(ClassSection).offset(skip).limit(limit)
    items = session.exec(statement).all()
    return list(items), count

def create_class_section(*, session: Session, item_create: ClassSectionCreate) -> ClassSection:
    db_item = ClassSection.model_validate(item_create)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

def update_class_section(*, session: Session, db_item: ClassSection, item_update: ClassSectionUpdate) -> ClassSection:
    item_data = item_update.model_dump(exclude_unset=True)
    for field, value in item_data.items():
        setattr(db_item, field, value)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

def delete_class_section(*, session: Session, db_item: ClassSection) -> None:
    session.delete(db_item)
    session.commit()
