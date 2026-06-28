from collections.abc import Generator
from datetime import date
import pytest

from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.api.deps import (
    get_current_active_superuser,
    get_db,
    get_current_account,
    get_current_active_lecturer,
    get_current_active_student,
)
from app.main import app
from app.models import (
    AuditLog,
    ClassSession,
    Staff,
    Attendance,
    Course,
    Appeal,
    ClassSection,
    Major,
    Student,
    Account,
)


@pytest.fixture(scope="session", autouse=True)
def db():
    """Override conftest.py global db fixture to avoid Render PG execution."""
    yield None


def make_test_client() -> Generator[tuple[TestClient, Session], None, None]:
    """Create a test client backed by an in-memory SQLite database."""
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
            AuditLog.__table__,
        ],
    )

    with Session(engine) as session:
        superuser = Account(
            account_id=1,
            username="admin",
            password_hash="hashed-password",
            role="ADMIN",
            status=True,
        )

        def override_get_db():
            """Yield the test database session."""
            yield session

        def override_superuser():
            """Bypass authentication for router tests."""
            return superuser

        def override_get_db():
            """Yield the test database session."""
            yield session

        def override_superuser():
            """Bypass authentication for router tests."""
            return superuser

        def override_current_account(request: Request):
            user_id = request.headers.get("x-test-user-id")
            if user_id:
                account = session.get(Account, int(user_id))
                if account:
                    return account
            return superuser

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_superuser] = override_superuser
        app.dependency_overrides[get_current_account] = override_current_account
        app.dependency_overrides[get_current_active_lecturer] = override_current_account
        app.dependency_overrides[get_current_active_student] = override_current_account
        with TestClient(app) as client:
            yield client, session
        app.dependency_overrides.clear()


def seed_appeal_data(session: Session):
    """Seed staff, class, attendance and complaints for complaint router tests."""
    other_account = Account(
        account_id=2,
        username="other_staff",
        password_hash="hashed-password",
        role="GIANG_VIEN",
        status=True,
    )
    session.add(other_account)
    session.commit()

    staff = Staff(last_name="Nguyen", first_name="Giang", google_ten_dang_nhap="giang@example.edu", account_id=1)
    other_staff = Staff(last_name="Tran", first_name="Khac", google_ten_dang_nhap="khac@example.edu", account_id=2)
    major = Major(major_name="Cong nghe thong tin")
    course = Course(
        course_id=701,
        course_name="Nhap mon AI",
        credit_count=3,
        status=True,
    )
    session.add_all([staff, other_staff, major, course])
    session.commit()
    session.refresh(staff)
    session.refresh(other_staff)
    session.refresh(major)

    student_1 = Student(last_name="Le", first_name="An", major_id=major.major_id)
    student_2 = Student(last_name="Pham", first_name="Binh", major_id=major.major_id)
    student_3 = Student(last_name="Do", first_name="Chi", major_id=major.major_id)
    session.add_all([student_1, student_2, student_3])
    session.commit()
    session.refresh(student_1)
    session.refresh(student_2)
    session.refresh(student_3)

    target_lop = ClassSection(
        course_id=course.course_id,
        staff_id=staff.staff_id,
        semester=1,
        academic_year="2025-2026",
    )
    other_lop = ClassSection(
        course_id=course.course_id,
        staff_id=other_staff.staff_id,
        semester=1,
        academic_year="2025-2026",
    )
    session.add_all([target_lop, other_lop])
    session.commit()
    session.refresh(target_lop)
    session.refresh(other_lop)

    target_class_session = ClassSession(
        class_section_id=target_lop.class_section_id,
        class_date=date(2025, 10, 15),
    )
    other_class_session = ClassSession(
        class_section_id=other_lop.class_section_id,
        class_date=date(2025, 10, 15),
    )
    session.add_all([target_class_session, other_class_session])
    session.commit()
    session.refresh(target_class_session)
    session.refresh(other_class_session)

    attendance_1 = Attendance(
        student_id=student_1.student_id,
        class_session_id=target_class_session.class_session_id,
        status="VANG",
    )
    attendance_2 = Attendance(
        student_id=student_2.student_id,
        class_session_id=target_class_session.class_session_id,
        status="VANG",
    )
    other_attendance = Attendance(
        student_id=student_3.student_id,
        class_session_id=other_class_session.class_session_id,
        status="VANG",
    )
    session.add_all([attendance_1, attendance_2, other_attendance])
    session.commit()
    session.refresh(attendance_1)
    session.refresh(attendance_2)
    session.refresh(other_attendance)

    appeal_1 = Appeal(
        attendance_id=attendance_1.attendance_id,
        student_id=student_1.student_id,
        reason="Em co mat trong lop",
        status="CHO_XU_LY",
    )
    appeal_2 = Appeal(
        attendance_id=attendance_2.attendance_id,
        student_id=student_2.student_id,
        reason="Em den muon",
        status="CHO_XU_LY",
    )
    other_appeal = Appeal(
        attendance_id=other_attendance.attendance_id,
        student_id=student_3.student_id,
        reason="Lop khac",
        status="CHO_XU_LY",
    )
    session.add_all([appeal_1, appeal_2, other_appeal])
    session.commit()
    session.refresh(appeal_1)
    session.refresh(appeal_2)
    session.refresh(other_appeal)

    return staff, other_staff, appeal_1, appeal_2, other_appeal


