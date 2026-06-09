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
    return crud.create_account(session=session, account_create=account_create)


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
