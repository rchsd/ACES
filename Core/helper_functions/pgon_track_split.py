import numpy as np
import trimesh
from helper_functions import split_mesh

def track_split(pgon, verts, plane, coef):
    # Ensure 'step' exists and is valid
    if 'step' not in pgon or not isinstance(pgon['step'], np.ndarray) or \
       pgon['step'].shape[0] != pgon['faces'].shape[0]:
        pgon['step'] = np.ones((pgon['faces'].shape[0], 1), dtype=bool)

    # Get working step indices
    work_step = np.where(pgon['step'][:, -1])[0]

    # Call pgonsplit_
    stacked_verts = np.hstack([pgon['vertices'], verts])
    temp, mask, orig = split_mesh.pgon_split(None, plane, coef, stacked_verts, pgon['faces'][work_step])

    # Ensure 'mask' exists and is valid
    if 'mask' not in pgon or pgon['mask'].shape[0] != pgon['faces'].shape[0]:
        pgon['mask'] = np.zeros((pgon['faces'].shape[0],), dtype=int)

    # Locate split faces
    orig_unique, indices, inverse = np.unique(orig, return_index=True, return_inverse=True)
    counts = np.bincount(inverse)
    split_flags = counts > 1

    # Expand step and mask arrays
    new_face_count = np.sum(split_flags[inverse])
    jj = np.arange(pgon['step'].shape[0], pgon['step'].shape[0] + new_face_count)
    #jj = jj.reshape(1, jj.shape[0]) 
    pgon['step'] = np.vstack((pgon['step'], np.zeros((new_face_count, pgon['step'].shape[1]), dtype=bool)))

    step_split = pgon['step'][:, -1].copy()
    step_split[step_split] = split_flags
    step_new = np.zeros_like(step_split, dtype=bool)
    step_new[jj] = True

    # Convert to original indices
    split = split_flags[inverse]
    orig = orig_unique[inverse]

    # Sort merged faces
    sort_indices = np.argsort(np.concatenate((np.arange(pgon['faces'].shape[0]), work_step[orig[split]])))

    # Expand polygon
    pgon['vertices'] = temp.vertices[:, :pgon['vertices'].shape[1]]
    pgon['faces'] = np.vstack((pgon['faces'], temp.faces[split]))
    pgon['mask'] = np.concatenate((pgon['mask'], pgon['mask'][work_step[orig[split]]]))

    # Sort outputs
    pgon['faces'] = pgon['faces'][sort_indices]
    pgon['step'] = pgon['step'][sort_indices]
    pgon['mask'] = pgon['mask'][sort_indices]
    step_split = step_split[sort_indices]
    step_new = step_new[sort_indices]

    # Update step
    new_step_column = (pgon['step'][:, -1] | step_new) & ~step_split
    pgon['step'] = np.hstack((pgon['step'], new_step_column[:, None]))

    # Update mask
    shift_amount = pgon['step'].shape[1] - 2
    update_indices = pgon['step'][:, -1]
    pgon['mask'][update_indices] = np.bitwise_or(
        pgon['mask'][update_indices] - 1,
        np.left_shift(mask.astype(int), shift_amount)
    ) + 1

    mesh = trimesh.Trimesh(vertices=pgon['vertices'], faces = pgon['faces'])
    pgon['mesh'] = mesh

    return pgon
