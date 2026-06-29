import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from sqlmodel import Session, text
from app.core.db import engine

def main():
    with Session(engine) as session:
        res = session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'auditlog'")).all()
        print("Auditlog columns:", [r[0] for r in res])

if __name__ == "__main__":
    main()
