import scipy.io as sio
import numpy as np
import trimesh
import polygon_separation_helper as psh
from collections import defaultdict

def separate(faces, mask):
    """
    Groups faces by their corresponding mask values and returns them in sorted order of group ID.
    """
    groups = defaultdict(list)
    for face, group_id in zip(faces, mask):
        groups[int(group_id)].append(face)
    return [groups[key] for key in sorted(groups.keys())]

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

# calls helper function
'''def create_submeshes(mesh, transform = None):
    psh.create_submeshes(mesh, transform)'''

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

def separate(faces, mask):
    groups = defaultdict(list)
    for face, group_id in zip(faces, mask):
        groups[group_id].append(face)
    return list(groups.values())

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

# Test with contour
'''mesh = trimesh.load("temp_mesh.stl")
reidx = [3, 2, 4, 1]  # Example mask
matlab_data_ii = sio.loadmat('ii.mat')
matlab_faces = sio.loadmat('faces.mat')
matlab_vertices = sio.loadmat('vertices.mat')
faces = matlab_faces.get('faces') - 1
vertices = matlab_vertices.get('vertices')
ii = matlab_data_ii.get('ii')
submeshes = create_submeshes_with_mask(mesh, ii, faces, vertices)'''

# Test with quadrants
'''mesh = trimesh.load('temp.stl')
matrix = sio.loadmat('quadrants.mat')
quadrants = matrix.get('i2')
print(quadrants)
submeshes = create_meshes_with_quadrants('temp.stl', quadrants)'''

# Test for splittin without mask
'''mesh = trimesh.load_mesh("1_Combined_Pelvis.stl")
submeshes = psh.create_submeshes(mesh)

for i, submesh in enumerate(submeshes):
    print(f"Submesh {i}:")
    faces = submesh.faces
    vertices = submesh.vertices

    print(f" Number of faces: {len(faces)}")
    print(f" Number of vertices: {len(vertices)}")'''