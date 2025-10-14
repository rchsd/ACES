import pyvista as pv
import numpy as np
import initialize_params

def get_projected_points(pgon, mask, cen, rad, bounds, num_points=8, radius=1):
    """
    Function to interactively select a point on the mesh and return projected points.

    Parameters:
    - mesh: The PyVista mesh object.
    - num_points: Number of points in the circle.
    - radius: Radius of the circle around the selected point.

    Returns:
    - projected_points: The coordinates of the projected points on the mesh surface.
    """

    # Initialize gui parameters
    #btform, gui = initialize_params.initialize_params(pgon, mask, cen, rad, bounds)
    tool = []

    pgon = pv.wrap(pgon)
    # Initialize the plotter
    plotter = pv.Plotter()

    # Variable to store projected points
    projected_points = []

    # Function to be called when a point is picked
    def on_pick(point):
        nonlocal projected_points
        # Generate points in a circle around the selected point
        angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
        circle_points = np.array([
            point + radius * np.array([np.cos(angle), np.sin(angle), 0])
            for angle in angles
        ])

        # Project the circle points onto the mesh surface
        projected_points = np.array([pgon.points[pgon.find_closest_point(p)] for p in circle_points])

        # Print the coordinates of the projected points
        print("Projected Points Coordinates:")
        for i, p in enumerate(projected_points):
            print(f"Point {i+1}: {p}")

        # Create a PyVista point cloud for the projected circle points
        projected_cloud = pv.PolyData(projected_points)

        # Add the projected circle points to the plotter
        plotter.add_mesh(projected_cloud, color='red', point_size=10, render_points_as_spheres=True)
        plotter.render()

    # Add the mesh to the plotter
    plotter.add_mesh(pgon, color='lightblue', opacity=1)

    # Enable picking and set the callback function
    plotter.enable_point_picking(callback=on_pick, show_message=True)

    # Start the interactive plotter
    plotter.show()

    return projected_points

#mesh = pv.read('c:\\MATLAB\\1_Combined_Pelvis.stl')
# Get projected points
#projected_points = get_projected_points(mesh)