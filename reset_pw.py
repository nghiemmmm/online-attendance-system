from app.core.security import get_password_hash
from app.core.db import engine
from sqlmodel import Session, text

hash_val = get_password_hash('password')
with Session(engine) as session:
    session.exec(text(f"UPDATE taikhoan SET mat_khau_hash = '{hash_val}'"))
    session.commit()
    print('Updated all passwords to password')
