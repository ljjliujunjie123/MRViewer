# PyQt5-based dicom image viewer template

## Building Environment
1. install miniconda (https://docs.conda.io/en/latest/miniconda.html) or anaconda
2. activate the conda environment in cli and switch current path to this directory
3. install the dependencies by `conda env create -f environment.yml` and activate it by `conda activate PyQt`
4. check your ***PyQt*** environment installation path by `conda env list` and find the ***designer.exe*** in 
``YOUR_PYQT_PATH/Lib/site-packages/qt5_applications/Qt/bin`` directory

## Running
1. `python main.py`
2. the viewer can load DICOM/Nifti based medical image and for DICOM images, you only need to choose one file of the series

## Tips for Editing
1. *main.py* is the main entrance of the viewer
2. *crosshairView.py* contains the rewritten view widgets
3. *window.ui* is the UI file to create the GUI and can be editted by the ***designer.exe***

## Tips for Building Environment
1. native python is ok for running the viewer, but you should at least install the **PyQt5, SimpleITK, pyqtgraph and numpy** packages by pip. The compatibility is not guaranteed
2. the viewer should work well in Linux and MacOS, but is not thoroughly tested.