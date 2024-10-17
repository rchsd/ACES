import matlab.engine
'''from PyInstaller.utils.hooks import collect_all
datas, binaries, hiddenimports = collect_all('matlab')'''

eng = matlab.engine.start_matlab()

def run_analysis():

    eng.cd(r'C:/MATLAB', nargout=0)

    # temporarily disabled for ui test, use for console input
    '''folderInput = input("Please enter the location of your stl files.")
    fileNameInput = input("Please enter the name you'd like to call your new pelvis.")
    rotateddPelvisInput = input("Please enter the name of your new rotated pelvis.")'''

    folder_path = "C:/MATLAB"
    left_stl_index = 1
    right_stl_index = 2
    custom_file_name = 'pelvisCombined.stl'
    rotated_pelvis_name = 'pelvisRotated.stl'
    # temporarily disabled for ui test, use for console input
    #customNames = [fileNameInput, rotateddPelvisInput]

    rotated_pelvis_index = 4

    # temporarily disabled for ui test, use for console input
    '''for x in customNames:
        if ".stl" not in x:
            customNames[0] += ".stl"
            customNames[1] += ".stl"'''

    eng.Py_StartHere(nargout = 0)
    # use for console input
    #eng.AcetabularAnalysisScript(folderInput, leftSTLIdx, rightSTLIdx, customNames[0], customNames[1], rotatedPelvisIdx, nargout=0)

    # test for ui, use for console input
    eng.AcetabularAnalysisScript(folder_path, left_stl_index, right_stl_index, custom_file_name, rotated_pelvis_name, rotated_pelvis_index, nargout=0)