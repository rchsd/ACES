import trimesh
import numpy as np

# Function to compute volume-weighted centroid with centering and offset
def volume_centroid(mesh):
    # Step 1: Compute bounding box center as offset
    offset = mesh.bounding_box.centroid

    # Step 2: Center the mesh vertices by subtracting the offset
    centered_vertices = mesh.vertices - offset

    # Step 3: Create a new mesh with centered vertices
    centered_mesh = trimesh.Trimesh(vertices=centered_vertices, faces=mesh.faces, process=False)

    # Step 4: Compute volume-weighted centroid of the centered mesh
    centered_centroid = centered_mesh.center_mass

    # Step 5: Translate the centroid back to original location using offset
    final_centroid = centered_centroid + offset

    return final_centroid

# Example usage with a sample mesh
# Replace this with your actual mesh loading
#mesh = trimesh.load('c:\\MATLAB\\new_mesh.stl')

# Compute centroid using the nuanced method
#centroid = volume_centroid(mesh)

# Print the result
#print("Volume-weighted centroid with offset applied:", mesh.vertices.shape, mesh.faces.shape)