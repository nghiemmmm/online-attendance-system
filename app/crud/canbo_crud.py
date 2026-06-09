from sqlalchemy import or_
from sqlmodel import Session, col, func, select

from app.models import CanBo, CanBoCreate, CanBoUpdate


def get_can_bo(*, session: Session, ma_can_bo: int) -> CanBo | None:
    """Lấy thông tin một cán bộ theo mã cán bộ."""
    return session.get(CanBo, ma_can_bo)


def get_can_bo_by_google_email(
    *, session: Session, google_email: str
) -> CanBo | None:
    """Tìm cán bộ theo Google email để kiểm tra trùng dữ liệu."""
    statement = select(CanBo).where(CanBo.google_email == google_email)
    return session.exec(statement).first()


def get_can_bo_by_account_id(
    *, session: Session, ma_tai_khoan: int
) -> CanBo | None:
    """Tìm cán bộ theo tài khoản liên kết để kiểm tra mỗi tài khoản chỉ gắn một hồ sơ."""
    statement = select(CanBo).where(CanBo.ma_tai_khoan == ma_tai_khoan)
    return session.exec(statement).first()


def get_can_bos(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
    q: str | None = None,
    trang_thai: bool | None = None,
) -> tuple[list[CanBo], int]:
    """Lấy danh sách cán bộ, hỗ trợ tìm kiếm theo tên/email/chức vụ và lọc trạng thái."""
    conditions = []
    if q:
        search = f"%{q.strip()}%"
        conditions.append(
            or_(
                CanBo.ho.ilike(search),
                CanBo.ten.ilike(search),
                CanBo.google_email.ilike(search),
                CanBo.chuc_vu.ilike(search),
            )
        )
    if trang_thai is not None:
        conditions.append(CanBo.trang_thai == trang_thai)

    count_statement = select(func.count()).select_from(CanBo)
    statement = select(CanBo).order_by(col(CanBo.ma_can_bo).desc())
    for condition in conditions:
        count_statement = count_statement.where(condition)
        statement = statement.where(condition)

    count = session.exec(count_statement).one()
    can_bos = session.exec(statement.offset(skip).limit(limit)).all()
    return list(can_bos), count


def create_can_bo(*, session: Session, can_bo_create: CanBoCreate) -> CanBo:
    """Tạo hồ sơ cán bộ mới."""
    db_can_bo = CanBo.model_validate(can_bo_create)
    session.add(db_can_bo)
    session.commit()
    session.refresh(db_can_bo)
    return db_can_bo


def update_can_bo(
    *, session: Session, db_can_bo: CanBo, can_bo_update: CanBoUpdate
) -> CanBo:
    """Cập nhật một phần thông tin cán bộ."""
    can_bo_data = can_bo_update.model_dump(exclude_unset=True)
    for field, value in can_bo_data.items():
        setattr(db_can_bo, field, value)

    session.add(db_can_bo)
    session.commit()
    session.refresh(db_can_bo)
    return db_can_bo


def delete_can_bo(*, session: Session, db_can_bo: CanBo) -> None:
    """Xóa hồ sơ cán bộ khỏi database."""
    session.delete(db_can_bo)
    session.commit()
