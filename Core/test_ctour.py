import numpy as np
from joblib import Parallel, delayed
from collections import defaultdict
import scipy.io as sio
import trimesh
import test_pgonsep_by_plane_index
import test_aabb

def compute_all_contours(mesh, plane_normal, plane_offsets):
    plane_offsets = np.asarray(plane_offsets).flatten()
    plane_offsets.sort()

    vertices = mesh.vertices
    faces = mesh.faces
    vcoefs = np.dot(vertices, plane_normal)

    segments = []
    face_indices = []
    plane_indices = []

    for i, face in enumerate(faces):
        face_vertices = vertices[face]
        face_coefs = vcoefs[face]

        min_coef = np.min(face_coefs)
        max_coef = np.max(face_coefs)

        intersecting_planes = plane_offsets[(plane_offsets >= min_coef) & (plane_offsets <= max_coef)]

        for offset in intersecting_planes:
            coefs = face_coefs - offset
            points = face_vertices
            intersections = []

            for j in range(3):
                k = (j + 1) % 3
                if coefs[j] * coefs[k] < 0:
                    t = coefs[k] / (coefs[k] - coefs[j])
                    p = points[k] * t + points[j] * (1 - t)
                    intersections.append(p)

            if len(intersections) == 2:
                segment = np.array(intersections)
                if segment.shape == (2, 3):
                    segments.append(segment)
                    face_indices.append(i)
                    plane_indices.append(np.where(plane_offsets == offset)[0][0])

    return segments, face_indices, plane_indices

def deduplicate_segments(segments):
    vertex_map = {}
    unique_vertices = []
    faces = []

    for segment in segments:
        face = []
        for point in segment:
            key = tuple(np.round(point, decimals=8))
            if key not in vertex_map:
                vertex_map[key] = len(unique_vertices)
                unique_vertices.append(point)
            face.append(vertex_map[key])
        faces.append(face)

    return {
        'faces': np.array(faces, dtype=int),
        'vertices': np.array(unique_vertices)
    }

def main_compute_all_contours(mesh, plane_normal, plane_offsets):
    plane_offsets = np.asarray(plane_offsets).flatten()
    plane_offsets.sort()

    results = Parallel(n_jobs=-1, backend='loky')(
        delayed(compute_all_contours)(mesh, plane_normal, [offset])
        for offset in plane_offsets
    )
    all_segments = []
    all_face_indices = []
    all_plane_indices = []
    for plane_idx, (segments, face_indices, _) in enumerate(results):
        all_segments.extend(segments)
        all_face_indices.extend(face_indices)
        all_plane_indices.extend([plane_idx] * len(segments))
    mesh_data = deduplicate_segments(all_segments)
    return mesh_data, all_face_indices, all_plane_indices

'''matrix = sio.loadmat('sample')
samples = matrix.get('sample')
mesh = trimesh.load('1_Combined_Pelvis.stl')

ctour, indices = compute_all_contours(mesh, (0, 0, 1), samples)
print(len(ctour), len(indices))'''