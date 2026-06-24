from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, func, select

from app import crud
from app.api.deps import (
    CurrentAccount,
    SessionDep,
    get_current_active_superuser,
)
from app.core.security import get_password_hash, verify_password
from app.models import (
    Message,
    TaiKhoan,
    TaiKhoanCreate,
    TaiKhoanListPublic,
    TaiKhoanProfile,
    TaiKhoanPublic,
    TaiKhoanRegister,
    TaiKhoanUpdate,
    UpdatePassword,
    SinhVien,
    CanBo,
    AnhKhuonMat,
    Nganh,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=TaiKhoanListPublic,
)
def read_accounts(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    count_statement = select(func.count()).select_from(TaiKhoan)
    count = session.exec(count_statement).one()

    statement = (
        select(TaiKhoan)
        .order_by(col(TaiKhoan.ngay_tao).desc())
        .offset(skip)
        .limit(limit)
    )
    accounts = session.exec(statement).all()
    accounts_public = [TaiKhoanPublic.model_validate(account) for account in accounts]
    return TaiKhoanListPublic(data=accounts_public, count=count)


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=TaiKhoanPublic,
)
def create_account(*, session: SessionDep, account_in: TaiKhoanCreate) -> Any:
    account = crud.get_account_by_username(
        session=session, ten_dang_nhap=account_in.ten_dang_nhap
    )
    if account:
        raise HTTPException(
            status_code=400,
            detail="The account with this username already exists",
        )
    return crud.create_account(session=session, account_create=account_in)


@router.post("/signup", response_model=TaiKhoanPublic)
def register_account(session: SessionDep, account_in: TaiKhoanRegister) -> Any:
    account = crud.get_account_by_username(
        session=session, ten_dang_nhap=account_in.ten_dang_nhap
    )
    if account:
        raise HTTPException(
            status_code=400,
            detail="The account with this username already exists",
        )
    account_create = TaiKhoanCreate.model_validate(account_in)
    db_account = crud.create_account(session=session, account_create=account_create)
    
    # Auto create a linked student profile if details are provided
    if account_in.vai_tro == "SINH_VIEN" and account_in.ho and account_in.ten:
        from app.models import SinhVien, Nganh
        
        nganh = session.exec(select(Nganh)).first()
        if not nganh:
            nganh = Nganh(ten_nganh="Công nghệ thông tin", mo_ta="Mặc định")
            session.add(nganh)
            session.commit()
            session.refresh(nganh)
            
        db_sinhvien = SinhVien(
            ho=account_in.ho,
            ten=account_in.ten,
            google_email=account_in.email,
            dien_thoai=account_in.dien_thoai,
            gioi_tinh=account_in.gioi_tinh,
            ma_nganh=nganh.ma_nganh,
            ma_tai_khoan=db_account.ma_tai_khoan
        )
        session.add(db_sinhvien)
        session.commit()
        session.refresh(db_sinhvien)
        
    return db_account


@router.get("/me", response_model=TaiKhoanPublic)
def read_account_me(current_account: CurrentAccount) -> Any:
    return current_account


@router.get("/me/profile", response_model=TaiKhoanProfile)
def read_account_profile(session: SessionDep, current_account: CurrentAccount) -> Any:
    return TaiKhoanProfile(
        tai_khoan=TaiKhoanPublic.model_validate(current_account),
        profile=crud.get_account_profile(session=session, account=current_account),
    )


@router.patch("/me", response_model=TaiKhoanPublic)
def update_account_me(
    *, session: SessionDep, account_in: TaiKhoanUpdate, current_account: CurrentAccount
) -> Any:
    if account_in.ten_dang_nhap:
        existing_account = crud.get_account_by_username(
            session=session, ten_dang_nhap=account_in.ten_dang_nhap
        )
        if (
            existing_account
            and existing_account.ma_tai_khoan != current_account.ma_tai_khoan
        ):
            raise HTTPException(status_code=409, detail="Username already exists")

    account_in = TaiKhoanUpdate(
        ten_dang_nhap=account_in.ten_dang_nhap,
        password=account_in.password,
    )
    return crud.update_account(
        session=session, db_account=current_account, account_in=account_in
    )


