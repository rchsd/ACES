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


def unpaired_edges_pgon(pgon):
    faces = pgon.faces
    edge_count = defaultdict(int)
    edge_to_face = defaultdict(list)

    # Step 1: Count all edges and track their parent faces
    for i, face in enumerate(faces):
        nsim = len(face)
        for j in range(nsim):
            v1 = face[j]
            v2 = face[(j + 1) % nsim]
            edge = tuple(sorted((v1, v2)))  # undirected edge
            edge_count[edge] += 1
            edge_to_face[edge].append(i)

    # Step 2: Identify unpaired edges
    unpaired = [edge for edge, count in edge_count.items() if count == 1]
    parent_faces = [edge_to_face[edge][0] for edge in unpaired]

    # Step 3: Format results
    results = np.array(unpaired)
    pfaces = np.array(parent_faces)

    return results, pfaces



