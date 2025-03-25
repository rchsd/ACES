import numpy as np
import math
from scipy.io import loadmat
import plot_sphere as ps

def sphereFit(points):
    # Ensure the input is a numpy array
    points = np.array(points)
    
    # Check if the points array has the correct shape
    if points.shape[1] != 3:
        raise ValueError("Input points array must have shape (n, 3)")
    
    # Assemble the A matrix
    A = np.hstack((2 * points, np.ones((points.shape[0], 1))))
    
    # Assemble the f vector
    f = np.sum(points**2, axis=1)
    
    # Solve the linear system using least squares
    C, residules, rank, singval = np.linalg.lstsq(A, f, rcond=None)
    
    # Extract the center and calculate the radius
    center = C[:3]
    radius = math.sqrt(C[3] + np.sum(center**2))

    ps.plotSphere(points, center, radius, 'c:\\Users\\bbeasley\\Documents\\Python Projects\\Matlab-GUI\\py_Rotated_Pelvis.stl')
    
    return center, radius

# for testing
'''
points = loadmat('C:\MATLAB\points.mat')
points_metadata_keys = {'__header__', '__version__', '__globals__'}
points_data_dict = {key: value for key, value in points.items() if key not in points_metadata_keys}
points_data = points_data_dict.get('points')

print(sphereFit(points_data))'''