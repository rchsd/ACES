import numpy as np


def compute_aabb_slices(separated_groups):
    """
    Computes the AABB for each group in the separated dictionary using only vertices
    referenced by faces, and rounding coordinates to 8 decimal places.

    Parameters:
    - separated_groups: dict mapping plane index to {'faces': np.ndarray, 'vertices': np.ndarray}

    Returns:
    - dict mapping plane index to {'min': np.ndarray, 'max': np.ndarray}
    """
    aabb_dict = {}

    for plane_idx, group in separated_groups.items():
        faces = group['faces']
        vertices = group['vertices']

        if faces.size == 0 or vertices.size == 0:
            continue

        used_indices = np.unique(faces.flatten())
        used_vertices = vertices[used_indices]
        used_vertices = np.round(used_vertices, decimals=8)

        aabb_min = np.min(used_vertices, axis=0)
        aabb_max = np.max(used_vertices, axis=0)

        aabb_dict[plane_idx] = {
            'min': aabb_min,
            'max': aabb_max
        }

    return aabb_dict


# Example: assuming `separated` is the dictionary of 24 groups
# For demonstration, we simulate a dummy structure
# Replace this with your actual `separated` dictionary
'''separated = {
    i: {
        'faces': np.random.randint(0, 100, (10, 3)),
        'vertices': np.random.rand(100, 3)
    } for i in range(24)
}

# Compute AABB for each group
aabb_results = {}
for plane_idx, group in separated.items():
    aabb_min, aabb_max = compute_aabb(group['faces'], group['vertices'])
    aabb_results[plane_idx] = {
        'min': aabb_min,
        'max': aabb_max
    }

# Print the results
for plane_idx in sorted(aabb_results):
    print(f"Plane {plane_idx}:")
    print(f"  AABB Min: {aabb_results[plane_idx]['min']}")
    print(f"  AABB Max: {aabb_results[plane_idx]['max']}")'''
