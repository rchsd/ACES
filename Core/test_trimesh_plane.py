import numpy as np
import trimesh

def compute_contours_with_trimesh(mesh, plane_normals, plane_offsets):
    """
    Compute mesh-plane intersections for multiple planes defined by normals and offsets.

    Parameters:
    - mesh: trimesh.Trimesh object
    - plane_normals: (n, 3) array-like or (3,) single normal vector
    - plane_offsets: (n,) array-like or single float

    Returns:
    - mesh_data: dict with 'faces' and 'vertices' from deduplicated segments
    - face_indices: (m,) array of mesh face indices intersected
    - plane_indices: (m,) array of corresponding plane indices
    """
    all_segments = []
    all_face_indices = []
    all_plane_indices = []

    # Convert inputs to arrays
    plane_offsets = np.atleast_1d(plane_offsets)
    plane_normals = np.asarray(plane_normals)

    # If a single normal is provided, replicate it to match the number of offsets
    if plane_normals.ndim == 1:
        plane_normals = np.tile(plane_normals, (len(plane_offsets), 1))

    if plane_normals.shape[0] != plane_offsets.shape[0]:
        raise ValueError(f"Mismatch: got {plane_normals.shape[0]} normals and {plane_offsets.shape[0]} offsets.")

    for plane_idx, (normal, offset) in enumerate(zip(plane_normals, plane_offsets)):
        normal = np.asarray(normal).flatten()
        origin = normal * offset  # Point on the plane

        lines, face_indices = trimesh.intersections.mesh_plane(
            mesh, plane_normal=normal, plane_origin=origin, return_faces=True
        )

        if lines is not None and len(lines) > 0:
            all_segments.extend(lines)
            all_face_indices.extend(face_indices)
            all_plane_indices.extend([plane_idx] * len(lines))

    mesh_data = deduplicate_segments(all_segments)
    return mesh_data, np.array(all_face_indices), np.array(all_plane_indices)

def deduplicate_segments(segments):
    vertex_map = {}
    unique_vertices = []
    faces = []

    for segment in segments:
        face = []
        for point in segment:
            key = tuple(np.round(point, decimals=8))
            if key not in vertex_map:
                vertex_map[key] = len(unique_vertices)
                unique_vertices.append(point)
            face.append(vertex_map[key])
        faces.append(face)

    return {
        'faces': np.array(faces, dtype=int),
        'vertices': np.array(unique_vertices)
    }
