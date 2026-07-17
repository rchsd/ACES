import trimesh
import numpy as np

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