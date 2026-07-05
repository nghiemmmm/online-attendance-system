import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from sqlmodel import Session, func, select

from app.core.db import engine
from app.models import ClassSection, ClassSession, Course, Staff


def main():
    with Session(engine) as session:
        staff_members = session.exec(select(Staff)).all()
        print("=== GIẢNG VIÊN TRONG CƠ SỞ DỮ LIỆU ===")
        for s in staff_members:
            classes = session.exec(
                select(ClassSection).where(ClassSection.staff_id == s.staff_id)
            ).all()
            class_ids = [c.class_section_id for c in classes]

            total_sessions = 0
            if class_ids:
                total_sessions = (
                    session.exec(
                        select(func.count(ClassSession.class_session_id)).where(
                            ClassSession.class_section_id.in_(class_ids)
                        )
                    ).first()
                    or 0
                )

            print(f"\n👨‍🏫 Mã cán bộ (ID): {s.staff_id}")
            print(f"   Họ và tên: {s.last_name} {s.first_name}")
            print(f"   Email: {s.google_email}")
            print(f"   Số điện thoại: {s.phone or 'N/A'}")
            print(f"   Số lớp học phần đang dạy: {len(classes)}")
            print(f"   Số buổi học đã tạo trong CSDL: {total_sessions}")
            for c in classes:
                course = session.get(Course, c.course_id)
                print(
                    f"     - Lớp HP #{c.class_section_id}: Môn {course.course_name if course else 'N/A'} (Học kỳ {c.semester}, Năm {c.academic_year})"
                )


if __name__ == "__main__":
    main()
