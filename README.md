# ACES Acetabular Coverage Analysis (Python GUI)

This repository contains a PyQt-based graphical application for performing automated acetabular coverage analysis on pelvic STL models using the Trimesh library. The tool is semi-automatic that guides the user through pelvis alignment, acetabulum detection, fossa selection, coverage angle calculations, and automated results export.

## Installation

### 1. Clone the Repository
```
git clone https://github.com/rchsd/ACES.git
```

### 2. Create and Activate a Virtual Environment
Python 3.10 or higher is supported. This project was developed using Python 3.14.
```
py -3.14 -m venv venv
source venv/bin/activate     # macOS/Linux
venv\Scripts\Activate        # Windows
```

### 3. Install Python Dependencies
```
pip install -r requirements.txt
```

## Running the Application

The main application entry point is the full absolute path to aces_main_window.py (for example: C:\...\ACES\Core\aces_main_window.py).
Run it using:
```
venv\Scripts\Activate
cd Core
python aces_main_window.py
```

## How to Use the Application

### 1. Start the Analysis
When the GUI with the title "Acetabular Analysis" launches, select:
**Start**

### 2. Enter Patient Information
A modal window will appear prompting for:
- Sex
- Age (must be between 8 and 18)(patients 18+ simply select 18)

Click **Run Analysis**.

### 3. Select Hip STL Files
A file browser window will open (defaulting to the user’s C: drive).

Steps:
1. Navigate to the folder containing the hip STL files, filename is usually "0stl".
2. Look for the files clearly labeled (e.g., pelvisL.stl, pelvisR.stl).
3. Ctrl + Click to select the left, then right hip in that order.
4. Click **Open** to start the analysis.

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

### Fossa Surface Selection (instructions also in window)
For each hip:
1. Select fossa points using the lasso tool, area will turn red.
2. Close the window, the area will be saved and the next one will appear.
3. Finish with the second fossa selection.
4. If the pelvis has a negative 'tilt' or 'right_tilt', the process will have to be repeated again.

## Output Files

### STL FILES
```
combined_pelvis.stl
```
Saved in: C:\...\ACES\Core


### Excel Output
```
python_coverage.xlsx
```
Saved in: C:\...\ACES\Core


### Image Outputs
Seven pelvis images at different orientations with a green vector and best fitting spheres.
Saved in: C:\...\ACES\Core\saved_snapshots

### Edge Case
- There's a chance that the program fails to align the pelvis even after the realignment.
- Immediately check the images to see if the pelvis was aligned properly.
- If the images are incorrect, run the program again.



## Creating a Standalone Executable
Navigate to the Core folder and run:
```
python -m PyInstaller aces_main_window.py --name aces --onedir --clean --noconfirm --paths . --add-data "EXAMPLE_Data_07-02-24.xlsx;." --collect-submodules jaraco --collect-submodules helper_functions
```

### Resulting Structure
```
Core/
    dist/
        aces/
            aces.exe
```

Running this executable launches the same GUI, and all outputs will be saved in the same folder as the .exe.


## Support
Open a GitHub Issue for questions or assistance.


## Acknowledgements (historical and current contributors to ACES)
#### Former (pre-Python) Developers:

- Josh Doan MEng; Engineer
- Byron Beasley Jr, MS; Innovation Engineer

#### Current Developers:

- Jared Falcon, BS; Innovation Engineer
- Parham Gholami, MS; Innovation Engineer, Lead

#### Leadership

- Christy Farnsworth, MS; Orthopedic Research Manager
- James D. Bomar, MS; Research Supervisor
- Justin R. Ryan, PhD; Director Webster Foundation 3D Innovations Lab
- Matthew R. Schmitz, MD; Orthopedic Surgeon, Rady Children's Hospital San Diego
- Salil V. Upasani, MD; Orthopedic Surgeon, Rady Children's Hospital San Diego
