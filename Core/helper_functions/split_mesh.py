import numpy as np
import trimesh
import numpy as np
import trimesh
from helper_functions import display_mesh

def pgon_split(mesh, normal, coefficient, vertices=None, faces=None, tol=1e-12):
    
    normal = np.asarray(normal)
    normal = normal / np.linalg.norm(normal)

    if mesh is None:
        vertices=vertices
        faces=faces
    else:
        vertices = mesh.vertices
        faces = mesh.faces
 
    dists = vertices @ normal - coefficient
    #rel_tol = tol * (np.abs(coefficient) + tol) #unused calculated variable --- maybe delete?
    #dists[np.abs(dists) < rel_tol] = 0
    dists[np.abs(dists / (np.abs(coefficient) + tol)) < tol] = 0

    new_vertices = vertices.tolist()
    new_faces = []
    over_plane_mask = []
    original_face_indices = []

    edge_to_new_vertex = {}

    for face_idx, face in enumerate(faces):
        v_idx = face
        v_dists = dists[v_idx]
        signs = np.sign(v_dists)

        # Determine which edges cross the plane
        crossing_edges = []
        edge_indices = [(0, 1), (1, 2), (2, 0)]
        split_indices = [None, None, None]

        for i, (a, b) in enumerate(edge_indices):
            sa, sb = signs[a], signs[b]
            if sa * sb < 0:
                edge = tuple(sorted((v_idx[a], v_idx[b])))
                if edge not in edge_to_new_vertex:
                    va, vb = vertices[edge[0]], vertices[edge[1]]
                    da, db = dists[edge[0]], dists[edge[1]]
                    t = da / (da - db)
                    new_point = va + t * (vb - va)
                    edge_to_new_vertex[edge] = len(new_vertices)
                    new_vertices.append(new_point.tolist())
                split_indices[i] = edge_to_new_vertex[edge]
                crossing_edges.append((i, edge))

        num_splits = len(crossing_edges)
        
        if num_splits == 0:
            new_faces.append(v_idx.tolist())
            over_plane_mask.append(np.any(signs > 0))
            original_face_indices.append(face_idx)
            

        elif num_splits == 1:
            i = crossing_edges[0][0]
            j = (i + 1) % 3
            k = (j + 1) % 3
            vi, vj, vk = v_idx[i], v_idx[j], v_idx[k]
            new_v = split_indices[i]
            new_faces.append([vi, new_v, vk])
            new_faces.append([new_v, vj, vk])
            over_plane_mask.extend([dists[vi] > 0, dists[vj] > 0])
            original_face_indices.extend([face_idx, face_idx])
            

        elif num_splits == 2:
            # Find the edge that was NOT split
            unsplit_edge = [i for i in range(3) if split_indices[i] is None][0]
            i = unsplit_edge
            j = (i + 1) % 3
            k = (j + 1) % 3
            vi, vj, vk = v_idx[i], v_idx[j], v_idx[k]
            new_vj = split_indices[j]
            new_vk = split_indices[k]

            # Triangle 1: between new vertices and vk
            new_faces.append([new_vj, vk, new_vk])
            # Triangle 2: between vj, new_vj, vi
            new_faces.append([vj, new_vj, vi])
            # Triangle 3: between new_vj, new_vk, vi
            new_faces.append([new_vj, new_vk, vi])

            over_plane_mask.extend([
                dists[vk] > 0,
                dists[vj] > 0,
                dists[vi] > 0
            ])
            original_face_indices.extend([face_idx] * 3)
            

        else:
            # More than 2 intersections on a triangle is invalid
            continue

    refined_mesh = trimesh.Trimesh(vertices=np.array(new_vertices),
                                   faces=np.array(new_faces),
                                   process=False)

   
    return refined_mesh, np.array(over_plane_mask), np.array(original_face_indices)

def pgon_split_two(mesh, normal, coefficient, vertices=None, faces=None, tol=1e-8):
    """
    Split a triangular mesh along a plane and return:
    - refined_mesh (Trimesh object)
    - over_plane_mask (bool array)
    - original_face_indices (int array)
    """
    # Normalize plane normal
    normal = np.asarray(normal)
    normal = normal / np.linalg.norm(normal)

    # Get vertices and faces
    if mesh is None:
        vertices = np.asarray(vertices)
        faces = np.asarray(faces)
    else:
        vertices = mesh.vertices
        faces = mesh.faces

    # Compute signed distances of vertices to plane
    dists = vertices @ normal - coefficient
    rel_tol = tol * (np.abs(coefficient) + tol)
    dists[np.abs(dists) < rel_tol] = 0

    new_vertices = vertices.tolist()
    new_faces = []
    over_plane_mask = []
    original_face_indices = []
    edge_to_new_vertex = {}

    for face_idx, face in enumerate(faces):
        v_idx = face
        v_dists = dists[v_idx]
        signs = np.sign(v_dists)

        # Determine which edges cross the plane
        crossing_edges = []
        edge_indices = [(0, 1), (1, 2), (2, 0)]
        split_indices = [None, None, None]

        for i, (a, b) in enumerate(edge_indices):
            sa, sb = signs[a], signs[b]
            if sa * sb < 0:  # Edge crosses plane
                edge = tuple(sorted((v_idx[a], v_idx[b])))
                if edge not in edge_to_new_vertex:
                    va, vb = vertices[edge[0]], vertices[edge[1]]
                    da, db = dists[edge[0]], dists[edge[1]]
                    t = da / (da - db)
                    t = np.clip(t, 0.0, 1.0)  # Clamp for stability
                    new_point = va + t * (vb - va)
                    edge_to_new_vertex[edge] = len(new_vertices)
                    new_vertices.append(new_point.tolist())
                split_indices[i] = edge_to_new_vertex[edge]
                crossing_edges.append((i, edge))

        num_splits = len(crossing_edges)

        if num_splits == 0:
            new_faces.append(v_idx.tolist())
            over_plane_mask.append(np.any(signs > 0))
            original_face_indices.append(face_idx)

        elif num_splits == 1:
            i = crossing_edges[0][0]
            j = (i + 1) % 3
            k = (j + 1) % 3
            vi, vj, vk = v_idx[i], v_idx[j], v_idx[k]
            new_v = split_indices[i]
            new_faces.append([vi, new_v, vk])
            new_faces.append([new_v, vj, vk])
            over_plane_mask.extend([dists[vi] > 0, dists[vj] > 0])
            original_face_indices.extend([face_idx, face_idx])

        elif num_splits == 2:
            unsplit_edge = [i for i in range(3) if split_indices[i] is None][0]
            i = unsplit_edge
            j = (i + 1) % 3
            k = (j + 1) % 3
            vi, vj, vk = v_idx[i], v_idx[j], v_idx[k]
            new_vj = split_indices[j]
            new_vk = split_indices[k]

            # Ensure consistent winding
            new_faces.append([new_vj, vk, new_vk])
            new_faces.append([vj, new_vj, vi])
            new_faces.append([new_vj, new_vk, vi])

            over_plane_mask.extend([
                dists[vk] > 0,
                dists[vj] > 0,
                dists[vi] > 0
            ])
            original_face_indices.extend([face_idx] * 3)

    # Build mesh and merge duplicate vertices
    refined_mesh = trimesh.Trimesh(vertices=np.array(new_vertices),
                                   faces=np.array(new_faces),
                                   process=False)
    refined_mesh.merge_vertices()  # Deduplicate vertices
    refined_mesh.remove_duplicate_faces()
    refined_mesh.remove_unreferenced_vertices()

    return refined_mesh, np.array(over_plane_mask), np.array(original_face_indices)