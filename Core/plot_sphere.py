import numpy as np
from stl import mesh
import pyvista as pv

def plotSphere(points, center, radius, stl_file_path):
    plotter = pv.Plotter()
    sphere = pv.Sphere(radius=radius, center=center)
    
    pelvis = mesh.Mesh.from_file(stl_file_path)
    stl_mesh = pv.PolyData(np.concatenate(pelvis.vectors))
    plotter.add_mesh(sphere, color='red', opacity=0.5)
    plotter.add_mesh(stl_mesh, color='green', opacity=0.3)
    plotter.add_points(points, color='blue', point_size=5)

    plotter.show()