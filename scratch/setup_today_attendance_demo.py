from datetime import date, time
from sqlmodel import Session, select, text
from app.core.db import engine
from app.models import ClassSession, CourseRegistration, Attendance, Account, Staff, Student, ClassSection, Course

def main():
    with Session(engine) as session:
        today = date.today()
        print(f"Setting up demo for date: {today}")
        
        # 1. Verify Class Section 1 (Lập trình Web - TS. Nguyễn Văn An)
        cs = session.get(ClassSection, 1)
        if not cs:
            print("Creating ClassSection 1...")
            cs = ClassSection(class_section_id=1, course_id=1, staff_id=2101, semester=1, academic_year="2025-2026", status=True)
            session.add(cs)
            session.commit()
            
        # 2. Verify CourseRegistration for Nguyễn Đức Nghiêm (21080001)
        reg = session.exec(
            select(CourseRegistration).where(
                CourseRegistration.class_section_id == 1,
                CourseRegistration.student_id == 21080001
            )
        ).first()
        if not reg:
            print("Registering student 21080001 for class_section_id 1...")
            reg = CourseRegistration(class_section_id=1, student_id=21080001)
            session.add(reg)
            session.commit()
            
        # 3. Find or Create ClassSession for TODAY with status DANG_DIEN_RA
        today_session = session.exec(
            select(ClassSession).where(
                ClassSession.class_section_id == 1,
                ClassSession.class_date == today
            )
        ).first()
        
        if not today_session:
            # Sync sequence
            session.exec(text("SELECT setval('class_sessions_class_session_id_seq', (SELECT COALESCE(MAX(class_session_id), 0) + 1 FROM class_sessions), false);"))
            today_session = ClassSession(
                class_section_id=1,
                class_date=today,
                start_time=time(7, 30),
                end_time=time(10, 0),
                session_number=5,
                status="DANG_DIEN_RA",
                late_grace_minutes=15,
                recognition_threshold=0.6,
                note="Phiên điểm danh trực tuyến hôm nay"
            )
            session.add(today_session)
            session.commit()
            session.refresh(today_session)
        else:
            today_session.status = "DANG_DIEN_RA"
            today_session.start_time = time(7, 30)
            today_session.end_time = time(10, 0)
            session.add(today_session)
            session.commit()
            session.refresh(today_session)
            
        print(f"Today ClassSession ID: {today_session.class_session_id} | Date: {today_session.class_date} | Status: {today_session.status}")
        
        # 4. Remove any existing attendance record for student 21080001 on today_session so they can check in fresh!
        existing_att = session.exec(
            select(Attendance).where(
                Attendance.class_session_id == today_session.class_session_id,
                Attendance.student_id == 21080001
            )
        ).first()
        if existing_att:
            session.delete(existing_att)
            session.commit()
            print("Cleared existing attendance record for fresh check-in test!")
            
        print("🎉 SUCCESS! Today attendance demo scenario setup complete!")

if __name__ == "__main__":
    main()
