import numpy as np
from collections import defaultdict
import trimesh
import scipy.io as sio
import test_trimesh_plane
from helper_functions import *

'''def find_unpaired_edges_with_faces(mesh):
    """
    Identify unpaired (boundary) edges in a mesh and return the edges
    along with the index of the face each belongs to.

    Parameters:
        mesh (trimesh.Trimesh): The input mesh.

    Returns:
        results (np.ndarray): Array of unpaired edges as vertex index pairs.
        pfaces (np.ndarray): Array of face indices associated with each unpaired edge.
    """
    edge_count = defaultdict(int)
    edge_to_face = defaultdict(list)

    for face_idx, face in enumerate(mesh.faces):
        for i in range(3):
            v1 = face[i]
            v2 = face[(i + 1) % 3]
            edge = tuple(sorted((v1, v2)))  # undirected edge
            edge_count[edge] += 1
            edge_to_face[edge].append(face_idx)

    unpaired = [edge for edge, count in edge_count.items() if count == 1]
    parent_faces = [edge_to_face[edge][0] for edge in unpaired]

    results = np.array(unpaired, dtype=int)
    pfaces = np.array(parent_faces, dtype=int)

    return results, pfaces'''

def find_unpaired_edges(mesh):
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

'''mesh = trimesh.load('c:\\MATLAB\\new.stl')
vertices, faces, v_indixes, mesh, edge = find_unpaired_edges(mesh)
norms = sio.loadmat('c:\\MATLAB\\norms.mat').get('norms')
coefs = sio.loadmat('c:\\MATLAB\\coefs.mat').get('coefs')
#edge = sio.loadmat('c:\\MATLAB\\edge.mat').get('edge')

lines, face_indices, n = test_trimesh_plane.compute_contours_with_trimesh(mesh, norms, coefs)
lines['faces'] = lines['faces'][:, 0]

test_ctour.main_compute_all_contours(edge, norms, coefs)
print('hello')'''