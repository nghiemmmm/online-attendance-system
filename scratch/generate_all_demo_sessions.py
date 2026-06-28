import sys
from sqlmodel import Session, select
from app.core.db import engine
from app.models import ClassSection
from app.services.session_generator_service import generate_sessions_for_class_section

from sqlalchemy import text

def main():
    with Session(engine) as session:
        session.exec(text("SELECT setval('class_sessions_class_session_id_seq', (SELECT COALESCE(MAX(class_session_id), 0) + 1 FROM class_sessions), false);"))
        session.commit()
        sections = session.exec(select(ClassSection)).all()
        print(f"Found {len(sections)} class sections.")
        for sec in sections:
            count = generate_sessions_for_class_section(session=session, class_section_id=sec.class_section_id)
            print(f"Generated {count} new sessions for ClassSection ID {sec.class_section_id}.")

if __name__ == "__main__":
    main()
