import numpy as np
import trimesh
import unitize
import pgon_track_splt
from helper_functions import *

def separate_old(pgon_struct, combined_mesh, centers, radii):
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
    components = combined_mesh.split(only_watertight=True)

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
        pgon_struct['mesh'] = mesh

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
    
    
def separate_new(pgon_struct, combined_mesh, centers, radii):
    """
    Separates a combined hip mesh into left and right components using reference centroids.

    Parameters:
    - pgon_struct: dictionary containing mesh data and step/mask arrays.
    - combined_mesh: trimesh.Trimesh object representing the combined mesh.
    - centers: (2, 3) numpy array of reference centroids [left_centroid; right_centroid].
    - radii: (2,) numpy array of reference radii for volume thresholding.

    Returns:
    - pgon_struct: updated dictionary with 'mask' and 'step' fields modified.
    - mesh: updated trimesh.Trimesh object.
    """

    # Split mesh into connected components
    components = combined_mesh.split(only_watertight=True)

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

        # Convert combined mesh faces to sorted tuples for comparison
        combined_faces_sorted = [tuple(sorted(face)) for face in combined_mesh.faces]

        for i, part in enumerate(selected_components):
            part_faces_sorted = set(tuple(sorted(face)) for face in part.faces)
            face_indices = [j for j, face in enumerate(combined_faces_sorted) if face in part_faces_sorted]
            face_mask[face_indices] = i + 1

        # Optional: warn if any faces remain unlabeled
        if np.any(face_mask == 0):
            print("Warning: Some faces were not assigned to any component.")

        # Update pgon_struct
        pgon_struct['mask'] = face_mask
        pgon_struct['step'] = np.ones((len(combined_mesh.faces), 2), dtype=bool)

        mesh = trimesh.Trimesh(vertices=pgon_struct['vertices'], faces=pgon_struct['faces'])
        pgon_struct['mesh'] = mesh

        return pgon_struct, mesh

    else:
        raise ValueError("Expected exactly two large components, but found {}".format(len(ii)))

#find_parts(polygon=None, method='vertex', mesh=None, max_angle=None):
def separate(pgon, combined_mesh, centers, radii):
    # Get polygon parts
    parts = pgon_parts.find_parts(None, method='vertex', mesh=combined_mesh, max_angle=None)

    # Compute volumes of each part
    vols = pgon_parts.compute_part_volumes(combined_mesh, parts)

    # Identify large pieces
    threshold = (4 * np.pi * np.mean(radii) ** 3) / 3
    ii = np.where(10 * vols > threshold)[0]

    if len(ii) == 2:
        # Keep only the two large pieces
        #mesh = pgon_separation.pgon_mask(combined_mesh, np.isin(parts, ii).astype(bool))
        parts = pgon_parts.find_parts(None, method='vertex', mesh=combined_mesh, max_angle=None)
        cent = pgon_parts.compute_part_centroids(combined_mesh, parts)

        # Determine left/right orientation
        distances = np.linalg.norm(centers - cent[0], axis=1)
        im = np.argmin(distances)
        if im != 0:
            parts = 3 - parts  # Flip labels

        # Update step and mask
        pgon['step'] = np.ones((pgon['faces'].shape[0], 2), dtype=bool)
        parts = np.array(parts)
        pgon['mask'] = parts.astype(int)

        mesh = trimesh.Trimesh(vertices=pgon['vertices'], faces=pgon['faces'])
        pgon['mesh'] = mesh

    elif len(ii) == 1:
        # Keep the one large piece and split it
        pgon = pgon_separation.pgon_mask(pgon, parts == ii[0])
        norm = unitize.unitize(np.diff(centers, axis=0)[0])
        pgon = pgon_track_splt.track_split(pgon, verts=[], plane=norm, coef=np.dot(norm, np.mean(centers, axis=0)))

    else:
        raise ValueError("Model could not be resolved into right and left halves.")

    return pgon

