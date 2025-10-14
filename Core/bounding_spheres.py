import numpy as np
import trimesh

def find_bounding_spheres(mesh: trimesh.Trimesh):
    # Get triangle vertices
    v1 = mesh.vertices[mesh.faces[:, 0]]
    v2 = mesh.vertices[mesh.faces[:, 1]]
    v3 = mesh.vertices[mesh.faces[:, 2]]

    # Side vectors
    s1 = v2 - v1
    s2 = v3 - v1

    # Dot products
    d11 = np.einsum('ij,ij->i', s1, s1)
    d12 = np.einsum('ij,ij->i', s1, s2)
    d22 = np.einsum('ij,ij->i', s2, s2)
    denoms = 2 * (d11 * d22 - d12 * d12)

    # Barycentric coordinates
    b1 = (d22 * d11 - d12 * d12) / denoms
    b2 = (d11 * d22 - d12 * d12) / denoms
    bcoor = np.stack([b1, b2], axis=1)

    # Initialize centers
    center = np.zeros_like(v1)

    # Conditions
    i1 = bcoor[:, 0] <= 0
    i2 = bcoor[:, 1] <= 0
    i3 = (bcoor[:, 0] + bcoor[:, 1]) >= 1
    i4 = ~(i1 | i2 | i3)

    # Compute centers
    center[i1] = (v1[i1] + v3[i1]) / 2
    center[i2] = (v1[i2] + v2[i2]) / 2
    center[i3] = (v2[i3] + v3[i3]) / 2
    center[i4] = v1[i4] + bcoor[i4, 0][:, None] * s1[i4] + bcoor[i4, 1][:, None] * s2[i4]

    # Compute radii
    radius = np.zeros(len(mesh.faces))
    radius[i3] = np.linalg.norm(v2[i3] - center[i3], axis=1)
    radius[~i3] = np.linalg.norm(v1[~i3] - center[~i3], axis=1)

    return center, radius