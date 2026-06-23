from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, func, col

from app.api.deps import SessionDep, get_current_active_giangvien, get_current_active_superuser, CurrentAccount
from app.models import LopHocPhan, LopHocPhanCreate, LopHocPhanUpdate, LopHocPhanPublic, LopHocPhansPublic, SinhVien, DangKyHocPhan, SinhViensPublic, DiemDanh, BuoiHoc
from app.crud import lophocphan_crud, canbo_crud



router = APIRouter(prefix="/lop-hoc-phan", tags=["lop-hoc-phan"])

@router.get("/", response_model=LopHocPhansPublic)
def read_lophocphans(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Lấy danh sách các lớp học phần."""
    items, count = lophocphan_crud.get_lophocphans(session=session, skip=skip, limit=limit)
    return {"data": items, "count": count}

@router.get("/{ma_lop_hoc_phan}", response_model=LopHocPhanPublic)
def read_lophocphan(
    session: SessionDep,
    ma_lop_hoc_phan: int,
) -> Any:
    """Lấy thông tin một lớp học phần cụ thể."""
    item = lophocphan_crud.get_lophocphan(session=session, ma_lop_hoc_phan=ma_lop_hoc_phan)
    if not item:
        raise HTTPException(status_code=404, detail="Lớp học phần không tồn tại")
    return item

@router.get("/{ma_lop_hoc_phan}/sinh-vien", dependencies=[Depends(get_current_active_giangvien)])
def read_lophocphan_sinhvien(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_lop_hoc_phan: int,
) -> Any:
    """Lấy danh sách sinh viên trong một lớp học phần (chỉ giảng viên phụ trách hoặc admin)."""
    item = lophocphan_crud.get_lophocphan(session=session, ma_lop_hoc_phan=ma_lop_hoc_phan)
    if not item:
        raise HTTPException(status_code=404, detail="Lớp học phần không tồn tại")
    
    can_bo = canbo_crud.get_can_bo_by_account_id(session=session, ma_tai_khoan=current_account.ma_tai_khoan)
    if current_account.vai_tro != "ADMIN" and (not can_bo or item.ma_can_bo != can_bo.ma_can_bo):
        raise HTTPException(status_code=403, detail="Not authorized to view students of this class")

    statement = (
        select(SinhVien)
        .join(DangKyHocPhan, DangKyHocPhan.ma_sinh_vien == SinhVien.ma_sinh_vien)
        .where(DangKyHocPhan.ma_lop_hoc_phan == ma_lop_hoc_phan)
    )
    sinh_viens = session.exec(statement).all()
    return {"data": sinh_viens, "count": len(sinh_viens)}

@router.get("/{ma_lop_hoc_phan}/thong-ke", dependencies=[Depends(get_current_active_giangvien)])
def read_lophocphan_thongke(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_lop_hoc_phan: int,
) -> Any:
    """Lấy thống kê điểm danh của lớp học phần (chỉ giảng viên phụ trách hoặc admin)."""
    item = lophocphan_crud.get_lophocphan(session=session, ma_lop_hoc_phan=ma_lop_hoc_phan)
    if not item:
        raise HTTPException(status_code=404, detail="Lớp học phần không tồn tại")
    
    can_bo = canbo_crud.get_can_bo_by_account_id(session=session, ma_tai_khoan=current_account.ma_tai_khoan)
    if current_account.vai_tro != "ADMIN" and (not can_bo or item.ma_can_bo != can_bo.ma_can_bo):
        raise HTTPException(status_code=403, detail="Not authorized to view stats of this class")

    # Đếm tổng số sinh viên
    so_luong_sinh_vien = session.exec(select(func.count()).select_from(DangKyHocPhan).where(DangKyHocPhan.ma_lop_hoc_phan == ma_lop_hoc_phan)).one()
    
    # Lấy tổng số buổi học đã diễn ra
    so_buoi_hoc = session.exec(select(func.count()).select_from(BuoiHoc).where(BuoiHoc.ma_lop_hoc_phan == ma_lop_hoc_phan, BuoiHoc.trang_thai == "DA_KET_THUC")).one()

    # Thống kê điểm danh
    statement = (
        select(DiemDanh.trang_thai, func.count(DiemDanh.ma_diem_danh))
        .join(BuoiHoc, BuoiHoc.ma_buoi_hoc == DiemDanh.ma_buoi_hoc)
        .where(BuoiHoc.ma_lop_hoc_phan == ma_lop_hoc_phan)
        .group_by(DiemDanh.trang_thai)
    )
    stats = session.exec(statement).all()
    
    thong_ke = {
        "so_luong_sinh_vien": so_luong_sinh_vien,
        "so_buoi_hoc": so_buoi_hoc,
        "chi_tiet": {stat[0]: stat[1] for stat in stats}
    }
    return thong_ke


@router.post("/", response_model=LopHocPhanPublic, dependencies=[Depends(get_current_active_superuser)])
def create_lophocphan(
    session: SessionDep,
    item_in: LopHocPhanCreate,
) -> Any:
    """Tạo lớp học phần mới (chỉ Admin)."""
    return lophocphan_crud.create_lophocphan(session=session, item_create=item_in)

@router.patch("/{ma_lop_hoc_phan}", response_model=LopHocPhanPublic, dependencies=[Depends(get_current_active_superuser)])
def update_lophocphan(
    session: SessionDep,
    ma_lop_hoc_phan: int,
    item_in: LopHocPhanUpdate,
) -> Any:
    """Cập nhật lớp học phần (chỉ Admin)."""
    item = lophocphan_crud.get_lophocphan(session=session, ma_lop_hoc_phan=ma_lop_hoc_phan)
    if not item:
        raise HTTPException(status_code=404, detail="Lớp học phần không tồn tại")
    return lophocphan_crud.update_lophocphan(session=session, db_item=item, item_update=item_in)

@router.delete("/{ma_lop_hoc_phan}", dependencies=[Depends(get_current_active_superuser)])
def delete_lophocphan(
    session: SessionDep,
    ma_lop_hoc_phan: int,
) -> Any:
    """Xóa lớp học phần (chỉ Admin)."""
    item = lophocphan_crud.get_lophocphan(session=session, ma_lop_hoc_phan=ma_lop_hoc_phan)
    if not item:
        raise HTTPException(status_code=404, detail="Lớp học phần không tồn tại")
    lophocphan_crud.delete_lophocphan(session=session, db_item=item)
    return {"message": "Xóa lớp học phần thành công"}
