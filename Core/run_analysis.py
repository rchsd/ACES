from helper_functions import standardize_alignment, display_mesh, ui_037, load_patient, process_default, print_data, snapshot
import trimesh
import numpy as np
from pathlib import Path
import logging as log
SAVE_SNAP = Path(__file__).resolve().parent / "saved_snapshots"

def correct_mesh_transform(mesh, axis="Z"):
    #Creates a 180-degree rotation matrix around the specified axis.
    direction = [0, 1, 0] if axis == "Y" else [0, 0, 1]
    rotation_matrix = trimesh.transformations.rotation_matrix(
        angle=np.radians(180), direction=direction, point=[0, 0, 0]
    )
    return mesh.apply_transform(rotation_matrix)

def perform_analysis(pelvis_path_left, pelvis_path_right, patient_age=8, patient_sex=5):
    log.info('Starting Analysis')

    #Start the alignment process
    transformation, pelvis = standardize_alignment.align_pelvis(pelvis_path_left, pelvis_path_right)
    rotated_pelvis = pelvis.copy().apply_transform(transformation)
    display_mesh.display_mesh(rotated_pelvis)
    export_stl(rotated_pelvis)

    def apply_analysis(mesh):
        pgon = ui_037.ui_037(mesh)
        pgon_struct, metadata = load_patient.load_new_patient(pgon)
        m_data = metadata[0]
        result, fossa_dict = process_default.default(pgon_struct['mesh'], m_data['mask'], m_data['centers'], m_data['radii'])
        return pgon_struct, m_data['centers'], m_data['radii'], result, fossa_dict

    #Run main analysis
    pgon_struct, centers, radii, result, fossa_dict = apply_analysis(rotated_pelvis)

    #Orientation corrections for negative tilts
    corrections = [('right_tilt', 'Y', 'RIGHT_TILT'), ('tilt', 'Z', 'TILT')]

    for key, axis, label in corrections:
        if result[key] < 0:
            log.info(f'Reruning analysis due to negative --- {label} --- pelvis orientation')
            rotated_pelvis = correct_mesh_transform(rotated_pelvis, axis=axis)
            pgon_struct, centers, radii, result, fossa_dict = apply_analysis(rotated_pelvis)

    #Export results/snapshots and log completion
    print_data.format_and_export_to_csv(result, "final_results.csv", patient_age, patient_sex)
    snapshot.take_snapshots(pgon_struct['mesh'], centers, fossa_dict, radii, SAVE_SNAP)
    log.info("Analysis complete")

def export_stl(rotated_pelvis):
    try:
        rotated_pelvis.export('combined_pelvis.stl', file_type = 'stl')
        log.info("Combined pelvis was SUCCESSFULLY saved as an STL object!")
    except Exception as error:
        log.exception(f"An unexpected error occurred while creating the STL object: {error}")
