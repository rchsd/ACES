import numpy as np
import trimesh

def unitize(vectors):
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / norms

def splitwrite(pgon):
    # Process mask field
    if 'mask' in pgon:
        mask = np.left_shift(np.uint16(np.array(pgon['mask']) - 1), 8)
    else:
        mask = np.zeros((len(pgon['faces']), 1), dtype=np.uint16)

    # Process step field
    step_encoded = None
    if 'step' in pgon:
        n_steps = pgon['step'].shape[1]
        bit_weights = 1 << np.arange(7, 7 - n_steps, -1)  # same as bitshift(1, 7:-1:(8-n_steps))
        step_encoded = (pgon['step'].astype(np.uint16) @ bit_weights).astype(np.uint16)
        mask = np.bitwise_or(mask, step_encoded)

    # Create mesh and write STL
    mesh = trimesh.Trimesh(vertices=pgon['vertices'], faces=pgon['faces'])

    # Return dictionary with mesh, mask, and step
    return {
        'mesh': mesh,
        "mask": mask,
        "step": step_encoded
    }
