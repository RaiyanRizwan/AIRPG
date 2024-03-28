import numpy as np

def normalize_vectors(vectors):
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return np.where(norms > 0, vectors / norms, vectors)

def scale_to_range(numbers, MAX=1):
    min_val, max_val = min(numbers), max(numbers)
    return [MAX * (x - min_val) / (max_val - min_val) if max_val > min_val else 0 for x in numbers]
