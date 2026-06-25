"""
Diem danh router.

Defines APIs for attendance statistics.
"""

from typing import Annotated, Any, List

from fastapi import APIRouter, Depends, Path, Query, HTTPException, Request
from pydantic import BaseModel

from app.api.deps import SessionDep, get_current_active_superuser, get_current_active_giangvien, CurrentAccount
from app.models import TongBuoiCoMatHocKyPublic, DiemDanhPublic
from app.services.diemdanh_summary_service import get_tong_buoi_co_mat_hoc_ky
from app.crud import diemdanh_crud, buoihoc_crud, canbo_crud
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
def read_tong_buoi_co_mat_hoc_ky_sinh_vien(
    session: SessionDep,
    ma_sinh_vien: Annotated[int, Path(ge=1)],
    hoc_ky: Annotated[int, Query(ge=1, le=3)],
    nam_hoc: Annotated[str, Query(max_length=20)],
) -> TongBuoiCoMatHocKyPublic:
    """Lay tong so buoi co mat cua sinh vien trong hoc ky."""
    return get_tong_buoi_co_mat_hoc_ky(
        session=session,
        ma_sinh_vien=ma_sinh_vien,
        hoc_ky=hoc_ky,
        nam_hoc=nam_hoc,
    )

@router.post("/tu-dong", response_model=dict)
def diem_danh_tu_dong(
    request_context: Request,
    request: AutoAttendanceRequest,
    session: SessionDep,
) -> Any:
    """AI gọi API này để gửi danh sách sinh viên quét được trong khung hình."""
    # API này có thể được gọi từ module AI nội bộ nên không nhất thiết phải có JWT Token của user (trong hệ thống lớn có thể dùng API Key riêng).
    # Tuy nhiên vì demo ta để mở hoặc dùng superuser/system account. Ở đây tạm để mở.
    result = diemdanh_crud.diem_danh_tu_dong_lo(
        session=session,
        ma_buoi_hoc=request.ma_buoi_hoc,
        danh_sach_ma_sinh_vien=request.danh_sach_ma_sinh_vien,
        do_tin_cay_trung_binh=request.do_tin_cay_trung_binh
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
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

@router.post("/thu-cong", response_model=DiemDanhPublic, dependencies=[Depends(get_current_active_giangvien)])
def diem_danh_thu_cong(
    request_context: Request,
    request: ManualAttendanceRequest,
    session: SessionDep,
    current_account: CurrentAccount,
) -> Any:
    """Giảng viên sửa/điểm danh thủ công cho 1 sinh viên."""
    buoi_hoc = buoihoc_crud.get_buoihoc(session=session, ma_buoi_hoc=request.ma_buoi_hoc)
    if not buoi_hoc:
        raise HTTPException(status_code=404, detail="Buổi học không tồn tại")
    
    # Kiểm tra quyền
    from app.models import LopHocPhan
    lhp = session.get(LopHocPhan, buoi_hoc.ma_lop_hoc_phan)
    can_bo = canbo_crud.get_can_bo_by_account_id(session=session, ma_tai_khoan=current_account.ma_tai_khoan)
    if current_account.vai_tro != "ADMIN" and (not can_bo or lhp.ma_can_bo != can_bo.ma_can_bo):
        raise HTTPException(status_code=403, detail="Không có quyền thao tác trên buổi học này")

    # Điểm danh
    diem_danh = diemdanh_crud.diem_danh_thu_cong(
        session=session,
        ma_buoi_hoc=request.ma_buoi_hoc,
        ma_sinh_vien=request.ma_sinh_vien,
        trang_thai=request.trang_thai,
        ghi_chu=request.ghi_chu
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
