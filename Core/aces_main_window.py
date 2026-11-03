import sys
import os
# block the Qt warning messages from printing to the console
os.environ["QT_LOGGING_RULES"] = "*.warning=false"
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from pathlib import Path
import aces_window_dialog
import logging

######### STYLES #############################################################
COLOR_STYLE = "color: #0064a4; font-weight: bold; border-radius: 20px;"
HIGHLIGHT_STYLE = """
                    QPushButton {
                    background-color: #0064a4;
                    color: white;
                    padding: 8px;

                    border: 2px solid #0064a4;
                    border-radius: 20px;
                    font-weight: 800;
                    }
                    QPushButton:hover {
                    background-color: white;
                    color: #0064a4;
                    border: 2px solid #0064a4;
                   }
                 """
ACTIVE_STYLE = """
    QPushButton {
        background-color: white;
        color: #0064a4;
        padding: 8px;
        border: 2px solid #0064a4;
        border-radius: 20px;
        font-weight: 800;
    }
    QPushButton:hover {
        background-color: #005286;
        color: white;
        border: 2px solid #005286;
    }
"""
COMBO_BOX = """
    QComboBox {
        background-color: #0064a4;
        color: white;
        padding: 6px 12px;
        border: 2px solid #0064a4;
        border-radius: 4px;
        font-weight: bold;
        min-height: 25px;
    }
    QComboBox:hover {
        background-color: white;
        color: #0064a4;
    }
    QComboBox::drop-down {
        border: none;
        padding-right: 10px;
    }
    QComboBox QAbstractItemView {
        background-color: white;
        color: #0064a4;
        border: 1px solid #0064a4;
        selection-background-color: #0064a4;
        selection-color: white;
    }
"""

class MainWindow(QMainWindow):

    def __init__(self):
         super().__init__()
         self.dialog_window = None
         self.setGeometry(700, 300, 500, 500)
         self.setFixedSize(500, 500)
         self.initUI()


    def initUI(self):

        #Window/Icon
        self.setStyleSheet('QMainWindow {background-color: #c4e8ff; }')
        self.setWindowTitle('RCH ACES Analysis')
        ICON_PATH = Path(__file__).parent/ "images"/ "choco2.png"
        self.setWindowIcon(QIcon(str(ICON_PATH.resolve())))


        #CHOCO LOGO
        LOGO2_PATH = Path(__file__).parent / "images" / "rch-choco.png"
        self.logo_label = QLabel(self)
        self.logo_label.setContentsMargins(0, 0, 0, 0)
        self.logo_label.setGeometry(170, 30, 200, 200)
        self.logo_label.setAlignment(Qt.AlignCenter)
        if LOGO2_PATH.exists():
            self.logo_pixmap = QPixmap(str(LOGO2_PATH.resolve()))
            self.scaled_pixmap = self.logo_pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(self.scaled_pixmap)
        else:
            self.logo_label.setText("LOGO") # Safe visual fallback
            self.logo_label.setStyleSheet("font-size: 32px;")


        self.title_label = QLabel("Rady Children's Health", self)
        self.title_label.setFont(QFont('Arial', 9))
        self.title_label.setStyleSheet(COLOR_STYLE)
        self.title_label.setGeometry(0, 190, 500, 50)
        self.title_label.setAlignment(Qt.AlignCenter)
        #Label/Title
        self.title_label = QLabel('ACES', self)
        self.title_label.setFont(QFont('Arial', 45))
        self.title_label.setStyleSheet(COLOR_STYLE)
        self.title_label.setGeometry(0, 220, 500, 50)
        self.title_label.setAlignment(Qt.AlignCenter)

        #Button
        self.start_button = QPushButton('START', self)
        self.start_button.setStyleSheet(HIGHLIGHT_STYLE)
        self.start_button.setGeometry(200, 290, 100, 50)
        self.start_button.clicked.connect(self.runAcetabularAnalysis)
        self.start_button.setCursor(Qt.PointingHandCursor)

        #Button
        self.exit_button = QPushButton('EXIT', self)
        self.exit_button.setStyleSheet(HIGHLIGHT_STYLE)
        self.exit_button.setGeometry(200, 360, 100, 50)
        self.exit_button.clicked.connect(QApplication.instance().quit)
        self.exit_button.setCursor(Qt.PointingHandCursor)

        #Other
        self.statusBar()
        self.show()

    def runAcetabularAnalysis(self):
        sender = self.sender()
        self.statusBar().showMessage(sender.text() + ' Running Acetabular Analysis')
        self.show_hip_selection_window()

    def resizeEvent(self, event):
        QMainWindow.resizeEvent(self, event)

    def show_hip_selection_window(self):
        self.dialog_window = aces_window_dialog.ACES_Dialog_Window()
        self.dialog_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    logging.basicConfig(level=logging.INFO)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
