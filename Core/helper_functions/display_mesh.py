import pyvista as pv
# function will be used to wrap trimesh object before displaying it to the screen

def display_mesh(mesh):
    polydata = pv.wrap(mesh)

    plotter = pv.Plotter(
        window_size=[800, 600],
        border=True,
        border_color="red",
        lighting="light kit"
    )
    plotter.set_background(color="black", top="darkgray")

    plotter.title = "Aligned Pelvis Display"

    plotter.add_mesh(
        polydata,
        color="#EAE6DF",          # Off-white
        smooth_shading=True,
        lighting=True,
        ambient=0.2,
        diffuse=0.7,
        specular=0.3,
        specular_power=20.0,
    )
    plotter.add_axes(color = 'white')

    plotter.add_mesh_clip_plane(polydata, color="#EAE3D2", assign_to_axis='z')

    plotter.show()
