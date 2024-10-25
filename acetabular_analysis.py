import matlab.engine

eng = matlab.engine.start_matlab()

def run_analysis():

    eng.cd(r'C:/MATLAB', nargout=0)

    folder_path = "C:/MATLAB"
    left_stl_index = 1
    right_stl_index = 2
    custom_file_name = 'pelvisCombined.stl'
    rotated_pelvis_name = 'pelvisRotated.stl'

    rotated_pelvis_index = 3

    eng.Py_StartHere(nargout = 0)

    eng.AcetabularAnalysisScript(folder_path, left_stl_index, right_stl_index, custom_file_name, rotated_pelvis_name, rotated_pelvis_index, nargout=0)