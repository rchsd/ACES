import trimesh
import numpy as np

def separate_parts(parts, mask, transform=[]):
    selected_faces = []
    selected_vertices = []
    
    if mask[0]:
        selected_faces.append(parts['faces'])
        selected_vertices.append(parts['vertices'])
    if mask[1]:
        selected_faces.append(parts['faces2'])
        selected_vertices.append(parts['vertices2'])
    
    merged_faces = np.concatenate(selected_faces)
    merged_vertices = np.concatenate(selected_vertices)

    merged_mesh = trimesh.Trimesh(vertices=merged_vertices, faces=merged_faces)
    tform_inv = np.linalg.inv(transform)
    pelvis = merged_mesh.apply_transform(tform_inv)
    
    return pelvis.center_mass

def merge_parts_with_inv_transform(faces, vertices, transform):
    merged_mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    tform_inv = np.linalg.inv(transform)
    pelvis = merged_mesh.apply_transform(tform_inv)
    
    return pelvis.center_mass

def pgon_merge(left, right):
    combined_mesh = trimesh.util.concatenate([left, right])

    return combined_mesh