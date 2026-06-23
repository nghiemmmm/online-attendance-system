import os
import io
import pickle
import numpy as np
from PIL import Image
import torch
import faiss
from facenet_pytorch import InceptionResnetV1, MTCNN

# Thư mục lưu trữ
UPLOAD_DIR = "uploads/faces"
DB_DIR = "vector_db/embeddings_db"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)

INDEX_PATH = os.path.join(DB_DIR, "faiss_index.bin")
META_PATH = os.path.join(DB_DIR, "names.pkl")

class FaceRecognitionService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FaceRecognitionService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.device = torch.device('cpu')
        
        self.mtcnn = MTCNN(
            image_size=160, margin=0, min_face_size=20,
            thresholds=[0.6, 0.7, 0.7], factor=0.709, post_process=True,
            device=self.device, keep_all=True  # keep_all=True để lấy nhiều khuôn mặt trong ảnh
        )
        
        self.model = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        
        self.index = None
        self.names = []
        self._load_faiss_index()

    def _load_faiss_index(self):
        if os.path.exists(INDEX_PATH) and os.path.exists(META_PATH):
            self.index = faiss.read_index(INDEX_PATH)
            with open(META_PATH, 'rb') as f:
                self.names = pickle.load(f)
        else:
            # Tạo index mới nếu chưa có
            self.index = faiss.IndexFlatL2(512)
            self.names = []
            self._save_faiss_index()

    def _save_faiss_index(self):
        faiss.write_index(self.index, INDEX_PATH)
        with open(META_PATH, 'wb') as f:
            pickle.dump(self.names, f)

    def extract_embeddings(self, image_bytes: bytes) -> list[np.ndarray]:
        """Trả về list các embedding tìm thấy trong ảnh."""
        try:
            img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            # Extract faces
            boxes, probs = self.mtcnn.detect(img)
            if boxes is None:
                return []
            
            # mtcnn(img) trả về tensor chứa các face crop
            faces = self.mtcnn(img)
            if faces is None:
                return []
            
            if faces.dim() == 3:
                faces = faces.unsqueeze(0)
            
            with torch.no_grad():
                embeddings = self.model(faces.to(self.device))
                
            return [e.cpu().numpy().astype('float32') for e in embeddings]
        except Exception as e:
            print(f"Error extracting embeddings: {e}")
            return []

    def register_face(self, ma_sinh_vien: int, image_bytes: bytes) -> tuple[bool, str, list[float]]:
        embeddings = self.extract_embeddings(image_bytes)
        if not embeddings:
            return False, "Không tìm thấy khuôn mặt trong ảnh", []
        
        if len(embeddings) > 1:
            return False, "Ảnh có nhiều hơn 1 khuôn mặt, vui lòng chụp lại", []
            
        emb = embeddings[0]
        
        # Thêm vào FAISS
        self.index.add(emb.reshape(1, -1))
        self.names.append(ma_sinh_vien)
        self._save_faiss_index()
        
        return True, "Đăng ký khuôn mặt thành công", emb.tolist()

    def recognize_faces(self, image_bytes: bytes, tolerance: float = 0.6) -> list[int]:
        if self.index.ntotal == 0:
            return []
            
        embeddings = self.extract_embeddings(image_bytes)
        if not embeddings:
            return []
            
        recognized_ids = set()
        
        for emb in embeddings:
            query = emb.reshape(1, -1)
            distances, indices = self.index.search(query, k=1)
            
            if len(indices[0]) > 0:
                idx = indices[0][0]
                dist = distances[0][0]
                if dist < tolerance and idx < len(self.names):
                    recognized_ids.add(self.names[idx])
                    
        return list(recognized_ids)

face_service = FaceRecognitionService()
