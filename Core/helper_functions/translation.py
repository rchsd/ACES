import numpy as np

#checks to see if the centroid is the right data type
#returns a 4x4 matrix translated using the centroid 
def translate(centroid):
    if not isinstance(centroid, (list, np.ndarray)) or len(centroid) != 3:
        raise ValueError("Target must be a 3-element list or array.")
    matrix = np.eye(4)
    matrix[:3, 3] = centroid
    return matrix

    """
    centroid = [x, y, z]

    matrix = np.eye(4) looks like ---> [1 0 0 0
                                        0 1 0 0
                                        0 0 1 0
                                        0 0 0 1]

    matrix[:3, 3] = centroid ---->     [1 0 0 x
                                        0 1 0 y
                                        0 0 1 z
                                        0 0 0 1]

    x, y, z being the values of the centroid
    [:3 (Rows): Selects rows 0, 1, and 2 (the top three rows).
    , 3] (Column): Selects column index 3 (the fourth column).
    """