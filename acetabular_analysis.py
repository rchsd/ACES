import matlab.engine

eng = matlab.engine.start_matlab()

def RunAnalysis():

    eng.cd(r'C:/MATLAB', nargout=0)

    # temporarily disabled for ui test, use for console input
    '''folderInput = input("Please enter the location of your stl files.")
    fileNameInput = input("Please enter the name you'd like to call your new pelvis.")
    rotateddPelvisInput = input("Please enter the name of your new rotated pelvis.")'''

    folderPath = "C:/MATLAB"
    leftSTLIdx = 1
    rightSTLIdx = 2
    customFileName = 'pelvisCombined.stl'
    rotatedPelvisName = 'pelvisRotated.stl'
    # temporarily disabled for ui test, use for console input
    #customNames = [fileNameInput, rotateddPelvisInput]

    rotatedPelvisIdx = 4

    # temporarily disabled for ui test, use for console input
    '''for x in customNames:
        if ".stl" not in x:
            customNames[0] += ".stl"
            customNames[1] += ".stl"'''

    eng.Py_StartHere(nargout = 0)
    # use for console input
    #eng.AcetabularAnalysisScript(folderInput, leftSTLIdx, rightSTLIdx, customNames[0], customNames[1], rotatedPelvisIdx, nargout=0)

    # test for ui, use for console input
    eng.AcetabularAnalysisScript(folderPath, leftSTLIdx, rightSTLIdx, customFileName, rotatedPelvisName, rotatedPelvisIdx, nargout=0)

#AnalysisQTTest()