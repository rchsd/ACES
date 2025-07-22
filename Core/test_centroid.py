# test to find centroid of vertices and faces
import trimesh

# Load the STL file
mesh = trimesh.load('c:\\MATLAB\\1_Combined_Pelvis.stl')

# Accessing data
print("Vertices:", mesh.vertices)
print("Faces:", mesh.faces)
print("Number of vertices:", len(mesh.vertices))
print("Number of faces:", len(mesh.faces))