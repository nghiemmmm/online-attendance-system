import io
import os
import pickle
from typing import Any

import faiss
import numpy as np
import torch
from facenet_pytorch import InceptionResnetV1, MTCNN
from PIL import Image
from sqlmodel import Session, select

from app.models import AnhKhuonMat
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
                statement = select(AnhKhuonMat).where(
                    AnhKhuonMat.embedding_vector.is_not(None),
                    AnhKhuonMat.trang_thai_duyet == "DA_DUYET",
                )
                records = session.exec(statement).all()

            vectors: list[list[float]] = []
            names: list[int] = []
            for record in records:
                embedding = normalize_embedding(record.embedding_vector)
                if len(embedding) == 512:
                    vectors.append(embedding)
                    names.append(record.ma_sinh_vien)

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

    def add_face_embedding(self, ma_sinh_vien: int, embedding: list[float]) -> None:
        """
        Add one student face embedding to the FAISS index.

        Args:
            ma_sinh_vien: Student identifier linked to the embedding.
            embedding: Face embedding values.

        Returns:
            None.
        """
        embedding = normalize_embedding(embedding)
        if len(embedding) != 512:
            return

        emb = np.array(embedding, dtype="float32")
        self.index.add(emb.reshape(1, -1))
        self.names.append(ma_sinh_vien)
        self._save_faiss_index()

    def register_face(
        self,
        ma_sinh_vien: int,
        image_bytes: bytes,
    ) -> tuple[bool, str, list[float]]:
        """
        Register a student's face from one image.

        Args:
            ma_sinh_vien: Student identifier linked to the face.
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
        self.names.append(ma_sinh_vien)
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
        trang_thai_duyet: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Any:
        """List face image registration requests for administrators."""
        from app.models import AnhKhuonMatsPublic
        from sqlmodel import select, func

        statement = select(AnhKhuonMat)
        if trang_thai_duyet:
            statement = statement.where(AnhKhuonMat.trang_thai_duyet == trang_thai_duyet)

        count_statement = select(func.count()).select_from(statement.subquery())
        total = session.exec(count_statement).one()

        statement = statement.offset(skip).limit(limit)
        results = session.exec(statement).all()

        return AnhKhuonMatsPublic(data=results, count=total)

    async def register_student_face_db(
        self,
        *,
        session: Session,
        ma_sinh_vien: int,
        content: bytes,
    ) -> Any:
        """Register a student's face from one image, save it to the filesystem, and write to database."""
        from app.models import SinhVien
        import aiofiles
        from app.core.exceptions import StudentNotFoundError, FaceQualityUnacceptableError

        sinh_vien = session.get(SinhVien, ma_sinh_vien)
        if not sinh_vien:
            raise StudentNotFoundError("Khong tim thay sinh vien")

        success, message, quality_score, embedding = self.assess_face_image(
            image_bytes=content
        )
        if not success:
            raise FaceQualityUnacceptableError(message)

        import re
        import unicodedata
        combined = f"{sinh_vien.ho or ''}_{sinh_vien.ten or ''}"
        nfkd_form = unicodedata.normalize("NFKD", combined)
        only_ascii = nfkd_form.encode("ASCII", "ignore").decode("utf-8")
        ho_ten_ascii = re.sub(r"[^a-zA-Z0-9_]", "", only_ascii.replace(" ", "_"))

        filename = f"sv{sinh_vien.ma_sinh_vien}_{ho_ten_ascii}.jpg"
        filepath = os.path.join("dataset", filename)

        async with aiofiles.open(filepath, "wb") as image_file:
            await image_file.write(content)

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
        return db_anh

    def approve_face_image(
        self,
        *,
        session: Session,
        ma_anh: int,
        reviewer_id: int,
    ) -> Any:
        """Approve a pending face image and update FAISS cache."""
        from datetime import datetime, timezone
        from app.core.exceptions import FaceImageNotFoundError, InvalidFaceEmbeddingError

        db_anh = session.get(AnhKhuonMat, ma_anh)
        if not db_anh:
            raise FaceImageNotFoundError("Khong tim thay anh khuon mat")

        embedding = normalize_embedding(db_anh.embedding_vector)
        if len(embedding) != 512:
            raise InvalidFaceEmbeddingError("Anh chua co embedding hop le")

        db_anh.trang_thai_duyet = "DA_DUYET"
        db_anh.ly_do_tu_choi = None
        db_anh.ma_nguoi_duyet = reviewer_id
        db_anh.thoi_gian_duyet = datetime.now(timezone.utc)
        
        session.add(db_anh)
        session.commit()
        session.refresh(db_anh)

        self.add_face_embedding(db_anh.ma_sinh_vien, embedding)
        return db_anh

    def reject_face_image(
        self,
        *,
        session: Session,
        ma_anh: int,
        reviewer_id: int,
        reason: str | None,
    ) -> Any:
        """Reject a pending face image."""
        from datetime import datetime, timezone
        from app.core.exceptions import FaceImageNotFoundError

        db_anh = session.get(AnhKhuonMat, ma_anh)
        if not db_anh:
            raise FaceImageNotFoundError("Khong tim thay anh khuon mat")

        db_anh.trang_thai_duyet = "TU_CHOI"
        db_anh.ly_do_tu_choi = reason
        db_anh.ma_nguoi_duyet = reviewer_id
        db_anh.thoi_gian_duyet = datetime.now(timezone.utc)

        session.add(db_anh)
        session.commit()
        session.refresh(db_anh)
        return db_anh


face_service = FaceRecognitionService()
