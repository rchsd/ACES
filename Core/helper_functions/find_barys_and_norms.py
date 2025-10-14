import numpy as np
import trimesh

def compute_vertex_normals(vertices, faces):
    V = len(vertices)
    vertex_normals = np.zeros((V, 3), dtype=np.float64)

    # Compute face normals
    v0 = vertices[faces[:, 0]]
    v1 = vertices[faces[:, 1]]
    v2 = vertices[faces[:, 2]]
    face_normals = np.cross(v1 - v0, v2 - v0)

    # Accumulate face normals to vertices
    for i in range(3):
        np.add.at(vertex_normals, faces[:, i], face_normals)

    # Normalize vertex normals
    norms = np.linalg.norm(vertex_normals, axis=1, keepdims=True)
    norms[norms == 0] = 1
    vertex_normals /= norms

    return vertex_normals

'''def find_barys_norms(mesh: trimesh.Trimesh):
    face_vertices = mesh.triangles
    barycenter = face_vertices.mean(axis=1)

    # Compute non-unitized face normals manually
    v0 = mesh.vertices[mesh.faces[:, 0]]
    v1 = mesh.vertices[mesh.faces[:, 1]]
    v2 = mesh.vertices[mesh.faces[:, 2]]

    edge1 = v1 - v0
    edge2 = v2 - v0
    non_unitized_normals = np.cross(edge1, edge2)

    # Unitized face normals from trimesh
    unitized_face_normals = mesh.face_normals

    # Correct unitized vertex normals (manual computation)
    unitized_vertex_normals = compute_vertex_normals(mesh.vertices, mesh.faces)

    return barycenter, non_unitized_normals, unitized_face_normals, unitized_vertex_normals'''

import numpy as np

def find_barys_norms(mesh: trimesh.Trimesh, mask=None):
    # Use all faces if no mask is provided
    if mask is None:
        mask = np.ones(len(mesh.faces), dtype=bool)

    # Filter face vertices
    face_vertices = mesh.triangles[mask]
    barycenter = face_vertices.mean(axis=1)

    # Compute non-unitized face normals manually
    faces = mesh.faces[mask]
    v0 = mesh.vertices[faces[:, 0]]
    v1 = mesh.vertices[faces[:, 1]]
    v2 = mesh.vertices[faces[:, 2]]

    edge1 = v1 - v0
    edge2 = v2 - v0
    non_unitized_normals = np.cross(edge1, edge2)

    # Unitized face normals from trimesh (already normalized)
    unitized_face_normals = mesh.face_normals[mask]

    # Correct unitized vertex normals (manual computation)
    vertex_normals = np.zeros_like(mesh.vertices)
    for i, face in enumerate(faces):
        for vertex_idx in face:
            vertex_normals[vertex_idx] += unitized_face_normals[i]

    # Normalize vertex normals
    norms = np.linalg.norm(vertex_normals, axis=1, keepdims=True)
    norms[norms == 0] = 1
    unitized_vertex_normals = vertex_normals / norms

    return barycenter, non_unitized_normals, unitized_face_normals, unitized_vertex_normals

#mesh = trimesh.load('c:\\Users\\bbeasley\\Documents\\Python Projects\\Matlab-GUI\\Tests\\Schmitz\\l hip 1.stl')

#a, b, c, vnorms = find_barys_norms(mesh)