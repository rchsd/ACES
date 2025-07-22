import mesh_analysis
import translation
import numpy as np
import merge_parts as mp
import pgon_separation as pgonsep
import alignment
import find_smallest_box as fsb
import reflection as r
import unitize
import split_mesh
import generate_random_points as grp
import test_ctour
import test_pgonsep_by_plane_index
import test_aabb
import pgon_parts
import find_barys_and_norms

# 0 = volume, 1 = centroid, 2 = faces, 3 = vertices, 4 = mesh_copy

def align_pelvis(left_pelvis_path, right_pelvis_path):
    combined_mesh = mp.pgon_merge(None, None, left_pelvis_path, right_pelvis_path)
    tform = translation.translate(-combined_mesh.center_mass)

    left = mesh_analysis.load_mesh(left_pelvis_path)
    right = mesh_analysis.load_mesh(right_pelvis_path)
    rl = np.subtract(left.center_mass, right.center_mass)
    tform2 = alignment.align(np.dot(rl, np.sign(rl[0])), [0, 1, 0])
    tform = tform2 @ tform

    # find smallest box code
    tform2 = fsb.find_smallest_box(tform, combined_mesh.faces, combined_mesh.vertices, 0, [0, 1, 0])
    tform = tform2 @ tform

    tform2 = fsb.find_smallest_box(tform, combined_mesh.faces, combined_mesh.vertices, 1, [0, 1, 0])
    tform = tform2 @ tform

    bounding_box = fsb.find_bounding_box(combined_mesh, tform)
    difference = np.array(np.diff(bounding_box, axis=0))

    # Smallest dimension should be x-dimension
    if np.dot([-1, 0, 1], difference.T) < 0:
        tform = np.dot(fsb.rotate_mesh(np.pi/2, [0, 1, 0]), tform)

    temp = mp.pgon_merge(left.copy().apply_transform(tform), right.copy().apply_transform(np.dot(r.reflection_simple([0, 1, 0]), tform)))
    temp2, i1, _ = split_mesh.pgon_split(temp, [1, 0, 0], 0)
    temp3, i2, i1i2 = split_mesh.pgon_split(temp2, [0, 0, 1], 0)
    i2 = (i1[i1i2].astype(int) * 2 + i2.astype(int) + 1)
    temp4 = pgonsep.create_meshes_with_quadrants(temp3, i2)
    quads = mesh_analysis.find_surface_area_centroid(temp4)

    # take absolute value
    quads = np.array(quads)
    if np.mean(quads[:, 1]) < 0:
        for mesh in temp4:
            mesh.apply_transform(r.reflection_simple([0, 1, 0]))
    quads = np.abs(quads)

    boxes = []
    for i in range(len(temp4)):
        box = fsb.find_bounding_box(temp4[i])
        boxes.append(box)
    # stack and reshape to match MATLAB's 2x3x4 format
    aabb = np.stack(boxes, axis=2)

    # find pubic symphysis
    temp = temp4
    s = [grp.sample_points_on_mesh(t, 500)[:, 1] for t in temp[:4]]
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
    aabb = fsb.find_bounding_box(combined_mesh, tform)
    steps = np.arange(4, 100, 4) / 100  
    z_range = aabb[1, 2] - aabb[0, 2]   
    sample = steps * z_range + aabb[0, 2]
    # makes a copy instead of transforming original mesh
    transformed_mesh = combined_mesh.copy().apply_transform(tform)
    ctour, _, ii = test_ctour.main_compute_all_contours(transformed_mesh, (0, 0, 1), sample)
    plane_slices = test_pgonsep_by_plane_index.separate_by_plane(ctour, ii)

    # bounds of top slices cover more area
    aabb = test_aabb.compute_aabb_slices(plane_slices)
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
    print(tform)
    transformed_mesh = combined_mesh.copy()
    barys, norms, _ = find_barys_and_norms.find_barys_norms(transformed_mesh)
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
        tform = np.dot(fsb.rotate_mesh(np.pi, rotate_about / np.linalg.norm(rotate_about)), tform)
    elif np.all(rotate_about == 0) and upside_down <= 2:
        pass  # No operation, equivalent to the empty elseif block in MATLAB
    else:
        print('Warning: Pelvis orientation unclear, using best guess.')
        if np.sum(rotate_about) == 1:
            tform = np.dot(fsb.rotate_mesh(np.pi, rotate_about), tform)
        elif np.sum(rotate_about) == 2:
            if rotate_about[2] != 0:
                if upside_down > 2:
                    rotate_about[2] = 0
                    tform = np.dot(fsb.rotate_mesh(np.pi, rotate_about), tform)
                else:
                    rotate_about[:2] = 0
                    tform = np.dot(fsb.rotate_mesh(np.pi, rotate_about), tform)
            else:
                tform = np.dot(fsb.rotate_mesh(np.pi, np.array([1, 0, 0])), tform)
        elif np.sum(rotate_about) == 3:
            if upside_down > 2:
                tform = np.dot(fsb.rotate_mesh(np.pi, np.array([1, 0, 0])), tform)
            else:
                tform = np.dot(fsb.rotate_mesh(np.pi, np.array([0, 0, 1])), tform)
    
    # get correct right and left sections 
    left = left.copy().apply_transform(tform)
    right = right.copy().apply_transform(tform)

    if np.dot(left.center_mass, (0, 1, 0)) < np.dot(right.center_mass, (0, 1, 0)):
        temp = left
        left = right
        right = temp

    # loop until reasonably aligned
    for j in range(100):
        # initialize max_angle
        max_angle = 0

        # remove axial plane rotation
        for i in range(100):
            center1 = np.mean(fsb.find_bounding_box(left), axis=0)
            center2 = np.mean(fsb.find_bounding_box(right), axis=0)
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
            tform2 = fsb.calculate_rotation_transform(angle, (0, 0, 1))
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
            tform2 = fsb.calculate_rotation_transform(-angle, (1, 0, 0))
            left.apply_transform(tform2)
            right.apply_transform(tform2)
            tform = tform2 @ tform

        # remove sagittal plane rotation
        for i in range(100):
            # calculate centers using your pgonaabb function or equivalent logic
            center1 = np.mean(fsb.find_bounding_box(left), axis=0)
            center2 = np.mean(fsb.find_bounding_box(right), axis=0)
            
            # select vertices above the calculated center
            top = np.vstack([
                left.vertices[left.vertices[:, 2] > center1[2]],
                right.vertices[right.vertices[:, 2] > center2[2]]
            ])
            
            # select vertices below the calculated center minus 40
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
            tform2 = fsb.calculate_rotation_transform(-angle, (0, 1, 0))
            left.apply_transform(tform2)
            right.apply_transform(tform2)
            tform = tform2 @ tform
        # exit when max angle is small enough
        if max_angle < np.pi / 18000: 
            break 
    # finalize
    mesh = mp.pgon_merge(left, right)
    tform = np.dot(translation.translate(-mesh.center_mass), tform)

    return tform

test_file_path = 'C:\\Users\\bbeasley\\Documents\\Python Projects\\Matlab-GUI\\Tests\\Schmitz\\'
combined_pelvis = test_file_path + '\\1_Combined_Pelvis.stl'
left_pelvis = test_file_path + 'l hip 1.stl'
right_pelvis = test_file_path + 'r hip 1.stl'
s = align_pelvis(combined_pelvis, left_pelvis, right_pelvis)
print(s)