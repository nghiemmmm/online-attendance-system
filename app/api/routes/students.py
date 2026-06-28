"""
Sinh vien router.

Defines APIs for managing student profiles.
"""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.deps import SessionDep, get_current_active_superuser, get_current_active_student, CurrentAccount
from app.models import (
    Message,
    StudentCreate,
    StudentPublic,
    StudentsPublic,
    StudentUpdate,
    StudentSchedulePublic,
    StudentAttendancePublic,
    StudentAvailableClassPublic,
    AbsenceWarningsPublic,
)
from app.services import student_service

router = APIRouter(prefix="/students", tags=["students"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=StudentsPublic,
)
def read_students(
    session: SessionDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    q: Annotated[str | None, Query(max_length=100)] = None,
    major_id: Annotated[int | None, Query(ge=1)] = None,
    academic_status: bool | None = None,
) -> StudentsPublic:
    """Lay danh sach sinh vien, last_name tro phan trang, tim kiem va loc."""
    students, count = student_service.list_students(
        session=session,
        skip=skip,
        limit=limit,
        q=q,
        major_id=major_id,
        academic_status=academic_status,
    )
    return StudentsPublic(data=students, count=count)


@router.get(
    "/me/schedules",
    dependencies=[Depends(get_current_active_student)],
    response_model=StudentSchedulePublic,
)
def get_my_schedule(session: SessionDep, current_account: CurrentAccount) -> Any:
    """Sinh viên xem lịch học của mình."""
    return student_service.get_my_schedule(
        session=session,
        account_id=current_account.account_id,
    )


@router.get(
    "/me/attendance",
    dependencies=[Depends(get_current_active_student)],
    response_model=StudentAttendancePublic,
)
def get_my_attendance(session: SessionDep, current_account: CurrentAccount) -> Any:
    """Sinh viên xem lịch sử điểm danh."""
    return student_service.get_my_attendance(
        session=session,
        account_id=current_account.account_id,
    )


@router.get(
    "/me/warnings",
    dependencies=[Depends(get_current_active_student)],
    response_model=AbsenceWarningsPublic,
)
def get_my_warnings(session: SessionDep, current_account: CurrentAccount) -> Any:
    """Sinh viên xem các cảnh báo vắng mặt."""
    return student_service.get_my_warnings(
        session=session,
        account_id=current_account.account_id,
    )


@router.get(
    "/{student_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=StudentPublic,
)
def read_student(
    session: SessionDep,
    student_id: Annotated[int, Path(ge=1)],
) -> StudentPublic:
    """Lay chi tiet mot sinh vien theo ma sinh vien."""
    return student_service.get_student_or_404(
        session=session,
        student_id=student_id,
    )


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=StudentPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_student(
    *,
    session: SessionDep,
    student_in: StudentCreate,
) -> StudentPublic:
    """Tao last_name so sinh vien moi."""
    return student_service.create_student(
        session=session,
        item_in=student_in,
    )


@router.patch(
    "/{student_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=StudentPublic,
)
def update_student(
    *,
    session: SessionDep,
    student_id: Annotated[int, Path(ge=1)],
    student_in: StudentUpdate,
) -> StudentPublic:
    """Cap nhat mot phan thong tin sinh vien."""
    return student_service.update_student(
        session=session,
        student_id=student_id,
        item_in=student_in,
    )


@router.delete(
    "/{student_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=Message,
)
def delete_student(
    session: SessionDep,
    student_id: Annotated[int, Path(ge=1)],
) -> Message:
    """Xoa last_name so sinh vien theo ma sinh vien."""
    return student_service.delete_student(
        session=session,
        student_id=student_id,
    )


@router.get(
    "/me/class-sections-available",
    dependencies=[Depends(get_current_active_student)],
    response_model=StudentAvailableClassPublic,
)
def get_available_class_sections(
    session: SessionDep,
    current_account: CurrentAccount,
    semester: int | None = None,
    academic_year: str | None = None,
) -> Any:
    """Lấy danh sách lớp học phần có sẵn và đánh dấu xem sinh viên hiện tại đã đăng ký chưa."""
    return student_service.get_available_class_sections(
        session=session,
        account_id=current_account.account_id,
        semester=semester,
        academic_year=academic_year,
    )


@router.post(
    "/me/course-registrations",
    dependencies=[Depends(get_current_active_student)],
    response_model=Message,
    status_code=status.HTTP_201_CREATED,
)
def register_my_class_section(
    session: SessionDep,
    current_account: CurrentAccount,
    class_section_id: int,
) -> Any:
    """Sinh viên tự đăng ký lớp học phần."""
    return student_service.register_my_class_section(
        session=session,
        account_id=current_account.account_id,
        class_section_id=class_section_id,
    )


@router.delete(
    "/me/course-registrations/{class_section_id}",
    dependencies=[Depends(get_current_active_student)],
    response_model=Message,
)
def cancel_my_class_section(
    session: SessionDep,
    current_account: CurrentAccount,
    class_section_id: int,
) -> Any:
    """Sinh viên tự hủy đăng ký lớp học phần."""
    return student_service.cancel_my_class_section(
        session=session,
        account_id=current_account.account_id,
        class_section_id=class_section_id,
    )
