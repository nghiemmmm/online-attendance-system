
from app.core.db import engine
from sqlmodel import Session, select
from app.models import TaiKhoan

with Session(engine) as session:
    users = session.exec(select(TaiKhoan)).all()
    for u in users:
        print(f'User: {u.ten_dang_nhap}')

