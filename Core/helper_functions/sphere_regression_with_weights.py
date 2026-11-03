import numpy as np
import math

def sphereFit(points, weights=None):
    # Ensure the input is a numpy array
    points = np.array(points)

    # Check if the points array has the correct shape
    if points.shape[1] != 3:
        raise ValueError("Input points array must have shape (n, 3)")

    # If weights are not provided, use equal weights
    if weights is None:
        weights = np.ones(points.shape[0])
    else:
        weights = np.array(weights)
        if len(weights) != points.shape[0]:
            raise ValueError("Weights array must have the same length as the number of points")

    # Assemble the weighted A matrix
    A = np.hstack((2 * points, np.ones((points.shape[0], 1))))
    A = A * weights[:, np.newaxis]  # Apply weights

    # Assemble the weighted f vector
    f = np.sum(points**2, axis=1)
    f = f * weights  # Apply weights

    # Solve the weighted linear system using least squares (C, residules, rank, singval)
    C, _, _, _ = np.linalg.lstsq(A, f, rcond=None)

    # Extract the center and calculate the radius
    center = C[:3]
    radius = math.sqrt(C[3] + np.sum(center**2))

    return center, radius
