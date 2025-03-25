import acetabular_analysis
import find_centroid as fc
from PyQt5.QtWidgets import QWidget, QPushButton, QFileDialog

class acetabular_analysis_window(QWidget):
    
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Selection Dialog")

        self.button_model_selection = QPushButton('Run Acetabular Analysis', self)
        self.button_model_selection.clicked.connect(self.getModels)


    def getModels(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        model_names, _ = QFileDialog.getOpenFileNames(self, "Open File", 'C:\MATLAB',"STL Files (*.stl)", options=options)
        if model_names:
            acetabular_analysis.model_list = model_names
            acetabular_analysis.run_analysis()
            self.close()