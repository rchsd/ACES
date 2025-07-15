import trimesh

def sample_points_on_mesh(mesh, num_points=500, return_indices=False):
    """
    Sample points on the surface of a watertight mesh.

    Parameters:
    - mesh: A trimesh.Trimesh object.
    - num_points: Number of points to sample.
    - return_indices: If True, also return the face indices of the sampled points.

    Returns:
    - points: Sampled points on the mesh surface.
    - face_indices (optional): Indices of the faces where each point was sampled.
    """
    new_mesh = trimesh.Trimesh(vertices=mesh.vertices, faces=mesh.faces)

    if return_indices:
        points, face_indices = new_mesh.sample(num_points, return_index=True)
        return points, face_indices
    else:
        points = new_mesh.sample(num_points)
        return points