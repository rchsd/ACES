from collections import defaultdict
import numpy as np

# Sample mesh_data and plane_indices for demonstration
# Replace these with actual data when running the function
'''mesh_data = {
    'faces': np.array([[0, 1, 2], [2, 3, 0], [4, 5, 6], [6, 7, 4]] * 6),  # 24 faces
    'vertices': np.random.rand(20, 3)  # 20 vertices
}'''
#plane_indices = [i // 1 for i in range(24)]  # 24 unique plane indices

def separate_by_plane(mesh_data, plane_indices):
    separated = defaultdict(lambda: {'faces': [], 'vertex_indices': set()})

    # Step 1: Collect faces and used vertex indices per plane
    for i, plane_idx in enumerate(plane_indices):
        face = mesh_data['faces'][i]
        separated[plane_idx]['faces'].append(face)
        separated[plane_idx]['vertex_indices'].update(face)

    # Step 2: Reindex vertices per plane
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

# Run the separation
#separated = separate_by_plane(mesh_data, plane_indices)

# Verify the number of distinct groups
#num_groups = len(separated)
#print(f"Number of distinct face/vertex groups: {num_groups}")