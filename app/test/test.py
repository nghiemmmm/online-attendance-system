import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import faiss
import pickle
import numpy as np
import torch
from PIL import Image
from facenet_pytorch import InceptionResnetV1, MTCNN

# ===============================
# Initialize FaceNet + MTCNN
# ===============================
device = torch.device('cpu')
print(f"[INFO] Using device: {device}")

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

model = InceptionResnetV1(pretrained='vggface2').eval().to(device)
print("[INFO] Models loaded!")

# ===============================
# Load FAISS index
# ===============================
index_path = r"vector_db\embeddings_db\faiss_index.bin"
metadata_path = r"vector_db\embeddings_db\names.pkl"

if not os.path.exists(index_path):
    print(f"[ERROR] FAISS index not found at {index_path}")
    print(f"[INFO] Creating test with sample data instead...")
    index = faiss.IndexFlatL2(512)
    names = []
else:
    index = faiss.read_index(index_path)
    print(f"[INFO] FAISS index loaded: {index.ntotal} embeddings")
    
    with open(metadata_path, "rb") as f:
        names = pickle.load(f)
    print(f"[INFO] Metadata loaded: {len(names)} names")

# ===============================
# Test with image
# ===============================
image_path = r"D:\TTCS\dataset\Avatar_Aaron_Eckhart.jpg"

if not os.path.exists(image_path):
    print(f"[ERROR] Test image not found at {image_path}")
else:
    print(f"\n[INFO] Testing with: {image_path}")
    
    # Load and detect face
    img = Image.open(image_path).convert('RGB')
    img_tensor = mtcnn(img)
    
    if img_tensor is None:
        print("[WARNING] No face detected in image")
    else:
        # Ensure proper shape
        if img_tensor.dim() == 3:
            img_tensor = img_tensor.unsqueeze(0)
        
        # Generate embedding
        with torch.no_grad():
            embedding = model(img_tensor.to(device)).cpu().numpy()[0].astype('float32')
        
        print(f"[INFO] Embedding shape: {embedding.shape}")
        print(f"[INFO] Embedding norm: {np.linalg.norm(embedding):.4f}")
        
        # Search in FAISS
        if index.ntotal > 0:
            query = np.expand_dims(embedding, axis=0)
            distances, indices = index.search(query, k=1)
            
            dist = distances[0][0]
            idx = indices[0][0]
            name = names[idx] if idx < len(names) else "unknown"
            matched = dist < 0.6
            
            print(f"\n[RESULT]")
            print(f"  Name: {name}")
            print(f"  Distance: {dist:.4f}")
            print(f"  Matched: {'YES' if matched else 'NO'}")
        else:
            print("[WARNING] FAISS index is empty, cannot search")