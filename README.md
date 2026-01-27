# ACES Acetabular Coverage Analysis (Python GUI)

This repository contains a PyQt-based graphical application for performing automated acetabular coverage analysis on pelvic STL models. The tool guides the user through pelvis alignment, acetabulum detection, fossa selection, coverage angle calculations, and automated results export.

---

## Installation

### 1. Clone the Repository
```
git clone https://github.com/3DILab/Matlab-GUI.git
cd Matlab-GUI
```

### 2. Create and Activate a Virtual Environment
Python 3.10 or higher is supported. This project was developed using Python 3.13.
```
python3.13 -m venv venv
source venv/bin/activate     # macOS/Linux
venv\Scriptsctivate        # Windows
```

### 3. Install Python Dependencies
```
pip install -r requirements.txt
```

---

## Running the Application

The main application entry point is:
```
Matlab-GUI/Core/aces_main_window.py
```
Run it using:
```
python Core/aces_main_window.py
```

---

## How to Use the Application

### 1. Start the Analysis
When the GUI launches, select:
**Acetabular Analysis**

### 2. Enter Patient Information
A modal window will appear prompting for:
- Sex
- Age (must be between 8 and 18)

Click **Run Analysis**.

### 3. Select Hip STL Files
A file browser window will open (defaulting to the user’s C: drive).

Steps:
1. Navigate to the folder containing the hip STL files.
2. Label the files clearly (e.g., left.stl, right.stl).
3. Ctrl + Click to select the left, then right hip in that order.
4. Click **Open** to start the analysis.

---

## Analysis Workflow

### Pelvic Alignment
The program standardizes the pelvis orientation.
You will see this console message:
```
Pelvis is now aligned, continuing analysis.
```
An image of the aligned pelvis will appear — close it to continue.

### Acetabulum Identification
The console will display:
```
Acetabulums identified.
```
A second image will show the acetabula highlighted in red. Close the window.

### Fossa Surface Selection
For each hip:
1. Select at least three points on the fossa.
2. Click **Finish**.
3. A preview window will appear — close it.

---

## Output Files

### Excel Output
```
python_coverage.xlsx
```
Saved in:
```
Matlab-GUI/Core/
```

### Image Outputs
Seven pelvis images at different orientations.

---

## Creating a Standalone Executable
Navigate to the Core folder and run:
```
py -3.13 -m PyInstaller aces_main_window.py --add-data "EXAMPLE_Data_07-02-24.xlsx;."
```

### Resulting Structure
```
dist/
    aces_main_window/
        aces_main_window.exe
```

Running this executable launches the same GUI, and all outputs will be saved in the same folder as the .exe.

---

## Support
Open a GitHub Issue for questions or assistance.