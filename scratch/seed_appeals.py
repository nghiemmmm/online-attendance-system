from datetime import datetime, date, timezone
from sqlmodel import Session, select, text
from app.core.db import engine
from app.models import ClassSession, Attendance, Appeal, Student, CourseRegistration

def main():
    with Session(engine) as session:
        # Check class sections owned by TS. Nguyễn Văn An (staff_id 2101)
        session_item = session.exec(
            select(ClassSession).where(ClassSession.class_section_id == 1).order_by(ClassSession.class_session_id)
        ).first()
        
        if not session_item:
            print("No class session found for class_section_id 1")
            return
        
        # Check students registered for class_section_id 1
        regs = session.exec(
            select(CourseRegistration).where(CourseRegistration.class_section_id == 1)
        ).all()
        
        student_ids = [r.student_id for r in regs]
        print("Registered student IDs:", student_ids)
        
        if not student_ids:
            student_ids = [21080001, 21080002]
            
        # Ensure attendance records exist with status VANG for these students
        attendance_ids = []
        for st_id in student_ids:
            att = session.exec(
                select(Attendance).where(
                    Attendance.class_session_id == session_item.class_session_id,
                    Attendance.student_id == st_id
                )
            ).first()
            
            if not att:
                # Sync attendance sequence
                session.exec(text("SELECT setval('attendance_attendance_id_seq', (SELECT COALESCE(MAX(attendance_id), 0) + 1 FROM attendance), false);"))
                att = Attendance(
                    class_session_id=session_item.class_session_id,
                    student_id=st_id,
                    status="VANG",
                    created_at=datetime.now(timezone.utc)
                )
                session.add(att)
                session.commit()
                session.refresh(att)
            else:
                att.status = "VANG"
                session.add(att)
                session.commit()
                session.refresh(att)
            
            attendance_ids.append((att.attendance_id, st_id))
            
        print("Attendance IDs for appeal seeding:", attendance_ids)
        
        # Sync appeals sequence
        session.exec(text("SELECT setval('appeals_appeal_id_seq', (SELECT COALESCE(MAX(appeal_id), 0) + 1 FROM appeals), false);"))
        
        # Clear existing pending appeals for clean demo if any
        existing_appeals = session.exec(select(Appeal).where(Appeal.status == "CHO_XU_LY")).all()
        for ea in existing_appeals:
            session.delete(ea)
        session.commit()
        
        # Create fresh demo appeals for TS. Nguyễn Văn An
        reasons = [
            "Em bị hỏng xe trên đường đến trường, xin Thầy điểm danh lại giúp em ạ.",
            "Em có giấy đi khám bệnh tại bệnh viện trường, em xin phép nộp minh chứng điểm danh bù ạ.",
            "Hệ thống AI lúc vào lớp quét bị lỗi mạng không ghi nhận, em có mặt suốt buổi học ạ."
        ]
        
        created_count = 0
        for idx, (att_id, st_id) in enumerate(attendance_ids):
            appeal_item = Appeal(
                attendance_id=att_id,
                student_id=st_id,
                reason=reasons[idx % len(reasons)],
                status="CHO_XU_LY",
                submitted_at=datetime.now(timezone.utc)
            )
            session.add(appeal_item)
            created_count += 1
            
        session.commit()
        print(f"Successfully created {created_count} demo appeals for TS. Nguyễn Văn An (gv2101)!")

if __name__ == "__main__":
    main()
