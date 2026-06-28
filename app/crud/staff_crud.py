from sqlalchemy import or_
from sqlmodel import Session, col, func, select

from app.models import Staff, StaffCreate, StaffUpdate


def get_staff_member(*, session: Session, staff_id: int) -> Staff | None:
    """Lấy thông tin một cán bộ theo mã cán bộ."""
    return session.get(Staff, staff_id)


def get_staff_member_by_google_email(
    *, session: Session, google_email: str
) -> Staff | None:
    """Tìm cán bộ theo Google email để kiểm tra trùng dữ liệu."""
    statement = select(Staff).where(Staff.google_email == google_email)
    return session.exec(statement).first()


def get_staff_member_by_account_id(
    *, session: Session, account_id: int
) -> Staff | None:
    """Tìm cán bộ theo tài khoản liên kết để kiểm tra mỗi tài khoản chỉ gắn một hồ sơ."""
    statement = select(Staff).where(Staff.account_id == account_id)
    return session.exec(statement).first()


def get_staff_members(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
    q: str | None = None,
    status: bool | None = None,
) -> tuple[list[Staff], int]:
    """Lấy danh sách cán bộ, hỗ trợ tìm kiếm theo tên/email/chức vụ và lọc trạng thái."""
    conditions = []
    if q:
        search = f"%{q.strip()}%"
        conditions.append(
            or_(
                Staff.last_name.ilike(search),
                Staff.first_name.ilike(search),
                Staff.google_email.ilike(search),
                Staff.position.ilike(search),
            )
        )
    if status is not None:
        conditions.append(Staff.status == status)

    count_statement = select(func.count()).select_from(Staff)
    statement = select(Staff).order_by(col(Staff.staff_id).desc())
    for condition in conditions:
        count_statement = count_statement.where(condition)
        statement = statement.where(condition)

    count = session.exec(count_statement).one()
    staff_members = session.exec(statement.offset(skip).limit(limit)).all()
    return list(staff_members), count


def create_staff_member(*, session: Session, staff_create: StaffCreate) -> Staff:
    """Tạo hồ sơ cán bộ mới."""
    db_staff = Staff.model_validate(staff_create)
    session.add(db_staff)
    session.commit()
    session.refresh(db_staff)
    return db_staff


def update_staff_member(
    *, session: Session, db_staff: Staff, staff_update: StaffUpdate
) -> Staff:
    """Cập nhật một phần thông tin cán bộ."""
    staff_data = staff_update.model_dump(exclude_unset=True)
    for field, value in staff_data.items():
        setattr(db_staff, field, value)

    session.add(db_staff)
    session.commit()
    session.refresh(db_staff)
    return db_staff


def delete_staff_member(*, session: Session, db_staff: Staff) -> None:
    """Xóa hồ sơ cán bộ khỏi database."""
    session.delete(db_staff)
    session.commit()
