"""Define APIs for face enrollment and live face verification."""

import re
import unicodedata
import uuid
from typing import Annotated, Any

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from pydantic import Field, field_validator
from sqlmodel import select

from app.api.deps import (
    CurrentAccount,
    SessionDep,
    get_current_account,
    get_current_active_superuser,
)
from app.crud import student_crud
from app.models import (
    AttendanceImage,
    FaceImage,
    FaceImagePublic,
    FaceImagesPublic,
)
from app.models.base import AppBaseModel
from app.services.audit_log_service import write_audit_log
from app.services.face_service import FaceRecognitionService, get_face_service

router = APIRouter(prefix="/face-images", tags=["face-images"])
verification_router = APIRouter(
    prefix="/face-verifications", tags=["face-verifications"]
)

ATTENDANCE_CONFIDENCE = 0.925
AUTO_REGISTER_CONFIDENCE = 0.95


def to_ascii_name(last_name: str, first_name: str) -> str:
    """
    Normalize Vietnamese names into filesystem-safe ASCII names.

    Args:
        last_name: Student family name.
        first_name: Student given name.

    Returns:
        ASCII-safe name fragment for filenames.
    """
    combined = f"{last_name}_{first_name}"
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
    attendance_id: int,
    image_bytes: bytes,
    confidence: float,
) -> str:
    """
    Save attendance evidence image and create its database record.

    Args:
        session: Active database session.
        attendance_id: Attendance record identifier.
        image_bytes: Raw attendance evidence image bytes.
        confidence: Face verification confidence value.

    Returns:
        Saved evidence image path.
    """
    from app.storage.storage_factory import get_storage_service

    storage_service = get_storage_service()
    evidence_name = f"dd_{attendance_id}_{uuid.uuid4().hex[:8]}.jpg"

    metadata = storage_service.save_image(
        file_bytes=image_bytes,
        filename=evidence_name,
        folder="online_attendance/evidence",
    )

    session.add(
        AttendanceImage(
            attendance_id=attendance_id,
            confidence=confidence,
            image_path=metadata.get("image_path"),
            storage_provider=metadata.get("storage_provider"),
            public_id=metadata.get("public_id"),
            secure_url=metadata.get("secure_url"),
            version=metadata.get("version"),
            file_size=metadata.get("file_size"),
            mime_type=metadata.get("mime_type"),
            width=metadata.get("width"),
            height=metadata.get("height"),
        )
    )
    session.commit()
    return metadata.get("secure_url") or metadata.get("image_path") or ""


