import numpy as np
import test_unpaired_edges
import test_trimesh_plane as ttp
from helper_functions import *
import trimesh

def default(pgon, mask, centers, radii, tform):
    # Define indexes
    r_fossa = 0
    l_fossa = 2
    r_hip = 1
    l_hip = 3

    angles = np.zeros((360, 4))
    #angles[:, r_fossa] = coverage_angles(pgon_separation.pgon_mask(pgon, mask == 6), centers[0])  # mask == (6 - 1) * 256
    #angles[:, l_fossa] = coverage_angles(pgon_separation.pgon_mask(pgon, mask == 7), centers[1])  # mask == (7 - 1) * 256
    angles[:, r_hip]   = coverage_angles(pgon_separation.pgon_mask(pgon, (mask & 3) == 2), centers[0])
    angles[:, l_hip] = coverage_angles(pgon_separation.pgon_mask(pgon, (mask & 3) == 3), centers[1])

    # Calculate surface areas
    areas = np.zeros((2, 2))

    # Right foss
    #selected_faces = (mask & 6)
    #masked_mesh = pgon.submesh([selected_faces], append=True)
    #areas[r_fossa] = masked_mesh.area

    # Left fossa
    #selected_faces = (mask & 7)
    #masked_mesh = pgon.submesh([selected_faces], append=True)
    #areas[l_fossa] = masked_mesh.area

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
    normals = pgon.face_normals[selected]
    summed = np.sum(normals, axis=0)
    unit_vector = summed / np.linalg.norm(summed)
    orient = np.zeros((2, 3))
    orient[0, :] = unit_vector

    selected = (mask & 3) == 3
    normals = pgon.face_normals[selected]
    summed = np.sum(normals, axis=0)
    unit_vector = summed / np.linalg.norm(summed)
    orient[1, :] = unit_vector

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
    result.update({'right_center': centers[0], 'right_radius': radii[0], 'right_total_area': areas.flat[r_hip], 'right_fossa_area': areas.flat[r_fossa], 'right_orientation': orient[0], 'right_version': np.degrees(np.arctan2(orient[0, 0], -orient[0, 1]))})
    result.update({'right_tilt': np.degrees(np.arctan2(-orient[0, 2], -orient[0, 1])), 'right_total_supine_coverage': np.bincount(mask1, weights=angles[:, r_hip])[1:] / 45, 'right_fossa_supine_coverage': np.bincount(mask1, weights=angles[:, r_fossa])[1:] / 45})
    result.update({'right_total_tilt_coverage': np.bincount(mask2, weights=angles[:, r_hip])[1:] / 45, 'right_fossa_tilt_coverage': np.bincount(mask2, weights=angles[:, r_fossa])[1:] / 45})
    selected_faces = (mask & 3) == 2
    new_mesh = pgon_separation.pgon_mask(pgon, selected_faces)
    result.update({'right_volume': new_mesh.volume})

    # Create left result dictionary
    result.update({'left_center': centers[1], 'left_radius': radii[1], 'left_total_area': areas.flat[l_hip], 'left_fossa_area': areas.flat[l_fossa], 'left_orientation': orient[1], 'left_version': np.degrees(np.arctan2(orient[1, 0], orient[1, 1]))})
    result.update({'left_tilt': np.degrees(np.arctan2(-orient[1, 2], orient[1, 1])), 'left_total_supine_coverage': np.bincount(mask1, weights=angles[:, l_hip])[1:] / 45, 'left_fossa_supine_coverage': np.bincount(mask1, weights=angles[:, l_fossa])[1:] / 45})
    result.update({'left_total_tilt_coverage': np.bincount(mask2, weights=angles[:, l_hip])[1:] / 45, 'left_fossa_tilt_coverage': np.bincount(mask2, weights=angles[:, l_fossa])[1:] / 45})
    selected_faces = (mask & 3) == 3
    new_mesh = pgon_separation.pgon_mask(pgon, selected_faces)
    result.update({'left_volume': new_mesh.volume})

    return result


def coverage_angles(pgon, center):
    # Flip and translate right-side
    if center[1] < 0:
        pgon = pgon.copy().apply_transform(reflection.reflection(np.array([0, 1, 0])) @ translation.translate(-center))
    # Translate only left-side
    else:
        pgon = pgon.apply_transform(translation.translate(-center))

    # Get open edges
    #edge = pgon_upe.unpaired_edges_pgon(pgon)
    a, b, c, edge = test_unpaired_edges.find_unpaired_edges(pgon)

    # Create sampling vector
    th = np.arange(0, 540) * np.pi / 540
    coefs = np.zeros(th.shape)

    # Create normals
    norms = np.column_stack((np.cos(th), coefs, -np.sin(th)))

    # Locate sample points
    points, _, in_mask = ttp.compute_contours_with_trimesh(edge, norms, coefs)
    points['faces'] = points['faces'][:, 0]
    points = points['vertices'][points['faces'], :]
    points[in_mask == 1, 0] = 0

    # Get angles about y-axis
    around = np.arctan2(points[:, 0], points[:, 2])
    around[around < 0] += 2 * np.pi

    # Get coverage angles
    signs = 2 * (around < np.pi) - 1
    result = np.arctan2(signs * np.linalg.norm(points[:, [0, 2]], axis=1), -points[:, 1])

    # Combine coverage angles
    pos = np.full(540, -np.inf)
    neg = np.full(540, np.inf)

    np.maximum.at(pos, in_mask, result)
    np.minimum.at(neg, in_mask, result)

    combined = np.concatenate([pos, -neg]).reshape(3, -1)
    result = np.mean(combined, axis=0) * 180 / np.pi

    return result