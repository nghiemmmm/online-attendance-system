"""Define APIs for face enrollment and live face verification."""

import os
import re
import unicodedata
import uuid
from datetime import datetime, timezone
from typing import Annotated, Any

import aiofiles
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from pydantic import BaseModel
from sqlmodel import select

from app.api.deps import (
    CurrentAccount,
    SessionDep,
    get_current_active_student,
    get_current_active_superuser,
)
from app.crud import sinhvien_crud
from app.models import (
    AnhDiemDanh,
    AnhKhuonMat,
    AnhKhuonMatPublic,
    AnhKhuonMatsPublic,
    SinhVien,
)
from app.services.audit_log_service import write_audit_log
from app.services.face_service import face_service, normalize_embedding
from app.utils.logger import logger

router = APIRouter(prefix="/anh-khuon-mat", tags=["anh-khuon-mat"])

ATTENDANCE_CONFIDENCE = 0.925
AUTO_REGISTER_CONFIDENCE = 0.95


def to_ascii_name(ho: str, ten: str) -> str:
    """
    Normalize Vietnamese names into filesystem-safe ASCII names.

    Args:
        ho: Student family name.
        ten: Student given name.

    Returns:
        ASCII-safe name fragment for filenames.
    """
    combined = f"{ho}_{ten}"
    nfkd_form = unicodedata.normalize("NFKD", combined)
    only_ascii = nfkd_form.encode("ASCII", "ignore").decode("utf-8")
    return re.sub(r"[^a-zA-Z0-9_]", "", only_ascii.replace(" ", "_"))


def get_attendance_status_text(status: str | None) -> str:
    """
    Map attendance status codes to short display text.

    Args:
        status: Attendance status code.

    Returns:
        Human-readable attendance status text.
    """
    status_map = {
        "CO_MAT": "Co mat",
        "DI_MUON": "Di muon",
        "VANG": "Vang",
    }
    return status_map.get(status, "Co mat")


def save_attendance_evidence(
    *,
    session: SessionDep,
    ma_diem_danh: int,
    image_bytes: bytes,
    confidence: float,
) -> str:
    """
    Save attendance evidence image and create its database record.

    Args:
        session: Active database session.
        ma_diem_danh: Attendance record identifier.
        image_bytes: Raw attendance evidence image bytes.
        confidence: Face verification confidence value.

    Returns:
        Saved evidence image path.
    """
    evidence_dir = os.path.join("uploads", "attendance")
    os.makedirs(evidence_dir, exist_ok=True)
    evidence_name = f"dd_{ma_diem_danh}_{uuid.uuid4().hex[:8]}.jpg"
    evidence_path = os.path.join(evidence_dir, evidence_name)

    with open(evidence_path, "wb") as evidence_file:
        evidence_file.write(image_bytes)

    session.add(
        AnhDiemDanh(
            ma_diem_danh=ma_diem_danh,
            duong_dan_anh=evidence_path,
            do_tin_cay=confidence,
        )
    )
    session.commit()
    return evidence_path