def test_actionable_appeal_flow() -> None:
    """Test list, detail, approve and reject APIs for staff pending complaints."""
    for client, session in make_test_client():
        staff, other_staff, appeal_1, appeal_2, other_appeal = (
            seed_appeal_data(session)
        )

        list_response = client.get(
            f"/api/appeals/staff/{staff.staff_id}?status=pending"
        )
        list_body = list_response.json()

        detail_response = client.get(
            f"/api/appeals/{appeal_1.appeal_id}?staff_id={staff.staff_id}"
        )
        approve_response = client.patch(
            f"/api/appeals/{appeal_1.appeal_id}?staff_id={staff.staff_id}",
            json={
                "status": "approved",
                "resolution_note": "Dong y cap nhat",
                "new_attendance_status": "CO_MAT",
            },
        )
        approve_again_response = client.patch(
            f"/api/appeals/{appeal_1.appeal_id}?staff_id={staff.staff_id}",
            json={"status": "approved", "new_attendance_status": "CO_MAT"},
        )
        reject_response = client.patch(
            f"/api/appeals/{appeal_2.appeal_id}?staff_id={staff.staff_id}",
            json={"status": "rejected", "resolution_note": "Khong du bang chung"},
        )
        other_response = client.get(
            f"/api/appeals/{other_appeal.appeal_id}?staff_id={staff.staff_id}"
        )
        wrong_staff_response = client.get(
            f"/api/appeals/{appeal_1.appeal_id}?staff_id={other_staff.staff_id}",
            headers={"x-test-user-id": "2"},
        )

        assert list_response.status_code == 200
        assert list_body["count"] == 2
        assert list_body["data"][0]["course_name"] == "Nhap mon AI"
        assert detail_response.status_code == 200
        assert detail_response.json()["appeal_id"] == appeal_1.appeal_id
        assert approve_response.status_code == 200
        assert approve_response.json()["status"] == "DA_CHAP_THUAN"
        assert approve_response.json()["attendance_status"] == "CO_MAT"
        assert approve_again_response.status_code == 409
        assert reject_response.status_code == 200
        assert reject_response.json()["status"] == "DA_TU_CHOI"
        assert other_response.status_code == 404
        assert wrong_staff_response.status_code == 404


def test_approve_appeal_rejects_invalid_attendance_status() -> None:
    """Test approve API rejects unsupported attendance status values."""
    for client, session in make_test_client():
        staff, _other_staff, appeal_1, _appeal_2, _other_appeal = (
            seed_appeal_data(session)
        )

        response = client.patch(
            f"/api/appeals/{appeal_1.appeal_id}?staff_id={staff.staff_id}",
            json={"status": "approved", "new_attendance_status": "SAI_TRANG_THAI"},
        )

        assert response.status_code == 400
        assert response.json()["message"] == "Invalid attendance status"
