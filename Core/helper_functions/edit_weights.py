import pyvista as pv
import numpy as np
import trimesh
from random import choice

def edit_weights_display(pgon: trimesh.Trimesh, w, threshold=0.5):
    # Copy weights
    k = w.copy()

    # Wrap mesh for PyVista
    mesh = pv.wrap(pgon)

    # Instead of NaNs, keep all values and use alpha blending
    opacity = np.where(w > threshold, 1.0, 0.2)  # ROI fully opaque, others semi-transparent

    # Create plotter
    plotter = pv.Plotter()
    plotter.add_mesh(
        mesh,
        scalars=w,                # Use original weights for smooth interpolation
        cmap='coolwarm',          # Similar to MATLAB colormap
        interpolate_before_map=True,  # Enables smooth color interpolation
        opacity=opacity,          # Highlight ROI visually
        show_edges=False
    )

    # Add a light for shading (similar to MATLAB's light)
    light = pv.Light(position=(1, 1, 1), focal_point=(0, 0, 0), color='white', intensity=1.5)
    plotter.add_light(light)

    plotter.show_grid()
    plotter.show()

    return k

def filter_mesh_with_submesh(pgon: trimesh.Trimesh, mask: np.ndarray):
    # Create a face mask: keep faces where all vertices are in the mask
    face_mask = np.all(mask[pgon.faces], axis=1)

    # Use trimesh.submesh to extract the filtered mesh
    filtered_mesh = pgon.submesh([face_mask], only_watertight=False, append=True)

    return filtered_mesh

def extract_highlighted_region(pgon: trimesh.Trimesh, w, threshold=0.5):
    # Wrap the mesh with PyVista
    mesh = pv.wrap(pgon)

    # Add scalars to the mesh
    mesh.point_data['weights'] = w

    # Threshold the mesh to extract the region of interest
    highlighted = mesh.threshold(value=threshold, scalars='weights')

    # Visualize the extracted region
    plotter = pv.Plotter()
    plotter.add_mesh(highlighted, color='red', show_edges=True)
    plotter.show()

    return highlighted

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