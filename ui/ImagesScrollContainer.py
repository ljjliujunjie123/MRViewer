from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import vtkmodules.all as vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class ImageScrollContainer(QFrame):

    imageViewers = []
    qvtkWidgets = []
    count = 0

    def __init__(self, ParentWidget):
        QFrame.__init__(self, ParentWidget)

        self.setGeometry(QRect(0, 0, 600, 1000))
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Plain)
        self.setObjectName("imageScrollContainer")

        self.imageVerticalScrollContainer = QScrollArea(self)
        self.imageVerticalScrollContainer.setFixedWidth(self.width())
        self.imageVerticalScrollContainer.setFixedHeight(self.height()/2)
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

    def initImages(self, fileNames):
        # self.addImageFrame("E:/DCMTK/CT2.dcm")
        # self.addImageFrame("E:/DCMTK/test10.dcm")
        for fileName in fileNames:
            print(fileName)
            self.addImageFrame(fileName)

    def addImageFrame(self, fileName):
        reader = vtk.vtkDICOMImageReader()
        reader.SetDataByteOrderToLittleEndian()
        reader.SetFileName(fileName)
        reader.Update()

        self.imageViewers.append(vtk.vtkImageViewer2())
        imageViewer = self.imageViewers[-1]
        imageViewer.SetInputConnection(reader.GetOutputPort())

        ren = vtk.vtkRenderer()

        firstImageFrame = QFrame(self.imageVerticalScrollWidget)
        firstImageFrame.setGeometry(80,10 + self.count * 500,self.imageVerticalScrollWidget.width(),500)
        self.count+=1

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
