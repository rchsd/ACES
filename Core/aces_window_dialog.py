from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QMessageBox, QPushButton, QFileDialog
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
from aces_main_window import ACTIVE_STYLE, HIGHLIGHT_STYLE, COLOR_STYLE, COMBO_BOX
import run_analysis

class ACES_Dialog_Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ACES Window Dialog")
        self.setGeometry(200, 200, 300, 220)
        self.setFixedSize(300, 220)
        self.setStyleSheet('QWidget {background-color: white; }')
        LOGO1_PATH = Path(__file__).parent / "choco2.png"
        self.setWindowIcon(QIcon(str(LOGO1_PATH.resolve())))

        # Track selections
        self.selected_option = None
        self.dropdown_value = None

        # Layouts
        self.main_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()

        # Patient Information Title Label
        self.title_label =  QLabel("Patient Information", self)
        self.title_label.setFont(QFont('Arial', 15))
        self.title_label.setStyleSheet(COLOR_STYLE)
        self.main_layout.addWidget(self.title_label)


        # Question label for buttons
        self.question_label = QLabel("Gender:", self)
        self.question_label.setFont(QFont('Arial', 10))
        self.question_label.setStyleSheet(COLOR_STYLE)
        self.main_layout.addWidget(self.question_label)

        # Buttons for choices
        self.button1 = QPushButton("Female", self)
        self.button1.setStyleSheet(HIGHLIGHT_STYLE)
        self.button1.clicked.connect(lambda: self.set_choice(1))
        self.button1.setCursor(Qt.PointingHandCursor)
        self.button_layout.addWidget(self.button1)

        self.button2 = QPushButton("Male", self)
        self.button2.setStyleSheet(HIGHLIGHT_STYLE)
        self.button2.clicked.connect(lambda: self.set_choice(2))
        self.button2.setCursor(Qt.PointingHandCursor)
        self.button_layout.addWidget(self.button2)

        self.main_layout.addLayout(self.button_layout)


        # Instruction label for dropdown
        self.dropdown_label = QLabel("Age:", self)
        self.dropdown_label.setFont(QFont('Arial', 10))
        self.dropdown_label.setStyleSheet(COLOR_STYLE)
        self.dropdown_label.setCursor(Qt.PointingHandCursor)
        self.main_layout.addWidget(self.dropdown_label)

        # Dropdown for values 8 to 18
        self.dropdown = QComboBox(self)
        self.dropdown.setStyleSheet(COMBO_BOX)
        self.dropdown.addItem("Select a value")  # Placeholder
        for i in range(8, 19):
            self.dropdown.addItem(str(i))
        self.dropdown.currentIndexChanged.connect(self.set_dropdown_value)
        self.dropdown.setCursor(Qt.PointingHandCursor)
        self.main_layout.addWidget(self.dropdown)

        # Continue button
        self.continue_button = QPushButton("Run Analysis", self)
        self.continue_button.setFont(QFont('Arial', 10))
        self.continue_button.setStyleSheet(HIGHLIGHT_STYLE)
        self.continue_button.clicked.connect(self.on_continue)
        self.continue_button.setCursor(Qt.PointingHandCursor)
        self.main_layout.addWidget(self.continue_button)

        self.setLayout(self.main_layout)

    def set_choice(self, choice):
        self.selected_option = choice
        # Highlight selected button
        if choice == 1:
            self.button1.setStyleSheet(ACTIVE_STYLE)
            self.button2.setStyleSheet(HIGHLIGHT_STYLE)
            self.button_value = 5
        else:
            self.button2.setStyleSheet(ACTIVE_STYLE)
            self.button1.setStyleSheet(HIGHLIGHT_STYLE)
            self.button_value = 6

    def set_dropdown_value(self):
        if self.dropdown.currentIndex() > 0:  # Ignore placeholder
            self.dropdown_value = int(self.dropdown.currentText())
        else:
            self.dropdown_value = None

    def on_continue(self):
        if self.selected_option is None or self.dropdown_value is None:
            QMessageBox.warning(self, "Incomplete", "Please make both selections before continuing.")
        else:
            self.getModels()

    def getModels(self):
        options = QFileDialog.Options()
        model_names, _ = QFileDialog.getOpenFileNames(self, "Open File", "C:\\","STL Files (*.stl)", options=options)
        if model_names:
            self.close()
            run_analysis.perform_analysis(model_names[0], model_names[1], self.dropdown_value, self.button_value)
