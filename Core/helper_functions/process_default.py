import numpy as np
from helper_functions import pgon_separation, find_barys_and_norms, pgon_props, fossa_selection_points_qt
from helper_functions import reflection, translation, pgon_upe, find_plane_contours
import pandas as pd
import numpy_groupies as ng

def default(pgon, mask, centers, radii):
    print('Calculating coverage angles.')
    # Define indexes
    r_fossa = 0
    l_fossa = 2
    r_hip = 1
    l_hip = 3

    angles = np.zeros((360, 4))
    r_fossa_mesh = fossa_selection_points_qt.find_fossa(pgon_separation.pgon_mask(pgon, (mask & 3) == 2), centers[0].copy())
    l_fossa_mesh = fossa_selection_points_qt.find_fossa(pgon_separation.pgon_mask(pgon, (mask & 3) == 3), centers[1].copy())

    angles[:, r_fossa] = coverage_angles(r_fossa_mesh, centers[0]) 
    angles[:, l_fossa] = coverage_angles(l_fossa_mesh, centers[1]) 
    angles[:, r_hip] = coverage_angles(pgon_separation.pgon_mask(pgon, (mask & 3) == 2), centers[0])
    angles[:, l_hip] = coverage_angles(pgon_separation.pgon_mask(pgon, (mask & 3) == 3), centers[1])

    # Calculate surface areas
    areas = np.zeros((2, 2))

    # Right fossa
    areas.flat[r_fossa] = r_fossa_mesh.area

    # Left fossa
    areas.flat[l_fossa] = l_fossa_mesh.area

    # Right hip
    selected_faces = (mask & 3) == 2
    masked_mesh = pgon.submesh([selected_faces], append=True)
    areas.flat[r_hip] = masked_mesh.area

    # Left hip
    selected_faces = (mask & 3) == 3
    masked_mesh = pgon.submesh([selected_faces], append=True)
    areas.flat[l_hip] = masked_mesh.area

    # Calculate orientations
    selected = (mask & 3) == 2
    _, normals, _, _ = find_barys_and_norms.find_barys_norms(pgon, selected)
    summed = np.sum(normals, axis=0)
    unit_vector = summed / np.linalg.norm(summed)
    orient = np.zeros((2, 3))
    orient[0, :] = unit_vector
    # needed for image generation in snapshot code
    right_ace_normals = normals

    selected = (mask & 3) == 3
    _  , normals, _, _ = find_barys_and_norms.find_barys_norms(pgon, selected)
    summed = np.sum(normals, axis=0)
    unit_vector = summed / np.linalg.norm(summed)
    orient[1, :] = unit_vector
    # needed for image generation in snapshot code
    left_ace_normals = normals

    elevation = np.cross(orient[0], orient[1])
    elevation /= np.linalg.norm(elevation)

    # Calculate orientation angles
    spread = np.degrees(np.arccos(np.dot(orient[0], orient[1])))
    tilt = np.degrees(np.arctan2(elevation[2], elevation[0]))

    # Get masks
    mask1 = np.roll(np.ceil(np.arange(1, 361) / 45).astype(int), -22)
    mask2 = np.roll(mask1, -round(tilt))

    # Create result dictionary
    result = dict()
    # To Do: give user option to type out filename
    result.update({'name': 'final_pelvis', 'width': (np.linalg.norm(np.diff(centers, axis=0), axis=1)[0]), 'spread': spread, 'tilt': tilt})

    # Create right result dictionary
    right_supine = pd.Series(angles[:, r_hip]).groupby(mask1).sum().div(45).to_numpy()
    right_fossa = pd.Series(angles[:, r_fossa]).groupby(mask1).sum().div(45).to_numpy()
    right_total_tilt = pd.Series(angles[:, r_hip]).groupby(mask2).sum().div(45).to_numpy()
    right_fossa_tilt = pd.Series(angles[:, r_fossa]).groupby(mask2).sum().div(45).to_numpy()

    result.update({'right_center': centers[0], 'right_radius': radii[0], 'right_total_area': areas.flat[r_hip], 'right_fossa_area': areas.flat[r_fossa], 'right_orientation': orient[0], 'right_version': np.degrees(np.arctan2(orient[0, 0], -orient[0, 1]))})
    result.update({'right_tilt': np.degrees(np.arctan2(-orient[0, 2], -orient[0, 1])), 'right_total_supine_coverage': right_supine, 'right_fossa_supine_coverage': right_fossa})
    result.update({'right_total_tilt_coverage': right_total_tilt, 'right_fossa_tilt_coverage': right_fossa_tilt})
    selected_faces = (mask & 3) == 2
    new_mesh = pgon_separation.pgon_mask(pgon, selected_faces)
    result.update({'right_volume': pgon_props.compute_mesh_volume(new_mesh, centers[0])})

    # Create left result dictionary
    left_supine = pd.Series(angles[:, l_hip]).groupby(mask1).sum().div(45).to_numpy()
    left_fossa = pd.Series(angles[:, l_fossa]).groupby(mask1).sum().div(45).to_numpy()
    left_total_tilt = pd.Series(angles[:, l_hip]).groupby(mask2).sum().div(45).to_numpy()
    left_fossa_tilt = pd.Series(angles[:, l_fossa]).groupby(mask2).sum().div(45).to_numpy()

    result.update({'left_center': centers[1], 'left_radius': radii[1], 'left_total_area': areas.flat[l_hip], 'left_fossa_area': areas.flat[l_fossa], 'left_orientation': orient[1], 'left_version': np.degrees(np.arctan2(orient[1, 0], orient[1, 1]))})
    result.update({'left_tilt': np.degrees(np.arctan2(-orient[1, 2], orient[1, 1])), 'left_total_supine_coverage': left_supine, 'left_fossa_supine_coverage': left_fossa})
    result.update({'left_total_tilt_coverage': left_total_tilt, 'left_fossa_tilt_coverage': left_fossa_tilt})
    selected_faces = (mask & 3) == 3
    new_mesh = pgon_separation.pgon_mask(pgon, selected_faces)
    result.update({'left_volume': pgon_props.compute_mesh_volume(new_mesh, centers[1])})

    # needed for image generation in snapshot code, stored in dictionary for later processing
    fossa_dict = dict()
    fossa_dict.update({'right_ace_normals': right_ace_normals, 'left_ace_normals': left_ace_normals})
    _, r_normals, _, _ = find_barys_and_norms.find_barys_norms(r_fossa_mesh)
    _, l_normals, _, _ = find_barys_and_norms.find_barys_norms(l_fossa_mesh)
    fossa_dict.update({'right_fossa_normals': r_normals, 'left_fossa_normals': l_normals})

    return result, fossa_dict


