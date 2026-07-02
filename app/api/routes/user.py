from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import Field, field_validator

from app.api.deps import (
    CurrentAccount,
    SessionDep,
    get_current_active_superuser,
)
from app.models import (
    Message,
    Account,
    AccountCreate,
    AccountListPublic,
    AccountProfile,
    AccountPublic,
    AccountRegister,
    AccountUpdate,
    UpdatePassword,
    SendOtpRequest,
    StudentRegisterRequest,
)
from app.models.base import AppBaseModel
from app.services.user_service import UserService, get_user_service
from app.services.otp_service import generate_and_send_otp

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=AccountListPublic,
)
def read_accounts(
    skip: int = 0,
    limit: int = 100,
    service: UserService = Depends(get_user_service),
) -> Any:
    result = service.read_accounts(skip=skip, limit=limit)
    accounts_public = [AccountPublic.model_validate(account) for account in result["data"]]
    return AccountListPublic(data=accounts_public, count=result["count"])


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=AccountPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_account(
    *,
    account_in: AccountCreate,
    service: UserService = Depends(get_user_service),
) -> Any:
    return service.create_account(account_in=account_in)


@router.post("/send-otp")
def send_otp(
    payload: SendOtpRequest,
    session: SessionDep,
) -> Any:
    """Gửi mã OTP xác thực đăng ký tài khoản sinh viên qua Email."""
    return generate_and_send_otp(
        session=session,
        mssv=payload.mssv,
        email=payload.email,
    )


@router.post(
    "/registrations",
    response_model=AccountPublic,
    status_code=status.HTTP_201_CREATED,
)
def register_account(
    payload: StudentRegisterRequest,
    service: UserService = Depends(get_user_service),
) -> Any:
    """Đăng ký tài khoản sinh viên mới bằng MSSV, Email và OTP."""
    return service.register_student_with_otp(payload=payload)


@router.get("/me", response_model=AccountPublic)
def read_account_me(current_account: CurrentAccount) -> Any:
    return current_account


@router.get("/me/profile", response_model=AccountProfile)
def read_account_profile(
    session: SessionDep,
    current_account: CurrentAccount,
) -> Any:
    # Bọc lấy profile qua crud hiện tại
    from app import crud
    return AccountProfile(
        account=AccountPublic.model_validate(current_account),
        profile=crud.get_account_profile(session=session, account=current_account),
    )


@router.patch("/me", response_model=AccountPublic)
def update_account_me(
    *,
    account_in: AccountUpdate,
    current_account: CurrentAccount,
    service: UserService = Depends(get_user_service),
) -> Any:
    return service.update_account_me(current_account=current_account, account_in=account_in)


@router.patch("/me/password", response_model=Message)
def update_password_me(
    body: UpdatePassword,
    current_account: CurrentAccount,
    service: UserService = Depends(get_user_service),
) -> Any:
    service.update_password_me(current_account=current_account, body=body)
    return Message(message="Password updated successfully")


@router.get(
    "/profiles",
    dependencies=[Depends(get_current_active_superuser)],
)
def read_user_profiles(
    role: str | None = None,
    status: str | None = None,
    q: str | None = None,
    skip: int = 0,
    limit: int = 100,
    service: UserService = Depends(get_user_service),
) -> Any:
    """Lấy danh sách tài khoản hệ thống kèm thông tin hồ sơ cho Admin."""
    return service.read_user_profiles(
        role=role,
        status=status,
        q=q,
        skip=skip,
        limit=limit,
    )


@router.get("/{account_id}", response_model=AccountPublic)
def read_account_by_id(
    account_id: int,
    session: SessionDep,
    current_account: CurrentAccount,
) -> Any:
    account = session.get(Account, account_id)
    if account == current_account:
        return account
    if current_account.role != "ADMIN":
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
    response_model=AccountPublic,
)
def update_account(
    *,
    account_id: int,
    account_in: AccountUpdate,
    service: UserService = Depends(get_user_service),
) -> Any:
    return service.update_account(account_id=account_id, account_in=account_in)


@router.delete("/me", response_model=Message)
def delete_user_me(
    current_account: CurrentAccount,
    service: UserService = Depends(get_user_service),
) -> Message:
    """Xóa tài khoản hiện tại."""
    service.delete_user_me(current_account=current_account)
    return Message(message="Account deleted successfully")


@router.delete("/{account_id}", dependencies=[Depends(get_current_active_superuser)])
def delete_account(
    current_account: CurrentAccount,
    account_id: int,
    service: UserService = Depends(get_user_service),
) -> Message:
    service.delete_account(current_account=current_account, account_id=account_id)
    return Message(message="Account deleted successfully")


class UserWithProfileCreate(AppBaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: str | None = Field(default=None, max_length=100)
    password: str = Field(min_length=5, max_length=128)
    role: str = Field(min_length=1, max_length=20)  # student, lecturer, admin
    last_name: str = Field(min_length=1, max_length=50)
    first_name: str = Field(min_length=1, max_length=50)
    phone: str | None = Field(default=None, max_length=15)
    gender: str | None = Field(default=None, max_length=10)

    @field_validator("role")
    @classmethod
    def _normalize_role(cls, value: str) -> str:
        normalized = value.strip().lower()
        allowed_roles = {"student", "lecturer", "admin"}
        if normalized not in allowed_roles:
            raise ValueError("role must be student, lecturer, or admin")
        return normalized


@router.post(
    "/profiles",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=AccountPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_account_with_profile(
    *,
    payload: UserWithProfileCreate,
    service: UserService = Depends(get_user_service),
) -> Any:
    """Tạo đồng thời cả tài khoản đăng nhập lẫn hồ sơ sinh viên/giảng viên."""
    return service.create_account_with_profile(payload=payload)


@router.patch(
    "/{account_id}/status",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=AccountPublic,
)
def toggle_account_status(
    *,
    account_id: int,
    service: UserService = Depends(get_user_service),
) -> Any:
    """Khóa hoặc mở khóa tài khoản."""
    return service.toggle_account_status(account_id=account_id)
