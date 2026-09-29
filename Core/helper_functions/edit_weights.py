import pyvista as pv
import numpy as np
import trimesh
from random import choice

import numpy as np
import trimesh
import pyvista as pv


def edit_weights_display(pgon: trimesh.Trimesh, w, threshold=0.5):
    #Copy weights
    k = w.copy()

    #Wrap mesh for PyVista
    mesh = pv.wrap(pgon)
    
    #Explicitly attach the weights array to the mesh data repository
    mesh.point_data['weight_scalars'] = w

    #Extract the ROI (values above threshold)
    #Using a float cast on max avoids clipping boundary errors
    roi_mesh = mesh.threshold([threshold, float(w.max())], scalars='weight_scalars')
    
    #Extract the context background (values below or equal to threshold)
    background_mesh = mesh.threshold([float(w.min()), threshold], scalars='weight_scalars')

    #Create plotter
    plotter = pv.Plotter()
    plotter.enable_depth_peeling()  # Ensures background doesn't clip/occlude the foreground

    #Fix global color bar range so both meshes share the exact same scale mapping
    color_limits = [float(w.min()), float(w.max())]
    plotter.set_background(color="darkgrey", top="black")
    #Add Context Background (Thin, Ghosted)
    plotter.add_mesh(
        background_mesh,
        scalars='weight_scalars',
        cmap='coolwarm',
        clim=color_limits, 
        opacity=0.15,               # Clean uniform dimming
        show_edges=False,
        smooth_shading=True,
        lighting=True,
        ambient=0.4,                # Brighter ambient to keep it readable while dim
        diffuse=0.4,
        specular=0.0,               # Turn off reflections on background
        show_scalar_bar=False,       # Don't duplicate color bars
        name = "pelvis_layer"       # Used for the button
    )

    #Add Highlighted ROI (Fully Solid & Specular Organic Tissue)
    plotter.add_mesh(
        roi_mesh,
        scalars='weight_scalars',
        cmap='coolwarm',
        clim=color_limits,
        opacity=1.0,                # COMPLETELY OPAQUE
        show_edges=False,
        smooth_shading=True,
        lighting=True,
        ambient=0.2,
        diffuse=0.7,
        specular=0.5,               # Higher specular flash to draw focus
        specular_power=25.0,
        #scalar_bar_args={'title': 'Weights Profile'},
        scalar_bar_args={
                'title': 'Weights Profile',
                'color': 'white',          # Sets both Title and Label text to white
                'title_font_size': 12,     # Custom title sizing
                'label_font_size': 10,     # Custom numerical ticks sizing
                'shadow': False,           # Strips the default black dropshadow
                'font_family': 'arial',  
            },
        name="roi_layer"            # Used for the button 
    )
    
    #Add the checkbox widget to the render window
    plotter.add_checkbox_button_widget(
        callback=lambda state: plotter.actors["pelvis_layer"].SetVisibility(state),
        value=True,                 # Starts as checked/visible
        color_on='blue',            # Color when active
        color_off='grey',           # Color when deactivated
        background_color='white',
        size=30,                    # Size of the widget in pixels
        position=(10, 10)           # Lower left-hand corner coordinates
    )
    #Add light for clinical shading depth
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