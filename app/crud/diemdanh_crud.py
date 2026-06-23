from datetime import datetime, date, timedelta
from sqlmodel import Session, select
from typing import List

from app.models import DiemDanh, BuoiHoc, DangKyHocPhan, DiemDanhCreate, DiemDanhUpdate

def tinh_trang_thai_diem_danh(buoi_hoc: BuoiHoc, current_time: datetime) -> str:
    """Xác định trạng thái CO_MAT hoặc MUON dựa trên giờ bắt đầu và số phút muộn tối đa."""
    if not buoi_hoc.gio_bat_dau:
        return "CO_MAT" # Nếu không cấu hình giờ, mặc định là có mặt
    
    # Kết hợp ngày học và giờ học
    thoi_gian_bat_dau = datetime.combine(buoi_hoc.ngay_hoc, buoi_hoc.gio_bat_dau)
    thoi_gian_muon_toi_da = thoi_gian_bat_dau + timedelta(minutes=buoi_hoc.so_phut_muon_toi_da)
    
    if current_time > thoi_gian_muon_toi_da:
        return "MUON"
    return "CO_MAT"

def diem_danh_tu_dong_lo(
    *, session: Session, ma_buoi_hoc: int, danh_sach_ma_sinh_vien: List[int], do_tin_cay_trung_binh: float = 0.8
) -> dict:
    """Xử lý điểm danh hàng loạt từ AI."""
    buoi_hoc = session.get(BuoiHoc, ma_buoi_hoc)
    if not buoi_hoc:
        return {"success": False, "message": "Buổi học không tồn tại"}
    
    if buoi_hoc.trang_thai != "DANG_DIEN_RA":
        return {"success": False, "message": "Buổi học không trong trạng thái ĐANG_DIEN_RA"}

    current_time = datetime.now()
    trang_thai_hien_tai = tinh_trang_thai_diem_danh(buoi_hoc, current_time)

    # Lấy các record điểm danh đã có của các sinh viên này trong buổi học
    statement = select(DiemDanh).where(
        DiemDanh.ma_buoi_hoc == ma_buoi_hoc,
        DiemDanh.ma_sinh_vien.in_(danh_sach_ma_sinh_vien)
    )
    existing_records = session.exec(statement).all()
    existing_map = {record.ma_sinh_vien: record for record in existing_records}

    new_records = []
    updated_records = []

    for ma_sv in danh_sach_ma_sinh_vien:
        if ma_sv in existing_map:
            # Nếu đã điểm danh rồi thì có thể không ghi đè, hoặc chỉ cập nhật nếu trạng thái hiện tại tốt hơn
            # Ví dụ: nếu đã là MUON, giờ lại quét được thì vẫn là MUON hoặc CO_MAT?
            # Thường thì lấy lần quét đầu tiên làm chuẩn. Hoặc nếu muốn cập nhật thì làm như sau:
            pass # Ở đây chúng ta bảo toàn record đầu tiên quét được
        else:
            new_dd = DiemDanh(
                ma_sinh_vien=ma_sv,
                ma_buoi_hoc=ma_buoi_hoc,
                trang_thai=trang_thai_hien_tai,
                phuong_thuc="KHUON_MAT",
                do_tin_cay=do_tin_cay_trung_binh,
                thoi_diem_diem_danh=current_time
            )
            new_records.append(new_dd)
    
    if new_records:
        session.add_all(new_records)
        session.commit()
    
    return {"success": True, "message": f"Đã điểm danh cho {len(new_records)} sinh viên", "trang_thai": trang_thai_hien_tai}


def diem_danh_thu_cong(
    *, session: Session, ma_buoi_hoc: int, ma_sinh_vien: int, trang_thai: str, ghi_chu: str | None = None
) -> DiemDanh:
    """Giảng viên điểm danh thủ công 1 sinh viên."""
    statement = select(DiemDanh).where(DiemDanh.ma_buoi_hoc == ma_buoi_hoc, DiemDanh.ma_sinh_vien == ma_sinh_vien)
    diem_danh = session.exec(statement).first()
    
    if diem_danh:
        diem_danh.trang_thai = trang_thai
        diem_danh.ly_do_chinh_sua = ghi_chu
        diem_danh.phuong_thuc = "THU_CONG"
        diem_danh.thoi_diem_diem_danh = datetime.now()
        session.add(diem_danh)
    else:
        diem_danh = DiemDanh(
            ma_sinh_vien=ma_sinh_vien,
            ma_buoi_hoc=ma_buoi_hoc,
            trang_thai=trang_thai,
            phuong_thuc="THU_CONG",
            thoi_diem_diem_danh=datetime.now(),
            ly_do_chinh_sua=ghi_chu
        )
        session.add(diem_danh)
    
    session.commit()
    session.refresh(diem_danh)
    return diem_danh

def chot_diem_danh_vang(*, session: Session, buoi_hoc: BuoiHoc) -> int:
    """Tạo bản ghi VANG cho toàn bộ sinh viên chưa có record khi buổi học kết thúc."""
    # Lấy toàn bộ sinh viên đăng ký lớp học phần
    statement = select(DangKyHocPhan.ma_sinh_vien).where(DangKyHocPhan.ma_lop_hoc_phan == buoi_hoc.ma_lop_hoc_phan)
    danh_sach_sv_dang_ky = session.exec(statement).all()
    
    # Lấy các sinh viên đã điểm danh
    statement_dd = select(DiemDanh.ma_sinh_vien).where(DiemDanh.ma_buoi_hoc == buoi_hoc.ma_buoi_hoc)
    danh_sach_sv_da_dd = set(session.exec(statement_dd).all())
    
    sv_chua_dd = [sv for sv in danh_sach_sv_dang_ky if sv not in danh_sach_sv_da_dd]
    
    new_vangs = []
    for ma_sv in sv_chua_dd:
        new_dd = DiemDanh(
            ma_sinh_vien=ma_sv,
            ma_buoi_hoc=buoi_hoc.ma_buoi_hoc,
            trang_thai="VANG",
            phuong_thuc="TU_DONG",
            thoi_diem_diem_danh=datetime.now(),
            ly_do_chinh_sua="Tự động đánh vắng khi chốt phiên"
        )
        new_vangs.append(new_dd)
        
    if new_vangs:
        session.add_all(new_vangs)
        session.commit()
        
    return len(new_vangs)