@router.patch("/me/password", response_model=Message)
def update_password_me(
    *, session: SessionDep, body: UpdatePassword, current_account: CurrentAccount
) -> Any:
    if not verify_password(body.current_password, current_account.mat_khau_hash):
        raise HTTPException(status_code=400, detail="Incorrect password")
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=400, detail="New password cannot be the same as the current one"
        )
    current_account.mat_khau_hash = get_password_hash(body.new_password)
    session.add(current_account)
    session.commit()
    return Message(message="Password updated successfully")


@router.get(
    "/profiles",
    dependencies=[Depends(get_current_active_superuser)],
)
def read_user_profiles(
    session: SessionDep,
    role: str | None = None,
    status: str | None = None,
    q: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Lấy danh sách tài khoản hệ thống kèm thông tin hồ sơ cho Admin."""
    statement = select(TaiKhoan)
    
    if role and role != "all":
        db_roles = []
        if role == "student":
            db_roles = ["SINH_VIEN"]
        elif role == "lecturer":
            db_roles = ["GIANG_VIEN", "CAN_BO"]
        elif role == "admin":
            db_roles = ["ADMIN"]
        else:
            db_roles = [role]
        statement = statement.where(TaiKhoan.vai_tro.in_(db_roles))
        
    if status and status != "all":
        db_status = True if status == "active" else False
        statement = statement.where(TaiKhoan.trang_thai == db_status)
        
    accounts = session.exec(statement.order_by(col(TaiKhoan.ngay_tao).desc())).all()
    
    data = []
    for acc in accounts:
        profile_data = {}
        if acc.vai_tro == "SINH_VIEN":
            sv = session.exec(select(SinhVien).where(SinhVien.ma_tai_khoan == acc.ma_tai_khoan)).first()
            if sv:
                profile_data = {
                    "name": f"{sv.ho} {sv.ten}".strip(),
                    "studentId": sv.ma_sinh_vien,
                    "google_email": sv.google_email,
                    "dien_thoai": sv.dien_thoai,
                    "gioi_tinh": sv.gioi_tinh
                }
        elif acc.vai_tro in ["GIANG_VIEN", "CAN_BO"]:
            cb = session.exec(select(CanBo).where(CanBo.ma_tai_khoan == acc.ma_tai_khoan)).first()
            if cb:
                profile_data = {
                    "name": f"{cb.ho} {cb.ten}".strip(),
                    "google_email": cb.google_email,
                    "dien_thoai": cb.dien_thoai,
                    "gioi_tinh": cb.gioi_tinh
                }
                
        name = profile_data.get("name", "") or ""
        email = profile_data.get("google_email", "") or acc.ten_dang_nhap or ""
        student_id_str = str(profile_data.get("studentId", ""))
        
        if q:
            q_lower = q.lower()
            if q_lower not in name.lower() and q_lower not in email.lower() and q_lower not in student_id_str.lower():
                continue
                
        # Kiểm tra đã đăng ký khuôn mặt chưa
        face_count = 0
        if acc.vai_tro == "SINH_VIEN" and profile_data.get("studentId"):
            face_count = session.exec(
                select(func.count(AnhKhuonMat.ma_anh))
                .where(AnhKhuonMat.ma_sinh_vien == profile_data.get("studentId"))
            ).first() or 0
            
        data.append({
            "id": acc.ma_tai_khoan,
            "name": name or acc.ten_dang_nhap,
            "email": email,
            "role": "student" if acc.vai_tro == "SINH_VIEN" else "lecturer" if acc.vai_tro in ["GIANG_VIEN", "CAN_BO"] else "admin",
            "status": "active" if acc.trang_thai else "locked",
            "createdAt": acc.ngay_tao.strftime("%d/%m/%Y") if acc.ngay_tao else "N/A",
            "lastLogin": acc.lan_dang_nhap_cuoi.strftime("%d/%m/%Y") if acc.lan_dang_nhap_cuoi else "N/A",
            "studentId": student_id_str if acc.vai_tro == "SINH_VIEN" else None,
            "faceDataStatus": "approved" if face_count > 0 else "none",
        })
        
    paginated_data = data[skip : skip + limit]
    return {"data": paginated_data, "count": len(data)}


@router.get("/{account_id}", response_model=TaiKhoanPublic)
def read_account_by_id(
    account_id: int, session: SessionDep, current_account: CurrentAccount
) -> Any:
    account = session.get(TaiKhoan, account_id)
    if account == current_account:
        return account
    if current_account.vai_tro != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="The account doesn't have enough privileges",
        )
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.patch(
    "/{account_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=TaiKhoanPublic,
)
def update_account(
    *,
    session: SessionDep,
    account_id: int,
    account_in: TaiKhoanUpdate,
) -> Any:
    db_account = session.get(TaiKhoan, account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    if account_in.ten_dang_nhap:
        existing_account = crud.get_account_by_username(
            session=session, ten_dang_nhap=account_in.ten_dang_nhap
        )
        if existing_account and existing_account.ma_tai_khoan != account_id:
            raise HTTPException(status_code=409, detail="Username already exists")

    return crud.update_account(
        session=session, db_account=db_account, account_in=account_in
    )


@router.delete("/{account_id}", dependencies=[Depends(get_current_active_superuser)])
def delete_account(
    session: SessionDep, current_account: CurrentAccount, account_id: int
) -> Message:
    account = session.get(TaiKhoan, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if account == current_account:
        raise HTTPException(
            status_code=403, detail="Admin accounts cannot delete themselves"
        )
    session.delete(account)
    session.commit()
    return Message(message="Account deleted successfully")


from pydantic import BaseModel


class UserWithProfileCreate(BaseModel):
    ten_dang_nhap: str
    password: str
    vai_tro: str  # student, lecturer, admin
    ho: str
    ten: str
    dien_thoai: str | None = None
    gioi_tinh: str | None = None




@router.post(
    "/with-profile",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=TaiKhoanPublic,
)
def create_account_with_profile(
    *,
    session: SessionDep,
    payload: UserWithProfileCreate,
) -> Any:
    """Tạo đồng thời cả tài khoản đăng nhập lẫn hồ sơ sinh viên/giảng viên."""
    # Kiểm tra trùng tên đăng nhập
    account = crud.get_account_by_username(
        session=session, ten_dang_nhap=payload.ten_dang_nhap
    )
    if account:
        raise HTTPException(
            status_code=400,
            detail="The account with this username already exists",
        )
        
    # Map role
    db_role = "SINH_VIEN"
    if payload.vai_tro == "lecturer":
        db_role = "GIANG_VIEN"
    elif payload.vai_tro == "admin":
        db_role = "ADMIN"
        
    # Tạo tài khoản
    db_account = TaiKhoan(
        ten_dang_nhap=payload.ten_dang_nhap,
        mat_khau_hash=get_password_hash(payload.password),
        vai_tro=db_role,
        trang_thai=True,
    )
    session.add(db_account)
    session.commit()
    session.refresh(db_account)
    
    # Tạo hồ sơ đi kèm
    if db_role == "SINH_VIEN":
        nganh = session.exec(select(Nganh)).first()
        if not nganh:
            nganh = Nganh(ten_nganh="Công nghệ thông tin", mo_ta="Default")
            session.add(nganh)
            session.commit()
            session.refresh(nganh)
            
        db_sinhvien = SinhVien(
            ho=payload.ho,
            ten=payload.ten,
            google_email=payload.ten_dang_nhap,
            dien_thoai=payload.dien_thoai,
            gioi_tinh=payload.gioi_tinh,
            ma_nganh=nganh.ma_nganh,
            ma_tai_khoan=db_account.ma_tai_khoan
        )
        session.add(db_sinhvien)
        session.commit()
    elif db_role == "GIANG_VIEN":
        db_canbo = CanBo(
            ho=payload.ho,
            ten=payload.ten,
            google_email=payload.ten_dang_nhap,
            dien_thoai=payload.dien_thoai,
            gioi_tinh=payload.gioi_tinh,
            ma_tai_khoan=db_account.ma_tai_khoan,
            chuc_vu="Giảng viên"
        )
        session.add(db_canbo)
        session.commit()
        
    return db_account


@router.patch(
    "/{account_id}/toggle-status",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=TaiKhoanPublic,
)
def toggle_account_status(
    *,
    session: SessionDep,
    account_id: int,
) -> Any:
    """Khóa hoặc mở khóa tài khoản."""
    db_account = session.get(TaiKhoan, account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    db_account.trang_thai = not db_account.trang_thai
    session.add(db_account)
    session.commit()
    session.refresh(db_account)
    return db_account
