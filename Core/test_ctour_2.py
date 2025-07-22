import numpy as np
import trimesh

def pgonctour(mesh: trimesh.Trimesh, normal: np.ndarray, coefs: np.ndarray):
    """
    Intersects a 3D mesh with multiple parallel planes.

    Parameters:
        mesh: trimesh.Trimesh
            The input mesh (transformed beforehand).
        normal: np.ndarray
            The slicing plane normal (e.g. [0, 0, 1]).
        coefs: np.ndarray
            Offsets along the normal defining each plane.

    Returns:
        intersecting_edges: np.ndarray
            Array of edges that intersected with the planes.
        intersecting_vertices: np.ndarray
            Array of vertices corresponding to intersection points.
        edge_indices: np.ndarray
            Indices of mesh edges that contributed to each intersection point.
        num_edges: int
            The number of unique edges that intersected with the planes.
    """
    contours = []
    edge_indices = []

    vertices = mesh.vertices
    faces = mesh.faces
    vertex_distances = vertices @ normal  # dot product

    # Iterate over each plane offset
    for plane_idx, offset in enumerate(coefs):
        signed = vertex_distances - offset

        # Determine which faces intersect the plane
        face_signs = signed[faces]
        intersects = np.any(face_signs < 0, axis=1) & np.any(face_signs > 0, axis=1)

        # Get the faces that intersect the plane
        intersecting_faces = faces[intersects]
        intersecting_signs = face_signs[intersects]

        # Vectorized edge intersection calculation
        for i, j in [(0, 1), (1, 2), (2, 0)]:
            da = intersecting_signs[:, i]
            db = intersecting_signs[:, j]

            # Calculate intersection points where da and db have opposite signs
            mask = da * db < 0
            va = vertices[intersecting_faces[:, i][mask]]
            vb = vertices[intersecting_faces[:, j][mask]]
            w = db[mask] / (db[mask] - da[mask])
            p = va * (1 - w[:, None]) + vb * w[:, None]

            contours.append(p)
            edge_indices.extend(np.where(intersects)[0][mask])

    # Concatenate results into arrays
    intersecting_vertices = np.concatenate(contours) if contours else np.array([])
    edge_indices_array = np.array(edge_indices)

    # Determine the number of unique edges
    num_edges = len(np.unique(edge_indices_array))

    return intersecting_faces[:, :2], intersecting_vertices, edge_indices_array, num_edges