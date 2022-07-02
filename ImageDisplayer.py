from PyQt5.QtWidgets import *
from Config import uiConfig
# from ui.CustomDecoratedLayout import CustomDecoratedLayout
# from controller.ImageShownLayoutController import ImageShownLayoutController
# from controller.InteractiveCrossBoxController import InteractiveCrossBoxController
# from controller.ImageShownBaseController import ImageShownBaseController
# from controller.ImageSlideShowController import ImageSlideShowController
from ui.SingleImageShownContainer import SingleImageShownContainer
class ImageDisplayer(QFrame):

    def __init__(self, parent):
        QFrame.__init__(self, parent)

        #! self.resize(uiConfig.calcShownContainerWidth(),self.parent().height())
        print("ImageDisplayer Geometry:")
        print(self.geometry())
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Plain)
        self.setObjectName("imageShownContainer")
        
        
        self.hlayout = QHBoxLayout()

        self.mainDisplayer = SingleImageShownContainer()
        self.axialDisplayer = SingleImageShownContainer()#横截面
        self.coronalDisplayer = SingleImageShownContainer()#冠状面
        self.sagittalDisplayer = SingleImageShownContainer()#矢状面

        self.vlayout = QVBoxLayout()
        self.vlayout.addWidget(self.axialDisplayer)
        self.vlayout.addWidget(self.coronalDisplayer)
        self.vlayout.addWidget(self.sagittalDisplayer)
        self.hlayout.addWidget(self.mainDisplayer)
        self.hlayout.addLayout(self.vlayout)
        self.hlayout.setStretchFactor(self.mainDisplayer,3)
        self.hlayout.setStretchFactor(self.vlayout,1)
        self.setLayout(self.hlayout)

    #     self.imageShownContainerWidget = QWidget(self)
    #     self.imageShownContainerWidget.setFixedSize(self.size())
    #     self.imageShownContainerWidget.setObjectName("imageShownContainerWidget")
    #     self.setStyleSheet("background-color: {0}".format(uiConfig.LightColor.Primary))

    #     self.imageShownContainerLayout = CustomDecoratedLayout(QGridLayout())
    #     self.imageShownContainerWidget.setLayout(self.imageShownContainerLayout.getLayout())

    #     #初始化controllers
    #     #layoutController需要首先加载，因为它负责SC的初始化
    #     self.imageShownLayoutController = ImageShownLayoutController(
    #         self.imageShownContainerLayout
    #     )
    #     self.imageShownLayoutController.initLayoutParams()
    #     self.imageShownLayoutController.initWidget()

    #     self.imageShownBaseController = ImageShownBaseController(
    #         self.imageShownContainerLayout
    #     )

    #     self.interactiveCrossBoxController = InteractiveCrossBoxController(
    #         self.imageShownContainerLayout
    #     )

    #     self.imageSlideShowController = ImageSlideShowController(
    #         self.imageShownContainerLayout
    #     )

    #     self.imageShownLayoutController.setAllContainerSignals(
    #         [
    #             self.imageShownBaseController.setContainerSignals,
    #             self.interactiveCrossBoxController.setContainerSignals
    #         ]
    #     )

    # def closeEvent(self, QCloseEvent):
    #     super().closeEvent(QCloseEvent)
    #     self.imageShownLayoutController.closeEvent(QCloseEvent)

    # def resizeEvent(self, *args, **kwargs):
    #     print("ImageShonwContainer ", self.rect())
    #     self.imageShownContainerWidget.setFixedSize(self.size())

    # def moveEvent(self, QMoveEvent):
    #     QFrame.moveEvent(self, QMoveEvent)
    #     def moveControl(container):
    #         container.moveEvent(QMoveEvent)
    #     self.imageShownContainerLayout.mapWidgetsFunc(moveControl)

    # def clearViews(self):
    #     self.imageShownBaseController.clearViews()
    #     self.imageShownLayoutController.clearViews()
    #     self.imageShownLayoutController.initWidget()

    #     self.imageShownLayoutController.setAllContainerSignals(
    #         [
    #             self.imageShownBaseController.setContainerSignals,
    #             self.interactiveCrossBoxController.setContainerSignals
    #         ]
    #     )