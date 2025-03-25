import numpy as np
import sys
import matlab.engine
import pyvista as pv
from scipy.spatial.transform import Rotation as R
sys.path.insert(1, 'C:\\Users\\bbeasley\\Documents\\Python Projects\\MATLAB-GUI\\Core')

import find_centroid as fc

def find_smallest_box(mesh, angles, axis):
    """
    Find the transformation matrix that rotates the mesh into its smallest bounding box.

    Parameters:
    - mesh: A PyVista PolyData object representing the polygonal mesh.
    - angles: A list or array of angles (in radians) to rotate the mesh.
    - axis: The axis around which to rotate the mesh (e.g., [0, 0, 1] for the Z-axis).

    Returns:
    - smallest_tform_rounded: The 4x4 transformation matrix that results in the smallest bounding box, rounded to 4 decimal places.
    """
    
    # Ensure the mesh is a PyVista PolyData object
    if not isinstance(mesh, pv.PolyData):
        raise ValueError("The input must be a PyVista PolyData object.")

    box_sizes = np.zeros(len(angles))
    transformations = []
    
    # Calculate the original center of the mesh
    original_center = np.array(mesh.center)
    
    for i, angle in enumerate(angles):
        # Create a rotation matrix for the given angle and axis using scipy
        rotation = R.from_rotvec(angle * np.array(axis))
        rotation_matrix = rotation.as_matrix()
        
        # Apply the transformation to the mesh
        transformed_mesh = mesh.copy()
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
    
    # Round the transformation matrix to 4 decimal places
    smallest_tform_rounded = np.around(smallest_tform, decimals=4)
    
    return smallest_tform_rounded


eng = matlab.engine.start_matlab()

def run_test():
    eng.cd(r'C:/MATLAB', nargout=0)
    eng.Py_StartHere(nargout = 0)
    centroid_of_volume = fc.find_centroid('c:\\0stl\\Test\\Pelvis\\pelvis_combined.stl')
    #print(centroid_of_volume)

    mesh = pv.read('c:\\0stl\\Test\\Pelvis\\pelvis_combined.stl')
    angles = np.arange(0, 18) * np.pi / 9
    axis = [0, 1, 0]

    tform = find_smallest_box(mesh, angles, axis)
    print(tform)

    eng.Py_Compare_Smallest_Box(nargout=0)

run_test()