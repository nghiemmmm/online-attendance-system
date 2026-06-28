import io
import os
import pickle
from typing import Any

import faiss
import numpy as np
import torch
from facenet_pytorch import InceptionResnetV1, MTCNN
from PIL import Image
from fastapi import Request
from sqlmodel import Session, select

from app.models import FaceImage
from app.utils.logger import logger

UPLOAD_DIR = "uploads/faces"
DB_DIR = "vector_db/embeddings_db"
INDEX_PATH = os.path.join(DB_DIR, "faiss_index.bin")
META_PATH = os.path.join(DB_DIR, "names.pkl")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)


def normalize_embedding(embedding: Any) -> list[float]:
    """
    Convert supported embedding values to a plain float list.

    Args:
        embedding: Raw embedding value from NumPy, SQLModel, or plain Python.

    Returns:
        Embedding converted to a list of floats, or an empty list.
    """
    if embedding is None:
        return []
    if isinstance(embedding, np.ndarray):
        return embedding.astype("float32").tolist()
    return list(embedding)


class FaceRecognitionService:
    """Manage face embeddings, FAISS cache, and face recognition."""

    _instance: "FaceRecognitionService | None" = None

    def __new__(cls) -> "FaceRecognitionService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        self.device = torch.device("cpu")
        self.mtcnn = MTCNN(
            image_size=160,
            margin=0,
            min_face_size=20,
            thresholds=[0.6, 0.7, 0.7],
            factor=0.709,
            post_process=True,
            device=self.device,
            keep_all=True,
        )
        self.model = InceptionResnetV1(pretrained="vggface2").eval().to(self.device)
        self.index = None
        self.names: list[int] = []
        self._load_faiss_index()

    def _load_faiss_index(self) -> None:
        """
        Load the FAISS index from disk or rebuild it from the database.

        Returns:
            None.
        """
        if os.path.exists(INDEX_PATH) and os.path.exists(META_PATH):
            self.index = faiss.read_index(INDEX_PATH)
            with open(META_PATH, "rb") as metadata_file:
                self.names = pickle.load(metadata_file)
            logger.info(
                "Loaded FAISS index from local cache: %s faces",
                self.index.ntotal,
            )
            return

        self.index = faiss.IndexFlatL2(512)
        self.names = []
        self._sync_faiss_index_from_database()

    def _sync_faiss_index_from_database(self) -> None:
        """
        Rebuild the FAISS index from approved database embeddings.

        Returns:
            None.
        """
        try:
            from app.core.db import engine

            with Session(engine) as session:
                statement = select(FaceImage).where(
                    FaceImage.embedding_vector.is_not(None),
                    FaceImage.review_status == "DA_DUYET",
                )
                records = session.exec(statement).all()

            vectors: list[list[float]] = []
            names: list[int] = []
            for record in records:
                embedding = normalize_embedding(record.embedding_vector)
                if len(embedding) == 512:
                    vectors.append(embedding)
                    names.append(record.student_id)

            if vectors:
                vector_array = np.array(vectors, dtype="float32")
                self.index.add(vector_array)
                self.names = names
                logger.info(
                    "Synchronized FAISS index from database: %s faces",
                    self.index.ntotal,
                )
        except Exception:
            logger.exception("Error synchronizing face embeddings from database")
        finally:
            self._save_faiss_index()

    def _save_faiss_index(self) -> None:
        """
        Persist the FAISS index and metadata to local storage.

        Returns:
            None.
        """
        faiss.write_index(self.index, INDEX_PATH)
        with open(META_PATH, "wb") as metadata_file:
            pickle.dump(self.names, metadata_file)

    def extract_embeddings(self, image_bytes: bytes) -> list[np.ndarray]:
        """
        Return face embeddings found in one image.

        Args:
            image_bytes: Raw image bytes to inspect.

        Returns:
            List of face embedding arrays detected in the image.
        """
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            boxes, _ = self.mtcnn.detect(image)
            if boxes is None:
                return []

            faces = self.mtcnn(image)
            if faces is None:
                return []
            if faces.dim() == 3:
                faces = faces.unsqueeze(0)

            with torch.no_grad():
                embeddings = self.model(faces.to(self.device))

            return [
                embedding.cpu().numpy().astype("float32")
                for embedding in embeddings
            ]
        except Exception:
            logger.exception("Error extracting embeddings")
            return []

    def assess_face_image(
        self,
        image_bytes: bytes,
        min_quality: float = 0.75,
    ) -> tuple[bool, str, float, list[float]]:
        """
        Validate one enrollment image and return its face embedding.

        Args:
            image_bytes: Raw enrollment image bytes.
            min_quality: Minimum detector confidence required for acceptance.

        Returns:
            Tuple containing success status, message, quality score, and
            embedding values.
        """
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            boxes, probs = self.mtcnn.detect(image)
            if boxes is None or probs is None or len(boxes) == 0:
                return False, "Khong tim thay khuon mat trong anh", 0.0, []
            if len(boxes) > 1:
                return False, "Anh co nhieu hon 1 khuon mat", 0.0, []

            faces = self.mtcnn(image)
            if faces is None:
                return False, "Khong cat duoc khuon mat hop le", 0.0, []
            if faces.dim() == 3:
                faces = faces.unsqueeze(0)

            with torch.no_grad():
                embedding = (
                    self.model(faces.to(self.device))[0]
                    .cpu()
                    .numpy()
                    .astype("float32")
                )

            quality_score = float(round(max(0.0, min(1.0, float(probs[0]))), 4))
            if quality_score < min_quality:
                return (
                    False,
                    "Chat luong anh chua dat "
                    f"({quality_score:.4f} < {min_quality:.2f})",
                    quality_score,
                    embedding.tolist(),
                )
            return True, "Anh khuon mat hop le", quality_score, embedding.tolist()
        except Exception:
            logger.exception("Error assessing face image")
            return False, "Khong the kiem tra chat luong anh", 0.0, []

    def add_face_embedding(self, student_id: int, embedding: list[float]) -> None:
        """
        Add one student face embedding to the FAISS index.

        Args:
            student_id: Student identifier linked to the embedding.
            embedding: Face embedding values.

        Returns:
            None.
        """
        embedding = normalize_embedding(embedding)
        if len(embedding) != 512:
            return

        emb = np.array(embedding, dtype="float32")
        self.index.add(emb.reshape(1, -1))
        self.names.append(student_id)
        self._save_faiss_index()

    def register_face(
        self,
        student_id: int,
        image_bytes: bytes,
    ) -> tuple[bool, str, list[float]]:
        """
        Register a student's face from one image.

        Args:
            student_id: Student identifier linked to the face.
            image_bytes: Raw enrollment image bytes.

        Returns:
            Tuple containing success status, message, and embedding values.
        """
        embeddings = self.extract_embeddings(image_bytes)
        if not embeddings:
            return False, "Khong tim thay khuon mat trong anh", []
        if len(embeddings) > 1:
            return False, "Anh co nhieu hon 1 khuon mat", []

        embedding = embeddings[0]
        self.index.add(embedding.reshape(1, -1))
        self.names.append(student_id)
        self._save_faiss_index()
        return True, "Dang ky khuon mat thanh cong", embedding.tolist()

    def recognize_faces(self, image_bytes: bytes, tolerance: float = 0.85) -> list[int]:
        """
        Recognize student IDs from faces in one image.

        Args:
            image_bytes: Raw image bytes to inspect.
            tolerance: Maximum FAISS distance accepted as a match.

        Returns:
            List of recognized student identifiers.
        """
        if self.index.ntotal == 0:
            return []

        embeddings = self.extract_embeddings(image_bytes)
        if not embeddings:
            return []

        recognized_ids: set[int] = set()
        for embedding in embeddings:
            distances, indices = self.index.search(embedding.reshape(1, -1), k=1)
            if len(indices[0]) == 0:
                continue

            idx = indices[0][0]
            distance = distances[0][0]
            if distance < tolerance and idx < len(self.names):
                recognized_ids.add(self.names[idx])

        return list(recognized_ids)

    def list_face_images(
        self,
        *,
        session: Session,
        review_status: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Any:
        """List face image registration requests for administrators."""
        from app.models import FaceImagesPublic
        from sqlmodel import select, func

        statement = select(FaceImage)
        if review_status:
            statement = statement.where(FaceImage.review_status == review_status)

        count_statement = select(func.count()).select_from(statement.subquery())
        total = session.exec(count_statement).one()

        statement = statement.offset(skip).limit(limit)
        results = session.exec(statement).all()

        return FaceImagesPublic(data=results, count=total)

    async def register_student_face_db(
        self,
        *,
        session: Session,
        student_id: int,
        content: bytes,
    ) -> Any:
        """Register a student's face from one image, save it to the filesystem, and write to database."""
        from app.models import Student
        import aiofiles
        from app.core.exceptions import StudentNotFoundError, FaceQualityUnacceptableError

        student = session.get(Student, student_id)
        if not student:
            raise StudentNotFoundError("Khong tim thay sinh vien")

        success, message, quality_score, embedding = self.assess_face_image(
            image_bytes=content
        )
        if not success:
            raise FaceQualityUnacceptableError(message)

        import re
        import unicodedata
        combined = f"{student.last_name or ''}_{student.first_name or ''}"
        nfkd_form = unicodedata.normalize("NFKD", combined)
        only_ascii = nfkd_form.encode("ASCII", "ignore").decode("utf-8")
        full_name_ascii = re.sub(r"[^a-zA-Z0-9_]", "", only_ascii.replace(" ", "_"))

        filename = f"sv{student.student_id}_{full_name_ascii}.jpg"
        filepath = os.path.join("dataset", filename)

        async with aiofiles.open(filepath, "wb") as image_file:
            await image_file.write(content)

        image_record = FaceImage(
            student_id=student.student_id,
            image_path=filepath,
            image_type="DANG_KY",
            embedding_vector=embedding,
            quality_score=quality_score,
            review_status="CHO_DUYET",
        )
        session.add(image_record)
        session.commit()
        session.refresh(image_record)
        return image_record

    def approve_face_image(
        self,
        *,
        session: Session,
        image_id: int,
        reviewer_id: int,
    ) -> Any:
        """Approve a pending face image and update FAISS cache."""
        from datetime import datetime, timezone
        from app.core.exceptions import FaceImageNotFoundError, InvalidFaceEmbeddingError

        image_record = session.get(FaceImage, image_id)
        if not image_record:
            raise FaceImageNotFoundError("Khong tim thay anh khuon mat")

        embedding = normalize_embedding(image_record.embedding_vector)
        if len(embedding) != 512:
            raise InvalidFaceEmbeddingError("Anh chua co embedding hop le")

        image_record.review_status = "DA_DUYET"
        image_record.rejection_reason = None
        image_record.reviewer_id = reviewer_id
        image_record.reviewed_at = datetime.now(timezone.utc)

        session.add(image_record)
        session.commit()
        session.refresh(image_record)

        self.add_face_embedding(image_record.student_id, embedding)
        return image_record

    def reject_face_image(
        self,
        *,
        session: Session,
        image_id: int,
        reviewer_id: int,
        reason: str | None,
    ) -> Any:
        """Reject a pending face image."""
        from datetime import datetime, timezone
        from app.core.exceptions import FaceImageNotFoundError

        image_record = session.get(FaceImage, image_id)
        if not image_record:
            raise FaceImageNotFoundError("Khong tim thay anh khuon mat")

        image_record.review_status = "TU_CHOI"
        image_record.rejection_reason = reason
        image_record.reviewer_id = reviewer_id
        image_record.reviewed_at = datetime.now(timezone.utc)

        session.add(image_record)
        session.commit()
        session.refresh(image_record)
        return image_record

    def save_attendance_evidence(
        self,
        *,
        session: Session,
        attendance_id: int,
        image_bytes: bytes,
        confidence: float,
    ) -> str:
        """Save attendance evidence image and create its database record."""
        from app.models import AttendanceImage
        import uuid

        evidence_dir = os.path.join("uploads", "attendance")
        os.makedirs(evidence_dir, exist_ok=True)
        evidence_name = f"dd_{attendance_id}_{uuid.uuid4().hex[:8]}.jpg"
        evidence_path = os.path.join(evidence_dir, evidence_name)

        with open(evidence_path, "wb") as evidence_file:
            evidence_file.write(image_bytes)

        session.add(
            AttendanceImage(
                attendance_id=attendance_id,
                image_path=evidence_path,
                confidence=confidence,
            )
        )
        session.commit()
        return evidence_path

    def auto_register_and_verify(
        self,
        *,
        session: Session,
        student_id: int,
        class_session_id: int | None,
        image_bytes: bytes,
        auto_register_confidence: float = 0.95,
    ) -> dict[str, Any]:
        """Auto-register a student's face and optionally record attendance."""
        from app.models import FaceImage
        from app.crud.attendance_crud import mark_attendance_by_lora

        try:
            success, message, quality_score, embedding = self.assess_face_image(
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
            filepath = os.path.join("dataset", f"sv{student_id}_auto.jpg")
            with open(filepath, "wb") as image_file:
                image_file.write(image_bytes)

            existing = session.exec(
                select(FaceImage)
                .where(FaceImage.student_id == student_id)
                .where(FaceImage.image_type == "DANG_KY")
            ).first()
            if existing:
                existing.image_path = filepath
                existing.embedding_vector = embedding
                existing.quality_score = quality_score
                existing.review_status = "DA_DUYET"
                session.add(existing)
            else:
                session.add(
                    FaceImage(
                        student_id=student_id,
                        image_path=filepath,
                        image_type="DANG_KY",
                        embedding_vector=embedding,
                        quality_score=quality_score,
                        review_status="DA_DUYET",
                    )
                )
            session.commit()

            self.add_face_embedding(student_id, embedding)
            logger.info("Auto-registered face for student %s", student_id)

            if class_session_id:
                result = mark_attendance_by_lora(
                    session=session,
                    class_session_id=class_session_id,
                    student_ids=[student_id],
                    average_confidence=auto_register_confidence,
                )

                # Check status text mapping
                status_map = {
                    "CO_MAT": "Co mat",
                    "DI_MUON": "Di muon",
                    "VANG": "Vang",
                }
                status_text = status_map.get(result.get("status"), "Co mat")
                return {
                    "verified": True,
                    "confidence": auto_register_confidence * 100,
                    "message": "Da tu dong dang ky khuon mat va diem danh "
                    f"thanh cong ({status_text})",
                }

            return {
                "verified": True,
                "confidence": auto_register_confidence * 100,
                "message": "Da tu dong dang ky khuon mat moi thanh cong",
            }
        except Exception:
            logger.exception("Auto-registration during verification failed")
            return {
                "verified": False,
                "confidence": 0,
                "message": "Loi trong qua trinh tu dong nhan dien",
            }


face_service: FaceRecognitionService | None = None


def get_or_create_face_service() -> FaceRecognitionService:
    """Return the process-local FaceRecognitionService singleton."""
    global face_service
    if face_service is None:
        face_service = FaceRecognitionService()
    return face_service


def get_face_service(request: Request) -> FaceRecognitionService:
    """Dependency provider that prefers the FastAPI app state cache."""
    service = getattr(request.app.state, "face_service", None)
    if service is None:
        service = get_or_create_face_service()
        request.app.state.face_service = service
    return service


