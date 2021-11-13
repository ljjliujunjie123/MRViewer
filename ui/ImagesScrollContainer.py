from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import vtkmodules.all as vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class ImageScrollContainer(QFrame):

    def __init__(self, ParentWidget):
        QFrame.__init__(self, ParentWidget)

        self.setGeometry(QRect(0, 0, 600, 1000))
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Plain)
        self.setObjectName("imageScrollContainer")

        self.imageVerticalScrollContainer = QScrollArea(self)
        self.imageVerticalScrollContainer.setFixedWidth(self.width())
        self.imageVerticalScrollContainer.setFixedHeight(self.height())
        self.imageVerticalScrollContainer.setObjectName("imageVerticalScrollContainer")
        self.imageVerticalScrollWidget = QWidget()
        self.imageVerticalScrollWidget.setGeometry(QRect(10, 10, 581, 981))
        self.verticalLayoutWidget_2 = QVBoxLayout(self.imageVerticalScrollWidget)
        self.verticalLayoutWidget_2.setContentsMargins(0,0,0,0)
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")

        self.imageVerticalScrollContainer.setWidget(self.imageVerticalScrollWidget)

        self.addImageFrame("E:/DCMTK/CT2.dcm")
        self.addImageFrame("E:/DCMTK/CT3.dcm")
        self.addImageFrame("E:/DCMTK/CT4.dcm")
        self.addImageFrame("E:/DCMTK/test10.dcm")

    def addImageFrame(self, fileName):
        print(fileName)