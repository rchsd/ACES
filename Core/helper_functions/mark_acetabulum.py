import numpy as np
import scipy.io as sio
from helper_functions import parse_inputs, pgon_separation, separate, find_barys_and_norms, edit_weights
from helper_functions import pgon_track_split, hole_fill, unitize

def mark_acetabulum(pgon_struct, centers, radii, params = dict()):
    params = parse_inputs.parse_inputs(params)
    # revert to original step if already split pgon passed in

    # returns dictionary of mesh, step and mask
    temp_pgon = pgon_separation.pgon_mask(pgon_struct['mesh'], pgon_struct['step'])
    temp_pgon_2 = separate.separate(pgon_struct, temp_pgon, centers, radii)

    # calculate vertex normals
    _, _, _, vnorms = find_barys_and_norms.find_barys_norms(temp_pgon_2['mesh'])

    # rvecs: vectors from each vertex to each center
    rvecs = centers.T[None, :, :] - temp_pgon_2['mesh'].vertices[:, :, None]

    # Calculate distance weights
    dw = np.squeeze(np.linalg.norm(rvecs, axis=1)) / radii[None, :]
    dw = dw - params['DistanceCutoff']
    dw[dw < 0] = 0
    dw = np.exp(-dw)
    
    # Calculate normal weights
    nw = np.squeeze(np.sum(unitize.unitize(rvecs, axis=1) * vnorms[:, :, None], axis=1))

    # Edit w, only displays acetabula since user can't draw fossa
    w = edit_weights.edit_weights_display(temp_pgon_2['mesh'], np.max(nw * dw, axis=1))

    w = np.array(w).reshape(-1, 1)

    # Select acetabulum
    split = pgon_track_split.track_split(temp_pgon_2, w, np.array([0, 0, 0, 1]), np.cos(np.deg2rad(params['AngleCutoff'])))
    pgon_dict = hole_fill.fill_holes(split)

    return pgon_dict
