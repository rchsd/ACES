import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, 
                             QLabel, QLineEdit, QVBoxLayout, QCheckBox, QComboBox)
from functools import partial
import acetabular_analysis
import spine_analysis

class SpineAnalysisWindow(QWidget):

    displayViewIndex = 0

    '''def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setGeometry(600, 600, 600, 300)
        self.btn3 = QPushButton('Analysis', self)
        self.btn3.clicked.connect(self.displaySpineView)
        self.setWindowTitle('Spine Analysis') 

    def displaySpineView(self):
        if self.displayViewIndex is 0:
            spine_analysis.RunAnalysis(self.displayViewIndex)'''
    
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt Checkboxes")

        spinePosition = ['Anterior', 'Posterior', 'Left', 'Right', 'Superior', 'Inferior']
        spineDisc = ['Spine Disc '] * 18


        spinePositionComboBox = QComboBox()

        for x in spinePosition:
            spinePositionComboBox.addItem(x)

        '''combobox1.addItem('Anterior')
        combobox1.addItem('Posterior')
        combobox1.addItem('Left')
        combobox1.addItem('Right')
        combobox1.addItem('Superior')
        combobox1.addItem('Inferior')'''

        layout = QVBoxLayout()
        layout.addWidget(spinePositionComboBox)

        # Create checkboxes
        self.toggleSnapshotWithDiscs = QCheckBox("Snapshot With Vertebral Discs")
        self.vertebralDiscBoxes = [None] * 18

        # Connect checkboxes to slots (functions to be called when checked/unchecked)
        self.toggleSnapshotWithDiscs.stateChanged.connect(self.toggleSnapshotWithDiscs_changed)
        #self.vertebralDiscBoxes.stateChanged.connect(self.vertebralDiscBoxes_changed(1))

        # Add checkboxes to layout
        layout.addWidget(self.toggleSnapshotWithDiscs)
        '''for i in range(18):
            if i > 0:
                spineDisc[i] = spineDisc[i] + str(i)
                self.vertebralDiscBoxes[i] = QCheckBox(spineDisc[i])
                layout.addWidget(self.vertebralDiscBoxes[i])'''
        
        for i in range(18):
            if i > 0:
                spineDisc[i] = spineDisc[i] + str(i)
                checkbox = QCheckBox(spineDisc[i])
                checkbox.stateChanged.connect(partial(self.vertebralDiscBoxes_changed, i))
                self.vertebralDiscBoxes.append(checkbox)
                layout.addWidget(checkbox)

        self.setLayout(layout)

    def toggleSnapshotWithDiscs_changed(self, state):
        if state is 1:
            if state == 2:  # 2 means checked
                print("Checkbox 1 is checked")
        else:
            print("Checkbox 1 is unchecked")

    def vertebralDiscBoxes_changed(self, index, state):
        #checkbox = self.sender

        if index is 1:
            if state == 2:
                print(index)
        elif index is 2:
            if state == 2:
                print(index)
        elif index is 3:
            if state == 2:
                print(index)
        elif index is 4:
            if state == 2:
                print(index)
        elif index is 5:
            if state == 2:
                print(index)
        elif index is 6:
            if state == 2:
                print(index)
        elif index is 7:
            if state == 2:
                print(index)
        elif index is 8:
            if state == 2:
                print(index)
        elif index is 9:
            if state == 2:
                print(index)
        elif index is 10:
            if state == 2:
                print(index)
        elif index is 11:
            if state == 2:
                print(index)
        elif index is 12:
            if state == 2:
                print(index)
        elif index is 13:
            if state == 2:
                print(index)
        elif index is 14:
            if state == 2:
                print(index)
        elif index is 2:
            if state == 15:
                print(index)
        elif index is 16:
            if state == 2:
                print(index)
        elif index is 17:
            if state == 2:
                print(index)
        
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