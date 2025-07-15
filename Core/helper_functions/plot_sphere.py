import numpy as np
from stl import mesh
import pyvista as pv

def plotSphere(points_1, points_2, center_1, center_2, radius_1, radius_2, stl_file_path):
    plotter = pv.Plotter()
    sphere_1 = pv.Sphere(radius=radius_1, center=center_1)
    sphere_2 = pv.Sphere(radius=radius_2, center=center_2)
    
    pelvis = mesh.Mesh.from_file(stl_file_path)
    stl_mesh = pv.PolyData(np.concatenate(pelvis.vectors))
    plotter.add_mesh(sphere_1, color='red', opacity=0.5)
    plotter.add_mesh(sphere_2, color='red', opacity=0.5)
    plotter.add_mesh(stl_mesh, color='green', opacity=0.3)
    plotter.add_points(points_1, color='blue', point_size=5)
    plotter.add_points(points_2, color='blue', point_size=5)

    plotter.show()