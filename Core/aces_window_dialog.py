import sys
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QMessageBox, QPushButton, QFileDialog
)
import run_analysis

class ACES_Dialog_Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ACES Window Dialog")
        self.setGeometry(200, 200, 300, 220)

        # Track selections
        self.selected_option = None
        self.dropdown_value = None

        # Layouts
        main_layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        # Question label for buttons
        question_label = QLabel("Is the patient male or female?")
        main_layout.addWidget(question_label)

        # Buttons for choices
        self.btn1 = QPushButton("Female")
        self.btn2 = QPushButton("Male")
        self.btn1.clicked.connect(lambda: self.set_choice(1))
        self.btn2.clicked.connect(lambda: self.set_choice(2))

        button_layout.addWidget(self.btn1)
        button_layout.addWidget(self.btn2)
        main_layout.addLayout(button_layout)

        # Instruction label for dropdown
        dropdown_label = QLabel("How old is the patient?")
        main_layout.addWidget(dropdown_label)

        # Dropdown for values 8 to 18
        self.dropdown = QComboBox()
        self.dropdown.addItem("Select a value")  # Placeholder
        for i in range(8, 19):
            self.dropdown.addItem(str(i))
        self.dropdown.currentIndexChanged.connect(self.set_dropdown_value)
        main_layout.addWidget(self.dropdown)

        # Continue button
        self.continue_btn = QPushButton("Run Analysis")
        self.continue_btn.clicked.connect(self.on_continue)
        main_layout.addWidget(self.continue_btn)

        self.setLayout(main_layout)

    def set_choice(self, choice):
        self.selected_option = choice
        # Highlight selected button
        if choice == 1:
            self.btn1.setStyleSheet("background-color: lightblue; font-weight: bold;")
            self.btn2.setStyleSheet("")
            self.btn_value = 5
        else:
            self.btn2.setStyleSheet("background-color: lightblue; font-weight: bold;")
            self.btn1.setStyleSheet("")
            self.btn_value = 6

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
        options |= QFileDialog.DontUseNativeDialog
        model_names, _ = QFileDialog.getOpenFileNames(self, "Open File", 'C:\\Users\\bbeasley\\Documents\\Python Projects\\Matlab-GUI\\Validation',"STL Files (*.stl)", options=options)
        if model_names:
            self.close()
            run_analysis.perform_analysis(model_names[0], self.dropdown_value, self.btn_value)