@router.post(
    "/admin/dang-ky",
    response_model=AnhKhuonMatPublic,
    dependencies=[Depends(get_current_active_superuser)],
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Lỗi file không đúng định dạng ảnh hoặc khuôn mặt không đạt yêu cầu chất lượng/không có khuôn mặt"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Không tìm thấy hồ sơ sinh viên tương ứng"
        }
    }
)
async def admin_dang_ky_khuon_mat(
    request: Request,
    session: SessionDep,
    current_account: CurrentAccount,
    ma_sinh_vien: Annotated[int, Form()],
    file: Annotated[UploadFile, File()],
) -> Any:
    """
    Allow an administrator to register a student's face image.

    Args:
        request: Incoming FastAPI request.
        session: Active database session.
        current_account: Authenticated administrator account.
        ma_sinh_vien: Student identifier.
        file: Uploaded face image.

    Returns:
        Created face enrollment image record.

    Raises:
        HTTPException: If the upload is invalid or the student is missing.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Vui long upload file anh JPEG hoac PNG",
        )

    content = await file.read()
    db_anh = await face_service.register_student_face_db(
        session=session,
        ma_sinh_vien=ma_sinh_vien,
        content=content,
    )
    write_audit_log(
        session=session,
        account=current_account,
        hanh_dong="DANG_KY_KHUON_MAT",
        doi_tuong="AnhKhuonMat",
        doi_tuong_id=db_anh.ma_anh,
        du_lieu_sau={
            "ma_sinh_vien": db_anh.ma_sinh_vien,
            "diem_chat_luong": db_anh.diem_chat_luong,
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
    """
    List face image registration requests for administrators.

    Args:
        session: Active database session.
        trang_thai_duyet: Optional review status filter.
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        Dictionary containing records and total count.
    """
    return face_service.list_face_images(
        session=session,
        trang_thai_duyet=trang_thai_duyet,
        skip=skip,
        limit=limit,
    )


class FaceReviewRequest(BaseModel):
    """Represent face review rejection data."""

    ly_do_tu_choi: str | None = None


@router.patch(
    "/admin/{ma_anh}/duyet",
    response_model=AnhKhuonMatPublic,
    dependencies=[Depends(get_current_active_superuser)],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Không tìm thấy ảnh khuôn mặt"
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Ảnh không hợp lệ để duyệt (thiếu dữ liệu embedding vector)"
        }
    }
)
def approve_face_image(
    request: Request,
    session: SessionDep,
    current_account: CurrentAccount,
    ma_anh: int,
) -> Any:
    """
    Approve a pending face image and add it to the FAISS cache.

    Args:
        request: Incoming FastAPI request.
        session: Active database session.
        current_account: Authenticated administrator account.
        ma_anh: Face image identifier.

    Returns:
        Approved face image record.

    Raises:
        HTTPException: If the image is missing or has invalid embedding data.
    """
    db_anh_pre = session.get(AnhKhuonMat, ma_anh)
    if not db_anh_pre:
        raise HTTPException(status_code=404, detail="Khong tim thay anh khuon mat")
    before = db_anh_pre.model_dump(mode="json", exclude={"embedding_vector"})

    db_anh = face_service.approve_face_image(
        session=session,
        ma_anh=ma_anh,
        reviewer_id=current_account.ma_tai_khoan,
    )
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
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Không tìm thấy ảnh khuôn mặt"
        }
    }
)
def reject_face_image(
    request: Request,
    session: SessionDep,
    current_account: CurrentAccount,
    ma_anh: int,
    payload: FaceReviewRequest,
) -> Any:
    """
    Reject a pending face image.

    Args:
        request: Incoming FastAPI request.
        session: Active database session.
        current_account: Authenticated administrator account.
        ma_anh: Face image identifier.
        payload: Rejection payload.

    Returns:
        Rejected face image record.

    Raises:
        HTTPException: If the image is missing.
    """
    db_anh_pre = session.get(AnhKhuonMat, ma_anh)
    if not db_anh_pre:
        raise HTTPException(status_code=404, detail="Khong tim thay anh khuon mat")
    before = db_anh_pre.model_dump(mode="json", exclude={"embedding_vector"})

    db_anh = face_service.reject_face_image(
        session=session,
        ma_anh=ma_anh,
        reviewer_id=current_account.ma_tai_khoan,
        reason=payload.ly_do_tu_choi or "Anh khong dat yeu cau",
    )
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
    """Represent live face verification result data."""

    verified: bool
    confidence: float | None = None
    message: str | None = None


@router.post(
    "/xac-minh-truc-tiep",
    response_model=VerificationResult,
    dependencies=[Depends(get_current_active_student)],
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Lỗi định dạng ảnh hoặc lỗi trong quá trình phân tích đặc trưng khuôn mặt"
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Không tìm thấy hồ sơ sinh viên liên kết với tài khoản đang đăng nhập"
        }
    }
)
async def xac_minh_truc_tiep(
    request: Request,
    session: SessionDep,
    current_account: CurrentAccount,
    file: Annotated[UploadFile, File()],
    ma_buoi_hoc: Annotated[int | None, Form()] = None,
) -> Any:
    """
    Verify a student's face from a live webcam frame.

    Args:
        request: Incoming FastAPI request.
        session: Active database session.
        current_account: Authenticated student account.
        file: Uploaded webcam frame image.
        ma_buoi_hoc: Optional lesson identifier for attendance recording.

    Returns:
        Face verification and optional attendance result data.
    """
    sinh_vien = sinhvien_crud.get_student_by_account_id(
        session=session,
        ma_tai_khoan=current_account.ma_tai_khoan,
    )
    if not sinh_vien:
        return {"verified": False, "message": "Khong tim thay thong tin sinh vien"}

    content = await file.read()
    recognized_ids = face_service.recognize_faces(image_bytes=content, tolerance=0.85)

    if sinh_vien.ma_sinh_vien in recognized_ids:
        if ma_buoi_hoc:
            return _record_verified_attendance(
                request=request,
                session=session,
                current_account=current_account,
                sinh_vien_id=sinh_vien.ma_sinh_vien,
                ma_buoi_hoc=ma_buoi_hoc,
                image_bytes=content,
            )

        return {
            "verified": True,
            "confidence": ATTENDANCE_CONFIDENCE * 100,
            "message": "Xac minh thanh cong",
        }

    return _auto_register_and_verify(
        session=session,
        ma_sinh_vien=sinh_vien.ma_sinh_vien,
        ma_buoi_hoc=ma_buoi_hoc,
        image_bytes=content,
    )


def _record_verified_attendance(
    *,
    request: Request,
    session: SessionDep,
    current_account: CurrentAccount,
    sinh_vien_id: int,
    ma_buoi_hoc: int,
    image_bytes: bytes,
) -> dict[str, Any]:
    """
    Record attendance after a successful face verification.

    Args:
        request: Incoming FastAPI request.
        session: Active database session.
        current_account: Authenticated student account.
        sinh_vien_id: Student identifier.
        ma_buoi_hoc: Lesson identifier.
        image_bytes: Raw evidence image bytes.

    Returns:
        Verification result payload with attendance status.
    """
    from app.crud.diemdanh_crud import mark_attendance_by_lora

    result = mark_attendance_by_lora(
        session=session,
        ma_buoi_hoc=ma_buoi_hoc,
        danh_sach_ma_sinh_vien=[sinh_vien_id],
        do_tin_cay_trung_binh=ATTENDANCE_CONFIDENCE,
    )
    if not result.get("success"):
        return {
            "verified": True,
            "confidence": ATTENDANCE_CONFIDENCE * 100,
            "message": f"Nhan dang khop nhung loi ghi nhan: {result.get('message')}",
        }

    ma_diem_danh = result.get("ma_diem_danh")
    if ma_diem_danh:
        evidence_path = save_attendance_evidence(
            session=session,
            ma_diem_danh=ma_diem_danh,
            image_bytes=image_bytes,
            confidence=ATTENDANCE_CONFIDENCE,
        )
        write_audit_log(
            session=session,
            account=current_account,
            hanh_dong="DIEM_DANH_KHUON_MAT",
            doi_tuong="DiemDanh",
            doi_tuong_id=ma_diem_danh,
            du_lieu_sau={
                "ma_buoi_hoc": ma_buoi_hoc,
                "ma_sinh_vien": sinh_vien_id,
                "do_tin_cay": ATTENDANCE_CONFIDENCE,
                "anh_bang_chung": evidence_path,
            },
            request=request,
        )

    status_text = get_attendance_status_text(result.get("trang_thai"))
    return {
        "verified": True,
        "confidence": ATTENDANCE_CONFIDENCE * 100,
        "message": f"Xac minh va diem danh thanh cong ({status_text})",
    }


def _auto_register_and_verify(
    *,
    session: SessionDep,
    ma_sinh_vien: int,
    ma_buoi_hoc: int | None,
    image_bytes: bytes,
) -> dict[str, Any]:
    """
    Auto-register a student's face and optionally record attendance.

    Args:
        session: Active database session.
        ma_sinh_vien: Student identifier.
        ma_buoi_hoc: Optional lesson identifier.
        image_bytes: Raw face image bytes.

    Returns:
        Verification result payload.
    """
    try:
        success, message, quality_score, embedding = face_service.assess_face_image(
            image_bytes,
            min_quality=0.5,
        )
        if not success or len(embedding) != 512:
            return {
                "verified": False,
                "confidence": 0,
                "message": f"Nhan dang that bai: {message}",
            }

        os.makedirs("dataset", exist_ok=True)
        filepath = os.path.join("dataset", f"sv{ma_sinh_vien}_auto.jpg")
        with open(filepath, "wb") as image_file:
            image_file.write(image_bytes)

        existing = session.exec(
            select(AnhKhuonMat)
            .where(AnhKhuonMat.ma_sinh_vien == ma_sinh_vien)
            .where(AnhKhuonMat.loai_anh == "DANG_KY")
        ).first()
        if existing:
            existing.duong_dan_anh = filepath
            existing.embedding_vector = embedding
            existing.diem_chat_luong = quality_score
            existing.trang_thai_duyet = "DA_DUYET"
            session.add(existing)
        else:
            session.add(
                AnhKhuonMat(
                    ma_sinh_vien=ma_sinh_vien,
                    duong_dan_anh=filepath,
                    loai_anh="DANG_KY",
                    embedding_vector=embedding,
                    diem_chat_luong=quality_score,
                    trang_thai_duyet="DA_DUYET",
                )
            )
        session.commit()

        face_service.add_face_embedding(ma_sinh_vien, embedding)
        logger.info("Auto-registered face for student %s", ma_sinh_vien)

        if ma_buoi_hoc:
            return _record_auto_registered_attendance(
                session=session,
                ma_sinh_vien=ma_sinh_vien,
                ma_buoi_hoc=ma_buoi_hoc,
            )

        return {
            "verified": True,
            "confidence": AUTO_REGISTER_CONFIDENCE * 100,
            "message": "Da tu dong dang ky khuon mat moi thanh cong",
        }
    except Exception:
        logger.exception("Auto-registration during verification failed")
        return {
            "verified": False,
            "confidence": 0,
            "message": "Loi trong qua trinh tu dong nhan dien",
        }


def _record_auto_registered_attendance(
    *,
    session: SessionDep,
    ma_sinh_vien: int,
    ma_buoi_hoc: int,
) -> dict[str, Any]:
    """
    Record attendance after an automatic face registration.

    Args:
        session: Active database session.
        ma_sinh_vien: Student identifier.
        ma_buoi_hoc: Lesson identifier.

    Returns:
        Verification result payload with attendance status.
    """
    from app.crud.diemdanh_crud import mark_attendance_by_lora

    result = mark_attendance_by_lora(
        session=session,
        ma_buoi_hoc=ma_buoi_hoc,
        danh_sach_ma_sinh_vien=[ma_sinh_vien],
        do_tin_cay_trung_binh=AUTO_REGISTER_CONFIDENCE,
    )
    status_text = get_attendance_status_text(result.get("trang_thai"))
    return {
        "verified": True,
        "confidence": AUTO_REGISTER_CONFIDENCE * 100,
        "message": "Da tu dong dang ky khuon mat va diem danh "
        f"thanh cong ({status_text})",
    }
