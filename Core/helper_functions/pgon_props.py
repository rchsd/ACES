import trimesh
import numpy as np

# Implements Scalar Triple Product
def compute_mesh_volume(mesh:trimesh):
    faces = mesh.faces
    vertices = mesh.vertices
    volume = 0.0
    for face in faces:
        v0, v1, v2 = vertices[face]
        vol = np.dot(v0, np.cross(v1, v2)) / 6.0
        volume += vol
    return abs(volume)