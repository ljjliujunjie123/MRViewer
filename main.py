import sys

import vtkmodules.all as vtk
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from ui.FileFolderWindow import FileFolderWindow
from ui.PlaneAndBallWindow import PlaneAndBallWindow
from ui.LJJMainWindow import LJJMainWindow
from ui.Reconstruction3DWindow import Reconstruction3DWindow

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox
from ui.FileFolderWindow import *

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = LJJMainWindow()
    # mainWindow = Reconstruction3DWindow()
    sys.exit(app.exec_())

