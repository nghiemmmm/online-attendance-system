from datetime import date, time

from sqlmodel import Session, select, text

from app.core.db import engine
from app.models import (
    Attendance,
    ClassSection,
    ClassSession,
    CourseRegistration,
)


def main():
    with Session(engine) as session:
        target_date = date(2026, 6, 29)
        print(f"Configuring live session for date: {target_date}")

        # 1. Verify ClassSection 1 (Lập trình Web - TS. Nguyễn Văn An)
        cs = session.get(ClassSection, 1)
        if not cs:
            cs = ClassSection(
                class_section_id=1,
                course_id=1,
                staff_id=2101,
                semester=1,
                academic_year="2025-2026",
                status=True,
            )
            session.add(cs)
            session.commit()

        # 2. Ensure CourseRegistrations for students
        for st_id in [21080001, 21080002]:
            reg = session.exec(
                select(CourseRegistration).where(
                    CourseRegistration.class_section_id == 1,
                    CourseRegistration.student_id == st_id,
                )
            ).first()
            if not reg:
                reg = CourseRegistration(
                    class_section_id=1, student_id=st_id, status=True
                )
                session.add(reg)
            else:
                reg.status = True
                session.add(reg)
        session.commit()

        # 3. Find or Create ClassSession for TODAY (2026-06-29)
        today_session = session.exec(
            select(ClassSession).where(
                ClassSession.class_section_id == 1,
                ClassSession.class_date == target_date,
            )
        ).first()

        if not today_session:
            session.exec(
                text(
                    "SELECT setval('class_sessions_class_session_id_seq', (SELECT COALESCE(MAX(class_session_id), 0) + 1 FROM class_sessions), false);"
                )
            )
            today_session = ClassSession(
                class_section_id=1,
                class_date=target_date,
                start_time=time(7, 30),
                end_time=time(11, 30),
                session_number=5,
                status="DANG_DIEN_RA",
                late_grace_minutes=15,
                recognition_threshold=0.6,
                note="Phiên điểm danh trực tuyến hôm nay",
            )
            session.add(today_session)
            session.commit()
            session.refresh(today_session)
        else:
            today_session.status = "DANG_DIEN_RA"
            today_session.start_time = time(7, 30)
            today_session.end_time = time(11, 30)
            session.add(today_session)
            session.commit()
            session.refresh(today_session)

        print(
            f"ClassSession ID: {today_session.class_session_id} | Date: {today_session.class_date} | Status: {today_session.status}"
        )

        # 4. Clear attendance & related foreign key records for student 21080001
        existing_atts = session.exec(
            select(Attendance).where(
                Attendance.class_session_id == today_session.class_session_id,
                Attendance.student_id == 21080001,
            )
        ).all()
        for att in existing_atts:
            session.execute(
                text("DELETE FROM attendance_images WHERE attendance_id = :att_id"),
                {"att_id": att.attendance_id},
            )
            session.execute(
                text("DELETE FROM appeals WHERE attendance_id = :att_id"),
                {"att_id": att.attendance_id},
            )
            session.delete(att)
        session.commit()

        print("Setup completed successfully!")


if __name__ == "__main__":
    main()
