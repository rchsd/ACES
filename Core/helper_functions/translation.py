import numpy as np

#checks to see if the centroid is the right data type
#returns a 4x4 matrix translated using the centroid
def translate(centroid):
    if not isinstance(centroid, (list, np.ndarray)) or len(centroid) != 3:
        raise ValueError("Target must be a 3-element list or array.")
    matrix = np.eye(4)
    matrix[:3, 3] = centroid
    return matrix
