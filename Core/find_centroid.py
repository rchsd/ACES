import trimesh
import numpy as np
import matlab.engine

def find_centroid(file_path):
    # Load the mesh
    mesh = trimesh.load_mesh(file_path)

    centroid_of_volume = np.round(mesh.center_mass, 4)

    print(centroid_of_volume)

    matrix = matlab.double(centroid_of_volume.tolist())

    return matrix

def find_centroid_of_surface_area(meshFilePath):
    # Load the mesh
    mesh = trimesh.load_mesh(meshFilePath) # Replace 'your_mesh.stl' with your mesh file

    # Calculate surface area
    surface_area = mesh.area

    # Calculate centroid
    centroid = surface_area.centroid
    print(centroid)
