import numpy as np
import trimesh

def reflection(vector):
    if vector == [1, 0, 0]:  # Reflection across the X-axis
        return np.array([
            [-1,  0,  0,  0],
            [ 0,  1,  0,  0],
            [ 0,  0,  1,  0],
            [ 0,  0,  0,  1]
        ])
    elif vector == [0, 1, 0]:  # Reflection across the Y-axis
        return np.array([
            [ 1,  0,  0,  0],
            [ 0, -1,  0,  0],
            [ 0,  0,  1,  0],
            [ 0,  0,  0,  1]
        ])
    elif vector == [0, 0, 1]:  # Reflection across the Z-axis
        return np.array([
            [ 1,  0,  0,  0],
            [ 0,  1,  0,  0],
            [ 0,  0, -1,  0],
            [ 0,  0,  0,  1]
        ])
    else:
        raise ValueError("Invalid vector")
    

import numpy as np

def reflection_simpl(vector):
    vector = np.asarray(vector)
    if not np.all(np.isin(vector, [0, 1])) or np.sum(vector) != 1:
        raise ValueError("Vector must be one of [1, 0, 0], [0, 1, 0], or [0, 0, 1]")

    reflection_matrix = np.eye(4)
    axis = np.argmax(vector)
    reflection_matrix[axis, axis] = -1
    return reflection_matrix

    
def apply_transform(mesh, transform):
    pelvis = trimesh.Trimesh(vertices=mesh.vertices, faces=mesh.faces)
    pelvis.apply_transform(transform)
    
    return mesh.apply_transform(transform)