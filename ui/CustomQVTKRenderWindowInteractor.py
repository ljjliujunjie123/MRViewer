from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from ui.CustomCrossBoxWidget import CustomCrossBoxWidget
from PyQt5.QtCore import QPoint

class CustomQVTKRenderWindowInteractor(QVTKRenderWindowInteractor):

    def __init__(self, parent = None):
        QVTKRenderWindowInteractor.__init__(self, parent)

    def wheelEvent(self, ev):
        return