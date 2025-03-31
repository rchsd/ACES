import numpy as np
import pyvista as pv
from scipy.spatial.transform import Rotation as R

def find_smallest_box(mesh, angles_selection, axis):
    """
    Find the transformation matrix that rotates the mesh into its smallest bounding box.

    Parameters:
    - mesh: A PyVista PolyData object representing the polygonal mesh.
    - angles_selection: Selection for angle range.
    - axis: The axis around which to rotate the mesh (e.g., [0, 0, 1] for the Z-axis).

    Returns:
    - smallest_rotation_rounded: The 3x3 rotation matrix, rounded to the nearest whole number.
    - offset_rounded: The translation offset vector, rounded to the nearest whole number.
    """

    angles = None

    if angles_selection == 0:
        angles = np.arange(0, 18) * np.pi / 9
    else:
        angles = np.arange(-5, 6) * np.pi / 45

    pelvis = pv.read(mesh)
    print(pelvis)

    # Ensure the mesh is a PyVista PolyData object
    if not isinstance(pelvis, pv.PolyData):
        raise ValueError("The input must be a PyVista PolyData object.")

    box_sizes = np.zeros(len(angles))
    transformations = []

    # Calculate the original center of the mesh
    original_center = np.array(pelvis.center)

    for i, angle in enumerate(angles):
        # Create a rotation matrix for the given angle and axis using scipy
        rotation = R.from_rotvec(angle * np.array(axis))
        rotation_matrix = rotation.as_matrix()

        # Apply the transformation to the mesh
        transformed_mesh = pelvis.copy()
        transformed_mesh.rotate_vector(axis, np.degrees(angle), inplace=True)

        # Calculate the new center of the transformed mesh
        new_center = np.array(transformed_mesh.center)

        # Calculate the difference in translation
        translation_difference = new_center - original_center

        # Calculate the axis-aligned bounding box
        bounds = transformed_mesh.bounds
        aabb_size = (bounds[1] - bounds[0]) * (bounds[3] - bounds[2]) * (bounds[5] - bounds[4])
        box_sizes[i] = aabb_size

        # Create the 4x4 transformation matrix
        transformation_matrix = np.eye(4)
        transformation_matrix[:3, :3] = rotation_matrix
        transformation_matrix[:3, 3] = translation_difference

        transformations.append(transformation_matrix)

    # Find the index of the smallest bounding box
    i = np.argmin(box_sizes)
    smallest_tform = transformations[i]

    # Extract the 3x3 rotation matrix and the offset
    smallest_rotation = smallest_tform[:3, :3]
    offset = smallest_tform[:3, 3]

    # Round both to the nearest whole number
    smallest_rotation_rounded = np.round(smallest_rotation, decimals=0)
    offset_rounded = np.round(offset, decimals=0)

    return smallest_rotation_rounded, offset_rounded

# for testing
#print(find_smallest_box('py_Rotated_Pelvis.stl', 0, [0, 1, 0]))