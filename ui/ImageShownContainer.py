from PyQt5.QtWidgets import *
from ui.config import uiConfig
from ui.CustomDecoratedLayout import CustomDecoratedLayout
from controller.ImageShownLayoutController import ImageShownLayoutController
from controller.InteractiveCrossBoxController import InteractiveCrossBoxController
from controller.ImageShownBaseController import ImageShownBaseController
from controller.ImageSlideShowController import ImageSlideShowController

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
        #layoutController需要首先加载，因为它负责SC的初始化
        self.imageShownLayoutController = ImageShownLayoutController(
            self.imageShownContainerLayout
        )
        self.imageShownLayoutController.initLayoutParams()
        self.imageShownLayoutController.initWidget()

        self.imageShownBaseController = ImageShownBaseController(
            self.imageShownContainerLayout
        )

        self.interactiveCrossBoxController = InteractiveCrossBoxController(
            self.imageShownContainerLayout
        )

        self.imageSlideShowController = ImageSlideShowController(
            self.imageShownContainerLayout
        )

        self.imageShownLayoutController.setAllContainerSignals(
            [
                self.imageShownBaseController.setContainerSignals,
                self.interactiveCrossBoxController.setContainerSignals
            ]
        )

    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
        self.imageShownLayoutController.closeEvent(QCloseEvent)

    def resizeEvent(self, *args, **kwargs):
        print("ImageShonwContainer ", self.rect())
        self.imageShownContainerWidget.setFixedSize(self.size())

    def moveEvent(self, QMoveEvent):
        QFrame.moveEvent(self, QMoveEvent)
        def moveControl(container):
            container.moveEvent(QMoveEvent)
        self.imageShownContainerLayout.mapWidgetsFunc(moveControl)

    def clearViews(self):
        if self.imageShownBaseController.selectedImageShownContainer is not None:
            self.imageShownBaseController.clearViews()
