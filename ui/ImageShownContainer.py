from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ui.m2DImageShownWidget import m2DImageShownWidget
from ui.m3DImageShownWidget import m3DImageShownWidget

class ImageShownContainer(QFrame):

    filePath = r'D:\respository\MRViewer_Scource\dicom_for_UItest\3D_vessel_phantom_transversal'

    def __init__(self, ParentWidget):
        QFrame.__init__(self, ParentWidget)

        self.setGeometry(QRect(600, 0, 1600, 1600))
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Plain)
        self.setObjectName("imageShownContainer")

        self.gridLayoutWidget = QWidget(self)
        self.gridLayoutWidget.setGeometry(QRect(0, 0, 1600, 1600))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.imageGridShownContainer = QGridLayout(self.gridLayoutWidget)
        self.imageGridShownContainer.setContentsMargins(0,0,0,0)
        self.imageGridShownContainer.setSpacing(10)
        self.imageGridShownContainer.setObjectName("imageGridShownContainer")

        self.crossXZContainer = m2DImageShownWidget()
        self.crossXZContainer.setGeometry(0,0,800,800)
        self.crossXZContainer.setFixedSize(800,800)
        self.crossXZContainer.setObjectName("crossXZContainer")
        self.imageGridShownContainer.addWidget(self.crossXZContainer, 0, 0, 1, 1)

        # self.RealTimeContainer = QWidget(self.gridLayoutWidget)
        # self.RealTimeContainer.setGeometry(0,0,500,500)
        # self.RealTimeContainer.setFixedSize(500,500)
        # self.RealTimeContainer.setObjectName("RealTimeContainer")
        # self.imageGridShownContainer.addWidget(self.RealTimeContainer, 0, 0, 1, 1)
        #
        self.vtk3DContainer = m3DImageShownWidget()
        self.vtk3DContainer.setGeometry(800,0,800,800)
        self.vtk3DContainer.setFixedSize(800,800)
        self.vtk3DContainer.setObjectName("vtk3DContainer")
        self.imageGridShownContainer.addWidget(self.vtk3DContainer, 0, 1, 1, 1)
        #
        # self.crossXZContainer = QWidget(self.gridLayoutWidget)
        # self.crossXZContainer.setGeometry(0,250,500,500)
        # self.crossXZContainer.setFixedSize(500,500)
        # self.crossXZContainer.setObjectName("crossXZContainer")
        # self.imageGridShownContainer.addWidget(self.crossXZContainer, 1, 0, 1, 1)
        #
        # self.crossYZContainer = QWidget(self.gridLayoutWidget)
        # self.crossYZContainer.setGeometry(250,250,500,500)
        # self.crossYZContainer.setFixedSize(500,500)
        # self.crossYZContainer.setObjectName("crossYZContainer")
        # self.imageGridShownContainer.addWidget(self.crossYZContainer, 1, 1, 1, 1)

    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
        if self.crossXZContainer.qvtkWidget is not None: self.crossXZContainer.qvtkWidget.Finalize()
        if self.vtk3DContainer.vtk3DWidget is not None: self.vtk3DContainer.vtk3DWidget.Finalize()
    #
    # def hideXZandYZDicom(self):
    #     if self.qvtkWidgetXZ is not None:self.qvtkWidgetXZ.setVisible(False)
    #     if self.qvtkWidgetYZ is not None:self.qvtkWidgetYZ.setVisible(False)
