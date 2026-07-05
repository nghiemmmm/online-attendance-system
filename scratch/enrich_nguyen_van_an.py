import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from datetime import date, datetime, time

from sqlmodel import Session, select, text

from app.core.db import engine
from app.models import (
    Attendance,
    ClassSection,
    ClassSession,
    Course,
    CourseRegistration,
)


def main():
    with Session(engine) as session:
        staff_id = 2101  # TS. Nguyễn Văn An
        print(
            f"Enriching dashboard data for Staff ID {staff_id} (TS. Nguyễn Văn An)..."
        )

        # 1. Ensure a second Course exists (e.g., Lập trình Di động Flutter)
        course2 = session.exec(
            select(Course).where(Course.course_name.like("%Flutter%"))
        ).first()
        if not course2:
            course2 = session.exec(select(Course).where(Course.course_id == 2)).first()
        if not course2:
            course2 = Course(
                course_id=2,
                course_code="COMP202",
                course_name="Lập trình Di động với Flutter",
                credits=3,
            )
            session.add(course2)
            session.commit()

        # 2. Ensure a second ClassSection for TS. Nguyễn Văn An
        cs2 = session.exec(
            select(ClassSection).where(
                ClassSection.staff_id == staff_id, ClassSection.class_section_id == 3
            )
        ).first()
        if not cs2:
            session.exec(
                text(
                    "SELECT setval('class_sections_class_section_id_seq', (SELECT COALESCE(MAX(class_section_id), 0) + 1 FROM class_sections), false);"
                )
            )
            cs2 = ClassSection(
                class_section_id=3,
                course_id=course2.course_id,
                staff_id=staff_id,
                semester=1,
                academic_year="2025-2026",
                status=True,
            )
            session.add(cs2)
            session.commit()
            session.refresh(cs2)

        # 3. Register students to ClassSection 1 and ClassSection 3
        students = [21080001, 21080002, 21080003]
        for cs_id in [1, 3]:
            for st_id in students:
                reg = session.exec(
                    select(CourseRegistration).where(
                        CourseRegistration.class_section_id == cs_id,
                        CourseRegistration.student_id == st_id,
                    )
                ).first()
                if not reg:
                    session.add(
                        CourseRegistration(
                            class_section_id=cs_id, student_id=st_id, status=True
                        )
                    )
        session.commit()

        # 4. Create past recent completed sessions with attendance records for analytics
        past_dates = [date(2026, 6, 22), date(2026, 6, 15), date(2026, 6, 8)]
        for idx, p_date in enumerate(past_dates):
            for cs_id in [1, 3]:
                sess_item = session.exec(
                    select(ClassSession).where(
                        ClassSession.class_section_id == cs_id,
                        ClassSession.class_date == p_date,
                    )
                ).first()
                if not sess_item:
                    session.exec(
                        text(
                            "SELECT setval('class_sessions_class_session_id_seq', (SELECT COALESCE(MAX(class_session_id), 0) + 1 FROM class_sessions), false);"
                        )
                    )
                    sess_item = ClassSession(
                        class_section_id=cs_id,
                        class_date=p_date,
                        start_time=time(7, 30),
                        end_time=time(11, 30),
                        session_number=4 - idx,
                        status="DA_KET_THUC",
                        late_grace_minutes=15,
                        recognition_threshold=0.6,
                        note="Buổi học chính khóa đã hoàn thành",
                    )
                    session.add(sess_item)
                    session.commit()
                    session.refresh(sess_item)

                # Add attendance records for students in this past session
                statuses = (
                    ["CO_MAT", "CO_MAT", "DI_MUON"]
                    if cs_id == 1
                    else ["CO_MAT", "DI_MUON", "VANG"]
                )
                for st_idx, st_id in enumerate(students):
                    att = session.exec(
                        select(Attendance).where(
                            Attendance.class_session_id == sess_item.class_session_id,
                            Attendance.student_id == st_id,
                        )
                    ).first()
                    st_status = statuses[st_idx % len(statuses)]
                    if not att:
                        session.add(
                            Attendance(
                                student_id=st_id,
                                class_session_id=sess_item.class_session_id,
                                status=st_status,
                                method="KHUON_MAT"
                                if st_status != "VANG"
                                else "TU_DONG",
                                confidence=0.95 if st_status != "VANG" else None,
                                attendance_time=datetime.combine(
                                    p_date,
                                    time(7, 35 if st_status == "CO_MAT" else 7, 50),
                                ),
                            )
                        )
                    else:
                        att.status = st_status
                        session.add(att)
        session.commit()

        print("Data enrichment for TS. Nguyễn Văn An completed successfully!")


if __name__ == "__main__":
    main()
