import numpy as np
import trimesh

def separate(pgon_struct, combined_mesh, centers, radii):
    """
    Separates a combined hip mesh into left and right components using reference centroids.

    Parameters:
    - pgon_struct: dictionary containing mesh data and step/mask arrays.
    - combined_mesh: trimesh.Trimesh object representing the combined mesh.
    - centers: (2, 3) numpy array of reference centroids [left_centroid; right_centroid].
    - radii: (2,) numpy array of reference radii for volume thresholding.

    Returns:
    - pgon_struct: updated dictionary with 'mask' and 'step' fields modified.
    """

    # Split mesh into connected components
    components = combined_mesh.split(only_watertight=False)

    # Compute volumes of each component
    volumes = np.array([comp.volume for comp in components])
    threshold = (4 * np.pi * np.mean(radii) ** 3) / 3
    ii = np.where(10 * volumes > threshold)[0]

    if len(ii) == 2:
        # Keep only the two large components
        selected_components = [components[i] for i in ii]

        # Compute centroids of selected components
        part_centroids = np.array([comp.centroid for comp in selected_components])

        # Match first part to closest reference center
        distances = np.linalg.norm(centers - part_centroids[0], axis=1)
        im = np.argmin(distances)

        # Flip labels if needed
        if im != 0:
            selected_components = selected_components[::-1]

        # Create face mask: 1 for left, 2 for right
        face_mask = np.zeros(len(combined_mesh.faces), dtype=int)
        for i, part in enumerate(selected_components):
            # Find matching face indices
            face_indices = np.where(np.isin(combined_mesh.faces, part.faces).all(axis=1))[0]
            face_mask[face_indices] = i + 1

        # Update pgon_struct
        pgon_struct['mask'] = face_mask
        pgon_struct['step'] = np.ones((len(combined_mesh.faces), 2), dtype=bool)

        mesh = trimesh.Trimesh(vertices=pgon_struct['vertices'], faces=pgon_struct['faces'])

        return pgon_struct, mesh

    elif len(ii) == 1:
        # Only one large component — split it using a plane between reference centers
        norm = centers[1] - centers[0]
        norm /= np.linalg.norm(norm)
        midpoint = np.mean(centers, axis=0)

        face_centers = combined_mesh.triangles_center
        side = np.dot(face_centers - midpoint, norm) > 0
        face_mask = np.where(side, 2, 1)

        pgon_struct['mask'] = face_mask
        pgon_struct['step'] = np.ones((len(combined_mesh.faces), 2), dtype=bool)

        return pgon_struct

    else:
        raise ValueError("Model could not be resolved into right and left halves.")