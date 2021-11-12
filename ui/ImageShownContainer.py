from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import vtkmodules.all as vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class ImageShownContainer(QFrame):
    imageViewers = []
    qvtkWidgets = []

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

        self.showDicomInFrame(self.crossXZContainer, "E:/DCMTK/CT2.dcm")
        self.showDicomInFrame(self.crossYZContainer, "E:/DCMTK/test10.dcm")

    def showDicomInFrame(self, container, fileName):
        reader = vtk.vtkDICOMImageReader()
        reader.SetDataByteOrderToLittleEndian()
        reader.SetFileName(fileName)
        reader.Update()

        self.imageViewers.append(vtk.vtkImageViewer2())
        imageViewer = self.imageViewers[-1]
        imageViewer.SetInputConnection(reader.GetOutputPort())

        ren = vtk.vtkRenderer()

        firstImageFrame = QFrame(container)
        firstImageFrame.setFixedWidth(container.width())
        firstImageFrame.setFixedHeight(container.height())

        self.qvtkWidgets.append(QVTKRenderWindowInteractor(firstImageFrame))
        qvtkWidget = self.qvtkWidgets[-1]
        qvtkWidget.GetRenderWindow().AddRenderer(ren)

        imageViewer.SetRenderer(ren)
        imageViewer.SetRenderWindow(qvtkWidget.GetRenderWindow())
        imageViewer.UpdateDisplayExtent()
        imageViewer.SetupInteractor(qvtkWidget.GetRenderWindow().GetInteractor())

        ren.ResetCamera()
        qvtkWidget.GetRenderWindow().Render()

    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
        print("close 事件")
        for qvtkWidget in self.qvtkWidgets:
            print("closing")
            qvtkWidget.Finalize()