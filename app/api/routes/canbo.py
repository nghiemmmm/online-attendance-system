"""
Can bo router.

Defines APIs for managing staff members and lecturer dashboards.
"""

from datetime import date
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.deps import SessionDep, get_current_active_superuser, get_current_active_lecturer, CurrentAccount
from app.models import (
    BuoiHocGanDaysPublic,
    CanBoCreate,
    CanBoPublic,
    CanBosPublic,
    CanBoUpdate,
    LichDaysPublic,
    Message,
    MonthlyAttendanceSummary,
    KhieuNaiChoXuLyMetric,
    SoLuongLopHocPhanDangDayPublic,
    StaffClassSectionsPublic,
    StaffAttendanceReportItem,
)
from app.services import staff_service

router = APIRouter(prefix="/canbo", tags=["canbo"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=CanBosPublic,
)
def read_staff_members(
    session: SessionDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    q: Annotated[str | None, Query(max_length=100)] = None,
    trang_thai: bool | None = None,
) -> CanBosPublic:
    """
    Lấy danh sách cán bộ.

    Hỗ trợ phân trang, tìm kiếm theo họ/tên/email/chức vụ và lọc theo trạng thái.
    """
    can_bos, count = staff_service.list_staff_members(
        session=session,
        skip=skip,
        limit=limit,
        q=q,
        trang_thai=trang_thai,
    )
    return CanBosPublic(data=can_bos, count=count)


@router.get(
    "/me/lich-day",
    dependencies=[Depends(get_current_active_lecturer)],
    response_model=LichDaysPublic,
)
def read_my_teaching_schedule(
    session: SessionDep,
    current_account: CurrentAccount,
    from_date: date | None = None,
    to_date: date | None = None,
    hoc_ky: Annotated[int | None, Query(ge=1, le=3)] = None,
    nam_hoc: Annotated[str | None, Query(max_length=20)] = None,
    trang_thai: bool | None = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
) -> Any:
    """Lấy lịch dạy của cán bộ đang đăng nhập."""
    return staff_service.read_my_teaching_schedule(
        session=session,
        ma_tai_khoan=current_account.ma_tai_khoan,
        from_date=from_date,
        to_date=to_date,
        hoc_ky=hoc_ky,
        nam_hoc=nam_hoc,
        trang_thai=trang_thai,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/me/lop-hoc-phan",
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
        ma_tai_khoan=current_account.ma_tai_khoan,
    )


@router.get(
    "/{ma_can_bo}/lich-day",
    dependencies=[Depends(get_current_active_lecturer)],
    response_model=LichDaysPublic,
)
def read_staff_teaching_schedule(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_can_bo: Annotated[int, Path(ge=1)],
    from_date: date | None = None,
    to_date: date | None = None,
    hoc_ky: Annotated[int | None, Query(ge=1, le=3)] = None,
    nam_hoc: Annotated[str | None, Query(max_length=20)] = None,
    trang_thai: bool | None = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
) -> LichDaysPublic:
    """Lấy lịch dạy của một cán bộ/giảng viên."""
    lich_day, count = staff_service.read_staff_teaching_schedule(
        session=session,
        current_account_id=current_account.ma_tai_khoan,
        ma_can_bo=ma_can_bo,
        from_date=from_date,
        to_date=to_date,
        hoc_ky=hoc_ky,
        nam_hoc=nam_hoc,
        trang_thai=trang_thai,
        skip=skip,
        limit=limit,
    )
    return LichDaysPublic(data=lich_day, count=count)


@router.get(
    "/{ma_can_bo}/buoi-hoc/gan-day",
    dependencies=[Depends(get_current_active_lecturer)],
    response_model=BuoiHocGanDaysPublic,
)
def read_staff_recent_lessons(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_can_bo: Annotated[int, Path(ge=1)],
    limit: Annotated[int, Query(ge=1, le=20)] = 5,
) -> BuoiHocGanDaysPublic:
    """Lay danh sach buoi hoc gan day cua can bo kem thong ke diem danh."""
    buoi_hocs, count = staff_service.read_staff_recent_lessons(
        session=session,
        current_account_id=current_account.ma_tai_khoan,
        ma_can_bo=ma_can_bo,
        limit=limit,
    )
    return BuoiHocGanDaysPublic(data=buoi_hocs, count=count)


@router.get(
    "/{ma_can_bo}/lop-hoc-phan/dang-day/count",
    dependencies=[Depends(get_current_active_lecturer)],
    response_model=SoLuongLopHocPhanDangDayPublic,
)
def count_current_teaching_class_sections(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_can_bo: Annotated[int, Path(ge=1)],
    as_of_date: date | None = None,
) -> SoLuongLopHocPhanDangDayPublic:
    count, hoc_ky, nam_hoc, target_date = staff_service.count_current_teaching_class_sections(
        session=session,
        current_account_id=current_account.ma_tai_khoan,
        ma_can_bo=ma_can_bo,
        as_of_date=as_of_date,
    )
    return SoLuongLopHocPhanDangDayPublic(
        ma_can_bo=ma_can_bo,
        hoc_ky=hoc_ky,
        nam_hoc=nam_hoc,
        as_of_date=target_date,
        count=count,
    )


@router.get(
    "/{ma_can_bo}/attendance/monthly-summary",
    dependencies=[Depends(get_current_active_lecturer)],
    response_model=MonthlyAttendanceSummary,
)
def read_monthly_attendance_summary(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_can_bo: Annotated[int, Path(ge=1)],
    reference_date: date | None = None,
) -> MonthlyAttendanceSummary:
    return staff_service.read_monthly_attendance_summary(
        session=session,
        current_account_id=current_account.ma_tai_khoan,
        ma_can_bo=ma_can_bo,
        reference_date=reference_date,
    )


@router.get(
    "/{ma_can_bo}/khieu-nai/cho-xu-ly/count",
    dependencies=[Depends(get_current_active_lecturer)],
    response_model=KhieuNaiChoXuLyMetric,
)
def read_pending_appeal_count(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_can_bo: Annotated[int, Path(ge=1)],
) -> KhieuNaiChoXuLyMetric:
    return staff_service.read_pending_appeal_count(
        session=session,
        current_account_id=current_account.ma_tai_khoan,
        ma_can_bo=ma_can_bo,
    )


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=CanBoPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_staff_member(
    *,
    session: SessionDep,
    can_bo_in: CanBoCreate,
) -> CanBoPublic:
    """Tạo hồ sơ cán bộ mới."""
    return staff_service.create_staff_member(
        session=session,
        item_in=can_bo_in,
    )


@router.patch(
    "/{ma_can_bo}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=CanBoPublic,
)
def update_staff_member(
    *,
    session: SessionDep,
    ma_can_bo: Annotated[int, Path(ge=1)],
    can_bo_in: CanBoUpdate,
) -> CanBoPublic:
    """Cập nhật một phần thông tin cán bộ."""
    return staff_service.update_staff_member(
        session=session,
        ma_can_bo=ma_can_bo,
        item_in=can_bo_in,
    )


@router.delete(
    "/{ma_can_bo}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=Message,
)
def delete_staff_member(
    session: SessionDep,
    ma_can_bo: Annotated[int, Path(ge=1)],
) -> Message:
    """Xóa hồ sơ cán bộ theo mã cán bộ."""
    return staff_service.delete_staff_member(
        session=session,
        ma_can_bo=ma_can_bo,
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
        ma_tai_khoan=current_account.ma_tai_khoan,
    )


@router.get(
    "/{ma_can_bo}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=CanBoPublic,
)
def read_staff_member(
    session: SessionDep,
    ma_can_bo: Annotated[int, Path(ge=1)],
) -> CanBoPublic:
    """Lấy chi tiết một cán bộ theo mã cán bộ."""
    return staff_service.get_staff_member_or_404(
        session=session,
        ma_can_bo=ma_can_bo,
    )
