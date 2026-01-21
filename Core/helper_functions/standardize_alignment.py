import numpy as np
import trimesh
from helper_functions import merge_parts, translation, find_volume_center, mesh_analysis, alignment, unitize
from helper_functions import find_smallest_box, split_mesh, pgon_separation, reflection, generate_random_points
from helper_functions import find_plane_contours, pgonsep_by_plane_index, find_slice_bounding_box, pgon_parts, find_barys_and_norms

def align_pelvis(pelvis_path):
    combined_mesh = trimesh.load(pelvis_path)
    tform = translation.translate(-find_volume_center.volume_centroid(combined_mesh))

    # Separate into right and left
    parts = combined_mesh.copy().apply_transform(tform).split(only_watertight=False)
    # Abs value used just in case mesh isn't watertight
    volumes = np.array([abs(p.volume) for p in parts])
    # Np.argsort sorts in ascending order by default, so negative volumes does the reverese
    ii = np.argsort(-volumes)
    idx_1, idx_2 = ii[0], ii[1]
    cent_1 = parts[idx_1].center_mass
    cent_2 = parts[idx_2].center_mass
    v = cent_2 - cent_1
    rl = unitize.unitize(v)
    # Cent_2 comes first in order to preserve original index order of parts
    projections = np.array([cent_2 @ rl, cent_1 @ rl])
    mask = projections > 0

    tform_inv = np.linalg.inv(tform)
    right_parts = [parts[i] for i, m in enumerate(mask) if m]
    left_parts  = [parts[i] for i, m in enumerate(mask) if not m]

    rp = trimesh.util.concatenate(right_parts) if right_parts else None
    lp = trimesh.util.concatenate(left_parts)  if left_parts else None
    rp.apply_transform(tform_inv)
    lp.apply_transform(tform_inv)

    # Update transform
    rl = lp.center_mass - rp.center_mass
    tform2 = alignment.align(np.dot(rl, np.sign(rl[0])), [0, 1, 0])
    tform = tform2 @ tform

    # find smallest box code
    tform2 = find_smallest_box.find_smallest_box(tform, combined_mesh.faces, combined_mesh.vertices, 0, [0, 1, 0])
    tform = tform2 @ tform

    tform2 = find_smallest_box.find_smallest_box(tform, combined_mesh.faces, combined_mesh.vertices, 1, [0, 1, 0])
    tform = tform2 @ tform

    bounding_box = find_smallest_box.find_bounding_box(combined_mesh, tform)
    difference = np.array(np.diff(bounding_box, axis=0))

    # Smallest dimension should be x-dimension
    if np.dot([-1, 0, 1], difference.T) < 0:
        tform = np.dot(find_smallest_box.calculate_rotation_transform(np.pi/2, [0, 1, 0]), tform)
        
    left = lp
    right = rp
    temp = merge_parts.pgon_merge(left.copy().apply_transform(tform), right.copy().apply_transform(np.dot(reflection.reflection_simple([0, 1, 0]), tform)))
    temp2, i1, _ = split_mesh.pgon_split(temp, [1, 0, 0], 0)
    temp3, i2, i1i2 = split_mesh.pgon_split(temp2, [0, 0, 1], 0)
    i2 = (i1[i1i2].astype(int) * 2 + i2.astype(int) + 1)
    temp4 = pgon_separation.create_meshes_with_quadrants(temp3, i2)
    quads = mesh_analysis.find_surface_area_centroid(temp4)

    # take absolute value
    quads = np.array(quads)
    if np.mean(quads[:, 1]) < 0:
        for mesh in temp4:
            mesh.apply_transform(reflection.reflection_simple([0, 1, 0]))
    quads = np.abs(quads)

    boxes = []
    for i in range(len(temp4)):
        box = find_smallest_box.find_bounding_box(temp4[i])
        boxes.append(box)
    # stack and reshape to match MATLAB's 2x3x4 format
    aabb = np.stack(boxes, axis=2)

    # find pubic symphysis
    temp = temp4
    s = [generate_random_points.sample_points_on_mesh(t, 500)[:, 1] for t in temp[:4]]
    s1, s2, s3, s4 = s
    cutoff = aabb[0, 1, 1] * 0.90 + aabb[1, 1, 1] * 0.10
    s = [np.sum(s1 < cutoff), np.sum(s2 < cutoff), np.sum(s3 < cutoff), np.sum(s4 < cutoff)]

    # perform quadrant voting
    im = s.index(max(s))  
    rotate_about = [int(im == 0), int(im == 1), int(im == 2)]
    im = np.argmax(quads[:, 1])

    rotate_about[0] = rotate_about[0] + (im == 3)
    rotate_about[1] = rotate_about[1] + (im == 2)
    rotate_about[2] = rotate_about[2] + (im == 1)

    im = np.argmax(quads[:, 2])

    rotate_about[0] = rotate_about[0] + (im == 1)
    rotate_about[1] = rotate_about[1] + (im == 0)
    rotate_about[2] = rotate_about[2] + (im == 3)

    # perform series of checks to see if pelvis is upside down
    aabb = find_smallest_box.find_bounding_box(combined_mesh.copy(), tform)
    steps = np.arange(4, 100, 4) / 100  
    z_range = aabb[1, 2] - aabb[0, 2]   
    sample = steps * z_range + aabb[0, 2]
    # makes a copy instead of transforming original mesh
    transformed_mesh = combined_mesh.copy().apply_transform(tform)
    ctour, _, ii = find_plane_contours.compute_contours_with_trimesh(transformed_mesh, np.array([0, 0, 1]), sample)
    plane_slices = pgonsep_by_plane_index.separate_by_plane(ctour, ii)

    # bounds of top slices cover more area
    aabb = find_slice_bounding_box.compute_aabb_slices(plane_slices)
    aabb_slices = np.zeros((2, 3, 24))
    for i in range(24):
        aabb_slices[0, :, i] = aabb[i]['min']
        aabb_slices[1, :, i] = aabb[i]['max']
    area = np.prod(np.squeeze(np.diff(aabb_slices[:, 0:2, :], axis=0)), axis=0)
    upside_down = float(np.dot(sample, area) / np.sum(area) < 0)        

    # bottom slices have more distinct contours
    nctours = np.zeros(len(plane_slices))
    for i, (plane_idx, poly) in enumerate(plane_slices.items()):
        parts = pgon_parts.find_parts(poly)
        nctours[i] = max(parts)
    upside_down = upside_down + float(np.dot(sample, nctours) / np.sum(nctours) > 0)
    
    # normals form bottom slices are more evenly distributed
    transformed_mesh = combined_mesh.copy()
    barys, norms, _, _ = find_barys_and_norms.find_barys_norms(transformed_mesh)
    n1 = np.sum(np.abs(norms[barys[:, 2] > 0]), axis=0)
    n2 = np.sum(np.abs(norms[barys[:, 2] < 0]), axis=0)
    # calculate means and check for validity
    mean_n1 = np.mean(n1[:2])
    mean_n2 = np.mean(n2[:2])
    condition = False
    if mean_n1 != 0 and not np.isnan(mean_n1) and mean_n2 != 0 and not np.isnan(mean_n2):
        condition = (n1[2] / mean_n1) > (n2[2] / mean_n2)
        upside_down += 2 * int(condition)
    
    # perform clear rotations
    rotate_about = np.array(rotate_about)
    if np.any(rotate_about >= 2) and (upside_down > 2) != (rotate_about[2] >= 2):
        tform = np.dot(find_smallest_box.rotate_mesh(np.pi, rotate_about / np.linalg.norm(rotate_about)), tform)
    elif np.all(rotate_about == 0) and upside_down <= 2:
        pass  # No operation, equivalent to the empty elseif block in MATLAB
    else:
        print('Warning: Pelvis orientation unclear, using best guess.')
        if np.sum(rotate_about) == 1:
            tform = np.dot(find_smallest_box.rotate_mesh(np.pi, rotate_about), tform)
        elif np.sum(rotate_about) == 2:
            if rotate_about[2] != 0:
                if upside_down > 2:
                    rotate_about[2] = 0
                    tform = np.dot(find_smallest_box.rotate_mesh(np.pi, rotate_about), tform)
                else:
                    rotate_about[:2] = 0
                    tform = np.dot(find_smallest_box.rotate_mesh(np.pi, rotate_about), tform)
            else:
                tform = np.dot(find_smallest_box.rotate_mesh(np.pi, np.array([1, 0, 0])), tform)
        elif np.sum(rotate_about) == 3:
            if upside_down > 2:
                tform = np.dot(find_smallest_box.rotate_mesh(np.pi, np.array([1, 0, 0])), tform)
            else:
                tform = np.dot(find_smallest_box.rotate_mesh(np.pi, np.array([0, 0, 1])), tform)
    
    # get correct right and left sections 
    left = left.copy().apply_transform(tform)
    right = right.copy().apply_transform(tform)

    if np.dot(find_volume_center.volume_centroid(left), (0, 1, 0)) < np.dot(find_volume_center.volume_centroid(right), (0, 1, 0)):
        temp = left
        left = right
        right = temp

    # loop until reasonably aligned
    for j in range(100):
        # initialize max_angle
        max_angle = 0

        # remove axial plane rotation
        for i in range(100):
            center1 = np.mean(find_smallest_box.find_bounding_box(left), axis=0)
            center2 = np.mean(find_smallest_box.find_bounding_box(right), axis=0)
            top1 = left.vertices[left.vertices[:, 2] > center1[2]]
            top2 = right.vertices[right.vertices[:, 2] > center2[2]]
            im1 = np.argmax(top1[:, 0])
            lx = top1[im1]
            im2 = np.argmax(top2[:, 0])
            rx = top2[im2]
            angle = np.arctan2(lx[0] - rx[0], lx[1] - rx[1])
            if abs(angle) > max_angle:
                max_angle = abs(angle)
            if abs(angle) < np.pi / 18000:
                break
            tform2 = find_smallest_box.calculate_rotation_transform(angle, (0, 0, 1))
            left.apply_transform(tform2)
            right.apply_transform(tform2)
            tform = tform2 @ tform
        
        # remove coronal plane rotation
        for i in range(100):
            # find the vertex with the maximum z-coordinate in lp
            im1 = np.argmax(left.vertices[:, 2])
            lx = left.vertices[im1]
            #fFind the vertex with the maximum z-coordinate in rp
            im2 = np.argmax(right.vertices[:, 2])
            rx = right.vertices[im2]
            # calculate the angle using atan2
            angle = np.arctan2(lx[2] - rx[2], lx[1] - rx[1])
            # update max_angle if necessary
            if abs(angle) > max_angle:
                max_angle = abs(angle)
            # break if angle is below threshold
            if abs(angle) < np.pi / 18000:
                break
            # apply rotation
            tform2 = find_smallest_box.calculate_rotation_transform(-angle, (1, 0, 0))
            left.apply_transform(tform2)
            right.apply_transform(tform2)
            tform = tform2 @ tform

        # remove sagittal plane rotation
        for i in range(100):
            # calculate centers using your pgonaabb function or equivalent logic
            center1 = np.mean(find_smallest_box.find_bounding_box(left), axis=0)
            center2 = np.mean(find_smallest_box.find_bounding_box(right), axis=0)
            
            # select vertices above the calculated center
            top = np.vstack([
                left.vertices[left.vertices[:, 2] > center1[2]],
                right.vertices[right.vertices[:, 2] > center2[2]]
            ])
            
            # select vertices whose z-coordinate is at least 40 units below the center
            bot = np.vstack([
                left.vertices[left.vertices[:, 2] + 40 < center1[2]],
                right.vertices[right.vertices[:, 2] + 40 < center2[2]]
            ])
            
            # find the vertex with the maximum x-coordinate in top
            im_top = np.argmax(top[:, 0])
            lx = top[im_top]
            # find the vertex with the maximum x-coordinate in bot
            im_bot = np.argmax(bot[:, 0])
            rx = bot[im_bot]
            # calculate the angle using atan2
            angle = np.arctan2(lx[0] - rx[0], lx[2] - rx[2])
            # Update max_angle if necessary
            if abs(angle) > max_angle:
                max_angle = abs(angle)
            # Break if angle is below threshold
            if abs(angle) < np.pi / 18000:
                break
            # Apply rotation
            tform2 = find_smallest_box.calculate_rotation_transform(-angle, (0, 1, 0))
            left.apply_transform(tform2)
            right.apply_transform(tform2)
            tform = tform2 @ tform
        # exit when max angle is small enough
        if max_angle < np.pi / 18000: 
            break 
    # finalize
    mesh = merge_parts.pgon_merge(left, right)
    tform = np.dot(translation.translate(-find_volume_center.volume_centroid(mesh)), tform)

    print('Pelvis is now aligned, continuing analysis.')

    return tform, combined_mesh.copy()