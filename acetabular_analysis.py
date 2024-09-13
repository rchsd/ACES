import matlab.engine
'''from PyInstaller.utils.hooks import collect_all
datas, binaries, hiddenimports = collect_all('matlab')'''

eng = matlab.engine.start_matlab()

def AnalysisQTTest():

    eng.cd(r'C:/MATLAB', nargout=0)

    # temporarily disabled for ui test
    '''folderInput = input("Please enter the location of your stl files.")
    fileNameInput = input("Please enter the name you'd like to call your new pelvis.")
    rotateddPelvisInput = input("Please enter the name of your new rotated pelvis.")'''

    folderPath = "C:/MATLAB"
    leftSTLIdx = 1
    rightSTLIdx = 2
    customFileName = 'pelvisCombined.stl'
    rotatedPelvisName = 'pelvisRotated.stl'
    # temporarily disabled for ui test
    #customNames = [fileNameInput, rotateddPelvisInput]

    rotatedPelvisIdx = 4

    # temporarily disabled for ui test
    '''for x in customNames:
        if ".stl" not in x:
            customNames[0] += ".stl"
            customNames[1] += ".stl"'''

    eng.Py_StartHere(nargout = 0)
    #eng.AcetabularAnalysisScript(folderInput, leftSTLIdx, rightSTLIdx, customNames[0], customNames[1], rotatedPelvisIdx, nargout=0)

    # test for ui
    eng.AcetabularAnalysisScript(folderPath, leftSTLIdx, rightSTLIdx, customFileName, rotatedPelvisName, rotatedPelvisIdx, nargout=0)

#AnalysisQTTest()