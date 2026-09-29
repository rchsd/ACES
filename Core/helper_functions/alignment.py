import trimesh
import numpy as np

TOLERANCE = 1e-12

def align(vector, axis):
    #normalize the vector and the axis
    vector = vector / np.linalg.norm(vector)
    axis = axis / np.linalg.norm(axis)
    
    #hinge line (axis of rotation) for the twist
    cross_prod = np.cross(vector, axis)

    #initial alignmnet between the vector and the axis before any rotation
    dot_prod = np.dot(vector, axis)

    #this is the total distance the vector needs to swing to be aligned
    angle = np.arccos(dot_prod)
    rotation_matrix = trimesh.transformations.rotation_matrix(angle, cross_prod)
    
    return rotation_matrix

def aligns(vector, axis):
    vector = np.asarray(vector, dtype=float)
    axis = np.asarray(axis, dtype=float)
 
    nv, na = np.linalg.norm(vector), np.linalg.norm(axis)

    if nv < TOLERANCE or na < TOLERANCE:
        return np.eye(4)

    vector, axis = vector / nv, axis / na
    cross_prod = np.cross(vector, axis)
    dot_prod = np.clip(np.dot(vector, axis), -1.0, 1.0)

    if np.linalg.norm(cross_prod) < TOLERANCE:
        if dot_prod > 0:
            return np.eye(4)
        perp = np.cross(axis, [1.0, 0.0, 0.0])
        if np.linalg.norm(perp) < TOLERANCE:
            perp = np.cross(axis, [0.0, 1.0, 0.0])
        
        return trimesh.transformations.rotation_matrix(np.pi, perp)

    return trimesh.transformations.rotation_matrix(np.arccos(dot_prod), cross_prod)