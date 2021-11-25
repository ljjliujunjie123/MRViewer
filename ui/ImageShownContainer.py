from PyQt5.QtWidgets import *

from ui.m2DImageShownWidget import m2DImageShownWidget
from ui.m3DImageShownWidget import m3DImageShownWidget
from ui.config import uiConfig
from controller.ImageShownLayoutController import ImageShownLayoutController

class ImageShownContainer(QFrame):

    def __init__(self, ParentWidget):
        QFrame.__init__(self, ParentWidget)

        self.setGeometry(uiConfig.calcShownContainerGeometry())
        print("ImageShownContainer Geometry:")
        print(self.geometry())
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Plain)
        self.setObjectName("imageShownContainer")

        self.imageShownContainerWidget = QWidget(self)
        self.imageShownContainerWidget.setFixedSize(self.size())
        self.imageShownContainerWidget.setObjectName("imageShownContainerWidget")

        self.imageShownContainerLayout = QGridLayout(self.imageShownContainerWidget)

        #初始化controller
        self.imageShownLayoutController = ImageShownLayoutController(
            self.imageShownContainerWidget,
            self.imageShownContainerLayout
        )
        self.imageShownLayoutController.initLayoutParams(uiConfig)

        self.RealTimeContainer = m2DImageShownWidget()
        self.vtk3DContainer = m3DImageShownWidget()
        self.crossXZContainer = m2DImageShownWidget()
        self.crossYZContainer = m2DImageShownWidget()

        self.imageShownLayoutController.addWidget(self.RealTimeContainer, 0, 0)
        self.imageShownLayoutController.addWidget(self.vtk3DContainer, 0, 1)
        self.imageShownLayoutController.addWidget(self.crossXZContainer, 1, 0)
        self.imageShownLayoutController.addWidget(self.crossYZContainer, 1, 1)

    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
        if self.RealTimeContainer.qvtkWidget is not None: self.RealTimeContainer.qvtkWidget.Finalize()
        if self.crossXZContainer.qvtkWidget is not None: self.crossXZContainer.qvtkWidget.Finalize()
        if self.crossYZContainer.qvtkWidget is not None: self.crossYZContainer.qvtkWidget.Finalize()
        if self.vtk3DContainer.vtk3DWidget is not None: self.vtk3DContainer.vtk3DWidget.Finalize()
