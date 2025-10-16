import trimesh
import numpy as np

def compute_mesh_volume(mesh:trimesh):
    faces = mesh.faces
    vertices = mesh.vertices
    volume = 0.0
    for face in faces:
        v0, v1, v2 = vertices[face]
        vol = np.dot(v0, np.cross(v1, v2)) / 6.0
        volume += vol
    return abs(volume)

#mesh = trimesh.load('c:\\MATLAB\\t.stl')
#print(compute_mesh_volume(mesh.faces, mesh.vertices))