def coverage_angles(pgon, center):
    # Flip and translate right-side
    if center[1] < 0:
        pgon = pgon.apply_transform(reflection.reflection(np.array([0, 1, 0])) @ translation.translate(-center))
    # Translate only left-side
    else:
        pgon = pgon.apply_transform(translation.translate(-center))

    # Get open edges
    _, _, _, _, edge = pgon_upe.unpaired_edges_pgon(pgon)

    # Create sampling vector
    th = np.arange(540) * np.pi / 540
    coefs = np.zeros(th.shape)

    # Create normals
    norms = np.column_stack((np.cos(th), coefs, -np.sin(th)))

    # Locate sample points
    points, _, in_mask = find_plane_contours.compute_contours_with_trimesh(edge, norms, coefs)
    # Extract faces and vertices
    faces = points['faces'][:, 0]
    vertices = points['vertices']

    # Zero out x where in_mask == 1
    vertices[faces[in_mask == 1], 0] = 0
    # Extract subset of vertices
    subset = vertices[faces, :]

    # Get angles about y-axis
    around = np.arctan2(subset[:, 0], subset[:, 2])
    around[around < 0] += 2 * np.pi

    signs = 2 * (around < np.pi) - 1
    xy_mag = np.linalg.norm(subset[:, [0, 2]], axis=1)
    result = np.arctan2(signs * xy_mag, -subset[:, 1])
    
    pos = ng.aggregate(in_mask, result, size=540, func='max')
    neg = -ng.aggregate(in_mask, result, size=540, func='min')

    # Reshaping for accurate results
    pos = pos.reshape(-1, 1)
    neg = neg.reshape(-1, 1)

    combined = np.reshape(np.vstack((pos, neg)), (3, -1), order='F')
    result = np.mean(combined, axis=0) * 180 / np.pi

    return result