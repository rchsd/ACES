import numpy as np

def translate(centroid):
    if not isinstance(centroid, (list, np.ndarray)) or not np.ndim(centroid) == 1:
            raise ValueError('Target point must be a row vector.')

    # Calculate translation matrix and offset
    Matrix = np.eye(len(centroid))
    Offset = np.conj(centroid)

    print('Matrix', Matrix)
    print('Offset', Offset)

    return Matrix, Offset