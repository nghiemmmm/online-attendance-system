"""
Student CRUD operations.

Contains database operations for student profiles.
"""

from sqlalchemy import or_
from sqlmodel import Session, col, func, select

from app.models import Student, StudentCreate, StudentUpdate


def get_student(*, session: Session, student_id: int) -> Student | None:
    """Lay thong tin mot sinh vien theo ma sinh vien."""
    return session.get(Student, student_id)


def get_student_by_google_email(
    *, session: Session, google_email: str
) -> Student | None:
    """Tim sinh vien theo Google email de kiem tra trung du lieu."""
    statement = select(Student).where(Student.google_email == google_email)
    return session.exec(statement).first()


def get_student_by_account_id(*, session: Session, account_id: int) -> Student | None:
    """Tim sinh vien theo tai khoan lien ket."""
    statement = select(Student).where(Student.account_id == account_id)
    return session.exec(statement).first()


def get_students(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
    q: str | None = None,
    major_id: int | None = None,
    academic_status: bool | None = None,
) -> tuple[list[Student], int]:
    """Lay danh sach sinh vien, last_name tro tim kiem va loc co ban."""
    conditions = []
    if q:
        search = f"%{q.strip()}%"
        conditions.append(
            or_(
                Student.last_name.ilike(search),
                Student.first_name.ilike(search),
                Student.google_email.ilike(search),
                Student.phone.ilike(search),
            )
        )
    if major_id is not None:
        conditions.append(Student.major_id == major_id)
    if academic_status is not None:
        conditions.append(Student.academic_status == academic_status)

    count_statement = select(func.count()).select_from(Student)
    statement = select(Student).order_by(col(Student.student_id).desc())
    for condition in conditions:
        count_statement = count_statement.where(condition)
        statement = statement.where(condition)

    count = session.exec(count_statement).one()
    students = session.exec(statement.offset(skip).limit(limit)).all()
    return list(students), count


def create_student(*, session: Session, student_create: StudentCreate) -> Student:
    """Tao last_name so sinh vien moi."""
    db_student = Student.model_validate(student_create)
    session.add(db_student)
    session.commit()
    session.refresh(db_student)
    return db_student


def update_student(
    *,
    session: Session,
    db_student: Student,
    student_update: StudentUpdate,
) -> Student:
    """Cap nhat mot phan thong tin sinh vien."""
    student_data = student_update.model_dump(exclude_unset=True)
    for field, value in student_data.items():
        setattr(db_student, field, value)

    session.add(db_student)
    session.commit()
    session.refresh(db_student)
    return db_student


def delete_student(*, session: Session, db_student: Student) -> None:
    """Xoa last_name so sinh vien khoi database."""
    session.delete(db_student)
    session.commit()
