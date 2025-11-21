import trimesh
import numpy as np

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
    
def random_sample(mesh: trimesh.Trimesh, npoints: int=500):
    if len(mesh.faces) == 0:
        raise ValueError("Empty mesh cannot be sampled.")

    # Get face areas
    areas = mesh.area_faces
    total_area = np.sum(areas)

    # Normalize areas to get probabilities
    probabilities = areas / total_area
    # Randomly select faces based on area weights
    selected_faces = np.random.choice(len(mesh.faces), size=npoints, p=probabilities)

    # Sample points within selected faces
    sampled_points = []
    for face_index in selected_faces:
        face = mesh.faces[face_index]
        vertices = mesh.vertices[face]

        # Barycentric sampling
        r1, r2 = np.random.rand(2)
        sqrt_r1 = np.sqrt(r1)
        point = (
            (1 - sqrt_r1) * vertices[0] +
            sqrt_r1 * (1 - r2) * vertices[1] +
            sqrt_r1 * r2 * vertices[2]
        )
        sampled_points.append(point)

    return np.array(sampled_points), selected_faces