import numpy as np
import trimesh

def analyze_mesh(mesh_file_path, transform = []):
    mesh = trimesh.load(mesh_file_path)
    mesh_copy = mesh.copy()

    if len(transform) != 0:
        mesh_copy.apply_transform(transform)
    
    centroid_of_volume = mesh_copy.center_mass

    return mesh_copy.volume, centroid_of_volume, mesh_copy.faces, mesh_copy.vertices, mesh_copy


def find_centroid(mesh_file_path):
    mesh = trimesh.load_mesh(mesh_file_path)

    return mesh.center_mass, mesh

def find_surface_area_centroid(mesh_list):
    centroids = []
    for mesh in mesh_list:
        centroids.append(mesh.centroid)
    return centroids

def create_new_mesh(vertices, faces):
    return trimesh.Trimesh(vertices=vertices, faces=faces)

def load_mesh(file_path):
    mesh = trimesh.load(file_path)

    return mesh

# for testing
'''
left_mesh = 'Schmitz/l hip 1.stl'
right_mesh = 'Schmitz/r hip 1.stl'
transform = np.array([
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]])
offset = np.array([-24.7660551658072, 44.9501128623997, 43.1640541421168])

#print(apply_transform(right_mesh, transform, offset))
#volume = apply_transform(right_mesh, transform, offset)
#sorted_descending = sorted(volume, reverse=True)
#print(volume)
#print(sorted_descending)
#volume_1, center_1, faces, vertices = apply_transform(left_mesh, transform, offset)
#print(center_1)
#volume_2 = apply_transform(right_mesh, transform, offset)
#new_matrix = volume_1, volume_2
#sorted_descending = sorted(new_matrix, reverse=True)
#print(sorted_descending)'''