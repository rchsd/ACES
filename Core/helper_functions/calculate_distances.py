import numpy as np

def calculate_pairwise_distances(grid):
    # Expand dimensions to perform broadcasting
    grid_expanded = np.expand_dims(grid, axis=1)  # Shape becomes (N, 1, 3)
    grid_transposed = np.expand_dims(grid, axis=0)  # Shape becomes (1, N, 3)

    # Subtract each row from every other row
    differences = grid_expanded - grid_transposed  # Shape becomes (N, N, 3)

    # Calculate magnitude (Euclidean norm) along the last axis
    magnitudes = np.linalg.norm(differences, axis=2)  # Shape becomes (N, N)

    return magnitudes