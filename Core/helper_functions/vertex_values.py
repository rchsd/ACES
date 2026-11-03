import numpy as np
from scipy.stats import mode
from scipy.spatial import cKDTree
from helper_functions import alignment, translation, make_pgon, pgon_pip, pgon_edges, pgon_parts, pgon_upe

# VERTEX_VALUES: Converts selection to vertex values
def find_vertex_values(p, b, c, r, s):

    side = s - 1
    v = (b - c[side, :]) / np.linalg.norm(b - c[side, :], axis=1, keepdims=True)
    n = v.sum(axis=0) / np.linalg.norm(v.sum(axis=0))
    cos_th = np.dot(v, np.array(n).reshape(1, 3).T)
    cones = [np.min(cos_th), np.max(cos_th)]

    # Get vertices in acetabulum mask
    selected = np.zeros((p['vertices'].shape[0], 1))
    selected[p['faces'][p['mask'] == s + 2, :]] = 1

    # Filter points
    mask = np.where(selected == 1)[0]
    v2 = (p['vertices'][mask] - c[side]) / np.linalg.norm(p['vertices'][mask] - c[side], axis=1, keepdims=True)
    cos_th2 = v2 @ n
    cos_th2 = np.array(cos_th2).flatten()

    selected[mask[cos_th2 >= cones[0]]] = 2
    selected[mask[cos_th2 >= cones[1]]] = 3

    # Project bounds points onto plane
    mask2 = np.where(selected[mask] == 2)[0]

    b = 2 * r[side] / cos_th * v + c[side, :]
    q = 2 * r[side] / cos_th2[mask2][:, np.newaxis] * v2[mask2, :] + c[side, :]

    # Convert points to 2D
    matrix = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1]
    ])
    tform = (matrix @ alignment.align(n, [0, 0, 1])) @ translation.translate(-c[side, :] - r[side] * n)
    temp = make_pgon.transform_and_project(b, tform)
    if make_pgon.calculate_volume_bounds(temp['faces'], temp['vertices']) < 0:
        temp = pgon_inv(temp)
    selected[selected == 2] = 2 * (pgon_pip.in_pgon(temp, q, tform) != 0) + 1

    # Keep largest contiguous selections
    edges, _, _, _ = pgon_edges.index_by_edges(p['faces'][p['step'][:, 2], :])
    ts = selected[edges] == 3
    ts = ts.squeeze(-1)
    edges = edges[np.logical_and(ts[:, 0], ts[:, 1]), :]
    parts, _ = pgon_parts.find_parts_edges(edges)
    edges = edges[parts == mode(parts, keepdims=False).mode]

    # Reset selection matrix
    neg = np.ones_like(selected, dtype=bool)
    neg[edges] = False

    # Calculate distance from selection polyhedron
    sel = make_pgon.transform_and_project(b, None, True)
    # Append a new vertex from c[side] to sel['vertices']
    sel['vertices'] = np.vstack([sel['vertices'], c[side]])
    # Update the third column of each face to reference the new vertex index
    sel['faces'][:, 2] = sel['vertices'].shape[0] - 1

    R = cKDTree(sel['vertices'], leafsize=10)
    vals = -np.inf * np.ones_like(selected)
    mask = mask.flatten()
    vals = vals.flatten()
    neg = neg.flatten()
    vals[mask] = R.query(p['vertices'][mask, :], k=1)[0]
    vals[vals < 1e-2] = 0
    vals[neg] = -vals[neg]

    f = p['faces'][p['step'][:, 2], :]
    f = f[p['mask'][p['step'][:, 2]] == s + 2, :]

    # Run the unpaired edges function
    faces, _ = pgon_upe.unpaired_edges_faces(f)

    # Ensure faces is a flat NumPy array
    faces = np.ravel(faces)

    # Clean up any NaNs or floating point values resulting from empty/small sample masks
    if faces.size > 0:
        # Strip out any non-finite (NaN or Inf) values that cause casting crashes
        faces = faces[np.isfinite(faces)]

        # If we still have valid values, force them to be raw integers so NumPy can index safely
        if faces.size > 0:
            faces = faces.astype(np.int64)
            vals[faces] = 0

    return vals

def pgon_inv(pgon):
        for i in range(len(pgon)):
             pgon[i]['faces'] = pgon[i]['faces'][:, [*range(pgon[i]['faces'].shape[1] - 2), pgon[i]['faces'].shape[1] - 1, pgon[i]['faces'].shape[1] - 2]]
        return pgon
