import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from sqlmodel import Session, func, select

from app.core.db import engine
from app.models import (
    Account,
    Appeal,
    Attendance,
    ClassSection,
    ClassSession,
    Course,
    CourseRegistration,
    Major,
    Staff,
    Student,
)


def main():
    with Session(engine) as session:
        print("=== DATABASE CURRENT ROW COUNTS ===")
        print(
            f"Accounts: {session.exec(select(func.count(Account.account_id))).first()}"
        )
        print(
            f"Students: {session.exec(select(func.count(Student.student_id))).first()}"
        )
        print(
            f"Staff (Lecturers): {session.exec(select(func.count(Staff.staff_id))).first()}"
        )
        print(f"Majors: {session.exec(select(func.count(Major.major_id))).first()}")
        print(f"Courses: {session.exec(select(func.count(Course.course_id))).first()}")
        print(
            f"ClassSections: {session.exec(select(func.count(ClassSection.class_section_id))).first()}"
        )
        print(
            f"ClassSessions: {session.exec(select(func.count(ClassSession.class_session_id))).first()}"
        )
        print(
            f"CourseRegistrations: {len(session.exec(select(CourseRegistration)).all())}"
        )
        print(
            f"Attendance Records: {session.exec(select(func.count(Attendance.attendance_id))).first()}"
        )
        print(f"Appeals: {session.exec(select(func.count(Appeal.appeal_id))).first()}")


if __name__ == "__main__":
    main()
