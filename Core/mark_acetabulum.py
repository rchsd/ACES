import numpy as np
import parse_inputs
import split_read
import separate
import unitize
import edit_weights
import trimesh
import scipy.io as sio
from helper_functions import *

def mark_acetabulum(rotated_mesh, centers, radii, n=None, params = dict()):
    params = parse_inputs.parse_inputs(params)
    # revert to original step if already split pgon passed in

    # returns dictionary of mesh, step and mask
    pgon_struct = split_read.split_read(rotated_mesh)
    # pgonmask
    temp_pgon = pgon_separation.separate_by_mask(pgon_struct['mesh'], pgon_struct['step'])
    temp_pgon_2, mesh = separate.separate(pgon_struct, temp_pgon, centers, radii)

    # calculate vertex normals
    _, _, _, vnorms = find_barys_and_norms.find_barys_norms(mesh)

    # rvecs: vectors from each vertex to each center
    rvecs = centers[:, None, :] - mesh.vertices[None, :, :]  # shape: (2, 321062, 3)

    # Distance weights
    magnitudes = np.linalg.norm(rvecs, axis=2)          # shape: (2, 321062)
    dw = magnitudes / radii[:, None]                    # shape: (2, 321062)
    dw = dw - params['DistanceCutoff']
    dw[dw < 0] = 0
    dw = np.exp(-dw)                                    # shape: (2, 321062)
    dw = np.array(dw).T

    # Normal weights
    # Normalize rvecs: shape (2, 321062, 3)
    unit_rvecs = rvecs / np.linalg.norm(rvecs, axis=2, keepdims=True)

    # Transpose to shape (321062, 2, 3) to align with vnorms
    unit_rvecs_transposed = np.transpose(unit_rvecs, (1, 0, 2))  # (vertices, centers, 3)

    # Expand vnorms to shape (321062, 1, 3)
    vnorms_expanded = vnorms[:, np.newaxis, :]  # (vertices, 1, 3)

    # Compute dot products: result is (321062, 2)
    nw = np.sum(unit_rvecs_transposed * vnorms_expanded, axis=2)

    # Edit w, only displays acetabula since user can't draw fossa
    edit_weights.edit_weights(mesh, np.max(nw * dw, axis=1))
    #w = edit_weights.edit_weights(rotated_mesh, n)

    return temp_pgon_2

'''mesh = trimesh.load('new_mesh.stl')
centers_mat = sio.loadmat('centers.mat')
centers = centers_mat.get('centers')
radii_mat = sio.loadmat('radii.mat')
radii = radii_mat.get('radii')
n_mat = sio.loadmat('n.mat')
n = n_mat.get('n')
mark_acetabulum(mesh, centers, radii, n)'''
