import pyvista as pv
from trimesh import Trimesh

def edit_weights(pgon: Trimesh, w):
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