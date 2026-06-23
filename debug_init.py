
from app.core.db import engine
from sqlmodel import Session, text

with Session(engine) as session:
    res = session.exec(text('SELECT count(*) FROM taikhoan')).first()
    print(f'Count in taikhoan: {res}')

