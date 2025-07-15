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

# 0 = volume, 1 = centroid, 2 = faces, 3 = vertices, 4 = mesh_copy

def align_pelvis(combined_pelvis, left_pelvis, right_pelvis):

    center, combined_mesh = mesh_analysis.find_centroid(combined_pelvis)
    tform = translation.translate(-center)

    # gets ref to volumes of temp meshes
    temp_mesh_left = mesh_analysis.analyze_mesh(left_pelvis, tform)
    temp_mesh_right = mesh_analysis.analyze_mesh(right_pelvis, tform)
    
    rp_center = mp.merge_parts_with_inv_transform(temp_mesh_right[2], temp_mesh_right[3], tform)
    lp_center = mp.merge_parts_with_inv_transform(temp_mesh_left[2], temp_mesh_left[3], tform)
    rl = np.subtract(lp_center, rp_center)
    tform2 = alignment.align(rl, [0, 1, 0])
    tform = tform2 @ tform

    # find smallest box code
    tform2 = fsb.find_smallest_box(tform, combined_mesh.faces, combined_mesh.vertices, 0, [0, 1, 0])
    tform = tform2 @ tform

    tform2 = fsb.find_smallest_box(tform, combined_mesh.faces, combined_mesh.vertices, 1, [0, 1, 0])
    tform = tform2 @ tform

    bounding_box = fsb.find_bounding_box(combined_mesh.faces, combined_mesh.vertices, tform)
    difference = np.array(np.diff(bounding_box, axis=0))

    # Smallest dimension should be x-dimension
    if np.dot([-1, 0, 1], difference.T) < 0:
        tform = np.dot(fsb.rotate_mesh(np.pi/2, [0, 1, 0]), tform)

    # divide into quadrants
    _, lp = mesh_analysis.find_centroid(left_pelvis)
    _, rp = mesh_analysis.find_centroid(right_pelvis)
    left = r.apply_transform(lp, tform)
    dot_prod = np.dot(r.reflection_simple([0, 1, 0]), tform)
    right = r.apply_transform(rp, dot_prod)
    temp = mp.pgon_merge(left, right)
    temp2, i1, _ = split_mesh.pgon_split(temp, [1, 0, 0], 0)
    temp3, i2, i1i2 = split_mesh.pgon_split(temp2, [0, 0, 1], 0)
    i2 = (i1[i1i2].astype(int) * 2 + i2.astype(int) + 1)
    temp4 = pgonsep.create_meshes_with_quadrants(temp3, i2)
    quads = mesh_analysis.find_surface_area_centroid(temp4)

    # take absolute value
    quads = np.array(quads)
    if np.mean(quads[:, 1]) < 0:
        temp4 = r.reflection_simple([0, 1, 0]) @ temp4
    quads = np.abs(quads)

    boxes = []
    for i in range(len(temp4)):
        box = fsb.find_bounding_box(temp4[i].faces, temp4[i].vertices, None)
        boxes.append(box)
    # Stack and reshape to match MATLAB's 2x3x4 format
    aabb = np.stack(boxes, axis=2)

    # find pubic symphysis
    temp = temp4
    s = [grp.sample_points_on_mesh(t, 500)[:, 1] for t in temp[:4]]
    s1, s2, s3, s4 = s
    cutoff = aabb[0, 1, 1] * 0.90 + aabb[1, 1, 1] * 0.10
    
    s = [np.sum(s1 < cutoff), np.sum(s2 < cutoff), np.sum(s3 < cutoff), np.sum(s4 < cutoff)]

    return s

test_file_path = 'C:\\Users\\bbeasley\\Documents\\Python Projects\\Matlab-GUI\\Tests\\Schmitz\\'
combined_pelvis = test_file_path + '\\1_Combined_Pelvis.stl'
left_pelvis = test_file_path + 'l hip 1.stl'
right_pelvis = test_file_path + 'r hip 1.stl'
s = align_pelvis(combined_pelvis, left_pelvis, right_pelvis)
print(s)
#print(mesh_separation.find_centroid())
#print(mesh_separation.analyze_mesh('Schmitz/r hip 1.stl')[1])
#align_pelvis('Schmitz/1_Combined_Pelvis.stl', 'Schmitz\parts_1.stl', 'Schmitz\parts_2.stl')
#print(mesh_separation.find_centroid('Schmitz\parts_1.stl'))
#align_pelvis('Schmitz/1_Combined_Pelvis.stl', 'Schmitz\l hip 1.stl', 'Schmitz\\r hip 1.stl')