from sqlmodel import Session, select

from app.core.db import engine
from app.models import ClassSection, Course, CourseRegistration, Staff, Student


def main():
    with Session(engine) as session:
        student = session.get(Student, 21080001)
        staff = session.get(Staff, 2101)

        if not student:
            print("Student 21080001 not found!")
            return
        if not staff:
            print("Staff 2101 not found!")
            return

        print(
            f"Student: {student.last_name} {student.first_name} (ID: {student.student_id})"
        )
        print(f"Lecturer: {staff.last_name} {staff.first_name} (ID: {staff.staff_id})")

        # Find all class sections taught by TS. Nguyễn Văn An
        sections = session.exec(
            select(ClassSection).where(ClassSection.staff_id == 2101)
        ).all()

        print(f"Found {len(sections)} class sections for TS. Nguyễn Văn An.")

        for sec in sections:
            course = session.get(Course, sec.course_id)
            course_name = course.course_name if course else f"Course #{sec.course_id}"

            reg = session.exec(
                select(CourseRegistration).where(
                    CourseRegistration.class_section_id == sec.class_section_id,
                    CourseRegistration.student_id == 21080001,
                )
            ).first()

            if not reg:
                reg = CourseRegistration(
                    class_section_id=sec.class_section_id, student_id=21080001
                )
                session.add(reg)
                session.commit()
                print(
                    f"-> Successfully registered for ClassSection #{sec.class_section_id} ({course_name})"
                )
            else:
                print(
                    f"-> Already registered for ClassSection #{sec.class_section_id} ({course_name})"
                )

        print("Registration setup complete!")


if __name__ == "__main__":
    main()
