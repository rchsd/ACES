from helper_functions import *
import trimesh
import numpy as np
from stl import mesh
import logging

def perform_analysis(pelvis_path_left, pelvis_path_right, patient_age=8, patient_sex=5):
    logging.debug('Starting Analysis')
    
    #sends in the left and right side models of the pelvis to be aligned
    tform, pelvis = standardize_alignment.align_pelvis(pelvis_path_left, pelvis_path_right)
    logging.debug(f'this is tform after the alignment: \n\n {tform}')
    rotated_pelvis = pelvis.copy().apply_transform(tform)
    display_mesh.display_mesh(rotated_pelvis)
    try:
        rotated_pelvis.export('combined_pelvis.stl', file_type = 'stl')
        print("Combined pelvis was Successfully saved as an STL object!")
    except Exception as error:
        print(f"An unexpected error occurred while creating the STL object: {error}")

    pgon = ui_037.ui_037(rotated_pelvis)
    pgon_struct, metadata = load_patient.load_new_patient(pgon)
    mask, centers, radii, tform = metadata[0]['mask'], metadata[0]['centers'], metadata[0]['radii'], metadata[0]['tform']

    result, fossa_dict = process_default.default(pgon_struct['mesh'], mask, centers, radii)
    
    print(f"THIS IS TILT -> {result['tilt']}   AND THIS IS RIGHT_TILT -> {result['right_tilt']}")
    
    #Accounts for backward orientation
    if result['right_tilt'] < 0:
        print('Reruning analysis due to negative --- RIGHT_TILT --- pelvis orientation')
        rotated_pelvis = correct_mesh_transformY(rotated_pelvis)
        pgon = ui_037.ui_037(rotated_pelvis)
        pgon_struct, metadata = load_patient.load_new_patient(pgon)
        mask, centers, radii, tform = metadata[0]['mask'], metadata[0]['centers'], metadata[0]['radii'], metadata[0]['tform']
        result, fossa_dict = process_default.default(pgon_struct['mesh'], mask, centers, radii)
    if result['tilt'] < 0:
        print('Reruning analysis due to negative --- TILT --- pelvis orientation')
        rotated_pelvis = correct_mesh_transform(rotated_pelvis)
        pgon = ui_037.ui_037(rotated_pelvis)
        pgon_struct, metadata = load_patient.load_new_patient(pgon)
        mask, centers, radii, tform = metadata[0]['mask'], metadata[0]['centers'], metadata[0]['radii'], metadata[0]['tform']
        result, fossa_dict = process_default.default(pgon_struct['mesh'], mask, centers, radii)

    print(f'This is the result at the end \n\n\n {result}')
    
    print_data.format_and_export_to_csv(result, "final_results.csv", patient_age, patient_sex)

    snapshot.take_snapshots(pgon_struct['mesh'], centers, fossa_dict) #radii=radii) #for spheres in acetabulum
    print("Analysis complete")

def correct_mesh_transform(mesh):
    # Create a 180-degree rotation matrix around Z-axis
    rotation_matrix = trimesh.transformations.rotation_matrix(
        angle=np.radians(180),
        direction=[0, 0, 1],
        point=[0, 0, 0]
    )
    mesh.apply_transform(rotation_matrix)
    
    return mesh

def correct_mesh_transformY(mesh):
    # Create a 180-degree rotation matrix around Z-axis
    rotation_matrix = trimesh.transformations.rotation_matrix(
        angle=np.radians(180),
        direction=[0, 1, 0],
        point=[0, 0, 0]
    )
    mesh.apply_transform(rotation_matrix)
    
    return mesh
