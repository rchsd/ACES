import numpy as np

def filter_faces(barys, norms, center, radius, angle):
    # Get faces within radius
    mask = np.linalg.norm(barys - center, axis=1) <= radius

    # Get faces that are within angle of center
    num = (center - barys) / np.linalg.norm(center - barys, axis=1)[:, np.newaxis]
    mask = mask & (np.sum(num * norms, axis=1) > np.cos(np.radians(angle)))

    return mask

'''def unitize(vectors):
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / norms'''
