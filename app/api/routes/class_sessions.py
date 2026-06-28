from typing import Any

from fastapi import APIRouter, Depends, status
from app.api.deps import (
    CurrentAccount,
    SessionDep,
    get_current_active_lecturer,
    get_current_active_superuser,
)
from app.models import (
    ClassSessionCreate,
    ClassSessionPublic,
    ClassSessionsPublic,
    ClassSessionUpdate,
    Message,
)
from app.services import timetable_service

router = APIRouter(prefix="/class-sessions", tags=["class-sessions"])


@router.get("/", response_model=ClassSessionsPublic)
def read_class_sessions(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    items, count = timetable_service.list_lessons(session=session, skip=skip, limit=limit)
    return {"data": items, "count": count}


@router.get(
    "/class-sections/{class_section_id}",
    dependencies=[Depends(get_current_active_lecturer)],
)
def read_class_sessions_by_class_section(
    session: SessionDep,
    current_account: CurrentAccount,
    class_section_id: int,
) -> Any:
    items = timetable_service.list_lessons_by_class_section(
        session=session,
        current_account=current_account,
        class_section_id=class_section_id,
    )
    # We still build details for frontend schema
    details = [
        timetable_service.get_lesson_detail(
            session=session, current_account=current_account, class_session_id=item.class_session_id
        )
        for item in items
    ]
    return {"data": details, "count": len(items)}


@router.get("/{class_session_id}", response_model=Any)
def read_class_session(
    session: SessionDep,
    current_account: CurrentAccount,
    class_session_id: int,
) -> Any:
    return timetable_service.get_lesson_detail(
        session=session,
        current_account=current_account,
        class_session_id=class_session_id,
    )


@router.post(
    "/",
    response_model=ClassSessionPublic,
    dependencies=[Depends(get_current_active_lecturer)],
    status_code=status.HTTP_201_CREATED,
)
def create_class_session(
    session: SessionDep,
    current_account: CurrentAccount,
    item_in: ClassSessionCreate,
) -> Any:
    return timetable_service.create_lesson(
        session=session,
        current_account=current_account,
        item_in=item_in,
    )


@router.patch(
    "/{class_session_id}",
    response_model=ClassSessionPublic,
    dependencies=[Depends(get_current_active_lecturer)],
)
def update_class_session(
    session: SessionDep,
    current_account: CurrentAccount,
    class_session_id: int,
    item_in: ClassSessionUpdate,
) -> Any:
    changed_fields = item_in.model_dump(exclude_unset=True)
    if set(changed_fields) == {"status"}:
        if item_in.status == "DANG_DIEN_RA":
            return timetable_service.open_attendance(
                session=session,
                current_account=current_account,
                class_session_id=class_session_id,
            )
        if item_in.status == "DA_KET_THUC":
            return timetable_service.close_attendance(
                session=session,
                current_account=current_account,
                class_session_id=class_session_id,
            )

    return timetable_service.update_lesson(
        session=session,
        current_account=current_account,
        class_session_id=class_session_id,
        item_in=item_in,
    )


@router.delete("/{class_session_id}", response_model=Message, dependencies=[Depends(get_current_active_superuser)])
def delete_class_session(
    session: SessionDep,
    class_session_id: int,
) -> Any:
    return timetable_service.delete_lesson(session=session, class_session_id=class_session_id)


@router.delete(
    "/{class_session_id}/lecturer",
    response_model=ClassSessionPublic,
    dependencies=[Depends(get_current_active_lecturer)],
)
def cancel_class_session_by_lecturer(
    session: SessionDep,
    current_account: CurrentAccount,
    class_session_id: int,
) -> Any:
    return timetable_service.cancel_lesson_by_lecturer(
        session=session,
        current_account=current_account,
        class_session_id=class_session_id,
    )


from fastapi import HTTPException
from app.models import ClassSession

@router.post(
    "/{class_session_id}/postpone",
    response_model=ClassSessionPublic,
    dependencies=[Depends(get_current_active_lecturer)],
)
def postpone_class_session(
    session: SessionDep,
    current_account: CurrentAccount,
    class_session_id: int,
    reason: str = "Giảng viên có lịch bận đột xuất",
) -> Any:
    item = session.get(ClassSession, class_session_id)
    if not item:
        raise HTTPException(status_code=404, detail="Buổi học không tồn tại")
    item.status = "HOAN_HOC"
    item.note = f"Hoãn học: {reason}"
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.get(
    "/{class_session_id}/attendance",
    dependencies=[Depends(get_current_active_lecturer)],
)
def read_class_session_attendance_list(
    session: SessionDep,
    current_account: CurrentAccount,
    class_session_id: int,
) -> Any:
    rows = timetable_service.get_lesson_attendance_list(
        session=session,
        current_account=current_account,
        class_session_id=class_session_id,
    )
    return {"data": rows, "count": len(rows)}
