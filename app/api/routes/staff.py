"""
Can bo router.

Defines APIs for managing staff members and lecturer dashboards.
"""

from datetime import date
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.deps import (
    CurrentAccount,
    SessionDep,
    get_current_active_lecturer,
    get_current_active_superuser,
)
from app.models import (
    ActiveClassSectionCountPublic,
    Message,
    MonthlyAttendanceSummary,
    PendingAppealMetric,
    RecentClassSessionsPublic,
    StaffAttendanceReportItem,
    StaffClassSectionsPublic,
    StaffCreate,
    StaffMembersPublic,
    StaffPublic,
    StaffUpdate,
    TeachingSchedulesPublic,
)
from app.services import staff_service

router = APIRouter(prefix="/staff", tags=["staff"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=StaffMembersPublic,
)
def read_staff_members(
    session: SessionDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    q: Annotated[str | None, Query(max_length=100)] = None,
    status: bool | None = None,
) -> StaffMembersPublic:
    """
    Lấy danh sách cán bộ.

    Hỗ trợ phân trang, tìm kiếm theo họ/tên/email/chức vụ và lọc theo trạng thái.
    """
    staff_members, count = staff_service.list_staff_members(
        session=session,
        skip=skip,
        limit=limit,
        q=q,
        status=status,
    )
    return StaffMembersPublic(data=staff_members, count=count)


@router.get(
    "/me/teaching-schedule",
    dependencies=[Depends(get_current_active_lecturer)],
    response_model=TeachingSchedulesPublic,
)
def read_my_teaching_schedule(
    session: SessionDep,
    current_account: CurrentAccount,
    from_date: date | None = None,
    to_date: date | None = None,
    semester: Annotated[int | None, Query(ge=1, le=3)] = None,
    academic_year: Annotated[str | None, Query(max_length=20)] = None,
    status: bool | None = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
) -> Any:
    """Lấy lịch dạy của cán bộ đang đăng nhập."""
    return staff_service.read_my_teaching_schedule(
        session=session,
        account_id=current_account.account_id,
        from_date=from_date,
        to_date=to_date,
        semester=semester,
        academic_year=academic_year,
        status=status,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/me/class-sections",
    dependencies=[Depends(get_current_active_lecturer)],
    response_model=StaffClassSectionsPublic,
)
def read_my_class_sections(
    session: SessionDep,
    current_account: CurrentAccount,
) -> Any:
    """Lấy danh sách các lớp học phần cán bộ đang giảng dạy."""
    return staff_service.read_my_class_sections(
        session=session,
        account_id=current_account.account_id,
    )


@router.get(
    "/{staff_id}/teaching-schedule",
    dependencies=[Depends(get_current_active_lecturer)],
    response_model=TeachingSchedulesPublic,
)
def read_staff_teaching_schedule(
    session: SessionDep,
    current_account: CurrentAccount,
    staff_id: Annotated[int, Path(ge=1)],
    from_date: date | None = None,
    to_date: date | None = None,
    semester: Annotated[int | None, Query(ge=1, le=3)] = None,
    academic_year: Annotated[str | None, Query(max_length=20)] = None,
    status: bool | None = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
) -> TeachingSchedulesPublic:
    """Lấy lịch dạy của một cán bộ/giảng viên."""
    teaching_schedule, count = staff_service.read_staff_teaching_schedule(
        session=session,
        current_account_id=current_account.account_id,
        staff_id=staff_id,
        from_date=from_date,
        to_date=to_date,
        semester=semester,
        academic_year=academic_year,
        status=status,
        skip=skip,
        limit=limit,
    )
    return TeachingSchedulesPublic(data=teaching_schedule, count=count)


@router.get(
    "/{staff_id}/class-sessions/recent",
    dependencies=[Depends(get_current_active_lecturer)],
    response_model=RecentClassSessionsPublic,
)
def read_staff_recent_lessons(
    session: SessionDep,
    current_account: CurrentAccount,
    staff_id: Annotated[int, Path(ge=1)],
    limit: Annotated[int, Query(ge=1, le=20)] = 5,
) -> RecentClassSessionsPublic:
    """Lay danh sach buoi hoc gan day cua can bo kem thong ke diem danh."""
    class_sessions, count = staff_service.read_staff_recent_lessons(
        session=session,
        current_account_id=current_account.account_id,
        staff_id=staff_id,
        limit=limit,
    )
    return RecentClassSessionsPublic(data=class_sessions, count=count)


@router.get(
    "/{staff_id}/class-sections/active/count",
    dependencies=[Depends(get_current_active_lecturer)],
    response_model=ActiveClassSectionCountPublic,
)
def count_current_teaching_class_sections(
    session: SessionDep,
    current_account: CurrentAccount,
    staff_id: Annotated[int, Path(ge=1)],
    as_of_date: date | None = None,
) -> ActiveClassSectionCountPublic:
    count, semester, academic_year, target_date = (
        staff_service.count_current_teaching_class_sections(
            session=session,
            current_account_id=current_account.account_id,
            staff_id=staff_id,
            as_of_date=as_of_date,
        )
    )
    return ActiveClassSectionCountPublic(
        staff_id=staff_id,
        semester=semester,
        academic_year=academic_year,
        as_of_date=target_date,
        count=count,
    )


@router.get(
    "/{staff_id}/attendance/monthly-summary",
    dependencies=[Depends(get_current_active_lecturer)],
    response_model=MonthlyAttendanceSummary,
)
def read_monthly_attendance_summary(
    session: SessionDep,
    current_account: CurrentAccount,
    staff_id: Annotated[int, Path(ge=1)],
    reference_date: date | None = None,
) -> MonthlyAttendanceSummary:
    return staff_service.read_monthly_attendance_summary(
        session=session,
        current_account_id=current_account.account_id,
        staff_id=staff_id,
        reference_date=reference_date,
    )


@router.get(
    "/{staff_id}/appeals/pending/count",
    dependencies=[Depends(get_current_active_lecturer)],
    response_model=PendingAppealMetric,
)
def read_pending_appeal_count(
    session: SessionDep,
    current_account: CurrentAccount,
    staff_id: Annotated[int, Path(ge=1)],
) -> PendingAppealMetric:
    return staff_service.read_pending_appeal_count(
        session=session,
        current_account_id=current_account.account_id,
        staff_id=staff_id,
    )


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=StaffPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_staff_member(
    *,
    session: SessionDep,
    staff_in: StaffCreate,
) -> StaffPublic:
    """Tạo hồ sơ cán bộ mới."""
    return staff_service.create_staff_member(
        session=session,
        item_in=staff_in,
    )


@router.patch(
    "/{staff_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=StaffPublic,
)
def update_staff_member(
    *,
    session: SessionDep,
    staff_id: Annotated[int, Path(ge=1)],
    staff_in: StaffUpdate,
) -> StaffPublic:
    """Cập nhật một phần thông tin cán bộ."""
    return staff_service.update_staff_member(
        session=session,
        staff_id=staff_id,
        item_in=staff_in,
    )


@router.delete(
    "/{staff_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=Message,
)
def delete_staff_member(
    session: SessionDep,
    staff_id: Annotated[int, Path(ge=1)],
) -> Message:
    """Xóa hồ sơ cán bộ theo mã cán bộ."""
    return staff_service.delete_staff_member(
        session=session,
        staff_id=staff_id,
    )


@router.get(
    "/me/reports",
    dependencies=[Depends(get_current_active_lecturer)],
    response_model=list[StaffAttendanceReportItem],
)
def read_my_reports(
    session: SessionDep,
    current_account: CurrentAccount,
) -> Any:
    """Lấy danh sách báo cáo chuyên cần các lớp học giảng viên đang dạy."""
    return staff_service.read_my_reports(
        session=session,
        account_id=current_account.account_id,
    )


@router.get(
    "/{staff_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=StaffPublic,
)
def read_staff_member(
    session: SessionDep,
    staff_id: Annotated[int, Path(ge=1)],
) -> StaffPublic:
    """Lấy chi tiết một cán bộ theo mã cán bộ."""
    return staff_service.get_staff_member_or_404(
        session=session,
        staff_id=staff_id,
    )
