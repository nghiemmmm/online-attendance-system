from sqlmodel import Session, text
from app.core.db import engine

def main():
    with Session(engine) as session:
        res = session.exec(text("SELECT setval('class_sessions_class_session_id_seq', (SELECT MAX(class_session_id) FROM class_sessions));")).first()
        session.commit()
        print("Sequence synced! New val:", res)

if __name__ == "__main__":
    main()
