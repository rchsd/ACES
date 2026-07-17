import scipy.io as sio
import numpy as np
import trimesh
from collections import defaultdict

def separate(faces, mask):
    """
    Groups faces by their corresponding mask values and returns them in sorted order of group ID.
    """
    groups = defaultdict(list)
    for face, group_id in zip(faces, mask):
        groups[int(group_id)].append(face)
    return [groups[key] for key in sorted(groups.keys())]

# creates multiple meshes
def create_submeshes_with_mask(mesh=None, mask=None, faces=None, vertices=None):
    """
    Separates a mesh into submeshes based on a mask applied to the faces.
    Accepts either a trimesh object or raw faces and vertices arrays.
    """
    # Handle structured or nested arrays
    if isinstance(faces, np.ndarray) and faces.ndim == 2 and faces.shape[1] == 1:
        faces = np.vstack(faces[:, 0])
    if isinstance(vertices, np.ndarray) and vertices.ndim == 2 and vertices.shape[1] == 1:
        vertices = np.vstack(vertices[:, 0])

    # If mesh is provided and faces/vertices are not, extract from mesh
    if mesh is not None and (faces is None or vertices is None):
        faces = mesh.faces
        vertices = mesh.vertices

    if len(faces) != len(mask):
        raise ValueError("Mask length must match number of faces.")

    separated_faces = separate(faces, mask)
    submeshes = []

    for group_faces in separated_faces:
        group_faces = np.array(group_faces)
        unique_indices = np.unique(group_faces)
        index_map = {old: new for new, old in enumerate(unique_indices)}

        new_faces = np.vectorize(index_map.get)(group_faces)
        new_vertices = vertices[unique_indices]

        # Handle 2D faces (edges) by padding to 3D for trimesh compatibility
        if new_faces.shape[1] == 2:
            padded_faces = np.pad(new_faces, ((0, 0), (0, 1)), mode='constant', constant_values=-1)
            submesh = trimesh.Trimesh(vertices=new_vertices, faces=padded_faces, process=False)
        else:
            submesh = trimesh.Trimesh(vertices=new_vertices, faces=new_faces, process=False)

        submeshes.append(submesh)

    return submeshes

# Separate mesh into submeshes based on reindexed labels
def create_meshes_with_quadrants(mesh, quadrants, isReindexed=True):
    py_quadrants = np.array(quadrants)
    if isReindexed:
        re_index = np.array([3, 2, 4, 1])
        labels = re_index[py_quadrants - 1]
    else:
        labels = py_quadrants
    submeshes = []
    for label in np.unique(labels):
        face_indices = np.where(labels == label)[0]
        submesh = mesh.submesh([face_indices], append=True)
        submeshes.append(submesh)
    return submeshes

def identify_parts(faces):
    parent = {}
    
    def find(v):
        if parent[v] != v:
            parent[v] = find(parent[v])  # Path compression
        return parent[v]
    
    def union(u, v):
        root_u = find(u)
        root_v = find(v)
        if root_u != root_v:
            parent[root_v] = root_u
    
    # Initialize parent for each vertex
    for face in faces:
        for v in face:
            if v not in parent:
                parent[v] = v
    
    # Union faces based on connectivity
    for face in faces:
        for i in range(1, len(face)):
            union(face[0], face[i])
    
    # Map each vertex to a group ID
    group_map = {}
    group_id = 0
    for v in parent:
        root = find(v)
        if root not in group_map:
            group_map[root] = group_id
            group_id += 1
    
    # Assign group IDs to faces
    face_groups = [group_map[find(face[0])] for face in faces]
    return face_groups

def create_submeshes(mesh, transform=None):
    if transform is not None and transform.any():
        mesh.apply_transform(transform)
    
    faces = mesh.faces
    vertices = mesh.vertices
    mask = identify_parts(faces)
    separated_faces = separate(faces, mask)
    submeshes = []
    
    for group in separated_faces:
        # Sort unique indices to ensure consistent ordering
        unique_indices = sorted(set(i for face in group for i in face))
        index_map = {old: new for new, old in enumerate(unique_indices)}
        
        # Create new faces using the index map
        new_faces = np.array([[index_map[i] for i in face] for face in group], dtype=np.uint32)
        new_vertices = vertices[unique_indices].astype(np.float64)
        
        # Create submesh with consistent indexing
        submesh = trimesh.Trimesh(vertices=new_vertices, faces=new_faces, process=False)
        submeshes.append(submesh)
    
    return submeshes

def pgon_mask(mesh, mask):
    # Ensure mask is a boolean array
    
    #new_mesh = trimesh.Trimesh(vertices=mesh.vertices, faces=mesh.faces) #test
    mask = np.asarray(mask, dtype=bool).flatten()

    # Verify that the mask length matches the number of faces
    if len(mask) != len(mesh.faces):#len(new_mesh.faces): #test
        raise ValueError("The length of the mask must match the number of faces in the mesh.")

    # Select faces based on the mask
    #selected_faces = new_mesh.faces[mask] #test
    selected_faces = mesh.faces[mask]
    # Check if any faces are selected
    if selected_faces.size == 0:
        print("No faces selected by the mask.")
        return None

    # Create a new mesh with the selected faces
    selected_mesh = trimesh.Trimesh(vertices=mesh.vertices, faces=selected_faces, process=False)
    selected_mesh.remove_unreferenced_vertices()

    return selected_mesh

# only creates one mesh, using indexes
def pgon_mask_index(mesh, mask_indices):
    """
    Extracts a subset of faces from a mesh using face indices,
    reindexes the vertices to include only those used, and returns
    both the new mesh and a mapping of original vertex indices used.
    
    Parameters:
        mesh (trimesh.Trimesh): The input mesh.
        mask_indices (array-like): Indices of faces to extract.
    
    Returns:
        selected_mesh (trimesh.Trimesh): The new mesh with reindexed vertices.
        original_vertex_indices (np.ndarray): Mapping of new vertices to original indices.
    """
    # Ensure mask is a flat array of valid indices
    mask_indices = np.asarray(mask_indices).flatten()
    
    # Validate face indices
    if np.any(mask_indices >= len(mesh.faces)) or np.any(mask_indices < 0):
        raise ValueError("Some face indices are out of bounds.")
    
    # Select faces
    selected_faces = mesh.faces[mask_indices]
    
    # Find unique vertex indices used by selected faces
    unique_vertex_indices, inverse_indices = np.unique(selected_faces, return_inverse=True)
    
    # Reindex faces to match new vertex array
    reindexed_faces = inverse_indices.reshape(selected_faces.shape)
    
    # Extract corresponding vertices
    new_vertices = mesh.vertices[unique_vertex_indices]
    
    # Create new mesh
    selected_mesh = trimesh.Trimesh(vertices=new_vertices, faces=reindexed_faces, process=False)
    
    # Return mesh and mapping of new vertex indices to original indices
    return selected_mesh, unique_vertex_indices