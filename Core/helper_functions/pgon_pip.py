from shapely.geometry import Point, Polygon
from typing import List, Tuple, Optional
import numpy as np

def in_pgon(pgon: dict, points: List[List[float]], tform: Optional[np.ndarray] = None) -> Tuple[List[int], List[int]]:
    """
    Point-in-polygon test using Shapely, with optional transformation and 3D-to-2D projection.

    Parameters:
        pgon (dict): Dictionary with 'vertices' and 'faces'. Assumes vertices are 2D.
        points (List[List[float]]): List of 3D or 2D points.
        tform (np.ndarray, optional): 4x4 transformation matrix. If provided, applies to points.

    Returns:
        Tuple[List[int], List[int]]:
            - List of 1s (inside), 0s (outside), 2s (on boundary).
            - List of -1s as placeholder for closest face.
    """
    if len(pgon["vertices"][0]) != 2:
        raise ValueError("Polygon vertices must be 2D for Shapely-based testing.")

    polygon_2d = Polygon(pgon["vertices"])

    # Convert to numpy array for transformation
    points_np = np.array(points)

    if tform is not None:
        # Convert to homogeneous coordinates
        ones = np.ones((points_np.shape[0], 1))
        points_hom = np.hstack([points_np, ones])
        # Apply transformation
        points_np = (tform @ points_hom.T).T[:, :3]

    results = []
    closest_faces = [-1] * len(points_np)

    for pt in points_np:
        pt2d = pt[:2]  # Project to 2D
        point = Point(pt2d)
        if polygon_2d.contains(point):
            results.append(1)
        elif polygon_2d.touches(point):
            results.append(2)
        else:
            results.append(0)

    return results, closest_faces