from helper_functions import *
import parse_inputs
import project_points
import grid_occupancy
import numpy as np
import sphere_regression_with_weights
import mark_acetabulum
import unitize
import trimesh
import scipy.io as sio
import load_patient
import split_read
import write_mesh_from_vertices_faces as wvf
import split_write
import process_default
import test_track_split

def ui_037(rotated_pelvis):
    pgon_dict = step_0(rotated_pelvis)
    pgon_dict, centers, radii = step_1(rotated_pelvis, pgon_dict)
    current_index = 0
    #pgon_dict = step_2(pgon_dict, centers, radii, current_index)
    pgon = step_3(pgon_dict, centers, radii)
    pgon_struct, metadata = load_patient.load_patient(pgon)
    mask, centers, radii, tform = metadata['mask'], metadata['centers'], metadata['radii'], metadata['tform']
    process_default.default(pgon_struct['mesh'], mask, centers, radii, tform)
    print('hello')
    
def step_0(pgon):
    pgon_struct = split_read.split_read(pgon)
    return pgon_struct
    
def step_1(rotated_pelvis, pgon_dict):
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
    
    # mesh is a dict that contains vertices, faces, steps, and mesh
    pgon_dict = mark_acetabulum.mark_acetabulum(pgon_dict, centers, radii)
    return pgon_dict, centers, radii

# not needed
def step_1_load(pgon_dict):
    # Get center faces
    cpgon = pgon_separation.pgon_mask(pgon_dict['mesh'], pgon_dict['mesh'] == 255)

    # Calculate centers
    centers, _, _, _ = find_barys_and_norms.find_barys_norms(cpgon)

    # Calculate radii
    radii, centers = [], []
    vertices = cpgon.vertices[cpgon.faces[0, :], :]
    result = np.mean(vertices, axis=1)
    diff = centers[0, :] - result
    radii[0] = np.mean(np.linalg.norm(diff))
    vertices = cpgon.vertices[cpgon.faces[1, :], :]
    result = np.mean(vertices, axis=1)
    diff = centers[1, :] - result
    radii[1] = np.mean(diff)

    return pgon_dict, centers, radii

# locates fossa
def step_2(pgon_struct, centers, radii, side):
    bounds = np.zeros((0, 2))

    # Get correct side of polygon
    #print(np.array( pgon_struct['step']).shape)
    temp = pgon_separation.pgon_mask(pgon_struct['mesh'], pgon_struct['step'][:,2])
    mask = pgon_struct['mask'][pgon_struct['step'][:,2]]
    temp_2 = pgon_separation.pgon_mask(temp, np.mod(mask, 1) == np.mod(side, 1))
    mask = mask[np.mod(mask, 1) == np.mod(side, 1)] > 2

    # Get whether or not each side exists
    '''exists = [] * 2
    exists[0] = np.any(np.isin(mesh['mask'], (5, 7)))
    exists[1] = np.any(np.isin(mesh['mask'], (6, 8)))'''

    # ignoring previous matlab steps since the user doesn't trace fossa
    # tracing fossa is what creates the bounds so I'm keeping them empty  
    '''if bounds.size == 0:
        vals = vertex_values(pgon_struct, bounds, centers, radii, side)
        pgon = pgontracksplit(pgon_struct, vals, [0, 0, 0, 1], 0);'''

    
    return None

# SET_CENTERS: Creates triangles to represent acetabulum center
def step_3(pgon, centers, radii):
    # Create vectors
    rl = unitize.unitize(np.diff(centers, axis=0))
    pa = unitize.unitize(np.cross((0, 0, 1), rl))
    i_s = np.cross(pa, rl)

    # Create output polygon
    cpgon = {'faces': np.array([[1, 2, 3], [4, 5, 6]])}

    # Calculate vectors
    up = np.array([-np.sin(np.radians(30)), np.cos(np.radians(30))])
    dn = np.array([-np.sin(np.radians(30)), -np.cos(np.radians(30))])

    # Create vertices
    cpgon['vertices'] = np.zeros((6, 3))
    rl_stacked = np.vstack([rl, i_s])  # shape (2, 3)
    dn_result = np.dot(dn, rl_stacked)    
    up_result = np.dot(up, rl_stacked)
    pa_stacked = np.vstack([pa, i_s])
    radii = radii.reshape(2,)  
    cpgon['vertices'][0, :] = centers[0, :] + radii[0] * rl
    cpgon['vertices'][1, :] = centers[0, :] + radii[0] * dn_result
    cpgon['vertices'][2, :] = centers[0, :] + radii[0] * up_result
    cpgon['vertices'][3, :] = centers[1, :] + radii[1] * pa
    cpgon['vertices'][4, :] = centers[1, :] + radii[1] * np.dot(dn, pa_stacked)
    cpgon['vertices'][5, :] = centers[1, :] + radii[1] * np.dot(up, pa_stacked)

    # Update polygon
    vertex_offset = pgon['vertices'].shape[0]
    # Append adjusted faces
    pgon['faces'] = np.vstack((pgon['faces'], cpgon['faces'] + vertex_offset))

    # Append vertices
    pgon['vertices'] = np.vstack((pgon['vertices'], cpgon['vertices']))

    # Append mask values (2 new entries with value 255)
    pgon['mask'] = np.concatenate([pgon['mask'], np.full(2, 255, dtype=pgon['mask'].dtype)])

    # Append step values (2 new rows of False)
    pgon['step'] = np.vstack([pgon['step'], np.zeros((2, pgon['step'].shape[1]), dtype=bool)])
    pgon_dict = split_write.splitwrite(pgon)
    #mesh = wvf.write_mesh(pgon['vertices'], pgon['faces'])
    #pgon['mesh'] = mesh

    return pgon_dict


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
    # Update grid size and range
    grid_size = params['GridSize'] / params['GridAdjustmentFactor']
    adjustment = np.array([-1, 1]) * np.sqrt(5 * params['GridSize'] ** 2) / 2
    radius_range = radii + adjustment

    # Loop through centers
    for c in range(0, 2):
        print('c: ', c)

        # Filter faces
        mask = filter_faces.filter_faces(barys, norms, centers[c, :], radius_range[1], 45)
        pgon = pgon_separation.pgon_mask(mesh, mask)
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
            pgon = pgon_separation.pgon_mask(mesh, mask)
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
                centers[c, :], radii[c] = sphere_regression_with_weights.sphereFit(points, weights)
    # Assume standard output coordinates (-x = left)
    centers = np.array(centers)
    radii = np.array(radii)
    ic = np.lexsort(centers.T[::-1])
    centers = centers[ic]                         
    radii = radii[ic]
    return centers, radii

'''mesh = trimesh.load('new_mesh.stl')
centers_mat = sio.loadmat('centers.mat')
centers = centers_mat.get('centers')
radii_mat = sio.loadmat('radii.mat')
radii = radii_mat.get('radii')
step_3(mesh, centers, radii)'''
