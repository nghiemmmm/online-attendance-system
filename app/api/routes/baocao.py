import io
import pandas as pd
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import select

from app.api.deps import SessionDep, get_current_active_giangvien, get_current_active_superuser, CurrentAccount
from app.models import LopHocPhan, BuoiHoc, DiemDanh, SinhVien, DangKyHocPhan, CanBo
from app.crud import canbo_crud

router = APIRouter(prefix="/bao-cao", tags=["bao-cao"])

@router.get("/lop-hoc-phan/{ma_lop_hoc_phan}/export-excel", dependencies=[Depends(get_current_active_giangvien)])
def export_excel_diem_danh(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_lop_hoc_phan: int,
) -> Any:
    """Giảng viên xuất file Excel điểm danh của lớp học phần."""
    # Kiểm tra lớp học phần
    lhp = session.get(LopHocPhan, ma_lop_hoc_phan)
    if not lhp:
        raise HTTPException(status_code=404, detail="Lớp học phần không tồn tại")
        
    # Kiểm tra quyền
    can_bo = canbo_crud.get_can_bo_by_account_id(session=session, ma_tai_khoan=current_account.ma_tai_khoan)
    if current_account.vai_tro != "ADMIN" and (not can_bo or lhp.ma_can_bo != can_bo.ma_can_bo):
        raise HTTPException(status_code=403, detail="Không có quyền truy cập dữ liệu lớp này")

    # Lấy danh sách sinh viên đăng ký
    statement_sv = select(SinhVien).join(DangKyHocPhan).where(DangKyHocPhan.ma_lop_hoc_phan == ma_lop_hoc_phan)
    danh_sach_sv = session.exec(statement_sv).all()

    # Lấy danh sách buổi học
    statement_bh = select(BuoiHoc).where(BuoiHoc.ma_lop_hoc_phan == ma_lop_hoc_phan).order_by(BuoiHoc.ngay_hoc, BuoiHoc.gio_bat_dau)
    danh_sach_bh = session.exec(statement_bh).all()

    # Tạo DataFrame data
    data = []
    for sv in danh_sach_sv:
        row = {
            "Mã sinh viên": sv.ma_sinh_vien,
            "Họ tên": sv.ho_ten,
        }
        
        # Lấy điểm danh cho từng buổi
        for bh in danh_sach_bh:
            ngay_str = bh.ngay_hoc.strftime("%d/%m/%Y")
            statement_dd = select(DiemDanh).where(DiemDanh.ma_buoi_hoc == bh.ma_buoi_hoc, DiemDanh.ma_sinh_vien == sv.ma_sinh_vien)
            dd = session.exec(statement_dd).first()
            if dd:
                row[ngay_str] = dd.trang_thai
            else:
                row[ngay_str] = "CHƯA_ĐIỂM_DANH"
                
        data.append(row)

    df = pd.DataFrame(data)

    # Chuyển DataFrame thành file Excel trong bộ nhớ
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="DiemDanh")
    output.seek(0)

    # Đặt tên file
    filename = f"DiemDanh_{ma_lop_hoc_phan}.xlsx"
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"'
    }

    return StreamingResponse(output, headers=headers, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
