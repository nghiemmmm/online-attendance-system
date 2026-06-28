"""
Diem danh router.

Defines APIs for attendance statistics.
"""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Path, Query, HTTPException, Request, status
from pydantic import Field, field_validator

from app.api.deps import SessionDep, get_current_active_superuser, get_current_active_lecturer, CurrentAccount
from app.models import SemesterAttendanceSummaryPublic, AttendancePublic
from app.models.base import AppBaseModel
from app.services.attendance_stats_service import (
    get_semester_present_lesson_total,
    mark_attendance_automatically_service,
    mark_attendance_manually_service,
)
from app.services.audit_log_service import write_audit_log

class AutoAttendanceRequest(AppBaseModel):
    class_session_id: Annotated[int, Field(gt=0)]
    student_ids: Annotated[list[int], Field(min_length=1)]
    average_confidence: Annotated[float, Field(ge=0.0, le=1.0)] = 0.8

    @field_validator("student_ids")
    @classmethod
    def _validate_unique_student_ids(cls, value: list[int]) -> list[int]:
        if len(value) != len(set(value)):
            raise ValueError("Danh sách sinh viên không được trùng lặp")
        return value


class ManualAttendanceRequest(AppBaseModel):
    class_session_id: Annotated[int, Field(gt=0)]
    student_id: Annotated[int, Field(gt=0)]
    status: Annotated[str, Field(min_length=1, max_length=20)]
    note: str | None = Field(default=None, max_length=500)

    @field_validator("status")
    @classmethod
    def _normalize_status(cls, value: str) -> str:
        normalized = value.strip().upper()
        allowed_statuses = {"CO_MAT", "DI_MUON", "VANG", "VANG_MAT", "XIN_PHEP"}
        if normalized not in allowed_statuses:
            raise ValueError("Trang thái điểm danh không hợp lệ")
        return normalized


router = APIRouter(prefix="/attendance-records", tags=["attendance-records"])


@router.get(
    "/students/{student_id}/present-session-count",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=SemesterAttendanceSummaryPublic,
)
def read_student_semester_present_lesson_total(
    session: SessionDep,
    student_id: Annotated[int, Path(ge=1)],
    semester: Annotated[int, Query(ge=1, le=3)],
    academic_year: Annotated[str, Query(max_length=20)],
) -> SemesterAttendanceSummaryPublic:
    """Lay tong so buoi co mat cua sinh vien trong hoc ky."""
    return get_semester_present_lesson_total(
        session=session,
        student_id=student_id,
        semester=semester,
        academic_year=academic_year,
    )

@router.post(
    "/",
    response_model=dict,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Lỗi xử lý điểm danh tự động (buổi học đã kết thúc, danh sách trống, v.v.)"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Buổi học không tồn tại"
        }
    }
)
def mark_attendance_automatically(
    request_context: Request,
    request: AutoAttendanceRequest,
    session: SessionDep,
) -> Any:
    """AI gọi API này để gửi danh sách sinh viên quét được trong khung hình."""
    # API này có thể được gọi từ module AI nội bộ nên không nhất thiết phải có JWT Token của user (trong hệ thống lớn có thể dùng API Key riêng).
    # Tuy nhiên vì demo ta để mở hoặc dùng superuser/system account. Ở đây tạm để mở.
    result = mark_attendance_automatically_service(
        session=session,
        class_session_id=request.class_session_id,
        student_ids=request.student_ids,
        average_confidence=request.average_confidence,
    )
    write_audit_log(
        session=session,
        action="DIEM_DANH_TU_DONG",
        target_type="ClassSession",
        target_id=request.class_session_id,
        after_data={
            "student_ids": request.student_ids,
            "average_confidence": request.average_confidence,
            "attendance_ids": result.get("attendance_ids", []),
        },
        request=request_context,
    )
    return result


@router.post(
    "/manual-adjustments",
    response_model=AttendancePublic,
    dependencies=[Depends(get_current_active_lecturer)],
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Lỗi dữ liệu đầu vào hoặc trạng thái điểm danh không hợp lệ"
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Không có quyền giảng viên trên buổi học hoặc lớp học phần này"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Buổi học không tồn tại"
        }
    }
)
def mark_attendance_manually(
    request_context: Request,
    request: ManualAttendanceRequest,
    session: SessionDep,
    current_account: CurrentAccount,
) -> Any:
    """Giảng viên sửa/điểm danh thủ công cho 1 sinh viên."""
    # Điểm danh
    attendance = mark_attendance_manually_service(
        session=session,
        current_account=current_account,
        class_session_id=request.class_session_id,
        student_id=request.student_id,
        status=request.status,
        note=request.note,
    )
    write_audit_log(
        session=session,
        account=current_account,
        action="DIEM_DANH_THU_CONG",
        target_type="Attendance",
        target_id=attendance.attendance_id,
        after_data=attendance.model_dump(mode="json"),
        request=request_context,
    )
    return attendance
