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

    # Divide into quadrants
    _, lp = mesh_analysis.find_centroid(left_pelvis)
    _, rp = mesh_analysis.find_centroid(right_pelvis)
    left = r.apply_transform(lp, tform)
    #dot_prod = np.dot(r.reflection_simpl([0, 1, 0]), tform)
    dot_prod = np.dot(r.reflection_simpl([0, 1, 0]), tform)
    right = r.apply_transform(rp, dot_prod)
    temp = mp.pgon_merge(left, right)
    temp2, i1, _ = split_mesh.pgon_split(temp, [1, 0, 0], 0)
    #i1 = np.array(i1)
    temp3, i2, i1i2 = split_mesh.pgon_split(temp2, [0, 0, 1], 0)
    #i2 = np.array(i2)
    #i1i2 = np.array(i1i2)
    #i2[i1i2] = i1[i1i2] * 2 + i2[i1i2] + 1
    i2 = (i1[i1i2].astype(int) * 2 + i2.astype(int) + 1)


    temp4 = pgonsep.create_meshes_with_quadrants(temp3, i2)

    quads = mesh_analysis.find_surface_area_centroid(temp4)

    # Divide into quadrants
    '''
    temp = pgonmerge(tform * lp, Reflection([0, 1, 0]) * tform * rp)
    [temp, i1] = pgonsplit_(temp, [1, 0, 0], 0)
    [temp, i2, i1i2] = pgonsplit_(temp, [0, 0, 1], 0)
    i2 = i1(i1i2) * 2 + i2 + 1; reidx = [3, 2, 4, 1]
    temp = pgonsep(temp, reidx(i2))
    quads = pgonacent(temp);=
    
    #Take absolute value
    if mean(quads(:, 2)) < 0
        temp = Reflection([0, 1, 0]) * temp
    end
    quads = abs(quads)'''

    #return np.round(temp.center_mass)
    #temp_copy.export('temp_copy.stl')
    #tform2 = fsb.find_smallest_box(combined_mesh.faces, combined_mesh.vertices, 1, [0, 1, 0])
    return quads

test_file_path = 'C:\\Users\\bbeasley\\Documents\\Python Projects\\Matlab-GUI\\Tests\\Schmitz\\'
combined_pelvis = test_file_path + '\\1_Combined_Pelvis.stl'
left_pelvis = test_file_path + 'l hip 1.stl'
right_pelvis = test_file_path + 'r hip 1.stl'
print(align_pelvis(combined_pelvis, left_pelvis, right_pelvis))
#print(mesh_separation.find_centroid())
#print(mesh_separation.analyze_mesh('Schmitz/r hip 1.stl')[1])
#align_pelvis('Schmitz/1_Combined_Pelvis.stl', 'Schmitz\parts_1.stl', 'Schmitz\parts_2.stl')
#print(mesh_separation.find_centroid('Schmitz\parts_1.stl'))
#align_pelvis('Schmitz/1_Combined_Pelvis.stl', 'Schmitz\l hip 1.stl', 'Schmitz\\r hip 1.stl')