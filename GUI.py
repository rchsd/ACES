import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
import acetabular_analysis

class Window(QMainWindow):

    def __init__(self):
         super().__init__()
         self.initUI()

    def initUI(self):
        #self.btn1 = QPushButton('Spine Analysis', self)
        #self.btn1.move(30, 50)
        self.btn2 = QPushButton('Acetabular Analysis', self)
        self.btn2.move(150, 50)
        #self.btn1.clicked.connect(self.runSpineAnalysis)
        self.btn2.clicked.connect(self.runAcetabularAnalysis)
        self.statusBar()
        self.setGeometry(300, 300, 300, 150)
        self.setWindowTitle('Matlab Analysis') 
        #self.btn1.resize(100, 100)
        self.btn2.resize(100, 100)
        self.show()
        self.show()

    def runSpineAnalysis(self):
        sender = self.sender()
        self.statusBar().showMessage(sender.text() + ' Running Spine Analysis')

    def runAcetabularAnalysis(self):
        sender = self.sender()
        self.statusBar().showMessage(sender.text() + ' Running Acetabular Analysis')
        acetabular_analysis.AnalysisQTTest()


    def resizeEvent(self, event):
        #self.btn1.move(self.rect().center()-self.btn1.rect().center())
        self.btn2.move(self.rect().center()-self.btn2.rect().center())
        QMainWindow.resizeEvent(self, event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Window()
    sys.exit(app.exec_())