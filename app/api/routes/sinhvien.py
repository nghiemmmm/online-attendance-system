"""
Sinh vien router.

Defines APIs for managing student profiles.
"""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.deps import SessionDep, get_current_active_superuser, get_current_active_student, CurrentAccount
from app.models import (
    Message,
    SinhVienCreate,
    SinhVienPublic,
    SinhViensPublic,
    SinhVienUpdate,
    StudentSchedulePublic,
    StudentAttendancePublic,
    StudentAvailableClassPublic,
    CanhBaoVangPublic,
)
from app.services import student_service

router = APIRouter(prefix="/sinh-vien", tags=["sinh-vien"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=SinhViensPublic,
)
def read_students(
    session: SessionDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    q: Annotated[str | None, Query(max_length=100)] = None,
    ma_nganh: Annotated[int | None, Query(ge=1)] = None,
    trang_thai_hoc: bool | None = None,
) -> SinhViensPublic:
    """Lay danh sach sinh vien, ho tro phan trang, tim kiem va loc."""
    sinh_viens, count = student_service.list_students(
        session=session,
        skip=skip,
        limit=limit,
        q=q,
        ma_nganh=ma_nganh,
        trang_thai_hoc=trang_thai_hoc,
    )
    return SinhViensPublic(data=sinh_viens, count=count)


@router.get(
    "/me/lich-hoc",
    dependencies=[Depends(get_current_active_student)],
    response_model=StudentSchedulePublic,
)
def get_my_schedule(session: SessionDep, current_account: CurrentAccount) -> Any:
    """Sinh viên xem lịch học của mình."""
    return student_service.get_my_schedule(
        session=session,
        ma_tai_khoan=current_account.ma_tai_khoan,
    )


@router.get(
    "/me/diem-danh",
    dependencies=[Depends(get_current_active_student)],
    response_model=StudentAttendancePublic,
)
def get_my_attendance(session: SessionDep, current_account: CurrentAccount) -> Any:
    """Sinh viên xem lịch sử điểm danh."""
    return student_service.get_my_attendance(
        session=session,
        ma_tai_khoan=current_account.ma_tai_khoan,
    )


@router.get(
    "/me/canh-bao",
    dependencies=[Depends(get_current_active_student)],
    response_model=CanhBaoVangPublic,
)
def get_my_warnings(session: SessionDep, current_account: CurrentAccount) -> Any:
    """Sinh viên xem các cảnh báo vắng mặt."""
    return student_service.get_my_warnings(
        session=session,
        ma_tai_khoan=current_account.ma_tai_khoan,
    )


@router.get(
    "/{ma_sinh_vien}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=SinhVienPublic,
)
def read_student(
    session: SessionDep,
    ma_sinh_vien: Annotated[int, Path(ge=1)],
) -> SinhVienPublic:
    """Lay chi tiet mot sinh vien theo ma sinh vien."""
    return student_service.get_student_or_404(
        session=session,
        ma_sinh_vien=ma_sinh_vien,
    )


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=SinhVienPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_student(
    *,
    session: SessionDep,
    sinh_vien_in: SinhVienCreate,
) -> SinhVienPublic:
    """Tao ho so sinh vien moi."""
    return student_service.create_student(
        session=session,
        item_in=sinh_vien_in,
    )


@router.patch(
    "/{ma_sinh_vien}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=SinhVienPublic,
)
def update_student(
    *,
    session: SessionDep,
    ma_sinh_vien: Annotated[int, Path(ge=1)],
    sinh_vien_in: SinhVienUpdate,
) -> SinhVienPublic:
    """Cap nhat mot phan thong tin sinh vien."""
    return student_service.update_student(
        session=session,
        ma_sinh_vien=ma_sinh_vien,
        item_in=sinh_vien_in,
    )


@router.delete(
    "/{ma_sinh_vien}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=Message,
)
def delete_student(
    session: SessionDep,
    ma_sinh_vien: Annotated[int, Path(ge=1)],
) -> Message:
    """Xoa ho so sinh vien theo ma sinh vien."""
    return student_service.delete_student(
        session=session,
        ma_sinh_vien=ma_sinh_vien,
    )


@router.get(
    "/me/lop-hoc-phan-available",
    dependencies=[Depends(get_current_active_student)],
    response_model=StudentAvailableClassPublic,
)
def get_available_class_sections(
    session: SessionDep,
    current_account: CurrentAccount,
    hoc_ky: int | None = None,
    nam_hoc: str | None = None,
) -> Any:
    """Lấy danh sách lớp học phần có sẵn và đánh dấu xem sinh viên hiện tại đã đăng ký chưa."""
    return student_service.get_available_class_sections(
        session=session,
        ma_tai_khoan=current_account.ma_tai_khoan,
        hoc_ky=hoc_ky,
        nam_hoc=nam_hoc,
    )


@router.post(
    "/me/dang-ky-hoc-phan",
    dependencies=[Depends(get_current_active_student)],
    response_model=Message,
    status_code=status.HTTP_201_CREATED,
)
def register_my_class_section(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_lop_hoc_phan: int,
) -> Any:
    """Sinh viên tự đăng ký lớp học phần."""
    return student_service.register_my_class_section(
        session=session,
        ma_tai_khoan=current_account.ma_tai_khoan,
        ma_lop_hoc_phan=ma_lop_hoc_phan,
    )


@router.delete(
    "/me/huy-dang-ky-hoc-phan/{ma_lop_hoc_phan}",
    dependencies=[Depends(get_current_active_student)],
    response_model=Message,
)
def cancel_my_class_section(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_lop_hoc_phan: int,
) -> Any:
    """Sinh viên tự hủy đăng ký lớp học phần."""
    return student_service.cancel_my_class_section(
        session=session,
        ma_tai_khoan=current_account.ma_tai_khoan,
        ma_lop_hoc_phan=ma_lop_hoc_phan,
    )
