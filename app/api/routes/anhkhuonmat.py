import os
import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from app.api.deps import SessionDep, get_current_active_sinhvien, get_current_active_superuser, CurrentAccount
from app.models import AnhKhuonMat, AnhKhuonMatPublic, SinhVien
from app.services.face_service import face_service
from app.crud import sinhvien_crud
from sqlmodel import select

router = APIRouter(prefix="/anh-khuon-mat", tags=["anh-khuon-mat"])

@router.post("/admin/dang-ky", response_model=AnhKhuonMatPublic, dependencies=[Depends(get_current_active_superuser)])
async def admin_dang_ky_khuon_mat(
    session: SessionDep,
    ma_sinh_vien: int = Form(...),
    file: UploadFile = File(...),
) -> Any:
    """Quản trị viên upload ảnh để đăng ký khuôn mặt cho sinh viên."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Vui lòng upload file ảnh (JPEG/PNG)")
    
    sinh_vien = session.get(SinhVien, ma_sinh_vien)
    if not sinh_vien:
        raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")

    content = await file.read()
    
    # Gọi AI Service
    success, message, embedding = face_service.register_face(ma_sinh_vien=sinh_vien.ma_sinh_vien, image_bytes=content)
    if not success:
        raise HTTPException(status_code=400, detail=message)

    # Hàm chuyển đổi tên tiếng Việt có dấu thành không dấu để đặt tên file
    def to_ascii_name(ho: str, ten: str) -> str:
        import unicodedata
        import re
        combined = f"{ho}_{ten}"
        # Loại bỏ dấu tiếng việt
        nfkd_form = unicodedata.normalize('NFKD', combined)
        only_ascii = nfkd_form.encode('ASCII', 'ignore').decode('utf-8')
        # Loại bỏ các ký tự không phải chữ cái/số/gạch dưới và bỏ khoảng trắng
        cleaned = re.sub(r'[^a-zA-Z0-9_]', '', only_ascii.replace(' ', '_'))
        return cleaned

    ho_ten_ascii = to_ascii_name(sinh_vien.ho or "", sinh_vien.ten or "")
    filename = f"sv{sinh_vien.ma_sinh_vien}_{ho_ten_ascii}.jpg"
    filepath = os.path.join("dataset", filename)
    
    with open(filepath, "wb") as f:
        f.write(content)

    # Lưu vào Database
    db_anh = AnhKhuonMat(
        ma_sinh_vien=sinh_vien.ma_sinh_vien,
        duong_dan_anh=filepath,
        loai_anh="DANG_KY",
        embedding_vector=embedding
    )
    session.add(db_anh)
    session.commit()
    session.refresh(db_anh)
    
    return db_anh

class VerificationResult(BaseModel):
    verified: bool
    confidence: float | None = None
    message: str | None = None

@router.post("/xac-minh-truc-tiep", response_model=VerificationResult, dependencies=[Depends(get_current_active_sinhvien)])
async def xac_minh_truc_tiep(
    session: SessionDep,
    current_account: CurrentAccount,
    file: UploadFile = File(...),
    ma_buoi_hoc: int | None = Form(default=None)
) -> Any:
    """Sinh viên gửi khung hình webcam để xác minh."""
    sinh_vien = sinhvien_crud.get_sinh_vien_by_account_id(session=session, ma_tai_khoan=current_account.ma_tai_khoan)
    if not sinh_vien:
        return {"verified": False, "message": "Không tìm thấy thông tin sinh viên"}
        
    content = await file.read()
    
    # Check faces
    recognized_ids = face_service.recognize_faces(image_bytes=content, tolerance=0.6)
    
    if sinh_vien.ma_sinh_vien in recognized_ids:
        if ma_buoi_hoc:
            from app.crud.diemdanh_crud import diem_danh_tu_dong_lo
            result = diem_danh_tu_dong_lo(
                session=session,
                ma_buoi_hoc=ma_buoi_hoc,
                danh_sach_ma_sinh_vien=[sinh_vien.ma_sinh_vien],
                do_tin_cay_trung_binh=0.925
            )
            if not result.get("success"):
                return {"verified": True, "confidence": 92.5, "message": f"Nhận dạng khớp nhưng lỗi ghi nhận: {result.get('message')}"}
            
            status_map = {
                "CO_MAT": "Có mặt",
                "DI_MUON": "Đi muộn",
                "VANG": "Vắng"
            }
            status_text = status_map.get(result.get("trang_thai"), "Có mặt")
            return {"verified": True, "confidence": 92.5, "message": f"Xác minh & Điểm danh thành công ({status_text})"}
            
        return {"verified": True, "confidence": 92.5, "message": "Xác minh thành công"}
    else:
        return {"verified": False, "confidence": 0, "message": "Khuôn mặt không khớp"}
