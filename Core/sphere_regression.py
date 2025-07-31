import numpy as np
import math
from scipy.io import loadmat
#import plot_sphere as ps

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
    
    return center, radius

# for testing

'''points = loadmat('c:\\Users\\bbeasley\\Documents\\Python Projects\\Matlab-GUI\\Tests\\points.mat')
print(points)
points_metadata_keys = {'__header__', '__version__', '__globals__'}
points_data_dict = {key: value for key, value in points.items() if key not in points_metadata_keys}
points_data = points_data_dict.get('points')

points_2 = loadmat('c:\\Users\\bbeasley\\Documents\\Python Projects\\Matlab-GUI\\Tests\\points_2.mat')
points_2_metadata_keys = {'__header__', '__version__', '__globals__'}
points_2_data_dict = {key: value for key, value in points_2.items() if key not in points_2_metadata_keys}
points_2_data = points_2_data_dict.get('points_2')

#print(sphereFit(points_data))

center_1, radius_1 = sphereFit(points_data)
center_2, radius_2 = sphereFit(points_2_data)
#ps.plotSphere(points_data, points_2_data, center_1, center_2, radius_1, radius_2, 'c:\\Users\\bbeasley\\Documents\\Python Projects\\Matlab-GUI\\Tests\\py_Rotated_Pelvis.stl')
'''
