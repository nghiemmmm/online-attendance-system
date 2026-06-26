from typing import Any

from fastapi import APIRouter, Depends, status
from app.api.deps import (
    CurrentAccount,
    SessionDep,
    get_current_active_lecturer,
    get_current_active_superuser,
)
from app.models import (
    BuoiHocCreate,
    BuoiHocPublic,
    BuoiHocsPublic,
    BuoiHocUpdate,
    Message,
)
from app.services import timetable_service

router = APIRouter(prefix="/buoi-hoc", tags=["buoi-hoc"])


@router.get("/", response_model=BuoiHocsPublic)
def read_buoihocs(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    items, count = timetable_service.list_lessons(session=session, skip=skip, limit=limit)
    return {"data": items, "count": count}


@router.get(
    "/lop-hoc-phan/{ma_lop_hoc_phan}",
    dependencies=[Depends(get_current_active_lecturer)],
)
def read_buoihocs_by_lop_hoc_phan(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_lop_hoc_phan: int,
) -> Any:
    items = timetable_service.list_lessons_by_lop_hoc_phan(
        session=session,
        current_account=current_account,
        ma_lop_hoc_phan=ma_lop_hoc_phan,
    )
    # We still build details for frontend schema
    details = [
        timetable_service.get_lesson_detail(
            session=session, current_account=current_account, ma_buoi_hoc=item.ma_buoi_hoc
        )
        for item in items
    ]
    return {"data": details, "count": len(items)}


@router.get("/{ma_buoi_hoc}", response_model=Any)
def read_buoihoc(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_buoi_hoc: int,
) -> Any:
    return timetable_service.get_lesson_detail(
        session=session,
        current_account=current_account,
        ma_buoi_hoc=ma_buoi_hoc,
    )


@router.post(
    "/",
    response_model=BuoiHocPublic,
    dependencies=[Depends(get_current_active_lecturer)],
    status_code=status.HTTP_201_CREATED,
)
def create_buoihoc(
    session: SessionDep,
    current_account: CurrentAccount,
    item_in: BuoiHocCreate,
) -> Any:
    return timetable_service.create_lesson(
        session=session,
        current_account=current_account,
        item_in=item_in,
    )


@router.patch(
    "/{ma_buoi_hoc}",
    response_model=BuoiHocPublic,
    dependencies=[Depends(get_current_active_lecturer)],
)
def update_buoihoc(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_buoi_hoc: int,
    item_in: BuoiHocUpdate,
) -> Any:
    return timetable_service.update_lesson(
        session=session,
        current_account=current_account,
        ma_buoi_hoc=ma_buoi_hoc,
        item_in=item_in,
    )


@router.post(
    "/{ma_buoi_hoc}/mo-diem-danh",
    response_model=BuoiHocPublic,
    dependencies=[Depends(get_current_active_lecturer)],
)
def mo_diem_danh(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_buoi_hoc: int,
) -> Any:
    return timetable_service.open_attendance(
        session=session,
        current_account=current_account,
        ma_buoi_hoc=ma_buoi_hoc,
    )


@router.post(
    "/{ma_buoi_hoc}/dong-diem-danh",
    response_model=BuoiHocPublic,
    dependencies=[Depends(get_current_active_lecturer)],
)
def dong_diem_danh(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_buoi_hoc: int,
) -> Any:
    return timetable_service.close_attendance(
        session=session,
        current_account=current_account,
        ma_buoi_hoc=ma_buoi_hoc,
    )


@router.delete("/{ma_buoi_hoc}", response_model=Message, dependencies=[Depends(get_current_active_superuser)])
def delete_buoihoc(
    session: SessionDep,
    ma_buoi_hoc: int,
) -> Any:
    return timetable_service.delete_lesson(session=session, ma_buoi_hoc=ma_buoi_hoc)


@router.delete(
    "/{ma_buoi_hoc}/giang-vien",
    response_model=BuoiHocPublic,
    dependencies=[Depends(get_current_active_lecturer)],
)
def cancel_buoihoc_by_giangvien(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_buoi_hoc: int,
) -> Any:
    return timetable_service.cancel_lesson_by_giangvien(
        session=session,
        current_account=current_account,
        ma_buoi_hoc=ma_buoi_hoc,
    )


@router.get(
    "/{ma_buoi_hoc}/diem-danh",
    dependencies=[Depends(get_current_active_lecturer)],
)
def read_buoihoc_diem_danh_list(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_buoi_hoc: int,
) -> Any:
    rows = timetable_service.get_lesson_attendance_list(
        session=session,
        current_account=current_account,
        ma_buoi_hoc=ma_buoi_hoc,
    )
    return {"data": rows, "count": len(rows)}
