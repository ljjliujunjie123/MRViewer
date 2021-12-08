from PyQt5.QtWidgets import *

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
        self.imageShownContainerWidget.setLayout(self.imageShownContainerLayout)

        #初始化controller
        self.imageShownLayoutController = ImageShownLayoutController(
            self.imageShownContainerWidget,
            self.imageShownContainerLayout
        )
        self.imageShownLayoutController.initLayoutParams(uiConfig)
        self.imageShownLayoutController.initWidget()

    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
        self.imageShownLayoutController.closeEvent(QCloseEvent)

    def resizeEvent(self, *args, **kwargs):
        print("ImageShonwContainer ", self.rect())
        self.imageShownContainerWidget.setFixedSize(self.size())
