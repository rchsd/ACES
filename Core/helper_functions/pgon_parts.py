import networkx as nx
import numpy as np
import trimesh

def find_parts(polygon=None, method='vertex', mesh=None, max_angle=None):
    """
    Identify connected parts of a polygon mesh using different algorithms.

    Parameters:
    - polygon: dict with 'faces' (Nx2 or Nx3 array), optionally 'normals' and 'neighbors'
    - method: 'vertex' or 'edge'
    - max_angle: optional angle threshold (in radians) for edge-based connectivity
    - mesh: optional trimesh.Trimesh object

    Returns:
    - List of part labels for each face
    """
    # If a trimesh object is provided, extract necessary data
    if mesh is not None:
        polygon = {
            'faces': mesh.faces,
            'normals': mesh.face_normals,
            'neighbors': [[] for _ in range(len(mesh.faces))]
        }

        # Build neighbor list from face adjacency
        for a, b in mesh.face_adjacency:
            polygon['neighbors'][a].append(b)
            polygon['neighbors'][b].append(a)

    #if polygon is None or 'faces' not in polygon:
        #raise ValueError("Either 'polygon' with 'faces' or a 'trimesh' object must be provided.")

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
        return face_labels

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

        for f in range(n_faces):
            if processed[f]:
                continue

            stack = [f]
            processed[f] = True
            parts[f] = ipart

            while stack:
                g = stack.pop()
                for neighbor in neighbors[g]:
                    if neighbor is None or processed[neighbor]:
                        continue
                    dot = np.dot(normals[g], normals[neighbor])
                    if dot >= limit:
                        processed[neighbor] = True
                        parts[neighbor] = ipart
                        stack.append(neighbor)

            ipart += 1

        return parts

    else:
        raise ValueError("Unknown method. Use 'vertex' or 'edge'.")
    
def max_part_area(mesh, parts):
    """
    Compute the maximum area of connected parts in a mesh.

    Parameters:
    - mesh: trimesh.Trimesh object
    - parts: list of part labels for each face

    Returns:
    - Maximum area among all parts
    """
    parts = np.array(parts)
    unique_parts = np.unique(parts)
    face_areas = mesh.area_faces

    part_areas = [face_areas[parts == label].sum() for label in unique_parts]
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
    import numpy as np
    import trimesh

    face_labels = np.array(face_labels)
    unique_labels = np.unique(face_labels)
    centroids = []

    for label in unique_labels:
        face_indices = np.where(face_labels == label)[0]
        part_faces = mesh.faces[face_indices]
        part_mesh = trimesh.Trimesh(vertices=mesh.vertices, faces=part_faces, process=False)
        centroids.append(part_mesh.center_mass)

    return np.array(centroids)

#mesh = trimesh.load('left_part.stl')
#parts = find_parts(None, 'edge', None, mesh)
#print('hello')