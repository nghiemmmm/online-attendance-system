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


def seed_attendance_summary_data(session: Session):
    """Seed student semester attendance data for summary tests."""
    staff = Staff(last_name="Nguyen", first_name="Giang", google_ten_dang_nhap="gv@example.edu")
    major = Major(major_name="Cong nghe thong tin")
    course = Course(course_id=1001, course_name="Co so du lieu")
    other_course = Course(course_id=1002, course_name="Tri tue nhan tao")
    session.add_all([staff, major, course, other_course])
    session.commit()
    session.refresh(staff)
    session.refresh(major)

    student = Student(last_name="Le", first_name="An", major_id=major.major_id)
    session.add(student)
    session.commit()
    session.refresh(student)

    target_lop = ClassSection(
        course_id=course.course_id,
        staff_id=staff.staff_id,
        semester=1,
        academic_year="2025-2026",
    )
    other_semester_lop = ClassSection(
        course_id=other_course.course_id,
        staff_id=staff.staff_id,
        semester=2,
        academic_year="2025-2026",
    )
    session.add_all([target_lop, other_semester_lop])
    session.commit()
    session.refresh(target_lop)
    session.refresh(other_semester_lop)

    session.add_all(
        [
            CourseRegistration(
                student_id=student.student_id,
                class_section_id=target_lop.class_section_id,
            ),
            CourseRegistration(
                student_id=student.student_id,
                class_section_id=other_semester_lop.class_section_id,
            ),
        ]
    )
    session.commit()

    target_lessons = [
        ClassSession(
            class_section_id=target_lop.class_section_id,
            class_date=date(2025, 10, day),
        )
        for day in range(1, 5)
    ]
    other_lesson = ClassSession(
        class_section_id=other_semester_lop.class_section_id,
        class_date=date(2026, 3, 1),
    )
    session.add_all([*target_lessons, other_lesson])
    session.commit()
    for lesson in target_lessons:
        session.refresh(lesson)
    session.refresh(other_lesson)

    session.add_all(
        [
            Attendance(
                student_id=student.student_id,
                class_session_id=target_lessons[0].class_session_id,
                status="CO_MAT",
            ),
            Attendance(
                student_id=student.student_id,
                class_session_id=target_lessons[1].class_session_id,
                status="DI_MUON",
            ),
            Attendance(
                student_id=student.student_id,
                class_session_id=target_lessons[2].class_session_id,
                status="VANG",
            ),
            Attendance(
                student_id=student.student_id,
                class_session_id=other_lesson.class_session_id,
                status="CO_MAT",
            ),
        ]
    )
    session.commit()
    return student


def test_read_semester_attendance_summary_returns_summary() -> None:
    """Test semester attendance summary counts present and total lessons."""
    for client, session in make_test_client():
        student = seed_attendance_summary_data(session)

        response = client.get(
            f"/api/attendance-records/students/{student.student_id}/present-session-count",
            params={"semester": 1, "academic_year": "2025-2026"},
        )
        body = response.json()

        assert response.status_code == 200
        assert body["student_id"] == student.student_id
        assert body["semester"] == 1
        assert body["academic_year"] == "2025-2026"
        assert body["present_session_count"] == 2
        assert body["total_class_sessions"] == 4
        assert body["attendance_rate"] == 50.0
        assert body["description"] == "2/4 buổi trong học kỳ"


def test_read_semester_attendance_summary_returns_zero_without_data() -> None:
    """Test semester attendance summary returns zeros when no classes are found."""
    for client, session in make_test_client():
        major = Major(major_name="He thong thong tin")
        session.add(major)
        session.commit()
        session.refresh(major)
        student = Student(last_name="Tran", first_name="Binh", major_id=major.major_id)
        session.add(student)
        session.commit()
        session.refresh(student)

        response = client.get(
            f"/api/attendance-records/students/{student.student_id}/present-session-count",
            params={"semester": 1, "academic_year": "2025-2026"},
        )
        body = response.json()

        assert response.status_code == 200
        assert body["present_session_count"] == 0
        assert body["total_class_sessions"] == 0
        assert body["attendance_rate"] == 0.0
        assert body["description"] == "0/0 buổi trong học kỳ"


def test_read_semester_attendance_summary_rejects_missing_student() -> None:
    """Test semester attendance summary returns 404 for missing student profile."""
    for client, _session in make_test_client():
        response = client.get(
            "/api/attendance-records/students/999/present-session-count",
            params={"semester": 1, "academic_year": "2025-2026"},
        )

        assert response.status_code == 404
        assert response.json()["message"] == "Not found"
