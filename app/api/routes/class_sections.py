"""Define class section HTTP routes."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import (
    CurrentAccount,
    SessionDep,
    get_current_active_lecturer,
    get_current_active_superuser,
)
from app.crud import class_section_crud
from app.models import (
    ClassSectionCreate,
    ClassSectionPublic,
    ClassSectionsPublic,
    ClassSectionUpdate,
)
from app.services.class_section_service import (
    ClassSectionService,
    get_class_section_service,
)

router = APIRouter(prefix="/class-sections", tags=["class-sections"])


@router.get("/", response_model=ClassSectionsPublic)
def read_class_sections(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Lấy danh sách các lớp học phần."""
    items, count = class_section_crud.get_class_sections(
        session=session, skip=skip, limit=limit
    )
    return {"data": items, "count": count}


@router.get("/{class_section_id}", response_model=ClassSectionPublic)
def read_class_section(
    session: SessionDep,
    class_section_id: int,
) -> Any:
    """Lấy thông tin một lớp học phần cụ thể."""
    item = class_section_crud.get_class_section(
        session=session, class_section_id=class_section_id
    )
    if not item:
        raise HTTPException(status_code=404, detail="Lớp học phần không tồn tại")
    return item


@router.get(
    "/{class_section_id}/students", dependencies=[Depends(get_current_active_lecturer)]
)
def read_class_section_students(
    class_section_id: int,
    current_account: CurrentAccount,
    service: ClassSectionService = Depends(get_class_section_service),
) -> Any:
    """Lấy danh sách sinh viên trong một lớp học phần (chỉ giảng viên phụ trách hoặc admin)."""
    return service.get_class_section_students(
        class_section_id=class_section_id,
        current_account=current_account,
    )


@router.get(
    "/{class_section_id}/statistics",
    dependencies=[Depends(get_current_active_lecturer)],
)
def read_class_section_statistics(
    class_section_id: int,
    current_account: CurrentAccount,
    service: ClassSectionService = Depends(get_class_section_service),
) -> Any:
    """Lấy thống kê điểm danh của lớp học phần (chỉ giảng viên phụ trách hoặc admin)."""
    return service.get_class_section_statistics(
        class_section_id=class_section_id,
        current_account=current_account,
    )


@router.get(
    "/{class_section_id}/warnings", dependencies=[Depends(get_current_active_lecturer)]
)
def read_class_section_warnings(
    class_section_id: int,
    current_account: CurrentAccount,
    absence_limit: float = 20.0,
    service: ClassSectionService = Depends(get_class_section_service),
) -> Any:
    """Lay danh sach sinh vien vang nhieu hoac co nguy co cam thi trong mot lop."""
    return service.get_class_section_warnings(
        class_section_id=class_section_id,
        current_account=current_account,
        absence_limit=absence_limit,
    )


from app.services.session_generator_service import generate_sessions_for_class_section


@router.post(
    "/",
    response_model=ClassSectionPublic,
    dependencies=[Depends(get_current_active_superuser)],
    status_code=status.HTTP_201_CREATED,
)
def create_class_section(
    session: SessionDep,
    item_in: ClassSectionCreate,
) -> Any:
    """Tạo lớp học phần mới (chỉ Admin). Tự động sinh danh sách buổi học."""
    new_section = class_section_crud.create_class_section(
        session=session, item_create=item_in
    )
    generate_sessions_for_class_section(
        session=session, class_section_id=new_section.class_section_id
    )
    return new_section


@router.post(
    "/{class_section_id}/generate-sessions",
    dependencies=[Depends(get_current_active_superuser)],
)
def generate_class_section_sessions(
    session: SessionDep,
    class_section_id: int,
) -> Any:
    """Tự động sinh các buổi học theo tín chỉ và thời khóa biểu cho lớp học phần."""
    item = class_section_crud.get_class_section(
        session=session, class_section_id=class_section_id
    )
    if not item:
        raise HTTPException(status_code=404, detail="Lớp học phần không tồn tại")
    count = generate_sessions_for_class_section(
        session=session, class_section_id=class_section_id
    )
    return {
        "message": f"Đã tự động sinh {count} buổi học mới thành công",
        "count": count,
    }


@router.patch(
    "/{class_section_id}",
    response_model=ClassSectionPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
def update_class_section(
    session: SessionDep,
    class_section_id: int,
    item_in: ClassSectionUpdate,
) -> Any:
    """Cập nhật lớp học phần (chỉ Admin)."""
    item = class_section_crud.get_class_section(
        session=session, class_section_id=class_section_id
    )
    if not item:
        raise HTTPException(status_code=404, detail="Lớp học phần không tồn tại")
    return class_section_crud.update_class_section(
        session=session, db_item=item, item_update=item_in
    )


@router.delete(
    "/{class_section_id}", dependencies=[Depends(get_current_active_superuser)]
)
def delete_class_section(
    session: SessionDep,
    class_section_id: int,
) -> Any:
    """Xóa lớp học phần (chỉ Admin)."""
    item = class_section_crud.get_class_section(
        session=session, class_section_id=class_section_id
    )
    if not item:
        raise HTTPException(status_code=404, detail="Lớp học phần không tồn tại")
    class_section_crud.delete_class_section(session=session, db_item=item)
    return {"message": "Xóa lớp học phần thành công"}
