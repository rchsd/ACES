import matlab.engine
import find_centroid as fc


eng = matlab.engine.start_matlab()
model_list = None
custom_file_name = None

def run_analysis():

    eng.cd(r'C:/MATLAB', nargout=0)

    file_path = 'c:/MATLAB/'
    custom_file_name = '1_pelvis_combined.stl'
    rotated_pelvis_name = '2_pelvis_rotated.stl'

    rotated_pelvis_index = 2

    eng.Py_StartHere(nargout = 0)

    # combines left and right halves
    #wm.combine_pelvis(model_list[0], model_list[1], file_path, custom_file_name)

    eng.Py_CombinePelvis(model_list[0], model_list[1], custom_file_name, nargout=0)
    # finds center of volume after pelvis have been combined
    centroid = fc.find_centroid(file_path + custom_file_name)

    eng.AcetabularAnalysisScript(custom_file_name, rotated_pelvis_name, rotated_pelvis_index, centroid, 1, nargout=0)
