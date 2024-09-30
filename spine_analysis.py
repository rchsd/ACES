import matlab.engine

eng = matlab.engine.start_matlab()

alphas = [0] * 17
folderPath = None

customSpinePosition = None

def RunAnalysis():

    eng.cd(r'C:/MATLAB', nargout=0)

    #folderPath = "C:/Users/bbeasley/Documents/Carrie Dicoms/3D Dicoms for Figure/2 yr Dicoms"

    customFileName = 'Spine'
    #customPosition = ['Anterior', 'Posterior', 'Left', 'Right', 'Superior', 'Inferior']

    eng.Py_StartHere(nargout = 0)

    eng.SpineAnalysisScript(folderPath, customFileName, customSpinePosition, alphas[0], alphas[1], alphas[2], alphas[3], alphas[4], alphas[5], alphas[6],alphas[7],
    alphas[8], alphas[9], alphas[10], alphas[11], alphas[12], alphas[13], alphas[14],
    alphas[15], alphas[16], nargout=0)