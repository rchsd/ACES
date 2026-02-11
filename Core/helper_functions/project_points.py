import numpy as np
from helper_functions import generate_random_points
import trimesh

def project_points(mesh, norms, npoints, range):
    pgon = trimesh.Trimesh(vertices=mesh.vertices, faces=mesh.faces)
    # Create points on surface
    #points, fi = generate_random_points.sample_points_on_mesh(pgon, npoints, True)
    points, fi = generate_random_points.random_sample(pgon, npoints)

    # Create distances from surface
    dists = np.random.rand(npoints, 1) * np.diff(range) + range[0]

    # Calculate projected points
    points = points + dists * norms[fi, :]

    return points, dists