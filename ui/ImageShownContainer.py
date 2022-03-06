from PyQt5.QtWidgets import *
from ui.config import uiConfig
from ui.CustomDecoratedLayout import CustomDecoratedLayout
from controller.ImageShownLayoutController import ImageShownLayoutController
from controller.InteractiveCrossBoxController import InteractiveCrossBoxController

class ImageShownContainer(QFrame):

    def __init__(self, ParentWidget):
        QFrame.__init__(self, ParentWidget)

        self.resize(uiConfig.calcShownContainerWidth(),self.parent().height())
        print("ImageShownContainer Geometry:")
        print(self.geometry())
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Plain)
        self.setObjectName("imageShownContainer")

        self.imageShownContainerWidget = QWidget(self)
        self.imageShownContainerWidget.setFixedSize(self.size())
        self.imageShownContainerWidget.setObjectName("imageShownContainerWidget")
        self.setStyleSheet("background: grey;")

        self.imageShownContainerLayout = CustomDecoratedLayout(QGridLayout())
        self.imageShownContainerWidget.setLayout(self.imageShownContainerLayout.getLayout())

        #初始化controllers
        self.imageShownLayoutController = ImageShownLayoutController(
            self.imageShownContainerLayout
        )
        self.imageShownLayoutController.initLayoutParams()
        self.imageShownLayoutController.initWidget()

        self.interactiveCrossBoxController = InteractiveCrossBoxController(
            self.imageShownContainerLayout
        )

    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
        self.imageShownLayoutController.closeEvent(QCloseEvent)

    def resizeEvent(self, *args, **kwargs):
        print("ImageShonwContainer ", self.rect())
        self.imageShownContainerWidget.setFixedSize(self.size())

    def clearViews(self):
        if self.imageShownLayoutController.selectedImageShownContainer is not None:
            self.imageShownLayoutController.clearViews()
