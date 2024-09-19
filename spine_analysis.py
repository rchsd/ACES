import matlab.engine

eng = matlab.engine.start_matlab()

def RunAnalysis(index):

    eng.cd(r'C:/MATLAB', nargout=0)

    folderPath = "C:/Users/bbeasley/Documents/Carrie Dicoms/3D Dicoms for Figure/2 yr Dicoms"

    customFileName = 'Spine'
    customPosition = ['Anterior', 'Posterior', 'Left', 'Right', 'Superior', 'Inferior']
    #index = 0

    eng.Py_StartHere(nargout = 0)

    eng.SpineAnalysisScript(folderPath, customFileName, customPosition[index], nargout=0)