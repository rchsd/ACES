import numpy as np
import trimesh
from helper_functions import *
import unitize

def load_patient(pgon_struct):

    meshes = []
    metadata = []

    # mask has parts with values of 255, becomes 65024 after bit shifting
    orts = pgon_separation.separate_by_mask(pgon_struct['mesh'], pgon_struct['mask'] == 65024)

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
    pgon = pgon_separation.separate_by_mask(pgon_struct['mesh'], pgon_struct['step'][:, 0])
    pgon_temp = pgon.copy().apply_transform(transform)
    vertices = pgon_temp.vertices
    faces = pgon_temp.faces

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    pgon_struct['mesh'] = mesh

    metadata.append({
        'mask': pgon_struct['mask'][pgon_struct['step'][:, 0]] - 1,
        'centers': apply_transform(centers, transform),
        'radii': radii,
        'tform': transform
    })

    #return meshes if len(meshes) > 1 else meshes[0], metadata if len(metadata) > 1 else metadata[0]
    return pgon_struct, metadata


def apply_transform(points, transform):
    # Convert to homogeneous coordinates
    points_h = np.hstack([points, np.ones((points.shape[0], 1))])
    # Apply transformation
    transformed = (transform @ points_h.T).T
    return transformed[:, :3]