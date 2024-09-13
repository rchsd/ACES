from PyQt6.QtCore import Qt
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton
import Tester_Class as tc

import sys

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("Tester app")

        label = QLabel("Test label")
        label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setCentralWidget(label)

        button = QPushButton("Press me!")
        button.setCheckable(True)
        button.clicked.connect(self.button_clicked)
        self.setCentralWidget(button)


    def button_clicked(self):
        tc.write_and_display_models(model_1, model_2, model_name)
        print("Clicked")

app = QApplication(sys.argv)

model_1 = 'c:/STLs/Reduced_Smoothed_Right_new_001.stl'
model_2 = 'c:/STLs/Reduced_Smoothed_Left_new_001.stl'
model_name = 'c:/STLs/new9.stl'

window = MainWindow()
window.show()

app.exec()