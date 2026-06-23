from app.core.db import engine
from sqlmodel import Session, select
from app.models import TaiKhoan
from app.core.security import verify_password

with Session(engine) as session:
    user = session.exec(select(TaiKhoan).where(TaiKhoan.ten_dang_nhap == 'sv001@student.edu.vn')).first()
    if not user:
        print('User not found')
    else:
        print('User found:')
        print(f'hash: {user.mat_khau_hash}')
        print(f'locked: {user.thoi_gian_khoa}')
        print(f'failed attempts: {user.so_lan_dang_nhap_sai}')
        print(f'status: {user.trang_thai}')
        print(f'role: {user.vai_tro}')
        print(f'verify password: {verify_password("password", user.mat_khau_hash)}')
