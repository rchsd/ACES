from helper_functions import *
import trimesh
import numpy as np

def perform_analysis(left_pelvis_path, right_pelvis_path, patient_age=8, patient_sex=5):
    print('Starting Analysis')
    tform, pelvis = standardize_alignment.align_pelvis(left_pelvis_path, right_pelvis_path)
    rotated_pelvis = pelvis.copy().apply_transform(tform)
    display_mesh.display_mesh(rotated_pelvis)

    pgon = ui_037.ui_037(rotated_pelvis)
    pgon_struct, metadata = load_patient.load_new_patient(pgon)
    mask, centers, radii, tform = metadata[0]['mask'], metadata[0]['centers'], metadata[0]['radii'], metadata[0]['tform']
    result = process_default.default(pgon_struct['mesh'], mask, centers, radii)

    # Accounts for backward orientation
    if result['tilt'] < 0:
        print('Reruning analysis due to negative pelvis orientation')
        rotated_pelvis = correct_mesh_transform(rotated_pelvis)
        pgon = ui_037.ui_037(rotated_pelvis)
        pgon_struct, metadata = load_patient.load_new_patient(pgon)
        mask, centers, radii, tform = metadata[0]['mask'], metadata[0]['centers'], metadata[0]['radii'], metadata[0]['tform']
        result = process_default.default(pgon_struct['mesh'], mask, centers, radii)

    print_data.format_and_export_to_csv(result, "final_results.csv", patient_age, patient_sex)
    print("Analysis complete")

    snapshot.take_snapshots(rotated_pelvis, 2)

def correct_mesh_transform(mesh):
    # Create a 180-degree rotation matrix around Z-axis
    rotation_matrix = trimesh.transformations.rotation_matrix(
        angle=np.radians(180),
        direction=[0, 0, 1],
        point=[0, 0, 0]
    )
    mesh.apply_transform(rotation_matrix)

    return mesh

test_file_path = 'C:\\Users\\bbeasley\\Documents\\Python Projects\\Matlab-GUI\\Tests\\Schmitz\\'
left_pelvis_path = 'c:\\Users\\bbeasley\\Documents\\Python Projects\\Matlab-GUI\\Tests\\Schmitz\\l hip 1.stl'
right_pelvis_path = 'c:\\Users\\bbeasley\\Documents\\Python Projects\\Matlab-GUI\\Tests\\Schmitz\\r hip 1.stl'
perform_analysis('c:\\Users\\bbeasley\\Documents\\Python Projects\\Matlab-GUI\\Validation\\16yoM_80\\Left Hip.stl', 
                 'c:\\Users\\bbeasley\\Documents\\Python Projects\\Matlab-GUI\\Validation\\16yoM_80\\Right Hip.stl')