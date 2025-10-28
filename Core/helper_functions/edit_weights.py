import pyvista as pv
import numpy as np
import trimesh
from random import choice

def edit_weights(pgon: trimesh.Trimesh, w):
    k = w.copy()
    mesh = pv.wrap(pgon)
    plotter = pv.Plotter()
    plotter.add_mesh(mesh, scalars=w, color='blue', show_edges=False)
    plotter.show_grid()

    light = pv.Light(
        position=(1, 1, 1), 
        focal_point=(0, 0, 0), 
        color='white',
        intensity=1.5  # Increase the intensity
    )
    plotter.add_light(light)

    plotter.show()

    return k

def edit_weights_with_mask(pgon, w, radii, centers):
    mesh = pv.wrap(pgon)
    k = w.copy()

    # Create plotter with 1x2 layout
    plotter = pv.Plotter(shape=(1, 2), border=True)

    # Subplot 0: Full mesh with scalar weights
    plotter.subplot(0, 0)
    plotter.add_text("Full Mesh with Weights", font_size=10)
    plotter.add_mesh(mesh, scalars=w, cmap='Blues', show_edges=False)
    plotter.show_grid()

    # Subplot 1: Only show acetabular masks
    plotter.subplot(0, 1)
    plotter.add_text("Acetabular Masks Only", font_size=10)

    # Enlarge radii to cover broader area
    enlarged_radii = [r * 1 for r in radii]
    points = mesh.points

    # Compute masks
    dist_to_left = np.linalg.norm(points - centers[0], axis=1)
    dist_to_right = np.linalg.norm(points - centers[1], axis=1)
    left_mask = dist_to_left < enlarged_radii[0]
    right_mask = dist_to_right < enlarged_radii[1]

    # Extract masked regions
    left_highlight = mesh.extract_points(left_mask, adjacent_cells=True)
    right_highlight = mesh.extract_points(right_mask, adjacent_cells=True)

    # Add masked regions to plot
    plotter.add_mesh(left_highlight, color='red', opacity=0.7)
    plotter.add_mesh(right_highlight, color='green', opacity=0.7)
    plotter.show_grid()

    # Add lighting
    light = pv.Light(position=(1, 1, 1), focal_point=(0, 0, 0), color='white', intensity=1.5)
    plotter.add_light(light)

    # Show the visualization
    plotter.show()

    # Return number of masks and the masks themselves
    masks = [left_mask, right_mask]
    return k, masks