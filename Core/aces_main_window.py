import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton)
import aces_window_dialog
        
class main_window(QMainWindow):

    def __init__(self):
         super().__init__()
         self.w = None
         self.initUI()
         self.isWindowOpen = False
         self.check = None

    def initUI(self):
        self.btn = QPushButton('Acetabular Analysis', self)
        self.btn.clicked.connect(self.runAcetabularAnalysis)
        self.statusBar()
        self.showMaximized()
        self.setWindowTitle('Matlab Analysis') 
        self.btn.resize(100, 100)
        self.show()

    def runAcetabularAnalysis(self):
        sender = self.sender()
        self.statusBar().showMessage(sender.text() + ' Running Acetabular Analysis')
        self.show_hip_selection_window()

    def resizeEvent(self, event):
        self.btn.move(self.rect().center()-self.btn.rect().topRight())
        QMainWindow.resizeEvent(self, event)

    def show_hip_selection_window(self):
        self.w = aces_window_dialog.ACES_Dialog_Window()
        self.w.show()

app = QApplication(sys.argv)
w = main_window()
w.show()
app.exec()