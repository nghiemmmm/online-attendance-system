import faiss
import numpy as np

def load_faiss_index(index_path):

    index = faiss.read_index(index_path)
    return index


def search_similar_features(query_embedding, index, label_map, k=5):

    query = np.array([query_embedding]).astype("float32")

    distances, indices = index.search(query, k)

    results = []

    for i in range(k):

        idx = indices[0][i]
        similarity = distances[0][i]

        name = label_map[idx]

        results.append((name, similarity))

    return results