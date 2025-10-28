import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton)
import acetabular_analysis_window
        
class main_window(QMainWindow):

    def __init__(self):
         super().__init__()
         self.w = None
         self.initUI()
         self.isWindowOpen = False
         self.check = None

    def initUI(self):
        self.btn_1 = QPushButton('Spine Analysis', self)
        self.btn_2 = QPushButton('Acetabular Analysis', self)
        self.btn_1.clicked.connect(self.runSpineAnalysis)
        self.btn_2.clicked.connect(self.runAcetabularAnalysis)
        self.statusBar()
        self.showMaximized()
        self.setWindowTitle('Matlab Analysis') 
        self.btn_1.resize(100, 100)
        self.btn_2.resize(100, 100)
        self.show()

    def runSpineAnalysis(self):
        sender = self.sender()
        self.statusBar().showMessage(sender.text() + ' Running Spine Analysis')
        self.show_spine_window()

    def runAcetabularAnalysis(self):
        sender = self.sender()
        self.statusBar().showMessage(sender.text() + ' Running Acetabular Analysis')
        self.show_hip_selection_window()


    def resizeEvent(self, event):
        self.btn_1.move(self.rect().center()-self.btn_1.rect().topRight())
        self.btn_2.move(self.rect().center()-self.btn_2.rect().topLeft())
        QMainWindow.resizeEvent(self, event)

    '''def show_spine_window(self):
        self.w = spine_analysis_window.spine_analysis_window()
        self.w.show()'''

    def show_hip_selection_window(self):
        self.w = acetabular_analysis_window.acetabular_analysis_window()
        self.w.show()

app = QApplication(sys.argv)
w = main_window()
w.show()
app.exec()