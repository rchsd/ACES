import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, 
                             QVBoxLayout, QCheckBox, QComboBox, QFileDialog)
from functools import partial
from pathlib import Path
import acetabular_analysis
import spine_analysis

class SpineAnalysisWindow(QWidget):

    displayViewIndex = 0
    
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt Checkboxes")

        self.spineButton = QPushButton('Run Spine Analysis', self)
        self.spineButton.clicked.connect(self.setDicomFileDirectory)

        self.spinePosition = ['Anterior', 'Posterior', 'Left', 'Right', 'Superior', 'Inferior']
        spineDisc = ['Spine Disc '] * 18


        self.spinePositionComboBox = QComboBox()

        for x in self.spinePosition:
            self.spinePositionComboBox.addItem(x)

        layout = QVBoxLayout()
        self.setGeometry(600, 600, 600, 300)
        layout.addWidget(self.spineButton)
        layout.addWidget(self.spinePositionComboBox)

        # Create checkboxes
        self.toggleSnapshotWithDiscs = QCheckBox("Snapshot With Vertebral Discs")
        self.vertebralDiscBoxes = [None] * 18

        # Connect checkboxes to slots (functions to be called when checked/unchecked)
        self.toggleSnapshotWithDiscs.stateChanged.connect(self.toggleSnapshotWithDiscs_changed)

        # Add checkboxes to layout
        layout.addWidget(self.toggleSnapshotWithDiscs)
        
        for i in range(18):
            if i > 0:
                spineDisc[i] = spineDisc[i] + str(i)
                checkbox = QCheckBox(spineDisc[i])
                checkbox.stateChanged.connect(partial(self.vertebralDiscBoxes_changed, i))
                self.vertebralDiscBoxes.append(checkbox)
                layout.addWidget(checkbox)

        self.setLayout(layout)

    def setDicomFileDirectory(self):
        # file dialog
        dir_name = QFileDialog.getExistingDirectory(self, "Select a Directory")
        if dir_name:
            path = Path(dir_name)
            # will prompt user to select director for dicoms before creating images
            spine_analysis.folderPath = str(path)
            self.displaySpineView()


#not working
    def displaySpineView(self):
        '''if self.spinePositionComboBox.currentText() is self.spinePosition[0]:
            spine_analysis.customSpinePosition = str(self.spinePosition[0])
        elif self.spinePositionComboBox.currentText() is self.spinePosition[1]:
            spine_analysis.customSpinePosition = self.spinePosition[1]
        elif self.spinePositionComboBox.currentText() is self.spinePosition[2]:
            spine_analysis.customSpinePosition = self.spinePosition[2]
        elif self.spinePositionComboBox.currentText() is self.spinePosition[3]:
            spine_analysis.customSpinePosition = self.spinePosition[3]
        elif self.spinePositionComboBox.currentText() is self.spinePosition[4]:
            spine_analysis.customSpinePosition = self.spinePosition[4]
        elif self.spinePositionComboBox.currentText() is self.spinePosition[5]:
            spine_analysis.customSpinePosition = self.spinePosition[5]'''

        spine_analysis.RunAnalysis()

    def toggleSnapshotWithDiscs_changed(self, state):
        if state is 1:
            if state == 2:  # 2 means checked
                print("Checkbox 1 is checked")
        else:
            print("Checkbox 1 is unchecked")

    def vertebralDiscBoxes_changed(self, index, state):

        if index is 1:
            if state == 2:
                spine_analysis.alphas[0] = 1
            else:
                spine_analysis.alphas[0] = 0
        elif index is 2:
            if state == 2:
                spine_analysis.alphas[1] = 1
            else:
                spine_analysis.alphas[1] = 0
        elif index is 3:
            if state == 2:
                spine_analysis.alphas[2] = 1
            else:
                spine_analysis.alphas[2] = 0
        elif index is 4:
            if state == 2:
                spine_analysis.alphas[3] = 1
            else:
                spine_analysis.alphas[3] = 0
        elif index is 5:
            if state == 2:
                spine_analysis.alphas[4] = 1
            else:
                spine_analysis.alphas[4] = 0
        elif index is 6:
            if state == 2:
                spine_analysis.alphas[5] = 1
            else:
                spine_analysis.alphas[5] = 0
        elif index is 7:
            if state == 2:
                spine_analysis.alphas[6] = 1
            else:
                spine_analysis.alphas[6] = 0
        elif index is 8:
            if state == 2:
                spine_analysis.alphas[7] = 1
            else:
                spine_analysis.alphas[7] = 0
        elif index is 9:
            if state == 2:
                spine_analysis.alphas[8] = 1
        elif index is 10:
            if state == 2:
                spine_analysis.alphas[9] = 1
            else:
                spine_analysis.alphas[9] = 0
        elif index is 11:
            if state == 2:
                spine_analysis.alphas[10] = 1
            else:
                spine_analysis.alphas[10] = 0
        elif index is 12:
            if state == 2:
                spine_analysis.alphas[11] = 1
            else:
                spine_analysis.alphas[11] = 0
        elif index is 13:
            if state == 2:
                spine_analysis.alphas[12] = 1
            else:
                spine_analysis.alphas[12] = 0
        elif index is 14:
            if state == 2:
                spine_analysis.alphas[13] = 1
            else:
                spine_analysis.alphas[13] = 0
        elif index is 2:
            if state == 15:
                spine_analysis.alphas[14] = 1
            else:
                spine_analysis.alphas[14] = 0
        elif index is 16:
            if state == 2:
                spine_analysis.alphas[15] = 1
            else:
                spine_analysis.alphas[15] = 0
        elif index is 17:
            if state == 2:
                spine_analysis.alphas[16] = 1
            else:
                spine_analysis.alphas[16] = 0
        
class MainWindow(QMainWindow):

    def __init__(self):
         super().__init__()
         self.w = None
         self.initUI()
         self.isWindowOpen = False

    def initUI(self):
        scriptSelectionComboBox = QComboBox()
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