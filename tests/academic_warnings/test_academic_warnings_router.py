from collections.abc import Generator
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.api.deps import get_current_active_superuser, get_db
from app.main import app
from app.models import (
    ClassSession,
    Staff,
    CourseRegistration,
    Attendance,
    Course,
    ClassSection,
    Major,
    Student,
    Account,
)


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
            Major.__table__,
            Student.__table__,
            Course.__table__,
            ClassSection.__table__,
            CourseRegistration.__table__,
            ClassSession.__table__,
            Attendance.__table__,
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

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_superuser] = override_superuser
        with TestClient(app) as client:
            yield client, session
        app.dependency_overrides.clear()


def seed_warning_data(session: Session):
    """Seed student, classes, lessons and attendance records for warning tests."""
    staff = Staff(last_name="Nguyen", first_name="Giang", google_ten_dang_nhap="gv@example.edu")
    major = Major(major_name="Cong nghe thong tin")
    course_1 = Course(course_id=901, course_name="Co so du lieu")
    course_2 = Course(course_id=902, course_name="Lap trinh web")
    session.add_all([staff, major, course_1, course_2])
    session.commit()
    session.refresh(staff)
    session.refresh(major)

    student = Student(last_name="Le", first_name="An", major_id=major.major_id)
    session.add(student)
    session.commit()
    session.refresh(student)

    warning_lop = ClassSection(
        course_id=course_1.course_id,
        staff_id=staff.staff_id,
        semester=1,
        academic_year="2025-2026",
    )
    safe_lop = ClassSection(
        course_id=course_2.course_id,
        staff_id=staff.staff_id,
        semester=1,
        academic_year="2025-2026",
    )
    session.add_all([warning_lop, safe_lop])
    session.commit()
    session.refresh(warning_lop)
    session.refresh(safe_lop)

    session.add_all(
        [
            CourseRegistration(
                student_id=student.student_id,
                class_section_id=warning_lop.class_section_id,
            ),
            CourseRegistration(
                student_id=student.student_id,
                class_section_id=safe_lop.class_section_id,
            ),
        ]
    )
    session.commit()

    warning_lessons = [
        ClassSession(
            class_section_id=warning_lop.class_section_id,
            class_date=date(2025, 10, day),
        )
        for day in range(1, 6)
    ]
    safe_lessons = [
        ClassSession(
            class_section_id=safe_lop.class_section_id,
            class_date=date(2025, 10, day),
        )
        for day in range(1, 6)
    ]
    session.add_all(warning_lessons + safe_lessons)
    session.commit()
    for lesson in warning_lessons + safe_lessons:
        session.refresh(lesson)

    session.add_all(
        [
            Attendance(
                student_id=student.student_id,
                class_session_id=warning_lessons[0].class_session_id,
                status="VANG",
            ),
            Attendance(
                student_id=student.student_id,
                class_session_id=warning_lessons[1].class_session_id,
                status="VANG_MAT",
            ),
            Attendance(
                student_id=student.student_id,
                class_session_id=safe_lessons[0].class_session_id,
                status="CO_MAT",
            ),
        ]
    )
    session.commit()
    return student, warning_lop, safe_lop


def test_read_absence_warnings_returns_warning_classes() -> None:
    """Test absence warning API returns classes near or over absence limit."""
    for client, session in make_test_client():
        student, warning_lop, _safe_lop = seed_warning_data(session)

        response = client.get(
            f"/api/academic-warnings/students/{student.student_id}/absences"
        )
        body = response.json()

        assert response.status_code == 200
        assert body["student_id"] == student.student_id
        assert body["count"] == 1
        assert body["data"][0]["class_section_id"] == warning_lop.class_section_id
        assert body["data"][0]["course_name"] == "Co so du lieu"
        assert body["data"][0]["total_class_sessions"] == 5
        assert body["data"][0]["absent_session_count"] == 2
        assert body["data"][0]["absence_rate"] == 40.0
        assert body["data"][0]["warning_threshold"] == 20.0
        assert body["data"][0]["warning_status"] == "VUOT_NGUONG"


def test_read_absence_warnings_can_include_safe_classes() -> None:
    """Test absence warning API can include safe classes when requested."""
    for client, session in make_test_client():
        student, _warning_lop, safe_lop = seed_warning_data(session)

        response = client.get(
            f"/api/academic-warnings/students/{student.student_id}/absences",
            params={"include_safe": True},
        )
        body = response.json()
        safe_item = next(
            item
            for item in body["data"]
            if item["class_section_id"] == safe_lop.class_section_id
        )

        assert response.status_code == 200
        assert body["count"] == 2
        assert safe_item["absence_rate"] == 0.0
        assert safe_item["warning_status"] == "AN_TOAN"


def test_read_absence_warnings_returns_empty_when_no_warnings() -> None:
    """Test absence warning API returns empty response when there are no warnings."""
    for client, session in make_test_client():
        staff = Staff(last_name="Tran", first_name="Giang", google_ten_dang_nhap="gv2@example.edu")
        major = Major(major_name="He thong thong tin")
        course = Course(course_id=903, course_name="Kiem weekday phan mem")
        session.add_all([staff, major, course])
        session.commit()
        session.refresh(staff)
        session.refresh(major)
        student = Student(last_name="Pham", first_name="Binh", major_id=major.major_id)
        session.add(student)
        session.commit()
        session.refresh(student)

        class_section = ClassSection(
            course_id=course.course_id,
            staff_id=staff.staff_id,
        )
        session.add(class_section)
        session.commit()
        session.refresh(class_section)
        session.add(
            CourseRegistration(
                student_id=student.student_id,
                class_section_id=class_section.class_section_id,
            )
        )
        session.commit()

        response = client.get(
            f"/api/academic-warnings/students/{student.student_id}/absences"
        )
        body = response.json()

        assert response.status_code == 200
        assert body["data"] == []
        assert body["count"] == 0


def test_read_absence_warnings_rejects_invalid_threshold_order() -> None:
    """Test absence warning API rejects warning threshold greater than absence limit."""
    for client, session in make_test_client():
        student, _warning_lop, _safe_lop = seed_warning_data(session)

        response = client.get(
            f"/api/academic-warnings/students/{student.student_id}/absences",
            params={"warning_threshold": 30, "absence_limit": 20},
        )

        assert response.status_code == 400
        assert response.json()["message"] == (
            "warning_threshold must be less than or equal to absence_limit"
        )
