from helper_functions import *
import parse_inputs
import project_points
import sphere_regression
import grid_occupancy
import numpy as np
import math

def ui_037(rotated_pelvis):
    locate_acetabulum(rotated_pelvis)
    return None

def locate_acetabulum(mesh, params = dict()):
    # calculate polygon unit normals and barycenters
    barys, _, norms = find_barys_and_norms.find_barys_norms(mesh)
    params = parse_inputs.parse_inputs(params)

    # project points off of polygon surface
    points, dists = project_points.project_points(mesh, norms, params['SamplePoints'], params['RadiusRange'])

    # calculate grid occupancy
    grid, count, reidx = grid_occupancy.get_grid_occupancy(points, params['GridSize'])

    sorted_count = np.sort(count)[::-1]
    # get indices for sorting in descending order
    ic = np.argsort(count)[::-1]
    grid_selected = grid[ic[:20], :]
    count_selected = sorted_count[:20]
    count_selected = count_selected.reshape(-1,1)

    # Locate pair of grid spaces that are highly occupied and far apart
    m1 = count_selected @ count_selected.T
    m2 = calculate_distances.calculate_pairwise_distances(grid_selected)
    r = np.unravel_index(np.argmax(m1 * m2), m1.shape)

    # Get preliminary centers and radii
    centers = grid_selected[r, :]
    r = np.array(r).flatten()
    radii = np.tile(np.mean(dists[np.isin(reidx, ic[r])]), 2)
    #radii = np.full(2, np.mean(dists[np.isin(reidx, ic[r])]))

    # Refine centers    
    for i in range(0, params['GridCycles'] - 1):

        # Update grid size and range
        params['GridSize'] = params['GridSize'] / params['GridAdjustmentFactor']
        adjustment = np.array([-1, 1]) * math.sqrt(5 * params['GridSize'] ** 2) / 2
        params['RadiusRange'] = radii + adjustment

        # Loop through centers
        for c in range(0, 1):

            # Filter faces
            mask = filter_faces.filter_faces(barys, norms, centers[c, :], params['RadiusRange'][1], 45)

            # Re-calculate points
            print("Mask type:", type(mask))
            print("Mask shape:", mask.shape)
            print("Mask dtype:", mask.dtype)
            print("Number of selected faces:", np.sum(mask) if mask.dtype == bool else len(mask))

            pgon = pgon_separation.separate_by_mask(mesh, mask)
            points, dists = project_points.project_points(pgon, norms[mask, :], params['SamplePoints'], params['RadiusRange'])

            # Get grid occupancy
            grid, count, reidx = grid_occupancy.get_grid_occupancy(points, params['GridSize'])

            # Locate best grid point
            r = np.argmax(count)
            new_grid = grid[r, :]
            centers[c, :] = new_grid
            radii[c] = np.mean(dists[reidx == r]); 

    # Calculate centers using spherefit
    for i in range(0, params['FitCycles']):
        # Loop through centers
        for c in range(0, 1):
            # Filter faces
            mask = filter_faces.filter_faces(barys, norms, centers[c, :], params['RadiusRange'][1], 60)

            # Sample polygon
            pgon = pgon_separation.separate_by_mask(mesh, mask)
            points, fi =  generate_random_points.sample_points_on_mesh(pgon, params['SamplePoints'], True)

            # Perform spherical regressions using different weights
            for j in range(0, params['WeightCycles']):

                # Calculate radial vectors
                rvecs = centers[c, :] - points
                mags = np.linalg.norm(rvecs, axis=1)
                rvecs = rvecs / mags[:, np.newaxis]

                # Calculate weights
                weights = (np.sum(rvecs * norms[fi, :], axis=1) + 1) / 2

                # Update weights
                if i > 0 or j > 0:
                    weights = weights * (4 ** (-np.maximum(mags - radii[c], 0)))

                # Calculate sphere fit, original function
                centers[c, :], radii[c] = sphere_regression.sphereFit(points)
    # Assume standard output coordinates (-x = left)
    centers = np.array(centers) 
    sorted_indices = np.argsort(centers, axis=0)
    centers = centers[sorted_indices]
    ic = sorted_indices
    print('done!!!')
