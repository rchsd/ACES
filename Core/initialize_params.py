import numpy as np
import unitize
import trimesh
import bounding_spheres
from helper_functions import *

def initialize_params(pgon: trimesh.Trimesh, mask, cen, rad, bounds):
    # Calculate transform
    _, norms, _, _  = find_barys_and_norms.find_barys_norms(pgon, mask)
    direction = np.array([0, 0, 1])
    tform = alignment.align(unitize.unitize(np.sum(norms, axis=0)), direction) @ translation.translate(-cen)

    # Apply transform to vertices and bounds
    pgon.vertices = (tform[:3, :3] @ pgon.vertices.T + tform[:3, 3:4]).T
    bounds = (tform[:3, :3] @ bounds.T + tform[:3, 3:4]).T

    # Calculate cutoff distance
    masked_faces = pgon.faces[mask]
    masked_vertices = pgon.vertices[masked_faces.reshape(-1)]
    dists = np.linalg.norm(masked_vertices, axis=1)
    cutoff = 1.5 * np.max(dists)

    # Create primitive sphere using trimesh
    sphere = trimesh.creation.icosphere(subdivisions=1, radius=cutoff)
    sphere.apply_translation(cen)

    # Compute normals and coefficients
    _, _, sphere_norms, _  = find_barys_and_norms.find_barys_norms(sphere)
    sphere_vertices = sphere.vertices
    sphere_faces = sphere.faces
    coefs = np.sum(sphere_vertices[sphere_faces[:, 0]] * sphere_norms, axis=1)

    # Crop polygon
    '''length = sphere_norms.shape[0]
    for i in range(length):
        pgon, keep, ii = split_mesh.pgon_split(pgon, -sphere_norms[i], -coefs[i])
        mask = mask[ii[keep]]
        pgon = pgon_separation.pgon_mask(pgon, keep)'''

    # Define colors
    colors = np.array([[1.00, 0.95, 0.90], [1.00, 0.25, 0.25]])

    # Scaled distances from vertices to center
    dists = (np.linalg.norm(pgon.vertices, axis=1) - rad) / rad

    # Bounding spheres
    cens, rads = bounding_spheres.find_bounding_spheres(pgon)
    rads = rads ** 2

    # GUI dictionary
    gui = {
        'pgon': pgon,
        'mask': mask,
        'bounds': bounds,
        'original_bounds': bounds.copy(),
        'cutoff': cutoff,
        'colors': colors[mask.astype(int)],
        'centers': cens,
        'radii': rads,
        'radius': rad,
        'one_shot': False,
        'dragging': 0,
        'rotating': False,
        'last_tform': np.eye(4),
        'last_pointer': None,
        'window_view': False,
        'vdists': dists,
        'fdists': np.mean(dists[pgon.faces[mask]], axis=1),
        'max_window': [0, np.max(np.max(dists[pgon.faces[mask]]))],
        'window': None,  # will be set to max_window below
        'cmap': None,    # You can add a colormap if needed
        'adjust_contour': False,
        'contour': np.nan,
        'changed': False,
        'next': np.inf,
        'erasing': False,
        'erase_radius': 5
    }

    gui['window'] = gui['max_window']
    return tform, gui
