import trimesh
import numpy as np
from collections import defaultdict

def identify_parts(faces):
    parent = {}
    def find(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v
    
    def union(u, v):
        root_u = find(u)
        root_v = find(v)
        if root_u != root_v:
            parent[root_v] = root_u
    for face in faces:
        for v in face:
            if v not in parent:
                parent[v] = v
        for i in range(1, len(face)):
            union(face[0], face[i])
    group_map = {}
    group_id = 0
    for v in parent:
        root = find(v)
        if root not in group_map:
            group_map[root] = group_id
            group_id += 1
    face_groups = [group_map[find(face[0])] for face in faces]
    return face_groups

def separate(faces, mask):
    groups = defaultdict(list)
    for face, group_id in zip(faces, mask):
        groups[group_id].append(face)
    return list(groups.values())

def create_submeshes(mesh, transform = None):
    if transform.all() != None:
        # assuming mesh is a trimesh object
        mesh.apply_transform(transform)
    faces = mesh.faces
    vertices = mesh.vertices
    mask = identify_parts(faces)
    separated_faces = separate(faces, mask)
    submeshes = []
    for group in separated_faces:
        unique_indices = sorted(set(i for face in group for i in face))
        index_map = {old: new for new, old in enumerate(unique_indices)}
        new_faces = np.array([[index_map[i] for i in face] for face in group])
        new_vertices = vertices[unique_indices]
        submesh = trimesh.Trimesh(vertices=new_vertices, faces=new_faces, process=False)
        submeshes.append(submesh)
    return submeshes

# Load your STL mesh
'''mesh = trimesh.load_mesh("1_Combined_Pelvis.stl")
new_mesh = [] * 2

# Create submeshes
submeshes = create_submeshes(mesh)
print(len(submeshes[1].faces))

# Export each submesh
for i, submesh in enumerate(submeshes):
    print(i)
    new_mesh[i] = trimesh.Trimesh(vertices=submesh.vertices, faces=submesh.faces)
    #submesh.export(f"part_{i+1}.stl")'''