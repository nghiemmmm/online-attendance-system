# -*- coding: utf-8 -*-
"""
Face Recognition CLI sử dụng FaceNet + FAISS:
- Xuất CSV: filename, name, distance
"""

import click
import os
import sys
import numpy as np
import pickle
import faiss
import torch
from PIL import Image
from facenet_pytorch import InceptionResnetV1, MTCNN

# ===============================
# Initialize models
# ===============================
device = torch.device('cpu')
print(f"[INFO] Using device: {device}")

print("[INFO] Loading MTCNN detector...")
mtcnn = MTCNN(
    image_size=160,
    margin=0,
    min_face_size=20,
    thresholds=[0.6, 0.7, 0.7],
    factor=0.709,
    post_process=True,
    device=device,
    keep_all=False
)

print("[INFO] Loading FaceNet model...")
model = InceptionResnetV1(pretrained='vggface2').eval().to(device)
print("[INFO] Models loaded successfully!")

# ===============================
# Load FAISS index + metadata
# ===============================
def load_faiss_index(faiss_path, metadata_path):
    """Load FAISS index and metadata"""
    try:
        if not os.path.exists(faiss_path):
            print(f"[ERROR] FAISS index not found: {faiss_path}")
            return None, None
        
        index = faiss.read_index(faiss_path)
        print(f"[INFO] FAISS index loaded: {faiss_path}")
        print(f"[INFO] Index contains {index.ntotal} embeddings")
        
        with open(metadata_path, 'rb') as f:
            names = pickle.load(f)
        print(f"[INFO] Metadata loaded: {len(names)} names")
        
        return index, names
    except Exception as e:
        print(f"[ERROR] Failed to load FAISS index: {e}")
        return None, None

# ===============================
# Extract embedding from image
# ===============================
def get_face_embedding(image_path):
    """Extract face embedding from image using FaceNet"""
    try:
        if not os.path.exists(image_path):
            print(f"[ERROR] Image not found: {image_path}")
            return None, None
        
        img = Image.open(image_path).convert('RGB')
        
        # Detect face using MTCNN
        img_tensor = mtcnn(img)
        if img_tensor is None:
            print(f"[WARNING] No face detected in {image_path}")
            return None, None
        
        # Ensure proper shape
        if img_tensor.dim() == 3:
            img_tensor = img_tensor.unsqueeze(0)
        
        # Generate embedding
        with torch.no_grad():
            embeddings = model(img_tensor.to(device))
        
        embedding = embeddings[0].cpu().numpy().astype('float32')
        return embedding, img
        
    except Exception as e:
        print(f"[ERROR] Failed to extract embedding: {e}")
        return None, None

# ===============================
# Search face in FAISS index
# ===============================
def search_face(embedding, index, names, tolerance=0.6):
    """Search for similar faces in FAISS index"""
    try:
        query_embedding = embedding.reshape(1, -1)
        distances, indices = index.search(query_embedding, k=1)
        
        if len(indices[0]) > 0:
            idx = indices[0][0]
            dist = distances[0][0]
            
            if idx < len(names):
                name = names[idx]
                return name, float(dist), dist < tolerance
        
        return "unknown", float('inf'), False
        
    except Exception as e:
        print(f"[ERROR] Failed to search: {e}")
        return "error", float('inf'), False

# ===============================
# Print result
# ===============================
def print_result(filename, name, distance=None, show_distance=False):
    if show_distance and distance is not None:
        print(f"{filename},{name},{distance:.4f}")
    else:
        print(f"{filename},{name}")

# ===============================
# Test image(s)
# ===============================
def test_image(image_path, index, names, tolerance=0.6, show_distance=False):
    """Test a single image against FAISS index"""
    if not os.path.exists(image_path):
        print(f"[ERROR] Image not found: {image_path}")
        return
    
    embedding, img = get_face_embedding(image_path)
    if embedding is None:
        print_result(image_path, "no_face_detected", show_distance=show_distance)
        return
    
    name, distance, matched = search_face(embedding, index, names, tolerance=tolerance)
    print_result(image_path, name, distance, show_distance)

# ===============================
# Lấy danh sách ảnh
# ===============================
def image_files_in_folder(folder):
    exts = (".jpg", ".jpeg", ".png")
    return [os.path.join(folder,f) for f in os.listdir(folder) if f.lower().endswith(exts)]

# ===============================
# CLI
# ===============================
@click.command()
@click.argument('known_people_folder')
@click.argument('image_to_check')
@click.option('--tolerance', default=0.6, type=float, help='Distance threshold (default: 0.6)')
@click.option('--show-distance', default=False, type=bool, help='Print distance')
@click.option('--index-path', default='vector_db/embeddings_db/faiss_index.bin', help='FAISS index path')
@click.option('--metadata-path', default='vector_db/embeddings_db/names.pkl', help='Metadata path')
def main(known_people_folder, image_to_check, tolerance, show_distance, index_path, metadata_path):
    """
    Face recognition using FaceNet + FAISS
    
    Usage:
        python face_recognition.py known_people/ test_image.jpg --tolerance 0.6 --show-distance True
    """
    
    print(f"\n{'='*60}")
    print(f"Face Recognition using FaceNet + FAISS")
    print(f"{'='*60}")
    print(f"Known people folder: {known_people_folder}")
    print(f"Image to check: {image_to_check}")
    print(f"Tolerance: {tolerance}")
    print(f"Show distance: {show_distance}")
    print(f"FAISS index: {index_path}")
    print(f"Metadata: {metadata_path}")
    print(f"{'='*60}\n")
    
    # Load FAISS index
    index, names = load_faiss_index(index_path, metadata_path)
    if index is None:
        print(f"[ERROR] Failed to load FAISS index.")
        print(f"[INFO] Run: python app/utils/create_ebedding_faiss.py")
        return
    
    if index.ntotal == 0:
        print(f"[ERROR] FAISS index is empty.")
        return
    
    # Test image(s)
    if os.path.isdir(image_to_check):
        files = image_files_in_folder(image_to_check)
        print(f"[INFO] Processing {len(files)} images...\n")
        for f in files:
            test_image(f, index, names, tolerance, show_distance)
    else:
        test_image(image_to_check, index, names, tolerance, show_distance)
    
    print(f"\n{'='*60}")

if __name__ == "__main__":
    main()