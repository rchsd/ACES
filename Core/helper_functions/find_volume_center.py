import trimesh

# Function to compute volume-weighted centroid with centering and offset
def volume_centroid(mesh):
    # Compute bounding box center as offset
    offset = mesh.bounding_box.centroid

    # Center the mesh vertices by subtracting the offset
    centered_vertices = mesh.vertices - offset

    # Create a new mesh with centered vertices
    centered_mesh = trimesh.Trimesh(vertices=centered_vertices, faces=mesh.faces, process=False)

    # Compute volume-weighted centroid of the centered mesh
    centered_centroid = centered_mesh.center_mass

    # Translate the centroid back to original location using offset
    final_centroid = centered_centroid + offset

    return final_centroid
