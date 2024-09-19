import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel, QLineEdit
import acetabular_analysis
import spine_analysis

class SpineAnalysisWindow(QWidget):

    displayViewIndex = 0

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setGeometry(600, 600, 600, 300)
        self.btn3 = QPushButton('Analysis', self)
        self.btn3.clicked.connect(self.displaySpineView)
        self.setWindowTitle('Spine Analysis') 

    def displaySpineView(self):
        if self.displayViewIndex is 0:
            spine_analysis.RunAnalysis(self.displayViewIndex)

class MainWindow(QMainWindow):

    def __init__(self):
         super().__init__()
         self.w = None
         self.initUI()
         self.isWindowOpen = False

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
        self.show_new_window()

    def runAcetabularAnalysis(self):
        sender = self.sender()
        self.statusBar().showMessage(sender.text() + ' Running Acetabular Analysis')
        acetabular_analysis.RunAnalysis()


    def resizeEvent(self, event):
        self.btn_1.move(self.rect().center()-self.btn_1.rect().topRight())
        self.btn_2.move(self.rect().center()-self.btn_2.rect().topLeft())
        QMainWindow.resizeEvent(self, event)

    def show_new_window(self):
        if self.isWindowOpen is False:
                self.isWindowOpen = True
                self.w = SpineAnalysisWindow()
                self.w.show()

        else: return

app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()