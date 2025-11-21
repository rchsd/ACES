import pyvista as pv
import numpy as np
import trimesh

def plot_best_fit_sphere(points, center, radius, mesh:trimesh):
    plotter = pv.Plotter()
    
    # Create the sphere
    sphere = pv.Sphere(radius=radius, center=center)
    
    # Convert trimesh to PyVista PolyData
    vertices = mesh.vertices
    faces = mesh.faces
    
    # PyVista expects faces in a flat array: [n_points, i0, i1, i2, ...]
    faces_pv = np.hstack([np.full((faces.shape[0], 1), 3), faces]).flatten()
    stl_mesh = pv.PolyData(vertices, faces_pv)
    
    # Add meshes and points
    plotter.add_mesh(sphere, color='red', opacity=0.5)
    plotter.add_mesh(stl_mesh, color='green', opacity=0.3)
    plotter.add_points(points, color='blue', point_size=5)
    
    plotter.show()

    # Extract vertices and faces
    vertices = sphere.points
    faces = sphere.faces.reshape(-1, 4)[:, 1:]  # PyVista stores faces with a leading count
    
    sphere_mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

    return sphere_mesh
