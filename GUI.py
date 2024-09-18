import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel, QLineEdit
from random import randint
import acetabular_analysis

class AnotherWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        '''self.label = QLabel("Another Window % d" % randint(0,100))
        layout.addWidget(self.label)'''
        self.setLayout(layout)
        self.setGeometry(600, 600, 600, 300)
        self.btn3 = QPushButton('Analysis', self)
        self.setWindowTitle('Spine Analysis') 

class MainWindow(QMainWindow):

    def __init__(self):
         super().__init__()
         self.w = None
         self.initUI()
         self.i = 0

    def initUI(self):
        self.btn_1 = QPushButton('Spine Analysis', self)
        self.btn_2 = QPushButton('Acetabular Analysis', self)
        #self.btn1.move(30, 50)
        #self.btn2.move(150, 50)
        self.btn_1.clicked.connect(self.runSpineAnalysis)
        self.btn_2.clicked.connect(self.runAcetabularAnalysis)
        self.statusBar()
        #self.setGeometry(600, 600, 600, 300)
        self.showMaximized()
        self.setWindowTitle('Matlab Analysis') 
        self.btn_1.resize(100, 100)
        self.btn_2.resize(100, 100)
        self.show()
        self.show()

    def toggle_window(self, checked):
        if self.w.isVisible(True):
            self.w.hide()

        else:
            self.w.show()

    def runSpineAnalysis(self):
        sender = self.sender()
        self.statusBar().showMessage(sender.text() + ' Running Spine Analysis')
        #self.btn_1.clicked.connect(self.show_new_window)
        self.show_new_window()
        #self.setCentralWidget(self.btn2)

    def runAcetabularAnalysis(self):
        sender = self.sender()
        self.statusBar().showMessage(sender.text() + ' Running Acetabular Analysis')
        acetabular_analysis.RunAnalysis()


    def resizeEvent(self, event):
        self.btn_1.move(self.rect().center()-self.btn_1.rect().topRight())
        self.btn_2.move(self.rect().center()-self.btn_2.rect().topLeft())
        QMainWindow.resizeEvent(self, event)

    def show_new_window(self):
        self.w = AnotherWindow()
        self.i += 1
        print(self.i)
        self.w.show()
        self.w.show()
        print('displayed')

app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()

'''if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())'''