import numpy as np
import trimesh
from scipy.spatial.transform import Rotation as R

def find_smallest_box(tform, faces, vertices, angles_selection, axis):
    """
    Finds the transformation that results in the smallest axis-aligned bounding box
    for a mesh rotated around a given axis.

    Parameters:
    - tform: 4x4 transformation matrix to apply to the mesh initially.
    - faces: Mesh face indices.
    - vertices: Mesh vertex coordinates.
    - angles_selection: 0 for full rotation (0 to 2π), 1 for fine rotation (-5 to 5 steps of π/45).
    - axis: Axis of rotation (e.g., [0, 1, 0]).

    Returns:
    - smallest_tform: 4x4 transformation matrix that minimizes the bounding box volume.
    """

    # Select angles based on the mode
    if angles_selection == 0:
        angles = np.arange(0, 18) * np.pi / 9  # 0 to 2π in 18 steps
    else:
        angles = np.arange(-5, 6) * np.pi / 45  # -5π/45 to 5π/45

    # Create and transform the mesh
    pelvis = trimesh.Trimesh(vertices=vertices, faces=faces)
    pelvis.apply_transform(tform)

    if not isinstance(pelvis, trimesh.Trimesh):
        raise ValueError("The input must be a Trimesh object.")

    box_sizes = np.zeros(len(angles))
    transformations = []

    original_center = pelvis.centroid

    for i, angle in enumerate(angles):
        # Rotation matrix using scipy
        rotation = R.from_rotvec(angle * np.array(axis))

        # Rotate around the centroid
        T1 = trimesh.transformations.translation_matrix(-original_center)
        R_mat = trimesh.transformations.rotation_matrix(angle, axis)
        T2 = trimesh.transformations.translation_matrix(original_center)
        #full_transform = T2 @ R_mat @ T1
        full_transform = R_mat

        # Apply transformation
        transformed_mesh = pelvis.copy()
        transformed_mesh.apply_transform(full_transform)

        # Compute bounding box volume
        bounds = transformed_mesh.bounds
        aabb_size = np.prod(bounds[1] - bounds[0])
        box_sizes[i] = aabb_size

        # Store transformation
        transformations.append(full_transform)

    # Return the transformation with the smallest bounding box
    i = np.argmin(box_sizes)
    smallest_tform = transformations[i]

    return smallest_tform

def find_bounding_box(faces, vertices, transform = None):
    pelvis = trimesh.Trimesh(faces=faces, vertices=vertices)
    if transform is not None:
        pelvis.apply_transform(transform)

    return pelvis.bounds

def rotate_mesh(degrees, axis):
    radians = np.radians(degrees)
    rotation_matrix = trimesh.transformations.rotation_matrix(radians, axis)
    return rotation_matrix


#print(find_smallest_box('py_Rotated_Pelvis.stl', 0, [0, 1, 0]))
'''combined_mesh = trimesh.load('Schmitz\\quad_1.stl')
tform2 = find_smallest_box(combined_mesh.faces, combined_mesh.vertices, 0, [1, 0, 0])
print(tform2)'''