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