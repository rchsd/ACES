import networkx as nx
import numpy as np
import trimesh


def find_parts(polygon:dict=None, method='vertex', mesh=None, max_angle=None):
    #Identify connected parts of a polygon mesh using different algorithms.
    # If a trimesh object is provided, extract necessary data
    if mesh is not None:
        polygon = {
            'faces': mesh.faces,
            'normals': mesh.face_normals,
            'neighbors': [[] for _ in range(len(mesh.faces))]
        }

        # Build neighbor list from face adjacency
        for face_a, face_b in mesh.face_adjacency:
            polygon['neighbors'][face_a].append(face_b)
            polygon['neighbors'][face_b].append(face_a)

    faces = polygon['faces']

    if method == 'vertex':
        # Vertex-based connectivity
        G = nx.Graph()
        # Add edges between vertices in each face
        for face in faces:
            for i in range(len(face)):
                G.add_edge(face[i], face[(i + 1) % len(face)])

        components = list(nx.connected_components(G))

        node_to_component = {}
        for label, component in enumerate(components, start=1):
            for node in component:
                node_to_component[node] = label

        # Assign each face a label based on the first vertex
        face_labels = [node_to_component[face[0]] for face in faces]
        return np.array(face_labels)

    elif method == 'edge':
        # Edge-based connectivity using face normals and neighbors
        if 'normals' not in polygon or 'neighbors' not in polygon:
            raise ValueError("Polygon must include 'normals' and 'neighbors' for edge-based method.")

        normals = polygon['normals']
        neighbors = polygon['neighbors']
        n_faces = len(faces)
        processed = [False] * n_faces
        parts = [None] * n_faces
        limit = -np.cos(max_angle) if max_angle is not None else -1.0
        ipart = 0

        for face_index in range(n_faces):
            if processed[face_index]:
                continue

            stack = [face_index]
            processed[face_index] = True
            parts[face_index] = ipart

            while stack:
                current_face = stack.pop()
                for neighbor in neighbors[current_face]:
                    if neighbor is None or processed[neighbor]:
                        continue
                    dot = np.dot(normals[current_face], normals[neighbor])
                    if dot >= limit:
                        processed[neighbor] = True
                        parts[neighbor] = ipart
                        stack.append(neighbor)

            ipart += 1

        return parts

    else:
        raise ValueError("Unknown method. Use 'vertex' or 'edge'.")

def find_parts_edges(edges):
    return np.arange(len(edges)), [{'nfaces': 1, 'ncncts': 1, 'cstate': 1} for _ in range(len(edges))]


def max_part_areas(mesh, parts):
    parts = np.array(parts)
    unique_parts = np.unique(parts)
    face_areas = mesh.area_faces

    part_areas = [face_areas[parts == label].sum() for label in unique_parts]
    return max(part_areas)

def max_part_area(mesh, parts):
    # Force parts to be a numpy array
    parts = np.array(parts)

    # If the parts array is empty, there are no areas to compute.
    # Return 0.0 immediately to prevent max() from crashing.
    if parts.size == 0:
        return 0.0

    unique_parts = np.unique(parts)
    face_areas = mesh.area_faces

    part_areas = [face_areas[parts == label].sum() for label in unique_parts]

    # Second safety layer in case part_areas list generation failed
    if not part_areas:
        return 0.0

    return max(part_areas)

def compute_part_volumes(mesh, face_labels):
    face_labels = np.array(face_labels)
    unique_labels = np.unique(face_labels)
    volumes = []

    for label in unique_labels:
        face_indices = np.where(face_labels == label)[0]
        part_faces = mesh.faces[face_indices]
        part_mesh = trimesh.Trimesh(vertices=mesh.vertices, faces=part_faces, process=False)
        volumes.append(part_mesh.volume)

    return np.array(volumes)


def compute_part_centroids(mesh, face_labels):
    face_labels = np.array(face_labels)
    unique_labels = np.unique(face_labels)
    centroids = []

    for label in unique_labels:
        face_indices = np.where(face_labels == label)[0]
        part_faces = mesh.faces[face_indices]
        part_mesh = trimesh.Trimesh(vertices=mesh.vertices, faces=part_faces, process=False)
        centroids.append(volume_centroid(part_mesh))

    return np.array(centroids)

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