@router.post(
    "/",
    response_model=FaceImagePublic,
    dependencies=[Depends(get_current_active_superuser)],
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Lỗi file không đúng định dạng ảnh hoặc khuôn mặt không đạt yêu cầu chất lượng/không có khuôn mặt"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Không tìm thấy hồ sơ sinh viên tương ứng"
        },
    },
)
async def admin_dang_ky_khuon_mat(
    request: Request,
    session: SessionDep,
    current_account: CurrentAccount,
    student_id: Annotated[int, Form()],
    file: Annotated[UploadFile, File()],
    image_type: Annotated[str, Form()] = "chinh_dien",
    face_service: FaceRecognitionService = Depends(get_face_service),
) -> Any:
    """
    Allow an administrator to register a student's face image.

    Args:
        request: Incoming FastAPI request.
        session: Active database session.
        current_account: Authenticated administrator account.
        student_id: Student identifier.
        file: Uploaded face image.
        image_type: Face angle type.

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
    image_record = await face_service.register_student_face_db(
        session=session,
        student_id=student_id,
        content=content,
        image_type=image_type,
    )
    write_audit_log(
        session=session,
        account=current_account,
        action="DANG_KY_KHUON_MAT",
        target_type="FaceImage",
        target_id=image_record.image_id,
        after_data={
            "student_id": image_record.student_id,
            "quality_score": image_record.quality_score,
            "review_status": image_record.review_status,
        },
        request=request,
    )

    return image_record


@router.get(
    "/",
    response_model=FaceImagesPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
def read_admin_face_images(
    session: SessionDep,
    review_status: str | None = None,
    skip: int = 0,
    limit: int = 100,
    face_service: FaceRecognitionService = Depends(get_face_service),
) -> Any:
    """
    List face image registration requests for administrators.

    Args:
        session: Active database session.
        review_status: Optional review status filter.
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        Dictionary containing records and total count.
    """
    return face_service.list_face_images(
        session=session,
        review_status=review_status,
        skip=skip,
        limit=limit,
    )


class FaceReviewRequest(AppBaseModel):
    """Represent face review rejection data."""

    review_status: str = Field(min_length=1, max_length=30)
    rejection_reason: str | None = Field(default=None, max_length=500)

    @field_validator("rejection_reason")
    @classmethod
    def _normalize_reason(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


@router.patch(
    "/{image_id}",
    response_model=FaceImagePublic,
    dependencies=[Depends(get_current_active_superuser)],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Không tìm thấy ảnh khuôn mặt"},
        status.HTTP_400_BAD_REQUEST: {
            "description": "Ảnh không hợp lệ để duyệt (thiếu dữ liệu embedding vector)"
        },
    },
)
def review_face_image(
    request: Request,
    session: SessionDep,
    current_account: CurrentAccount,
    image_id: int,
    payload: FaceReviewRequest,
    face_service: FaceRecognitionService = Depends(get_face_service),
) -> Any:
    """
    Approve a pending face image and add it to the FAISS cache.

    Args:
        request: Incoming FastAPI request.
        session: Active database session.
        current_account: Authenticated administrator account.
        image_id: Face image identifier.

    Returns:
        Approved face image record.

    Raises:
        HTTPException: If the image is missing or has invalid embedding data.
    """
    existing_image_before = session.get(FaceImage, image_id)
    if not existing_image_before:
        raise HTTPException(status_code=404, detail="Khong tim thay anh khuon mat")
    before = existing_image_before.model_dump(mode="json", exclude={"embedding_vector"})

    normalized_status = payload.review_status.strip().lower()
    if normalized_status in {"rejected", "tu_choi", "tu-choi"}:
        image_record = face_service.reject_face_image(
            session=session,
            image_id=image_id,
            reviewer_id=current_account.account_id,
            reason=payload.rejection_reason or "Anh khong dat yeu cau",
        )
        write_audit_log(
            session=session,
            account=current_account,
            action="TU_CHOI_KHUON_MAT",
            target_type="FaceImage",
            target_id=image_record.image_id,
            before_data=before,
            after_data=image_record.model_dump(
                mode="json", exclude={"embedding_vector"}
            ),
            request=request,
        )
        return image_record

    if normalized_status not in {"approved", "da_duyet", "da-duyet"}:
        raise HTTPException(status_code=400, detail="Unsupported review status")

    image_record = face_service.approve_face_image(
        session=session,
        image_id=image_id,
        reviewer_id=current_account.account_id,
    )
    write_audit_log(
        session=session,
        account=current_account,
        action="DUYET_KHUON_MAT",
        target_type="FaceImage",
        target_id=image_record.image_id,
        before_data=before,
        after_data=image_record.model_dump(mode="json", exclude={"embedding_vector"}),
        request=request,
    )
    return image_record


@router.patch(
    "/{image_id}",
    response_model=FaceImagePublic,
    dependencies=[Depends(get_current_active_superuser)],
    include_in_schema=False,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Không tìm thấy ảnh khuôn mặt"}
    },
)
def reject_face_image(
    request: Request,
    session: SessionDep,
    current_account: CurrentAccount,
    image_id: int,
    payload: FaceReviewRequest,
    face_service: FaceRecognitionService = Depends(get_face_service),
) -> Any:
    """
    Reject a pending face image.

    Args:
        request: Incoming FastAPI request.
        session: Active database session.
        current_account: Authenticated administrator account.
        image_id: Face image identifier.
        payload: Rejection payload.

    Returns:
        Rejected face image record.

    Raises:
        HTTPException: If the image is missing.
    """
    existing_image_before = session.get(FaceImage, image_id)
    if not existing_image_before:
        raise HTTPException(status_code=404, detail="Khong tim thay anh khuon mat")
    before = existing_image_before.model_dump(mode="json", exclude={"embedding_vector"})

    image_record = face_service.reject_face_image(
        session=session,
        image_id=image_id,
        reviewer_id=current_account.account_id,
        reason=payload.rejection_reason or "Anh khong dat yeu cau",
    )
    write_audit_log(
        session=session,
        account=current_account,
        action="TU_CHOI_KHUON_MAT",
        target_type="FaceImage",
        target_id=image_record.image_id,
        before_data=before,
        after_data=image_record.model_dump(mode="json", exclude={"embedding_vector"}),
        request=request,
    )
    return image_record


class VerificationResult(AppBaseModel):
    """Represent live face verification result data."""

    verified: bool
    confidence: float | None = Field(default=None, ge=0.0, le=100.0)
    message: str | None = None


@verification_router.post(
    "/",
    response_model=VerificationResult,
    dependencies=[Depends(get_current_account)],
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Lỗi định dạng ảnh hoặc lỗi trong quá trình phân tích đặc trưng khuôn mặt"
        }
    },
)
async def xac_minh_truc_tiep(
    request: Request,
    session: SessionDep,
    current_account: CurrentAccount,
    background_tasks: BackgroundTasks,
    file: Annotated[UploadFile, File()],
    class_session_id: Annotated[int | None, Form()] = None,
    face_service: FaceRecognitionService = Depends(get_face_service),
) -> Any:
    """
    Verify a student's face from a live webcam frame.
    """
    content = await file.read()
    student = student_crud.get_student_by_account_id(
        session=session,
        account_id=current_account.account_id,
    )
    if not student:
        from app.core.config import settings

        recognized_ids = face_service.recognize_faces(
            image_bytes=content, tolerance=settings.FACE_RECOGNITION_TOLERANCE
        )
        return {
            "verified": bool(recognized_ids),
            "confidence": 95.0 if recognized_ids else 0.0,
            "message": f"Nhận diện thành công sinh viên ID {recognized_ids[0]}"
            if recognized_ids
            else "Không tìm thấy hồ sơ sinh viên liên kết",
        }
    # Check if student has any approved face registrations
    from app.models import FaceImage

    face_exists = session.exec(
        select(FaceImage)
        .where(FaceImage.student_id == student.student_id)
        .where(FaceImage.review_status == "DA_DUYET")
    ).first()

    if not face_exists:
        return {
            "verified": False,
            "confidence": 0.0,
            "message": "Sinh viên chưa đăng ký khuôn mặt hoặc chưa được phê duyệt",
        }

    from app.core.config import settings

    recognized_ids = face_service.recognize_faces(
        image_bytes=content, tolerance=settings.FACE_RECOGNITION_TOLERANCE
    )

    if student.student_id in recognized_ids:
        if class_session_id:
            return _record_verified_attendance(
                request=request,
                session=session,
                current_account=current_account,
                background_tasks=background_tasks,
                student_id=student.student_id,
                class_session_id=class_session_id,
                image_bytes=content,
                face_service=face_service,
            )

        return {
            "verified": True,
            "confidence": ATTENDANCE_CONFIDENCE * 100,
            "message": "Xác minh thành công",
        }

    return {
        "verified": False,
        "confidence": 0.0,
        "message": "Khuôn mặt không khớp với cơ sở dữ liệu đăng ký",
    }


def _record_verified_attendance(
    *,
    request: Request,
    session: SessionDep,
    current_account: CurrentAccount,
    background_tasks: BackgroundTasks,
    student_id: int,
    class_session_id: int,
    image_bytes: bytes,
    face_service: FaceRecognitionService,
) -> dict[str, Any]:
    """
    Record attendance after a successful face verification.

    Args:
        request: Incoming FastAPI request.
        session: Active database session.
        current_account: Authenticated student account.
        background_tasks: Background tasks runner.
        student_id: Student identifier.
        class_session_id: Lesson identifier.
        image_bytes: Raw evidence image bytes.
        face_service: Injected FaceRecognitionService.

    Returns:
        Verification result payload with attendance status.
    """
    from app.crud.attendance_crud import mark_attendance_by_lora

    result = mark_attendance_by_lora(
        session=session,
        class_session_id=class_session_id,
        student_ids=[student_id],
        average_confidence=ATTENDANCE_CONFIDENCE,
    )
    if not result.get("success"):
        return {
            "verified": True,
            "confidence": ATTENDANCE_CONFIDENCE * 100,
            "message": f"Nhan dang khop nhung loi ghi nhan: {result.get('message')}",
        }

    attendance_id = result.get("attendance_id")
    if attendance_id:
        # Define a helper function to perform the save in the background
        def upload_evidence_task(att_id: int, img_bytes: bytes, conf: float):
            from sqlmodel import Session

            from app.core.db import engine

            with Session(engine) as bg_session:
                face_service.save_attendance_evidence(
                    session=bg_session,
                    attendance_id=att_id,
                    image_bytes=img_bytes,
                    confidence=conf,
                )

        background_tasks.add_task(
            upload_evidence_task, attendance_id, image_bytes, ATTENDANCE_CONFIDENCE
        )

        write_audit_log(
            session=session,
            account=current_account,
            action="DIEM_DANH_KHUON_MAT",
            target_type="Attendance",
            target_id=attendance_id,
            after_data={
                "class_session_id": class_session_id,
                "student_id": student_id,
                "confidence": ATTENDANCE_CONFIDENCE,
                "evidence_image": f"Pending background upload for attendance {attendance_id}",
            },
            request=request,
        )

    status_text = get_attendance_status_text(result.get("status"))
    return {
        "verified": True,
        "confidence": ATTENDANCE_CONFIDENCE * 100,
        "message": f"Xac minh va diem danh thanh cong ({status_text})",
    }
