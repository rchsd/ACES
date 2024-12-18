import sys
import matlab.engine
sys.path.insert(1, 'C:\\Users\\bbeasley\\Documents\\Python Projects\\MATLAB-GUI\\Core')

import find_centroid as fc

eng = matlab.engine.start_matlab()

def run_test():
    eng.cd(r'C:/MATLAB', nargout=0)
    eng.Py_StartHere(nargout = 0)
    centroid_of_volume = fc.find_centroid('c:\MATLAB\Combined_Pelvis.stl')
    #print(centroid_of_volume)
    eng.Py_Compare_Pgoncent(centroid_of_volume, nargout=0)

run_test()

