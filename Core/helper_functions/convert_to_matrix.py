from scipy.io import savemat
import matlab.engine
import numpy as np

def convert_array(centroid):
    mat_a = matlab.double(centroid.tolist())
    savemat('c:/MATLAB/centroid.mat', {'centroid':mat_a})

#array = np.array([1, 1, 1])
#convert_array(array)