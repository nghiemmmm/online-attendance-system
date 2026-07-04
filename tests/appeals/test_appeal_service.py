from datetime import date, time, timedelta

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.core.exceptions import (
    AppealTimeLimitExceededError,
    DuplicateAppealError,
    PermissionDeniedError,
)
from app.models import (
    Account,
    Appeal,
    AppealCreate,
    Attendance,
    ClassSection,
    ClassSession,
    Course,
    Major,
    Staff,
    Student,
)
from app.services import appeal_service


@pytest.fixture(scope="session", autouse=True)
def db():
    """Override conftest.py global db fixture to avoid Render PG execution."""
    yield None


def make_test_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(
        engine,
        tables=[
            Account.__table__,
            Staff.__table__,
            Course.__table__,
            ClassSection.__table__,
            ClassSession.__table__,
            Major.__table__,
            Student.__table__,
            Attendance.__table__,
            Appeal.__table__,
        ],
    )
    return Session(engine)


def seed_test_data(session: Session):
    staff = Staff(
        staff_id=1,
        last_name="Nguyen",
        first_name="Giang",
        google_ten_dang_nhap="giang@example.edu",
        account_id=10,
    )
    major = Major(major_id=1, major_name="Cong nghe thong tin")
    course = Course(
        course_id=701, course_name="Nhap mon AI", credit_count=3, status=True
    )
    session.add_all([staff, major, course])
    session.commit()

    student_account = Account(
        account_id=2, username="sv001", role="STUDENT", password_hash="hashed-password"
    )
    student = Student(
        student_id=1, last_name="Le", first_name="An", major_id=1, account_id=2
    )
    session.add_all([student_account, student])
    session.commit()

    lop = ClassSection(
        class_section_id=1,
        course_id=701,
        staff_id=1,
        semester=1,
        academic_year="2025-2026",
    )
    session.add(lop)
    session.commit()

    # 1. Buoi hoc hop le (class_date hom nay, ket thuc 10:00)
    valid_class_session = ClassSession(
        class_session_id=1,
        class_section_id=1,
        class_date=date.today(),
        start_time=time(8, 0),
        end_time=time(10, 0),
    )
    # 2. Buoi hoc qua han 48 gio
    expired_class_session = ClassSession(
        class_session_id=2,
        class_section_id=1,
        class_date=date.today() - timedelta(days=3),
        start_time=time(8, 0),
        end_time=time(10, 0),
    )
    session.add_all([valid_class_session, expired_class_session])
    session.commit()

    valid_attendance = Attendance(
        attendance_id=1, student_id=1, class_session_id=1, status="VANG"
    )
    expired_attendance = Attendance(
        attendance_id=2, student_id=1, class_session_id=2, status="VANG"
    )
    session.add_all([valid_attendance, expired_attendance])
    session.commit()

    return student_account, student


def test_create_appeal_success():
    session = make_test_session()
    student_account, student = seed_test_data(session)

    payload = AppealCreate(
        student_id=1, attendance_id=1, reason="Em co di hoc", minh_chung="anh.jpg"
    )
    appeal = appeal_service.create_appeal(
        session=session, payload=payload, current_account=student_account
    )
    assert appeal.appeal_id is not None
    assert appeal.attendance_id == 1
    assert appeal.status == "CHO_XU_LY"


def test_create_appeal_expired():
    session = make_test_session()
    student_account, student = seed_test_data(session)

    payload = AppealCreate(
        student_id=1, attendance_id=2, reason="Em co di hoc tre", minh_chung="anh.jpg"
    )
    with pytest.raises(AppealTimeLimitExceededError) as excinfo:
        appeal_service.create_appeal(
            session=session, payload=payload, current_account=student_account
        )
    assert excinfo.value.status_code == 400
    assert "Đã quá thời hạn 48 giờ" in excinfo.value.detail


def test_create_appeal_duplicate():
    session = make_test_session()
    student_account, student = seed_test_data(session)

    payload = AppealCreate(
        student_id=1, attendance_id=1, reason="Ly do 1", minh_chung="anh.jpg"
    )
    appeal_service.create_appeal(
        session=session, payload=payload, current_account=student_account
    )

    with pytest.raises(DuplicateAppealError) as excinfo:
        appeal_service.create_appeal(
            session=session, payload=payload, current_account=student_account
        )
    assert excinfo.value.status_code == 400
    assert "Đã tồn tại khiếu nại" in excinfo.value.detail


def test_create_appeal_unauthorized_student():
    session = make_test_session()
    student_account, student = seed_test_data(session)

    payload = AppealCreate(
        student_id=999, attendance_id=1, reason="Em co di hoc", minh_chung="anh.jpg"
    )
    with pytest.raises(PermissionDeniedError) as excinfo:
        appeal_service.create_appeal(
            session=session, payload=payload, current_account=student_account
        )
    assert excinfo.value.status_code == 403
    assert "Cannot submit claim for another student" in excinfo.value.detail
