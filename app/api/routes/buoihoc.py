from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, func

from app.api.deps import SessionDep, get_current_active_giangvien, get_current_active_superuser, CurrentAccount
from app.models import BuoiHoc, BuoiHocCreate, BuoiHocUpdate, BuoiHocPublic, BuoiHocsPublic, SinhVien, DangKyHocPhan, DiemDanh, LopHocPhan
from app.crud import buoihoc_crud, diemdanh_crud, canbo_crud


router = APIRouter(prefix="/buoi-hoc", tags=["buoi-hoc"])

@router.get("/", response_model=BuoiHocsPublic)
def read_buoihocs(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Lấy danh sách các buổi học."""
    items, count = buoihoc_crud.get_buoihocs(session=session, skip=skip, limit=limit)
    return {"data": items, "count": count}

@router.get("/{ma_buoi_hoc}", response_model=BuoiHocPublic)
def read_buoihoc(
    session: SessionDep,
    ma_buoi_hoc: int,
) -> Any:
    """Lấy thông tin một buổi học."""
    item = buoihoc_crud.get_buoihoc(session=session, ma_buoi_hoc=ma_buoi_hoc)
    if not item:
        raise HTTPException(status_code=404, detail="Buổi học không tồn tại")
    return item

@router.post("/", response_model=BuoiHocPublic, dependencies=[Depends(get_current_active_giangvien)])
def create_buoihoc(
    session: SessionDep,
    item_in: BuoiHocCreate,
) -> Any:
    """Tạo buổi học mới (Giảng viên/Admin)."""
    return buoihoc_crud.create_buoihoc(session=session, item_create=item_in)

@router.patch("/{ma_buoi_hoc}", response_model=BuoiHocPublic, dependencies=[Depends(get_current_active_giangvien)])
def update_buoihoc(
    session: SessionDep,
    ma_buoi_hoc: int,
    item_in: BuoiHocUpdate,
) -> Any:
    """Cập nhật buổi học (Giảng viên/Admin)."""
    item = buoihoc_crud.get_buoihoc(session=session, ma_buoi_hoc=ma_buoi_hoc)
    if not item:
        raise HTTPException(status_code=404, detail="Buổi học không tồn tại")
    return buoihoc_crud.update_buoihoc(session=session, db_item=item, item_update=item_in)

@router.post("/{ma_buoi_hoc}/mo-diem-danh", response_model=BuoiHocPublic, dependencies=[Depends(get_current_active_giangvien)])
def mo_diem_danh(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_buoi_hoc: int,
) -> Any:
    """Giảng viên mở phiên điểm danh."""
    item = buoihoc_crud.get_buoihoc(session=session, ma_buoi_hoc=ma_buoi_hoc)
    if not item:
        raise HTTPException(status_code=404, detail="Buổi học không tồn tại")
    
    # Kiểm tra quyền (phải là giảng viên phụ trách)
    # Lấy lophocphan để check ma_can_bo
    from app.models import LopHocPhan
    lhp = session.get(LopHocPhan, item.ma_lop_hoc_phan)
    can_bo = canbo_crud.get_can_bo_by_account_id(session=session, ma_tai_khoan=current_account.ma_tai_khoan)
    if current_account.vai_tro != "ADMIN" and (not can_bo or lhp.ma_can_bo != can_bo.ma_can_bo):
        raise HTTPException(status_code=403, detail="Không có quyền thao tác trên buổi học này")

    item.trang_thai = "DANG_DIEN_RA"
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

@router.post("/{ma_buoi_hoc}/dong-diem-danh", response_model=BuoiHocPublic, dependencies=[Depends(get_current_active_giangvien)])
def dong_diem_danh(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_buoi_hoc: int,
) -> Any:
    """Giảng viên đóng phiên điểm danh. Tự động chốt vắng cho những sinh viên chưa điểm danh."""
    item = buoihoc_crud.get_buoihoc(session=session, ma_buoi_hoc=ma_buoi_hoc)
    if not item:
        raise HTTPException(status_code=404, detail="Buổi học không tồn tại")
    
    from app.models import LopHocPhan
    lhp = session.get(LopHocPhan, item.ma_lop_hoc_phan)
    can_bo = canbo_crud.get_can_bo_by_account_id(session=session, ma_tai_khoan=current_account.ma_tai_khoan)
    if current_account.vai_tro != "ADMIN" and (not can_bo or lhp.ma_can_bo != can_bo.ma_can_bo):
        raise HTTPException(status_code=403, detail="Không có quyền thao tác trên buổi học này")

    if item.trang_thai != "DANG_DIEN_RA":
        raise HTTPException(status_code=400, detail="Buổi học chưa được mở điểm danh hoặc đã kết thúc")

    item.trang_thai = "DA_KET_THUC"
    session.add(item)
    session.commit()
    session.refresh(item)
    
    # Chốt vắng
    diemdanh_crud.chot_diem_danh_vang(session=session, buoi_hoc=item)
    
    return item

@router.delete("/{ma_buoi_hoc}", dependencies=[Depends(get_current_active_superuser)])
def delete_buoihoc(
    session: SessionDep,
    ma_buoi_hoc: int,
) -> Any:
    """Xóa buổi học (chỉ Admin)."""
    item = buoihoc_crud.get_buoihoc(session=session, ma_buoi_hoc=ma_buoi_hoc)
    if not item:
        raise HTTPException(status_code=404, detail="Buổi học không tồn tại")
    buoihoc_crud.delete_buoihoc(session=session, db_item=item)
    return {"message": "Xóa buổi học thành công"}


@router.get("/{ma_buoi_hoc}/diem-danh", dependencies=[Depends(get_current_active_giangvien)])
def read_buoihoc_diem_danh_list(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_buoi_hoc: int,
) -> Any:
    """Lấy danh sách sinh viên đăng ký lớp và trạng thái điểm danh trong buổi học."""
    buoi_hoc = session.get(BuoiHoc, ma_buoi_hoc)
    if not buoi_hoc:
        raise HTTPException(status_code=404, detail="Buổi học không tồn tại")
    
    lhp = session.get(LopHocPhan, buoi_hoc.ma_lop_hoc_phan)
    if not lhp:
        raise HTTPException(status_code=404, detail="Lớp học phần không tồn tại")
    
    can_bo = canbo_crud.get_can_bo_by_account_id(session=session, ma_tai_khoan=current_account.ma_tai_khoan)
    if current_account.vai_tro != "ADMIN" and (not can_bo or lhp.ma_can_bo != can_bo.ma_can_bo):
        raise HTTPException(status_code=403, detail="Không có quyền truy cập dữ liệu buổi học này")
    
    statement_sv = (
        select(SinhVien)
        .join(DangKyHocPhan, DangKyHocPhan.ma_sinh_vien == SinhVien.ma_sinh_vien)
        .where(DangKyHocPhan.ma_lop_hoc_phan == buoi_hoc.ma_lop_hoc_phan)
    )
    sinh_viens = session.exec(statement_sv).all()
    
    statement_dd = select(DiemDanh).where(DiemDanh.ma_buoi_hoc == ma_buoi_hoc)
    diem_danhs = session.exec(statement_dd).all()
    dd_map = {dd.ma_sinh_vien: dd for dd in diem_danhs}
    
    result = []
    for sv in sinh_viens:
        dd = dd_map.get(sv.ma_sinh_vien)
        
        status = "pending"
        confidence = "medium"
        verified_at = None
        
        if dd:
            if dd.trang_thai == "CO_MAT":
                status = "present"
            elif dd.trang_thai == "DI_MUON":
                status = "late"
            elif dd.trang_thai == "VANG":
                status = "absent"
            
            if (dd.do_tin_cay or 0) >= 0.85:
                confidence = "high"
            elif (dd.do_tin_cay or 0) >= 0.70:
                confidence = "medium"
            else:
                confidence = "low"
            verified_at = dd.thoi_diem_diem_danh.strftime("%H:%M:%S") if dd.thoi_diem_diem_danh else None
            
        result.append({
            "id": str(sv.ma_sinh_vien),
            "name": f"{sv.ho} {sv.ten}".strip(),
            "studentId": f"SV{sv.ma_sinh_vien:03d}",
            "status": status,
            "confidence": confidence,
            "hasCamera": status != "absent",
            "verifiedAt": verified_at
        })
        
    return result
