import trimesh
import numpy as np

def separate_parts(parts, mask, transform=[]):
    selected_faces = []
    selected_vertices = []
    mask = np.array(mask)
    
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

def pgon_merge(left = None, right = None, left_file_path = None, right_file_path = None):
    combined_mesh = None
    # assumes that left and right pelvis are already trimesh objects
    # if they aren't, objects will be created before combining meshes
    if left is not None:
        combined_mesh = trimesh.util.concatenate([left, right])
    else:
        left = trimesh.load(left_file_path)
        right = trimesh.load(right_file_path)
        combined_mesh = trimesh.util.concatenate([left, right])

    return combined_mesh

def merge_stl_files_or_objects(stl_file_path1=None, stl_file_path2=None, mesh1=None, mesh2=None):
    """
    Merges two STL files or trimesh objects into a single polygon using trimesh.
    
    Parameters:
        stl_file_path1 (str, optional): File path to the first STL file.
        stl_file_path2 (str, optional): File path to the second STL file.
        mesh1 (trimesh.Trimesh, optional): First trimesh object.
        mesh2 (trimesh.Trimesh, optional): Second trimesh object.
    
    Returns:
        tuple: Merged polygon, face indices, vertex indices
    """
    # Load the STL files into trimesh objects if not provided
    if mesh1 is None and stl_file_path1 is not None:
        mesh1 = trimesh.load(stl_file_path1)
    if mesh2 is None and stl_file_path2 is not None:
        mesh2 = trimesh.load(stl_file_path2)
    
    # Ensure that we have valid meshes to work with
    if mesh1 is None or mesh2 is None:
        raise ValueError("Both mesh1 and mesh2 must be provided either as file paths or trimesh objects.")

    # List of polygons to merge
    polygons = [mesh1, mesh2]

    # Initialize lists to store merged vertices and faces
    merged_vertices = []
    merged_faces = []
    
    # Lists to track the source of each face and vertex
    face_sources = []
    vertex_sources = []

    # Offset for vertex indices
    offset = 0

    # Iterate over each polygon
    for input_index, polygon in enumerate(polygons):
        # Add vertices and track their source
        merged_vertices.extend(polygon.vertices)
        vertex_sources.extend([input_index] * len(polygon.vertices))

        # Add faces with updated indices and track their source
        for face in polygon.faces:
            merged_faces.append(face + offset)
            face_sources.append(input_index)

        # Update the offset for the next polygon's vertices
        offset += len(polygon.vertices)

    # Create the merged polygon
    merged_polygon = trimesh.Trimesh(vertices=merged_vertices, faces=merged_faces)

    return merged_polygon, face_sources, vertex_sources

def merge_and_transform(meshes, mask, transform):
    # Filter meshes based on the mask
    submeshes = [mesh for mesh, m in zip(meshes, mask) if m]
    
    # Merge all submeshes into one Trimesh object
    merged_vertices = np.concatenate([mesh.vertices for mesh in submeshes])
    merged_faces = np.concatenate([mesh.faces for mesh in submeshes])
    
    # Create a merged Trimesh object
    merged_mesh = trimesh.Trimesh(vertices=merged_vertices, faces=merged_faces)
    
    # Compute the inverse of the transformation matrix
    tform_inv = np.linalg.inv(transform)
    
    # Apply the inverse transformation to the merged mesh
    merged_mesh.apply_transform(tform_inv)
    
    return merged_mesh