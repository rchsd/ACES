import standardize_alignment
import ui_037
import numpy as np
from helper_functions import display_mesh
from helper_functions import snapshot

def perform_analysis(left_pelvis_path, right_pelvis_path):
    tform, pelvis = standardize_alignment.align_pelvis(left_pelvis_path, right_pelvis_path)
    rotated_pelvis = pelvis.copy().apply_transform(tform)
    display_mesh.display_mesh(rotated_pelvis)
    ui_037.ui_037(rotated_pelvis)

    #snapshot.take_snapshots(rotated_pelvis, 2)


    return tform, pelvis

test_file_path = 'C:\\Users\\bbeasley\\Documents\\Python Projects\\Matlab-GUI\\Tests\\Schmitz\\'
left_pelvis_path = 'c:\\Users\\bbeasley\\Documents\\Python Projects\\Matlab-GUI\\Tests\\Schmitz\\l hip 1.stl'
right_pelvis_path = 'c:\\Users\\bbeasley\\Documents\\Python Projects\\Matlab-GUI\\Tests\\Schmitz\\r hip 1.stl'
tform, pelvis = perform_analysis(left_pelvis_path, right_pelvis_path)
print(tform)
print(pelvis)