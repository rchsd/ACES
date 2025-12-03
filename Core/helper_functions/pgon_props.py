import trimesh
import numpy as np

# Implements Scalar Triple Product
def compute_mesh_volume(mesh:trimesh, center=None):
    faces = mesh.faces
    vertices = mesh.vertices
    if center is None:
        center = 0
    volume = 0.0
    for face in faces:
        v0, v1, v2 = vertices[face] - center
        vol = np.dot(v0, np.cross(v1, v2)) / 6.0
        volume += vol
    return abs(volume)

# Build tetrahedra mesh
def build_pgon(mesh, center):
    tetra_vertices = []
    tetra_faces = []
    for idx, face in enumerate(mesh.faces):
        v0, v1, v2 = mesh.vertices[face] - center  
        base_index = len(tetra_vertices)
        tetra_vertices.extend([v0, v1, v2, np.zeros(3)])
        tetra_faces.extend([
            [base_index, base_index+1, base_index+2],
            [base_index, base_index+1, base_index+3],
            [base_index+1, base_index+2, base_index+3],
            [base_index+2, base_index, base_index+3]
        ])
    return trimesh.Trimesh(vertices=tetra_vertices, faces=tetra_faces)
