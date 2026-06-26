"""
Diem danh router.

Defines APIs for attendance statistics.
"""

from typing import Annotated, Any, List

from fastapi import APIRouter, Depends, Path, Query, HTTPException, Request, status
from pydantic import BaseModel

from app.api.deps import SessionDep, get_current_active_superuser, get_current_active_lecturer, CurrentAccount
from app.models import TongBuoiCoMatHocKyPublic, DiemDanhPublic
from app.services.diemdanh_summary_service import (
    get_semester_present_lesson_total,
    mark_attendance_automatically_service,
    mark_attendance_manually_service,
)
from app.services.audit_log_service import write_audit_log

class AutoAttendanceRequest(BaseModel):
    ma_buoi_hoc: int
    danh_sach_ma_sinh_vien: List[int]
    do_tin_cay_trung_binh: float = 0.8

class ManualAttendanceRequest(BaseModel):
    ma_buoi_hoc: int
    ma_sinh_vien: int
    trang_thai: str
    ghi_chu: str | None = None


router = APIRouter(prefix="/diem-danh", tags=["diem-danh"])


@router.get(
    "/sinh-vien/{ma_sinh_vien}/tong-buoi-co-mat",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=TongBuoiCoMatHocKyPublic,
)
def read_student_semester_present_lesson_total(
    session: SessionDep,
    ma_sinh_vien: Annotated[int, Path(ge=1)],
    hoc_ky: Annotated[int, Query(ge=1, le=3)],
    nam_hoc: Annotated[str, Query(max_length=20)],
) -> TongBuoiCoMatHocKyPublic:
    """Lay tong so buoi co mat cua sinh vien trong hoc ky."""
    return get_semester_present_lesson_total(
        session=session,
        ma_sinh_vien=ma_sinh_vien,
        hoc_ky=hoc_ky,
        nam_hoc=nam_hoc,
    )

@router.post(
    "/tu-dong",
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
        ma_buoi_hoc=request.ma_buoi_hoc,
        danh_sach_ma_sinh_vien=request.danh_sach_ma_sinh_vien,
        do_tin_cay_trung_binh=request.do_tin_cay_trung_binh,
    )
    write_audit_log(
        session=session,
        hanh_dong="DIEM_DANH_TU_DONG",
        doi_tuong="BuoiHoc",
        doi_tuong_id=request.ma_buoi_hoc,
        du_lieu_sau={
            "danh_sach_ma_sinh_vien": request.danh_sach_ma_sinh_vien,
            "do_tin_cay_trung_binh": request.do_tin_cay_trung_binh,
            "diem_danh_ids": result.get("diem_danh_ids", []),
        },
        request=request_context,
    )
    return result


@router.post(
    "/thu-cong",
    response_model=DiemDanhPublic,
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
    diem_danh = mark_attendance_manually_service(
        session=session,
        current_account=current_account,
        ma_buoi_hoc=request.ma_buoi_hoc,
        ma_sinh_vien=request.ma_sinh_vien,
        trang_thai=request.trang_thai,
        ghi_chu=request.ghi_chu,
    )
    write_audit_log(
        session=session,
        account=current_account,
        hanh_dong="DIEM_DANH_THU_CONG",
        doi_tuong="DiemDanh",
        doi_tuong_id=diem_danh.ma_diem_danh,
        du_lieu_sau=diem_danh.model_dump(mode="json"),
        request=request_context,
    )
    return diem_danh
