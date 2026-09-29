import numpy as np
from helper_functions import generate_random_points
import trimesh

def project_pointss(mesh, norms, npoints, range):
    
    pgon = trimesh.Trimesh(vertices=mesh.vertices, faces=mesh.faces)
    # Create points on surface
    #points, fi = generate_random_points.sample_points_on_mesh(pgon, npoints, True)
    points, fi = generate_random_points.random_sample(pgon, npoints)

    # Create distances from surface
    dists = np.random.rand(npoints, 1) * np.diff(range) + range[0]

    # Calculate projected points
    points = points + dists * norms[fi, :]

    return points, dists


def project_points(mesh, norms, npoints, range_input):
    pgon = trimesh.Trimesh(vertices=mesh.vertices, faces=mesh.faces)
    
    # Create points on surface
    points, fi = generate_random_points.random_sample(pgon, npoints)


    # Convert range boundaries explicitly to flat scalar floats, 
    # regardless of whether a list, tuple, or NumPy array was passed in.
    r_min = float(np.ravel(range_input)[0])
    r_max = float(np.ravel(range_input)[1])
    
    # Create distances from surface as a clean, predictable shape
    dists = np.random.rand(npoints, 1) * (r_max - r_min) + r_min
  

    # Calculate projected points smoothly
    points = points + dists * norms[fi, :]

    return points, dists
