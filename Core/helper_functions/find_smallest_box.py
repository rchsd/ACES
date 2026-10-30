import numpy as np
import trimesh

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
        #Rotate around the centroid
        T1 = trimesh.transformations.translation_matrix(-original_center)
        R_mat = trimesh.transformations.rotation_matrix(angle, axis)
        T2 = trimesh.transformations.translation_matrix(original_center)
        full_transform = T2 @ R_mat @ T1

        #Extract 3x3 rotation and 3x1 translation vectors
        rotation_3x3 = full_transform[:3, :3]
        translation_3x1 = full_transform[:3, 3]

        #Rotate vertices directly via matrix multiplication
        rotated_vertices = pelvis.vertices @ rotation_3x3.T + translation_3x1

        #Axis Aligned BB min/max bounds calculation
        bbox_min = rotated_vertices.min(axis=0)
        bbox_max = rotated_vertices.max(axis=0)

        box_sizes[i] = np.prod(bbox_max - bbox_min)
        transformations.append(full_transform)

    # Return the transformation index with the smallest bounding box
    index = np.argmin(box_sizes)
    smallest_tform = transformations[index]

    return smallest_tform

def find_bounding_box(mesh, transform = None):
    pelvis = trimesh.Trimesh(faces=mesh.faces, vertices=mesh.vertices)
    if transform is not None:
        pelvis.apply_transform(transform)

    return pelvis.bounds

def rotate_mesh(radians, axis):
    rotation_matrix = trimesh.transformations.rotation_matrix(radians, axis)
    return rotation_matrix


def calculate_rotation_transform(angle, axis=None, about=None):
    """
    Calculate rotation transform matrix and offset.

    Parameters:
    angle (float): Angle of rotation (must be numeric scalar).
    axis (array-like, optional): Axis of rotation.
    about (array-like, optional): Rotation offset.

    Returns:
    tuple: (rotation_matrix, offset)
    """
    # Validate angle
    if not isinstance(angle, (int, float)):
        raise ValueError("Angle of rotation must be numeric scalar.")
    # Default axis and about
    axis = np.array(axis) if axis is not None else np.array([0, 0, 1])
    about = np.array(about) if about is not None else np.zeros(len(axis))
    # Ensure axis is 3D for simplicity
    if len(axis) < 3:
        axis = np.pad(axis, (0, 3 - len(axis)))
    # Normalize axis
    axis = axis / np.linalg.norm(axis)
    # Calculate rotation matrix
    c = np.cos(angle)
    s = np.sin(angle)
    t = 1 - c
    x, y, z = axis
    rotation_matrix = np.array([
        [t*x*x + c, t*x*y - s*z, t*x*z + s*y],
        [t*x*y + s*z, t*y*y + c, t*y*z - s*x],
        [t*x*z - s*y, t*y*z + s*x, t*z*z + c]
    ])
    # Calculate offset
    offset = about - rotation_matrix @ about
    transform_matrix = np.eye(4)
    transform_matrix[:3, :3] = rotation_matrix
    transform_matrix[:3, 3] = offset

    return transform_matrix
