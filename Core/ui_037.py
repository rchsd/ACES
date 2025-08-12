from helper_functions import *
import parse_inputs
import project_points
import grid_occupancy
import numpy as np
import sphere_regression_with_weights
import mark_acetabulum

def ui_037(rotated_pelvis):
    centers, radii = [], []
    try:
        for k in range(20):
            try:
                centers, radii = locate_acetabulum(rotated_pelvis)
                break
            except Exception as e:
                print('failed, trying again...')
                if k != 19:
                    continue
            centers, radii = locate_acetabulum(rotated_pelvis)
    except Exception as ex:
        print('none')
        return None
    
    # Mark acetabulum
    mesh = mark_acetabulum.mark_acetabulum( rotated_pelvis, centers, radii)
    return None

def locate_acetabulum(mesh, params = dict()):
    # calculate polygon unit normals and barycenters
    barys, _, norms, _ = find_barys_and_norms.find_barys_norms(mesh)
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
    #for i in range(params['GridCycles'] - 1):
    # Update grid size and range
    grid_size = params['GridSize'] / params['GridAdjustmentFactor']
    adjustment = np.array([-1, 1]) * np.sqrt(5 * params['GridSize'] ** 2) / 2
    radius_range = radii + adjustment

    # Loop through centers
    for c in range(0, 2):
        print('c: ', c)

        # Filter faces
        mask = filter_faces.filter_faces(barys, norms, centers[c, :], radius_range[1], 45)
        pgon = pgon_separation.separate_by_mask(mesh, mask)
        points, dists = project_points.project_points(pgon, norms[mask, :], params['SamplePoints'], radius_range)

        # Get grid occupancy
        grid, count, reidx = grid_occupancy.get_grid_occupancy(points, grid_size)

        # Locate best grid point
        r = np.argmax(count)
        new_grid = grid[r, :]
        centers[c, :] = new_grid
        radii[c] = np.mean(dists[reidx == r]); 

    # Calculate centers using spherefit
    for i in range(1, params['FitCycles'] + 1):
        print('fit cycles: ', i)
        # Loop through centers
        for c in range(0, 2):
            print('c: ', c)
            # Filter faces
            mask = filter_faces.filter_faces(barys, norms, centers[c, :], params['RadiusRange'][1], 60)

            # Sample polygon
            pgon = pgon_separation.separate_by_mask(mesh, mask)
            points, fi =  generate_random_points.sample_points_on_mesh(pgon, params['SamplePoints'], True)

            # Perform spherical regressions using different weights
            for j in range(1, params['WeightCycles'] + 1):  
                print('j: ', j)

                # Calculate radial vectors
                rvecs = centers[c, :] - points
                mags = np.linalg.norm(rvecs, axis=1)
                rvecs = rvecs / mags[:, np.newaxis]

                # Calculate weights
                weights = (np.sum(rvecs * norms[fi, :], axis=1) + 1) / 2

                # Update weights
                if i > 1 or j > 1:
                    weights = weights * (4 ** (-np.maximum(mags - radii[c], 0)))

                # Calculate sphere fit, original function
                #centers[c, :], radii[c] = sphere_regression.sphereFit(points)
                centers[c, :], radii[c] = sphere_regression_with_weights.sphereFit(points, weights)
    # Assume standard output coordinates (-x = left)
    centers = np.array(centers)
    radii = np.array(radii)
    ic = np.lexsort(centers.T[::-1])
    centers = centers[ic]                         
    radii = radii[ic]
    print('done!!!')
    return centers, radii
