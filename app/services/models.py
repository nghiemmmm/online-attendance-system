# -*- coding: utf-8 -*-
"""
core_facenet.py
Module core FaceNet + MTCNN:
- Load ảnh
- Detect face
- Trích xuất embedding 512-d
- So sánh face bằng L2
"""

import torch
import numpy as np
from PIL import Image
from facenet_pytorch import InceptionResnetV1, MTCNN

# ===============================
# Initialize FaceNet + MTCNN
# ===============================
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

def load_model(model_class=InceptionResnetV1, detector_class=MTCNN, keep_all=True):
    """
    Load both FaceNet model and MTCNN detector.
    """
    model = model_class(pretrained='vggface2').eval().to(device)
    detector = detector_class(device=device, keep_all=keep_all)
    print(f"[INFO] FaceNet + MTCNN model loaded on {device}")
    return model, detector


model, mtcnn = load_model()


def load_image_file(file_path):
    """
    Load ảnh từ file, trả về PIL Image
    """
    img = Image.open(file_path).convert('RGB')
    return img

# ===============================
# Detect face
# ===============================
def face_locations(img):
    """
    Trả về list bounding boxes (top, right, bottom, left)
    """
    boxes, _ = mtcnn.detect(img)
    if boxes is None:
        return []
    return [(int(y1), int(x2), int(y2), int(x1)) for x1, y1, x2, y2 in boxes]

# ===============================
# Lấy embedding
# ===============================
def face_encodings(img, known_face_locations=None):
    """
    Trích xuất embedding 512-d cho từng face
    Nếu known_face_locations=None → detect tất cả
    """
    embeddings = []

    if known_face_locations is None:
        faces, _ = mtcnn(img, return_prob=True)
        if faces is None:
            return []
        for face in faces:
            face_embedding = model(face.unsqueeze(0).to(device))
            embeddings.append(face_embedding.detach().cpu().numpy()[0])
    else:
        for box in known_face_locations:
            y1, x2, y2, x1 = box
            face_crop = img.crop((x1, y1, x2, y2))
            # extract manually
            face_tensor = mtcnn(face_crop)
            if face_tensor is not None:
                face_embedding = model(face_tensor.unsqueeze(0).to(device))
                embeddings.append(face_embedding.detach().cpu().numpy()[0])
    return embeddings

# ===============================
# Khoảng cách giữa các face
# ===============================
def face_distance(face_encodings, face_to_compare):
    """
    Khoảng cách L2 giữa embeddings
    """
    if len(face_encodings) == 0:
        return np.empty((0))
    return np.linalg.norm(np.array(face_encodings) - face_to_compare, axis=1)

# ===============================
# So sánh face
# ===============================
def compare_faces(known_face_encodings, face_encoding_to_check, tolerance=0.8):
    """
    So sánh embedding mới với list embedding đã biết
    """
    return list(face_distance(known_face_encodings, face_encoding_to_check) <= tolerance)


def is_face_match(known_face_encodings, face_encoding_to_check, tolerance=0.8):
    """
    Trả về True/False để xác định khuôn mặt có khớp hay không.

    Logic:
    - Dùng compare_faces(...) để lấy danh sách khớp theo ngưỡng tolerance.
    - Dùng face_distance(...) để đảm bảo có ít nhất một khoảng cách hợp lệ.
    """
    if face_encoding_to_check is None:
        return False

    if known_face_encodings is None or len(known_face_encodings) == 0:
        return False

    matches = compare_faces(known_face_encodings, face_encoding_to_check, tolerance)
    distances = face_distance(known_face_encodings, face_encoding_to_check)

    return bool(any(matches)) and bool(len(distances) > 0)