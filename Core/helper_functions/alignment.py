import trimesh
import numpy as np

def align(vector, axis):
    vector = vector / np.linalg.norm(vector)
    axis = axis / np.linalg.norm(axis)

    cross_prod = np.cross(vector, axis)
    dot_prod = np.dot(vector, axis)
    angle = np.arccos(dot_prod)
    rotation_matrix = trimesh.transformations.rotation_matrix(angle, cross_prod)
    
    return rotation_matrix