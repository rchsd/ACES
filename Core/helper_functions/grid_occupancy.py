import numpy as np

def get_grid_occupancy(points, grid_size):
    # Calculate grid points
    grid = np.floor(points / grid_size) * grid_size + grid_size / 2

    # Sort grid points
    ig = np.lexsort(grid.T[::-1])
    grid_sorted = grid[ig]

    # Get unique grid points and their indices
    grid_unique, ag, bg = np.unique(grid_sorted, axis=0, return_index=True, return_inverse=True)

    # Calculate occupancy counts
    count = np.diff(np.concatenate(([0], ag)))

    # Save re-indexing vector
    reidx = np.empty_like(bg)
    reidx[ig] = bg

    return grid_unique, count, reidx
