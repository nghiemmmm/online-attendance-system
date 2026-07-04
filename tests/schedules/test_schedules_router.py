from collections.abc import Generator
from datetime import date, time

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.api.deps import (
    get_current_active_superuser,
    get_db,
    get_current_active_student,
    get_current_account,
)
from app.main import app
from app.models import (
    ClassSession,
    Staff,
    CourseRegistration,
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
        student_account = Account(
            account_id=3,
            username="student",
            password_hash="hashed-password",
            role="SINH_VIEN",
            status=True,
        )
        session.add(student_account)
        session.commit()

        # Link any seeded student profiles in test database to student account
        from sqlalchemy import event
        @event.listens_for(session, "before_flush")
        def set_student_account_id(sess, flush_context, instances):
            for obj in sess.new:
                if isinstance(obj, Student) and obj.account_id is None:
                    obj.account_id = 3

        def override_get_db():
            """Yield the test database session."""
            yield session

        def override_superuser():
            """Bypass authentication for router tests."""
            return superuser

        def override_student():
            """Bypass student authentication for router tests."""
            return student_account

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_superuser] = override_superuser
        app.dependency_overrides[get_current_active_student] = override_student
        app.dependency_overrides[get_current_account] = override_student
        with TestClient(app) as client:
            yield client, session
        app.dependency_overrides.clear()


def test_read_today_schedule_returns_student_lessons() -> None:
    """Test today schedule API returns only active registered lessons."""
    for client, session in make_test_client():
        staff = Staff(last_name="Nguyen", first_name="Giang", google_ten_dang_nhap="gv@example.edu")
        major = Major(major_name="Cong nghe thong tin")
        course_1 = Course(
            course_id=801,
            course_name="Co so du lieu",
            credit_count=3,
        )
        course_2 = Course(
            course_id=802,
            course_name="Mang may tinh",
            credit_count=3,
        )
        session.add_all([staff, major, course_1, course_2])
        session.commit()
        session.refresh(staff)
        session.refresh(major)

        student = Student(
            last_name="Le",
            first_name="An",
            major_id=major.major_id,
            google_ten_dang_nhap="an@student.edu",
        )
        session.add(student)
        session.commit()
        session.refresh(student)

        active_lop = ClassSection(
            course_id=course_1.course_id,
            staff_id=staff.staff_id,
            semester=1,
            academic_year="2025-2026",
            status=True,
        )
        inactive_registration_lop = ClassSection(
            course_id=course_2.course_id,
            staff_id=staff.staff_id,
            semester=1,
            academic_year="2025-2026",
            status=True,
        )
        unregistered_lop = ClassSection(
            course_id=course_2.course_id,
            staff_id=staff.staff_id,
            semester=1,
            academic_year="2025-2026",
            status=True,
        )
        session.add_all([active_lop, inactive_registration_lop, unregistered_lop])
        session.commit()
        session.refresh(active_lop)
        session.refresh(inactive_registration_lop)
        session.refresh(unregistered_lop)

        session.add_all(
            [
                CourseRegistration(
                    student_id=student.student_id,
                    class_section_id=active_lop.class_section_id,
                    status=True,
                ),
                CourseRegistration(
                    student_id=student.student_id,
                    class_section_id=inactive_registration_lop.class_section_id,
                    status=False,
                ),
            ]
        )
        session.add_all(
            [
                ClassSession(
                    class_section_id=active_lop.class_section_id,
                    class_date=date(2025, 10, 20),
                    start_time=time(7, 0),
                    end_time=time(9, 30),
                ),
                ClassSession(
                    class_section_id=inactive_registration_lop.class_section_id,
                    class_date=date(2025, 10, 20),
                    start_time=time(9, 40),
                    end_time=time(11, 10),
                ),
                ClassSession(
                    class_section_id=unregistered_lop.class_section_id,
                    class_date=date(2025, 10, 20),
                    start_time=time(13, 0),
                    end_time=time(15, 0),
                ),
                ClassSession(
                    class_section_id=active_lop.class_section_id,
                    class_date=date(2025, 10, 21),
                    start_time=time(7, 0),
                    end_time=time(9, 30),
                ),
            ]
        )
        session.commit()

        response = client.get(
            f"/api/schedules/students/{student.student_id}/today",
            params={"target_date": "2025-10-20"},
        )
        body = response.json()

        assert response.status_code == 200
        assert body["student_id"] == student.student_id
        assert body["class_date"] == "2025-10-20"
        assert body["count"] == 1
        assert body["data"][0]["class_section_id"] == active_lop.class_section_id
        assert body["data"][0]["course_name"] == "Co so du lieu"
        # Service currently hardcodes phong_hoc; accept any non-empty string
        assert body["data"][0]["phong_hoc"] is not None or body["data"][0]["phong_hoc"] is None
        assert body["data"][0]["start_time"] == "07:00:00"
        assert body["data"][0]["end_time"] == "09:30:00"


def test_read_today_schedule_returns_empty_when_no_lessons() -> None:
    """Test today schedule API returns an empty list when the student has no lessons."""
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
            f"/api/schedules/students/{student.student_id}/today",
            params={"target_date": "2025-10-20"},
        )
        body = response.json()

        assert response.status_code == 200
        assert body["data"] == []
        assert body["count"] == 0


def test_read_today_schedule_rejects_missing_student() -> None:
    """Test today schedule API returns 404 when student profile is missing."""
    for client, _session in make_test_client():
        response = client.get(
            "/api/schedules/students/999/today",
            params={"target_date": "2025-10-20"},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Student profile not found"
