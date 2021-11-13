from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import vtkmodules.all as vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class ImageShownContainer(QFrame):

    def __init__(self, ParentWidget):
        QFrame.__init__(self, ParentWidget)

        self.setGeometry(QRect(600, 0, 1000, 1000))
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Plain)
        self.setObjectName("imageShownContainer")

        self.gridLayoutWidget = QWidget(self)
        self.gridLayoutWidget.setGeometry(QRect(0, 0, 1000, 1000))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.imageGridShownContainer = QGridLayout(self.gridLayoutWidget)
        self.imageGridShownContainer.setContentsMargins(0, 0, 0, 0)
        self.imageGridShownContainer.setObjectName("imageGridShownContainer")

        self.RealTimeContainer = QFrame(self.gridLayoutWidget)
        self.RealTimeContainer.setGeometry(0,0,500,500)
        self.RealTimeContainer.setFrameShape(QFrame.StyledPanel)
        self.RealTimeContainer.setFrameShadow(QFrame.Plain)
        self.RealTimeContainer.setObjectName("RealTimeContainer")
        self.imageGridShownContainer.addWidget(self.RealTimeContainer, 0, 0, 1, 1)

        self.vtk3DContainer = QFrame(self.gridLayoutWidget)
        self.vtk3DContainer.setGeometry(250,0,500,500)
        self.vtk3DContainer.setFrameShape(QFrame.StyledPanel)
        self.vtk3DContainer.setFrameShadow(QFrame.Plain)
        self.vtk3DContainer.setObjectName("vtk3DContainer")
        self.imageGridShownContainer.addWidget(self.vtk3DContainer, 0, 1, 1, 1)

        self.crossXZContainer = QFrame(self.gridLayoutWidget)
        self.crossXZContainer.setGeometry(0,250,500,500)
        self.crossXZContainer.setFrameShape(QFrame.StyledPanel)
        self.crossXZContainer.setFrameShadow(QFrame.Plain)
        self.crossXZContainer.setObjectName("crossXZContainer")
        self.imageGridShownContainer.addWidget(self.crossXZContainer, 1, 0, 1, 1)

        self.crossYZContainer = QFrame(self.gridLayoutWidget)
        self.crossYZContainer.setGeometry(250,250,500,500)
        self.crossYZContainer.setFrameShape(QFrame.StyledPanel)
        self.crossYZContainer.setFrameShadow(QFrame.Plain)
        self.crossYZContainer.setObjectName("crossYZContainer")
        self.imageGridShownContainer.addWidget(self.crossYZContainer, 1, 1, 1, 1)

        self.initXZandYZDicom()

    def initXZandYZDicom(self):
        self.readerXZ = None
        self.imageViewerXZ = None
        self.renXZ = None
        self.imageFrameXZ = None
        self.qvtkWidgetXZ = None

        self.readerYZ = None
        self.imageViewerYZ = None
        self.renYZ = None
        self.imageFrameYZ = None
        self.qvtkWidgetYZ = None

    def showXZDicom(self, fileName):
        print("showXZDicom begin")
        if self.readerXZ is None:
            self.readerXZ = vtk.vtkDICOMImageReader()
        self.readerXZ.SetDataByteOrderToLittleEndian()
        self.readerXZ.SetFileName(fileName)
        self.readerXZ.Update()

        if self.imageViewerXZ is None:
            self.imageViewerXZ =  vtk.vtkImageViewer2()
        self.imageViewerXZ.SetInputConnection(self.readerXZ.GetOutputPort())
        self.imageViewerXZ.SetColorLevel(315.5)
        self.imageViewerXZ.SetColorWindow(315.5)

        if self.renXZ is None:
            self.renXZ = vtk.vtkRenderer()

        if self.imageFrameXZ is None:
            self.imageFrameXZ = QFrame(self.crossXZContainer)
        self.imageFrameXZ.setFixedWidth(self.crossXZContainer.width())
        self.imageFrameXZ.setFixedHeight(self.crossXZContainer.height())

        if self.qvtkWidgetXZ is None:
            self.qvtkWidgetXZ = QVTKRenderWindowInteractor(self.imageFrameXZ)
        self.qvtkWidgetXZ.GetRenderWindow().AddRenderer(self.renXZ)

        self.imageViewerXZ.SetRenderer(self.renXZ)
        self.imageViewerXZ.SetRenderWindow(self.qvtkWidgetXZ.GetRenderWindow())
        self.imageViewerXZ.UpdateDisplayExtent()
        self.imageViewerXZ.SetupInteractor(self.qvtkWidgetXZ.GetRenderWindow().GetInteractor())

        self.renXZ.ResetCamera()
        self.qvtkWidgetXZ.GetRenderWindow().Render()

        if self.imageFrameXZ.isVisible() is False: self.imageFrameXZ.setVisible(True)
        print("showXZDicom end")

    def showYZDicom(self, fileName):
        print("showYZDicom begin")
        if self.readerYZ is None:
            self.readerYZ = vtk.vtkDICOMImageReader()
        self.readerYZ.SetDataByteOrderToLittleEndian()
        self.readerYZ.SetFileName(fileName)
        self.readerYZ.Update()

        if self.imageViewerYZ is None:
            self.imageViewerYZ =  vtk.vtkImageViewer2()
        self.imageViewerYZ.SetInputConnection(self.readerYZ.GetOutputPort())
        self.imageViewerYZ.SetColorLevel(315.5)
        self.imageViewerYZ.SetColorWindow(315.5)

        if self.renYZ is None:
            self.renYZ = vtk.vtkRenderer()

        if self.imageFrameYZ is None:
            self.imageFrameYZ = QFrame(self.crossYZContainer)
        self.imageFrameYZ.setFixedWidth(self.crossYZContainer.width())
        self.imageFrameYZ.setFixedHeight(self.crossYZContainer.height())

        if self.qvtkWidgetYZ is None:
            self.qvtkWidgetYZ = QVTKRenderWindowInteractor(self.imageFrameYZ)
        self.qvtkWidgetYZ.GetRenderWindow().AddRenderer(self.renYZ)

        self.imageViewerYZ.SetRenderer(self.renYZ)
        self.imageViewerYZ.SetRenderWindow(self.qvtkWidgetYZ.GetRenderWindow())
        self.imageViewerYZ.UpdateDisplayExtent()
        self.imageViewerYZ.SetupInteractor(self.qvtkWidgetYZ.GetRenderWindow().GetInteractor())

        self.renYZ.ResetCamera()
        self.qvtkWidgetYZ.GetRenderWindow().Render()

        if self.imageFrameYZ.isVisible() is False: self.imageFrameYZ.setVisible(True)
        print("showYZDicom end")

    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
        if self.qvtkWidgetXZ is not None: self.qvtkWidgetXZ.Finalize()
        if self.qvtkWidgetYZ is not None: self.qvtkWidgetYZ.Finalize()

    def hideXZandYZDicom(self):
        if self.imageFrameXZ is not None:self.imageFrameXZ.setVisible(False)
        if self.imageFrameYZ is not None:self.imageFrameYZ.setVisible(False)
