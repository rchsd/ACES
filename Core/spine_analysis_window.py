import spine_analysis
from functools import partial
from pathlib import Path
from PyQt5.QtWidgets import QWidget, QPushButton, QComboBox, QVBoxLayout, QCheckBox, QFileDialog

class spine_analysis_window(QWidget):

    displayViewIndex = 0
    
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt Checkboxes")

        self.spineButton = QPushButton('Run Spine Analysis', self)
        self.spineButton.clicked.connect(self.setDicomFileDirectory)

        self.spinePosition = ['Anterior', 'Posterior', 'Left', 'Right', 'Superior', 'Inferior']
        spineDisc = ['Spine Disc '] * 18


        self.spinePositionComboBox = QComboBox()
        self.spinePositionComboBox.activated.connect(self.setSpineView)

        for x in self.spinePosition:
            self.spinePositionComboBox.addItem(x)

        layout = QVBoxLayout()
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
            spine_analysis.folder_path = str(path)
            #function that creates the images, also setting initial combox index so that default analysis can run
            if spine_analysis.custom_spine_position is None:
                spine_analysis.custom_spine_position = 'Anterior'
                spine_analysis.run_analysis()

    def setSpineView(self, index):
        if index is 0:
            spine_analysis.custom_spine_position = 'Anterior'
        elif index is 1:
            spine_analysis.custom_spine_position = 'Posterior'
        elif index is 2:
            spine_analysis.custom_spine_position = 'Left'
        elif index is 3:
            spine_analysis.custom_spine_position = 'Right'
        elif index is 4:
            spine_analysis.custom_spine_position = 'Superior'
        elif index is 4: # maybe its 5? -------- 5/29
            spine_analysis.custom_spine_position = 'Inferior'

    def toggleSnapshotWithDiscs_changed(self, state):
        if state is 1:
            if state == 2:  # 2 means checked
                print("Checkbox 1 is checked")
        else:
            print("Checkbox 1 is unchecked")

    def vertebralDiscBoxes_changed(self, index, state):
        # Can/will be cleaned up ------ 5/29 
        if index is 1:
            i = 1 if state == 2 else 0
            spine_analysis.alphas[index-1] = i
        elif index is 2:
            i = 1 if state == 2 else 0
            spine_analysis.alphas[index-1] = i
        elif index is 3:
            i = 1 if state == 2 else 0
            spine_analysis.alphas[index-1] = i
        elif index is 4:
            i = 1 if state == 2 else 0
            spine_analysis.alphas[index-1] = i
        elif index is 5:
            i = 1 if state == 2 else 0
            spine_analysis.alphas[index-1] = i
        elif index is 6:
            i = 1 if state == 2 else 0
            spine_analysis.alphas[index-1] = i
        elif index is 7:
            i = 1 if state == 2 else 0
            spine_analysis.alphas[index-1] = i
        elif index is 8:
            i = 1 if state == 2 else 0
            spine_analysis.alphas[index-1] = i
        elif index is 9:
            i = 1 if state == 2 else 0
            spine_analysis.alphas[index-1] = i
        elif index is 10:
            i = 1 if state == 2 else 0
            spine_analysis.alphas[index-1] = i
        elif index is 11:
            i = 1 if state == 2 else 0
            spine_analysis.alphas[index-1] = i
        elif index is 12:
            i = 1 if state == 2 else 0
            spine_analysis.alphas[index-1] = i
        elif index is 13:
            i = 1 if state == 2 else 0
            spine_analysis.alphas[index-1] = i
        elif index is 14:
            i = 1 if state == 2 else 0
            spine_analysis.alphas[index-1] = i
        elif index is 15:
            i = 1 if state == 2 else 0
            spine_analysis.alphas[index-1] = i
        elif index is 16:
            i = 1 if state == 2 else 0
            spine_analysis.alphas[index-1] = i
        elif index is 17:
            i = 1 if state == 2 else 0
            spine_analysis.alphas[index-1] = i