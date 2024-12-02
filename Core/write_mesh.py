import trimesh

def combine_pelvis(left_hip, right_hip, new_pelvis_location, pelvis_name):
    mesh1 = trimesh.load(left_hip)
    mesh2 = trimesh.load(right_hip)

    combined = mesh1 + mesh2
    combined.export(new_pelvis_location + pelvis_name)