from sqlmodel import Session, text

from app.core.db import engine

with Session(engine) as session:
    res = session.exec(text("SELECT count(*) FROM taikhoan")).first()
    print(f"Count in taikhoan: {res}")
