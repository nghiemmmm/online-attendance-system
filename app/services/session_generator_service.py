"""
Session generator service.

Provides business logic to automatically deduce and populate class sessions
based on course credits, timetable weekday, and start/end dates.
"""

from datetime import date, timedelta

from sqlmodel import Session, select

from app.models import ClassSection, ClassSession, Course, Timetable


def generate_sessions_for_class_section(
    *,
    session: Session,
    class_section_id: int,
) -> int:
    """
    Deduce and auto-generate class sessions for a class section.

    Returns:
        Number of newly inserted class session records.
    """
    class_section = session.get(ClassSection, class_section_id)
    if not class_section:
        return 0

    course = session.get(Course, class_section.course_id)
    if not course:
        return 0

    timetable = session.exec(
        select(Timetable).where(Timetable.class_section_id == class_section_id)
    ).first()

    # Fallback default dates if timetable is missing
    start_date = (
        timetable.start_date if timetable and timetable.start_date else date(2026, 2, 2)
    )
    end_date = (
        timetable.end_date if timetable and timetable.end_date else date(2026, 5, 31)
    )
    # Target weekday (1=Monday, 7=Sunday in standard ISOWEEKDAY)
    target_weekday = timetable.weekday if timetable and timetable.weekday else 1
    start_time = timetable.start_time if timetable else None
    end_time = timetable.end_time if timetable else None

    # Credit-to-sessions calculation: 1 credit = 15 periods. Default 3 periods/session.
    credit_count = course.credit_count or 3
    total_lessons = credit_count * 15
    max_sessions = max(1, round(total_lessons / 3))

    # Check existing sessions to prevent duplicates
    existing_sessions = session.exec(
        select(ClassSession).where(ClassSession.class_section_id == class_section_id)
    ).all()
    existing_dates = {s.class_date for s in existing_sessions}
    existing_max_number = max(
        [s.session_number for s in existing_sessions if s.session_number], default=0
    )

    inserted_count = 0
    current_date = start_date
    session_num = existing_max_number + 1

    while current_date <= end_date and session_num <= max_sessions:
        # Check if current_date matches target weekday (isoweekday: Mon=1, Sun=7)
        if (
            current_date.isoweekday() == target_weekday
            and current_date not in existing_dates
        ):
            new_session = ClassSession(
                class_section_id=class_section_id,
                class_date=current_date,
                start_time=start_time,
                end_time=end_time,
                session_number=session_num,
                late_grace_minutes=15,
                recognition_threshold=0.6,
                status="CHUA_DIEM_DANH",
                note=f"Buổi {session_num} (Tự động khởi tạo)",
            )
            session.add(new_session)
            existing_dates.add(current_date)
            inserted_count += 1
            session_num += 1
        current_date += timedelta(days=1)

    if inserted_count > 0:
        session.commit()

    return inserted_count
