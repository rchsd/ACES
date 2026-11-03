import numpy as np
import trimesh
from helper_functions import pgon_separation, find_barys_and_norms, unitize

def load_new_patient(pgon_struct):
    metadata = []
    attributes = pgon_struct['mask']
    pgon_struct['mask'] = (attributes >> 8) + 1
    pgon_struct['step'] = (attributes[:, None] & (1 << np.arange(7, -1, -1))) != 0

    # Remove extra steps
    pgon_struct['step'] = pgon_struct['step'][:, :np.max(np.where(np.any(pgon_struct['step'], axis=0))) + 1]

    orts = pgon_separation.pgon_mask(pgon_struct['mesh'], pgon_struct['mask'] == 255)

    # Sort faces so right comes first
    barys, norms, _, _ = find_barys_and_norms.find_barys_norms(orts)
    sort_idx = np.argsort(np.abs(norms @ np.diff(barys, axis=0).T).flatten())
    orts.faces = orts.faces[sort_idx]
    centers, _, _, _ = find_barys_and_norms.find_barys_norms(orts)

    radii = [
        np.mean(np.linalg.norm(orts.vertices[orts.faces[0]] - centers[0], axis=1)),
        np.mean(np.linalg.norm(orts.vertices[orts.faces[1]] - centers[1], axis=1))
    ]

    is_vec = unitize.unitize(
    unitize.unitize(np.diff(orts.vertices[orts.faces[0, [2, 1]]], axis=0)[0]) +
    unitize.unitize(np.diff(orts.vertices[orts.faces[1, [2, 1]]], axis=0)[0]))
    rl_vec = unitize.unitize(np.diff(centers, axis=0)[0])
    pa_vec = np.cross(rl_vec, is_vec)

    # Create transformation matrix
    R = np.vstack([pa_vec, rl_vec, is_vec])
    T = -np.mean(centers, axis=0)
    transform = np.eye(4)
    transform[:3, :3] = R
    transform[:3, 3] = T @ R.T

    # Apply transformation
    pgon = pgon_separation.pgon_mask(pgon_struct['mesh'], pgon_struct['step'][:, 3])
    pgon_temp = pgon.copy().apply_transform(transform)
    vertices = pgon_temp.vertices
    faces = pgon_temp.faces

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    pgon_struct['mesh'] = mesh

    centers_homogeneous = np.hstack([centers, np.ones((centers.shape[0], 1))])
    transformed_centers_homogeneous = (transform @ centers_homogeneous.T).T
    centers = transformed_centers_homogeneous[:, :3]

    metadata.append({
        'mask': pgon_struct['mask'][pgon_struct['step'][:, 3]] - 1,
        'centers': centers,
        'radii': radii,
        'tform': transform
    })

    return pgon_struct, metadata


def apply_transform(points, transform):
    # Convert to homogeneous coordinates
    points_h = np.hstack([points, np.ones((points.shape[0], 1))])
    # Apply transformation
    transformed = (transform @ points_h.T).T
    return transformed[:, :3]
