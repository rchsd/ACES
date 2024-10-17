import matlab.engine

eng = matlab.engine.start_matlab()

alphas = [0] * 17
folder_path = None

custom_spine_position = None

def run_analysis():

    eng.cd(r'C:/MATLAB', nargout=0)

    custom_file_name = 'Spine'

    eng.Py_StartHere(nargout = 0)

    eng.SpineAnalysisScript(folder_path, custom_file_name, custom_spine_position, alphas[0], alphas[1], alphas[2], alphas[3], alphas[4], alphas[5], alphas[6],alphas[7],
    alphas[8], alphas[9], alphas[10], alphas[11], alphas[12], alphas[13], alphas[14],
    alphas[15], alphas[16], nargout=0)