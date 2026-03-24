# -*- coding: utf-8 -*-
"""
embedding_only.py

Chức năng:
- Nhận một folder chứa ảnh người đã biết
- Tạo embedding 512-d bằng FaceNet cho mỗi mặt
- Lưu embeddings vào FAISS index
- Lưu metadata (tên người = tên file) để mapping sau này
"""

import os
import cv2
import numpy as np
import faiss
import pickle
import torch
from facenet_pytorch import InceptionResnetV1, MTCNN
from PIL import Image

# =========================
# 1️⃣ Initialize FaceNet model + MTCNN detector
# =========================
device = torch.device('cpu')
mtcnn = MTCNN(device=device, keep_all=False)  # Face detector
model = InceptionResnetV1(pretrained='vggface2').eval().to(device)
print(f"[INFO] FaceNet + MTCNN model loaded on {device}")

# =========================
# 2️⃣ Setup FAISS + metadata
# =========================
embedding_dim = 512
faiss_index_path = "vector_db/embeddings_db/faiss_index.bin"
metadata_path = "vector_db/embeddings_db/names.pkl"
os.makedirs("vector_db/embeddings_db", exist_ok=True)

# Nếu đã có index + metadata thì load, nếu chưa thì tạo mới
if os.path.exists(faiss_index_path) and os.path.exists(metadata_path):
    index = faiss.read_index(faiss_index_path)
    with open(metadata_path, "rb") as f:
        names = pickle.load(f)
else:
    index = faiss.IndexFlatL2(embedding_dim)
    names = []

# =========================
# 3️⃣ Helper: scan folder
# =========================
def image_files_in_folder(folder):
    """Trả về danh sách file ảnh jpg/png"""
    exts = (".jpg", ".jpeg", ".png")
    return [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(exts)]

# =========================
# 4️⃣ Tạo embedding 1 ảnh
# =========================
def get_face_embedding(image_path):
    """Detect face + trả về embedding 512-d"""
    try:
        img = Image.open(image_path).convert('RGB')
        
        # Detect face using MTCNN
        img_tensor = mtcnn(img)
        if img_tensor is None:
            print(f"[WARNING] Không tìm thấy face trong {image_path}")
            return None
        
        # Inference to get embedding
        if img_tensor.dim() == 3:  # Single face
            img_tensor = img_tensor.unsqueeze(0)
        
        with torch.no_grad():
            embedding = model(img_tensor.to(device)).cpu().numpy()[0].astype('float32')
        return embedding
    except Exception as e:
        print(f"[WARNING] Lỗi xử lý {image_path}: {e}")
        return None

# =========================
# 5️⃣ Hàm chính: scan folder + lưu embedding
# =========================
def register_faces_folder(folder_path):
    """Tạo embedding cho toàn bộ folder ảnh và lưu vào FAISS + metadata"""
    global index, names
    
    if not os.path.exists(folder_path):
        print(f"[ERROR] Folder không tồn tại: {folder_path}")
        return
    
    files = image_files_in_folder(folder_path)
    if not files:
        print(f"[WARNING] Không tìm thấy ảnh trong {folder_path}")
        return
    
    for file in files:
        name = os.path.splitext(os.path.basename(file))[0]  # tên = tên file
        embedding = get_face_embedding(file)
        if embedding is not None:
            index.add(np.array([embedding]))  # thêm embedding vào FAISS
            names.append(name)
            print(f"[INFO] Thêm {name} vào FAISS index")
    
    # Lưu index + metadata ra đĩa
    faiss.write_index(index, faiss_index_path)
    with open(metadata_path, "wb") as f:
        pickle.dump(names, f)
    print(f"[INFO] Lưu xong FAISS index và metadata. Tổng {len(names)} người")

# =========================
# 6️⃣ Test
# =========================
if __name__ == "__main__":
    register_faces_folder(r"D:\TTCS\dataset")  # folder chứa ảnh