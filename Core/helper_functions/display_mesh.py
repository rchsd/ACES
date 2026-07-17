import pyvista as pv
import numpy as np
import trimesh
# function will be used to wrap trimesh object before displaying it to the screen

def display_mesh(mesh):

    coordinates = mesh.vertices
    x , y, z = coordinates[0]
    print(f"this is the coordinates {x}, {y}, {z}")
    
    polydata = pv.wrap(mesh)
    polydata.rotate_z(45, inplace=True)
    polydata.rotate_y(5, inplace=True)
    plotter = pv.Plotter(
        window_size=[800, 600],       # Width and height in pixels
        border=True,                  # Enable window borders
        border_color="red",           # Draw a custom-colored border
        lighting="light kit"          # Set standard aesthetic lighting
    )
    plotter.set_background(color="black", top="darkgray")
    plotter.title = "Aligned Pelvis Display"
    #plotter.add_mesh(polydata, show_scalar_bar = True, color='white')
    plotter.add_mesh(
        polydata,
        color="#EAE6DF",          # Off-white 
        smooth_shading=True,      # Smooths out segmentation
        lighting=True,            # Activates light 
        ambient=0.2,              # Soft base lighting 
        diffuse=0.7,              # Matte surface illumination
        specular=0.3,             # Mirroring organic bone tissue
        specular_power=20.0,      # Non-metallic highlights
    )
    plotter.add_axes(color = 'white')
    # Add a text box placeholder in the top-left corner
    
    #plotter.view_xz()
    plotter.show()