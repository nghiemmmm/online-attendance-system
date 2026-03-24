import os
import numpy as np
import faiss
import torch
from facenet_pytorch import InceptionResnetV1

class FaceNetLoader:
    def __init__(self, model_path='models/facenet/', label_map='facenet_label_map.npy', index_file='facenet_features.index'):
        self.model_path = model_path
        self.label_map_file = label_map
        self.index_file = index_file
        self.model = None
        self.index = None
        self.label_map = None
        self.all_embeddings = None
        self._load_resources()
    
    def _load_resources(self):
        """Load all resources: model, index, label map, and embeddings."""
        # Load FaceNet model
        self.model = InceptionResnetV1(pretrained='vggface2').eval()
        
        # Load Faiss index and label map
        index_path = os.path.join(self.model_path, self.index_file)
        label_path = os.path.join(self.model_path, self.label_map_file)
        
        if not os.path.exists(index_path) or not os.path.exists(label_path):
            raise FileNotFoundError("Faiss index or label map not found.")
        
        self.index = faiss.read_index(index_path)
        self.label_map = np.load(label_path)
        self.all_embeddings = self.index.reconstruct_n(0, self.index.ntotal)
    
    def get_model(self):
        return self.model
    
    def get_index(self):
        return self.index
    
    def get_label_map(self):
        return self.label_map
    
    def get_all_embeddings(self):
        return self.all_embeddings
    
    def search_similar_features(self, query_feature, k=5, threshold=0.3):
        """
        Search for similar features in the Faiss index.
        
        Args:
            query_feature (np.ndarray): The query feature vector (shape: [512])
            k (int): Number of similar features to retrieve
            threshold (float): Minimum similarity threshold
        
        Returns:
            list: List of tuples (employee_name, similarity, index)
        """
        if self.index is None or self.label_map is None:
            return []
        
        # Search the index
        similarities, indices = self.index.search(np.array([query_feature]), k)
        
        results = []
        for i in range(len(indices[0])):
            similarity = similarities[0][i]
            if similarity > threshold:
                employee_name = self.label_map[indices[0][i]]
                results.append((employee_name, similarity, indices[0][i]))
        return results