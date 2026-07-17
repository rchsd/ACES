import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import aces_window_dialog

######### STYLES #############################################################
ACTIVE_STYLE = "background-color: lightblue; font-weight: bold; padding: 8px"
COLOR_STYLE = "color: #0064a4; " 
HIGHLIGHT_STYLE = """
                    QPushButton {
                    background-color: #0064a4;
                    color: white;
                    padding: 8px;
                    border: 1px azure blue;
                    }
                    QPushButton:hover {
                    background-color: white;
                    color: #0064a4;                                
                   }
                 """
COMBO_BOX =     """
                    QComboBox {
                    background-color: #0064a4;
                    color: white;
                    padding: 8px;
                    border: 1px azure blue;
                    }
                    QComboBox:hover {
                    background-color: white;
                    color: #0064a4;                                
                   }
                 """

class main_window(QMainWindow):

    def __init__(self):
         super().__init__()
         self.dialog_window = None
         self.setGeometry(700, 300, 500, 500)
         self.setFixedSize(500, 500)
         self.initUI()
         self.isWindowOpen = False
         self.check = None

    def initUI(self):

        #Window 
        self.setStyleSheet('QMainWindow {background-color: #c4e8ff; }')#a4d8f9
        self.setWindowTitle('Acetabular Analysis')

        #Label/Title
        self.title_label = QLabel('Acetabular Analysis', self)
        self.title_label.setFont(QFont('Arial', 30))
        self.title_label.setStyleSheet(COLOR_STYLE)
        #Make sure the label resizes to fit text
        self.title_label.setGeometry(0, 100, 500, 50)
        self.title_label.setAlignment(Qt.AlignCenter)
        
        #Button
        self.start_button = QPushButton('START >', self)
        self.start_button.setStyleSheet(HIGHLIGHT_STYLE)
        self.start_button.setGeometry(200, 180, 100, 50)
        self.start_button.clicked.connect(self.runAcetabularAnalysis)
        
        
        #Other 
        self.statusBar()
        self.show()

    def runAcetabularAnalysis(self):
        sender = self.sender()
        self.statusBar().showMessage(sender.text() + ' Running Acetabular Analysis')
        self.show_hip_selection_window()

    def resizeEvent(self, event):
        #self.btn.move(self.rect().center()-self.btn.rect().topLeft())
        QMainWindow.resizeEvent(self, event)

    def show_hip_selection_window(self):
        self.dialog_window = aces_window_dialog.ACES_Dialog_Window()
        self.dialog_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = main_window()
    window.show()
    sys.exit(app.exec())