import sys
import acetabular_analysis
from PyQt5.QtCore import Qt
#from PyQt5.QtGui import QAction
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QLineEdit, QVBoxLayout, QWidget, QLabel

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.show()
        self.setWindowTitle("Orthopedics Analysis Library")

        label = QLabel("Please type in the name for your stl model")
        label.setAlignment(Qt.AlignmentFlag.AlignTop)
        #self.setCentralWidget(label)

        self.input = QLineEdit()

        layout = QVBoxLayout()
        layout.addWidget(self.input)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_context_menu)

    def on_context_menu(self, pos):
        context = QMenu(self)
        #action_1 = QAction("Acetabular Analysis", self)
        #action_2 = QAction("Spine Analysis", self)

        context.addAction("Acetabular Analysis", self)
        context.addAction("Spine Analysis", self)
        #context.addAction(QAction("test 3", self))

        #action_1.triggered.connect(self.trigger_action)
        context.exec(self.mapToGlobal(pos))

    def trigger_action(self):
        outputFileName = self.input.text()
        outputFileLocation = 'c:/STLs/' + outputFileName
        #outputFileLocation = self.label.text()

        if outputFileName == "":
            outputFileName = 'new_stl.stl'
            outputFileLocation = 'c:/STLs/' + outputFileName

        print(outputFileLocation)
        
        #tc.write_and_display_models('c:/STLs/Reduced_Smoothed_Right_new_001.stl', 'c:/STLs/Reduced_Smoothed_Left_new_001.stl', outputFileLocation + ".stl")
        #acetabular_analysis.AnalysisQTTest()

        


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()