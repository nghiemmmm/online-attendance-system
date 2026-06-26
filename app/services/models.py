# -*- coding: utf-8 -*-
"""Core FaceNet and MTCNN helpers."""

import numpy as np
import torch
from facenet_pytorch import InceptionResnetV1, MTCNN
from PIL import Image

from app.utils.logger import logger

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model = None
mtcnn = None


def load_model(
    model_class=InceptionResnetV1,
    detector_class=MTCNN,
    keep_all: bool = True,
):
    """Load both FaceNet model and MTCNN detector."""
    loaded_model = model_class(pretrained="vggface2").eval().to(device)
    detector = detector_class(device=device, keep_all=keep_all)
    logger.info("FaceNet + MTCNN model loaded on %s", device)
    return loaded_model, detector


def ensure_model_loaded():
    """Return initialized FaceNet and MTCNN instances."""
    global model, mtcnn
    if model is None or mtcnn is None:
        model, mtcnn = load_model()
    return model, mtcnn


def load_image_file(file_path):
    """Load an image file as RGB."""
    return Image.open(file_path).convert("RGB")


def face_locations(img):
    """Return face bounding boxes as top, right, bottom, left tuples."""
    _, detector = ensure_model_loaded()
    boxes, _ = detector.detect(img)
    if boxes is None:
        return []
    return [(int(y1), int(x2), int(y2), int(x1)) for x1, y1, x2, y2 in boxes]


def face_encodings(img, known_face_locations=None):
    """Extract 512-dimensional embeddings for faces in an image."""
    face_model, detector = ensure_model_loaded()
    embeddings = []

    if known_face_locations is None:
        faces, _ = detector(img, return_prob=True)
        if faces is None:
            return []
        for face in faces:
            face_embedding = face_model(face.unsqueeze(0).to(device))
            embeddings.append(face_embedding.detach().cpu().numpy()[0])
        return embeddings

    for box in known_face_locations:
        y1, x2, y2, x1 = box
        face_crop = img.crop((x1, y1, x2, y2))
        face_tensor = detector(face_crop)
        if face_tensor is not None:
            face_embedding = face_model(face_tensor.unsqueeze(0).to(device))
            embeddings.append(face_embedding.detach().cpu().numpy()[0])

    return embeddings


def face_distance(face_encodings, face_to_compare):
    """Calculate L2 distances between known embeddings and one face."""
    if len(face_encodings) == 0:
        return np.empty((0))
    return np.linalg.norm(np.array(face_encodings) - face_to_compare, axis=1)


def compare_faces(known_face_encodings, face_encoding_to_check, tolerance=0.8):
    """Compare one face embedding against known embeddings."""
    distances = face_distance(known_face_encodings, face_encoding_to_check)
    return list(distances <= tolerance)


def is_face_match(known_face_encodings, face_encoding_to_check, tolerance=0.8):
    """Return whether one face embedding matches any known embedding."""
    if face_encoding_to_check is None:
        return False
    if known_face_encodings is None or len(known_face_encodings) == 0:
        return False

    matches = compare_faces(known_face_encodings, face_encoding_to_check, tolerance)
    distances = face_distance(known_face_encodings, face_encoding_to_check)
    return bool(any(matches)) and bool(len(distances) > 0)
