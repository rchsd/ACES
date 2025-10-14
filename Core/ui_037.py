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
import split_read
import write_mesh_from_vertices_faces as wvf
import split_write
import pgon_track_splt
import vertex_values
import step_02_gui as tpp

def ui_037(rotated_pelvis):
    file = {'mesh': rotated_pelvis}
    pgon_dict = step_0(file)
    pgon_dict, centers, radii = step_1(rotated_pelvis, pgon_dict)
    for current_index in range(1, 3):
        pgon_dict = step_2(pgon_dict, centers, radii, current_index)
    pgon = step_3(pgon_dict, centers, radii)
    
    return pgon
    
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
    bounds = np.zeros((0, 3))
    index = side - 1

    # Get correct side of polygon
    temp = pgon_separation.pgon_mask(pgon_struct['mesh'], pgon_struct['step'][:,2])
    mask = pgon_struct['mask'][pgon_struct['step'][:,2]]
    temp_2 = pgon_separation.pgon_mask(temp, np.mod(mask, 1) == np.mod(side, 1))
    mask = mask[np.mod(mask, 1) == np.mod(side, 1)] > 2
    next = None
    #bounds = tpp.get_projected_points(temp_2, mask, centers[side, :], radii[side], bounds)

    # Get bounds from GUI, made placeholder values
    if side == 1:     
        bounds = [
            [1.61130533155253, 62.2104774804963, -59.9403544387100],
            [-2.98932152246617, 65.0650606157165, -51.6403794430619],
            [-7.34775112723169, 67.2217866734611, -45.0245965083881],
            [-7.72200918223249, 69.3480503089603, -39.6956700566565],
            [-5.43729393271627, 72.2822761564305, -33.8127287727286],
            [4.20327163457286, 71.0439532607862, -26.9901709307782],
            [15.3015917738291, 71.6722849902156, -26.4668214238727],
            [19.4608502629328, 66.4420422475634, -31.9885584898059],
            [21.1244803732521, 61.7369738673751, -41.9030427539932],
            [23.3351779795573, 63.9742418931808, -51.2725106300571],
            [21.5039262916537, 60.9578688263805, -56.3143169343964],
            [1.61130533155253, 62.2104774804963, -59.9403544387100]]

        next = 1
    else:
        bounds = [
            [25.3045585876297, -63.5475473763193, -58.5582828041084],
            [24.1332604996705, -66.1454693708478, -44.1019601497463],
            [21.1636168024839, -69.6240646536135, -33.0447749133765],
            [13.6114116876227, -73.9058089049435, -28.2780929142467],
            [2.27276953826547, -74.9146182228626, -30.3890602286426],
            [-3.00053887140878, -74.3440647221311, -34.4490504628709],
            [-5.82578793780910, -73.0278049023276, -40.1903990382810],
            [-6.35175508242096, -72.0343244658184, -46.4807911318309],
            [-5.71131604262102, -72.4100879360961, -50.5798107243275],
            [-4.54250949739974, -66.9258561970092, -49.4445593297409],
            [-1.50041971067511, -65.7641390475811, -53.0062114755565],
            [3.02803482928811, -64.2295630281545, -58.8743715723273],
            [5.52932169182047, -62.9618628548538, -63.0824055430105],
            [25.3045585876297, -63.5475473763193, -58.5582828041084]]
        next = 2

    # Get whether or not each side exists
    exists = [
        np.any(np.isin(pgon_struct['mask'], [5, 7])),
        np.any(np.isin(pgon_struct['mask'], [6, 8]))
    ]

    # Delete only current side if both sides exist
    if np.all(exists):
        pgon_struct['step'][pgon_struct['step'][:, -2] & (pgon_struct['mask'] % 2 == side % 2), -1] = True
        keep = ~np.isin(pgon_struct['mask'], side + np.array([4, 6]))
        temp = pgon_separation.pgon_mask(pgon_struct['mesh'], keep)
        pgon_struct['faces'] = temp.faces
        pgon_struct['vertices'] = temp.vertices
        pgon_struct['step'] = pgon_struct['step'][keep, :]
        pgon_struct['mask'] = pgon_struct['mask'][keep]

    # If current mask exists, delete it
    elif exists[index]:
        pgon_struct['step'] = pgon_struct['step'][:, :-1]
        keep = np.any(pgon_struct['step'], axis=1)
        temp = pgon_separation.pgon_mask(pgon_struct['mesh'], keep)
        pgon_struct['faces'] = temp.faces
        pgon_struct['vertices'] = temp.vertices
        pgon_struct['step'] = pgon_struct['step'][keep, :]
        pgon_struct['mask'] = pgon_struct['mask'][keep]

    # Get vertex values to use for split
    vals = vertex_values.find_vertex_values(pgon_struct, bounds, centers, radii, side)

    # Split polygon
    vals = vals.reshape(-1, 1)
    pgon = pgon_track_splt.track_split(pgon_struct, vals, [0, 0, 0, 1], 0)

    # If other step exists, merge steps
    if exists[2 - side]:
        pgon['step'][:, -2] = pgon['step'][:, -1]
        pgon['step'] = pgon['step'][:, :-1]
        pgon['mask'][pgon['mask'] > 8] = pgon['mask'][pgon['mask'] > 8] - 4

    return pgon

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
