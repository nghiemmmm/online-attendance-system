"""
Canh bao hoc tap router.

Defines APIs for student academic warnings.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import AbsenceWarningsPublic
from app.services.academic_warning_service import get_absence_warnings_by_student

router = APIRouter(prefix="/academic-warnings", tags=["academic-warnings"])


@router.get(
    "/students/{student_id}/absences",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=AbsenceWarningsPublic,
)
def read_student_absence_warnings(
    session: SessionDep,
    student_id: Annotated[int, Path(ge=1)],
    warning_threshold: Annotated[float, Query(ge=0, le=100)] = 15.0,
    absence_limit: Annotated[float, Query(ge=0, le=100)] = 20.0,
    include_safe: bool = False,
) -> AbsenceWarningsPublic:
    """Lay danh sach mon hoc gan vuot hoac da vuot nguong vang cua sinh vien."""
    return get_absence_warnings_by_student(
        session=session,
        student_id=student_id,
        warning_threshold=warning_threshold,
        absence_limit=absence_limit,
        include_safe=include_safe,
    )
