from collections import defaultdict
import numpy as np

def separate_by_plane(mesh_data, plane_indices):
    separated = defaultdict(lambda: {'faces': [], 'vertex_indices': set()})

    # Collect faces and used vertex indices per plane
    for i, plane_idx in enumerate(plane_indices):
        face = mesh_data['faces'][i]
        separated[plane_idx]['faces'].append(face)
        separated[plane_idx]['vertex_indices'].update(face)

    # Reindex vertices per plane
    for plane_idx, group in separated.items():
        used_indices = sorted(group['vertex_indices'])
        index_map = {old_idx: new_idx for new_idx, old_idx in enumerate(used_indices)}
        reindexed_faces = np.array([[index_map[idx] for idx in face] for face in group['faces']], dtype=int)
        vertices = mesh_data['vertices'][used_indices]

        separated[plane_idx] = {
            'faces': reindexed_faces,
            'vertices': vertices
        }


    num_groups = len(separated)
    return separated