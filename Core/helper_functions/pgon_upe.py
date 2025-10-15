from collections import defaultdict
from typing import List, Tuple
import numpy as np
import trimesh

def unpaired_edges_faces(faces):
    """
    Accepts a list of faces and returns unpaired edges and their parent face indices.

    Args:
        faces: List of faces, where each face is a list of vertex indices.

    Returns:
        A tuple:
            - List of unpaired edges (each as a tuple of vertex indices).
            - List of indices of the parent faces for each unpaired edge.
    """
    edge_count = defaultdict(int)
    edge_to_face = defaultdict(list)

    for face_index, face in enumerate(faces):
        n = len(face)
        for i in range(n):
            v1, v2 = face[i], face[(i + 1) % n]
            edge = tuple(sorted((v1, v2)))
            edge_count[edge] += 1
            edge_to_face[edge].append((face_index, (v1, v2)))

    unpaired_edges = []
    parent_faces = []

    for edge, count in edge_count.items():
        if count == 1:
            face_index, original_edge = edge_to_face[edge][0]
            unpaired_edges.append(original_edge)
            parent_faces.append(face_index)

    return np.array(unpaired_edges), np.array(parent_faces)


def unpaired_edges_pgon(mesh):
    # Find boundary edge indices
    index = trimesh.grouping.group_rows(mesh.edges_sorted, require_count=1)
    unique_edges = mesh.edges[index]

    # Get unique vertex indices and their coordinates
    boundary_vertex_indices = np.unique(unique_edges.flatten())
    boundary_vertex_coords = mesh.vertices[boundary_vertex_indices]

    # Create a mapping from global vertex indices to local ones
    index_map = {old_idx: new_idx for new_idx, old_idx in enumerate(boundary_vertex_indices)}

    # Remap edge vertex indices to local indices
    remapped_edges = np.array([[index_map[v0], index_map[v1]] for v0, v1 in unique_edges])

    degenerate_faces = np.hstack([remapped_edges, remapped_edges[:, [0]]])  # shape (M, 3)
    mesh = trimesh.Trimesh(vertices=boundary_vertex_coords, faces=degenerate_faces, process=False)

    return boundary_vertex_coords, remapped_edges, boundary_vertex_indices, mesh



