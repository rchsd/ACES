import pyvista as pv
# function will be used to wrap trimesh object before displaying it to the screen

def display_mesh(mesh):
    polydata = pv.wrap(mesh)
    plotter = pv.Plotter()
    plotter.add_mesh(polydata, color='white')
    plotter.show()