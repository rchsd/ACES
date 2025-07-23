import trimesh
import numpy as np

def find_barys_norms(mesh):
    face_vertices = mesh.triangles
    barycenter = face_vertices.mean(axis=1)

    # compute non-unitized normals manually
    v0 = mesh.vertices[mesh.faces[:, 0]]
    v1 = mesh.vertices[mesh.faces[:, 1]]
    v2 = mesh.vertices[mesh.faces[:, 2]]

    # compute edge vectors
    edge1 = v1 - v0
    edge2 = v2 - v0

    # cross product gives area-weighted normal
    non_unitized_normals = np.cross(edge1, edge2)

    normalized_face_normals = mesh.face_normals

    return barycenter, non_unitized_normals, normalized_face_normals