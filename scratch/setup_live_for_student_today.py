import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from datetime import date, time
from sqlmodel import Session, select, text
from app.core.db import engine
from app.models import ClassSession, CourseRegistration, Attendance, ClassSection

def main():
    with Session(engine) as session:
        target_date = date(2026, 6, 29)
        student_id = 21080001 # Nguyễn Đức Nghiêm
        print(f"Setting up live active attendance session for Student {student_id} on {target_date}...")
        
        # 1. Ensure ClassSection 1 exists & active
        cs = session.get(ClassSection, 1)
        if not cs:
            cs = ClassSection(class_section_id=1, course_id=1, staff_id=2101, semester=1, academic_year="2025-2026", status=True)
            session.add(cs)
            session.commit()
            
        # 2. Ensure CourseRegistration for student 21080001
        reg = session.exec(select(CourseRegistration).where(CourseRegistration.class_section_id == 1, CourseRegistration.student_id == student_id)).first()
        if not reg:
            session.add(CourseRegistration(class_section_id=1, student_id=student_id, status=True))
            session.commit()
            
        # 3. Ensure ClassSession for TODAY is DANG_DIEN_RA
        today_session = session.exec(select(ClassSession).where(ClassSession.class_section_id == 1, ClassSession.class_date == target_date)).first()
        if not today_session:
            session.exec(text("SELECT setval('class_sessions_class_session_id_seq', (SELECT COALESCE(MAX(class_session_id), 0) + 1 FROM class_sessions), false);"))
            today_session = ClassSession(
                class_section_id=1,
                class_date=target_date,
                start_time=time(7, 30),
                end_time=time(11, 30),
                session_number=5,
                status="DANG_DIEN_RA",
                late_grace_minutes=15,
                recognition_threshold=0.6,
                note="Phiên điểm danh trực tuyến đang mở"
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
            
        print(f"Active Session ID: {today_session.class_session_id} | Date: {today_session.class_date} | Status: {today_session.status}")
        
        # 4. Clear any existing attendance record for student 21080001 for clean check-in test
        existing_atts = session.exec(select(Attendance).where(Attendance.class_session_id == today_session.class_session_id, Attendance.student_id == student_id)).all()
        for att in existing_atts:
            session.execute(text("DELETE FROM attendance_images WHERE attendance_id = :att_id"), {"att_id": att.attendance_id})
            session.execute(text("DELETE FROM appeals WHERE attendance_id = :att_id"), {"att_id": att.attendance_id})
            session.delete(att)
        session.commit()
        
        print("Database setup completed! The student dashboard now has the green active attendance button ready.")

if __name__ == "__main__":
    main()
