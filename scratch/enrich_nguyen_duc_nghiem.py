import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from datetime import date, datetime, time, timedelta

from sqlmodel import Session, select, text

from app.core.db import engine
from app.models import (
    Appeal,
    Attendance,
    ClassSession,
    CourseRegistration,
    Student,
)


def main():
    with Session(engine) as session:
        student_id = 21080001  # Nguyễn Đức Nghiêm
        print(
            f"Enriching database data for Student ID {student_id} (Nguyễn Đức Nghiêm)..."
        )

        # 1. Update Student profile info
        st = session.get(Student, student_id)
        if st:
            st.phone = "0988776655"
            st.gender = "NAM"
            session.add(st)
            session.commit()

        # 2. Ensure registered in ClassSections 1, 2, 3
        for cs_id in [1, 2, 3]:
            reg = session.exec(
                select(CourseRegistration).where(
                    CourseRegistration.class_section_id == cs_id,
                    CourseRegistration.student_id == student_id,
                )
            ).first()
            if not reg:
                session.add(
                    CourseRegistration(
                        class_section_id=cs_id, student_id=student_id, status=True
                    )
                )
        session.commit()

        # 3. Add rich past attendance records across sessions
        past_sessions = session.exec(
            select(ClassSession).where(ClassSession.class_date < date(2026, 6, 29))
        ).all()
        for idx, sess in enumerate(past_sessions):
            att = session.exec(
                select(Attendance).where(
                    Attendance.class_session_id == sess.class_session_id,
                    Attendance.student_id == student_id,
                )
            ).first()
            # Alternating statuses to show nice history: CO_MAT, DI_MUON, CO_MAT, VANG...
            status_cycle = ["CO_MAT", "CO_MAT", "DI_MUON", "CO_MAT", "VANG"]
            chosen_status = status_cycle[idx % len(status_cycle)]

            if not att:
                session.add(
                    Attendance(
                        student_id=student_id,
                        class_session_id=sess.class_session_id,
                        status=chosen_status,
                        method="KHUON_MAT" if chosen_status != "VANG" else "TU_DONG",
                        confidence=0.96 if chosen_status != "VANG" else None,
                        attendance_time=datetime.combine(
                            sess.class_date,
                            time(7, 32 if chosen_status == "CO_MAT" else 7, 48),
                        ),
                    )
                )
            else:
                att.status = chosen_status
                session.add(att)
        session.commit()

        # 4. Ensure an Appeal record exists for testing claims
        att_absent = session.exec(
            select(Attendance).where(
                Attendance.student_id == student_id, Attendance.status == "VANG"
            )
        ).first()
        if att_absent:
            existing_appeal = session.exec(
                select(Appeal).where(Appeal.attendance_id == att_absent.attendance_id)
            ).first()
            if not existing_appeal:
                session.exec(
                    text(
                        "SELECT setval('appeals_appeal_id_seq', (SELECT COALESCE(MAX(appeal_id), 0) + 1 FROM appeals), false);"
                    )
                )
                session.add(
                    Appeal(
                        attendance_id=att_absent.attendance_id,
                        student_id=student_id,
                        reason="Hôm đó em bị sốt cao có giấy khám của y tế trường, xin thầy duyệt lại chuyên cần giúp em.",
                        status="CHO_XU_LY",
                        submission_date=datetime.now() - timedelta(days=1),
                    )
                )
                session.commit()

        print("Data enrichment for Nguyễn Đức Nghiêm completed successfully!")


if __name__ == "__main__":
    main()
