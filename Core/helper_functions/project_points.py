import numpy as np
from helper_functions import generate_random_points
import trimesh

def project_points(mesh, norms, npoints, range):
    pgon = trimesh.Trimesh(vertices=mesh.vertices, faces=mesh.faces)
    # Create points on surface
    points, fi = generate_random_points.sample_points_on_mesh(pgon, npoints, True)

    # Create distances from surface
    dists = np.random.rand(npoints, 1) * np.diff(range) + range[0]

    # Calculate projected points
    points = points + dists * norms[fi, :]

    return points, dists

'''mesh = trimesh.load('c:\\Users\\bbeasley\\Documents\\Python Projects\\Matlab-GUI\\Tests\\Schmitz\\1_Combined_Pelvis_0.stl')
project_points(mesh, [0, 1, 0], 5000, [15, 35])'''