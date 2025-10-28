import numpy as np
import scipy.io as sio

def index_by_edges(faces: np.ndarray):
    """
    Extract all edges from triangle faces, identify unique edges,
    index each face by its edges, and track whether each edge is flipped.

    Parameters:
        faces (np.ndarray): (n, 3) array of triangle face indices.

    Returns:
        tuple:
            - all_edges: (3n, 2) array of all edges (unsorted, duplicates allowed)
            - unique_edges: (m, 2) array of unique edges
            - indexed_faces: (n, 3) array of edge indices for each face
            - flip_flags: (n, 3) boolean array indicating if edge is flipped
    """
    edge_dict = {}
    unique_edges = []
    indexed_faces = np.zeros_like(faces, dtype=np.uint32)
    flip_flags = np.zeros_like(faces, dtype=bool)
    all_edges = []

    for i, face in enumerate(faces):
        for j, (v1, v2) in enumerate([(face[0], face[1]), (face[1], face[2]), (face[2], face[0])]):
            all_edges.append([v1, v2])  # preserve original direction
            edge = tuple(sorted((v1, v2)))  # sorted for uniqueness
            flipped = v1 > v2

            if edge not in edge_dict:
                edge_dict[edge] = len(unique_edges)
                unique_edges.append(edge)

            indexed_faces[i, j] = edge_dict[edge]
            flip_flags[i, j] = flipped

    return (np.array(all_edges, dtype=np.uint32), np.array(unique_edges, dtype=np.uint32), indexed_faces, flip_flags)
