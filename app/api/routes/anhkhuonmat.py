import os
import uuid
from datetime import datetime, timezone
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from pydantic import BaseModel

from app.api.deps import SessionDep, get_current_active_sinhvien, get_current_active_superuser, CurrentAccount
from app.models import AnhDiemDanh, AnhKhuonMat, AnhKhuonMatPublic, AnhKhuonMatsPublic, SinhVien
from app.services.face_service import face_service, normalize_embedding
from app.services.audit_log_service import write_audit_log
from app.crud import sinhvien_crud
from sqlmodel import select

router = APIRouter(prefix="/anh-khuon-mat", tags=["anh-khuon-mat"])

@router.post("/admin/dang-ky", response_model=AnhKhuonMatPublic, dependencies=[Depends(get_current_active_superuser)])
async def admin_dang_ky_khuon_mat(
    request: Request,
    session: SessionDep,
    current_account: CurrentAccount,
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
    success, message, quality_score, embedding = face_service.assess_face_image(image_bytes=content)
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
        embedding_vector=embedding,
        diem_chat_luong=quality_score,
        trang_thai_duyet="CHO_DUYET",
    )
    session.add(db_anh)
    session.commit()
    session.refresh(db_anh)
    write_audit_log(
        session=session,
        account=current_account,
        hanh_dong="DANG_KY_KHUON_MAT",
        doi_tuong="AnhKhuonMat",
        doi_tuong_id=db_anh.ma_anh,
        du_lieu_sau={
            "ma_sinh_vien": sinh_vien.ma_sinh_vien,
            "diem_chat_luong": quality_score,
            "trang_thai_duyet": db_anh.trang_thai_duyet,
        },
        request=request,
    )
    
    return db_anh


@router.get(
    "/admin",
    response_model=AnhKhuonMatsPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
def read_admin_anh_khuon_mat(
    session: SessionDep,
    trang_thai_duyet: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    statement = select(AnhKhuonMat)
    if trang_thai_duyet:
        statement = statement.where(AnhKhuonMat.trang_thai_duyet == trang_thai_duyet)
    rows = session.exec(statement).all()
    return {"data": rows[skip : skip + limit], "count": len(rows)}


class FaceReviewRequest(BaseModel):
    ly_do_tu_choi: str | None = None


@router.patch(
    "/admin/{ma_anh}/duyet",
    response_model=AnhKhuonMatPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
def approve_face_image(
    request: Request,
    session: SessionDep,
    current_account: CurrentAccount,
    ma_anh: int,
) -> Any:
    db_anh = session.get(AnhKhuonMat, ma_anh)
    if not db_anh:
        raise HTTPException(status_code=404, detail="Khong tim thay anh khuon mat")
    embedding = normalize_embedding(db_anh.embedding_vector)
    if len(embedding) != 512:
        raise HTTPException(status_code=400, detail="Anh chua co embedding hop le")

    before = db_anh.model_dump(mode="json", exclude={"embedding_vector"})
    db_anh.trang_thai_duyet = "DA_DUYET"
    db_anh.ly_do_tu_choi = None
    db_anh.ma_nguoi_duyet = current_account.ma_tai_khoan
    db_anh.thoi_gian_duyet = datetime.now(timezone.utc)
    session.add(db_anh)
    session.commit()
    session.refresh(db_anh)
    face_service.add_face_embedding(db_anh.ma_sinh_vien, embedding)
    write_audit_log(
        session=session,
        account=current_account,
        hanh_dong="DUYET_KHUON_MAT",
        doi_tuong="AnhKhuonMat",
        doi_tuong_id=db_anh.ma_anh,
        du_lieu_truoc=before,
        du_lieu_sau=db_anh.model_dump(mode="json", exclude={"embedding_vector"}),
        request=request,
    )
    return db_anh


@router.patch(
    "/admin/{ma_anh}/tu-choi",
    response_model=AnhKhuonMatPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
def reject_face_image(
    request: Request,
    session: SessionDep,
    current_account: CurrentAccount,
    ma_anh: int,
    payload: FaceReviewRequest,
) -> Any:
    db_anh = session.get(AnhKhuonMat, ma_anh)
    if not db_anh:
        raise HTTPException(status_code=404, detail="Khong tim thay anh khuon mat")

    before = db_anh.model_dump(mode="json", exclude={"embedding_vector"})
    db_anh.trang_thai_duyet = "TU_CHOI"
    db_anh.ly_do_tu_choi = payload.ly_do_tu_choi or "Anh khong dat yeu cau"
    db_anh.ma_nguoi_duyet = current_account.ma_tai_khoan
    db_anh.thoi_gian_duyet = datetime.now(timezone.utc)
    session.add(db_anh)
    session.commit()
    session.refresh(db_anh)
    write_audit_log(
        session=session,
        account=current_account,
        hanh_dong="TU_CHOI_KHUON_MAT",
        doi_tuong="AnhKhuonMat",
        doi_tuong_id=db_anh.ma_anh,
        du_lieu_truoc=before,
        du_lieu_sau=db_anh.model_dump(mode="json", exclude={"embedding_vector"}),
        request=request,
    )
    return db_anh


class VerificationResult(BaseModel):
    verified: bool
    confidence: float | None = None
    message: str | None = None

@router.post("/xac-minh-truc-tiep", response_model=VerificationResult, dependencies=[Depends(get_current_active_sinhvien)])
async def xac_minh_truc_tiep(
    request: Request,
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
            
            ma_diem_danh = result.get("ma_diem_danh")
            if ma_diem_danh:
                evidence_dir = os.path.join("uploads", "attendance")
                os.makedirs(evidence_dir, exist_ok=True)
                evidence_name = f"dd_{ma_diem_danh}_{uuid.uuid4().hex[:8]}.jpg"
                evidence_path = os.path.join(evidence_dir, evidence_name)
                with open(evidence_path, "wb") as evidence_file:
                    evidence_file.write(content)
                session.add(
                    AnhDiemDanh(
                        ma_diem_danh=ma_diem_danh,
                        duong_dan_anh=evidence_path,
                        do_tin_cay=0.925,
                    )
                )
                session.commit()
                write_audit_log(
                    session=session,
                    account=current_account,
                    hanh_dong="DIEM_DANH_KHUON_MAT",
                    doi_tuong="DiemDanh",
                    doi_tuong_id=ma_diem_danh,
                    du_lieu_sau={
                        "ma_buoi_hoc": ma_buoi_hoc,
                        "ma_sinh_vien": sinh_vien.ma_sinh_vien,
                        "do_tin_cay": 0.925,
                        "anh_bang_chung": evidence_path,
                    },
                    request=request,
                )

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
