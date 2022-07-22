from PyQt5.QtCore import *
from ui.SingleImageShownContainer import SingleImageShownContainer
from Config import uiConfig
from copy import deepcopy

class ImageShownLayoutController(QObject):
    """
    该类负责渲染区SC的初始化与布局调整
    """
    def __init__(
            self,
            imageShownContainerLayout
    ):
        QObject.__init__(self)
        self.imageShownContainerLayout = imageShownContainerLayout

        self.curlayout = (0, 0, 1, 1)
        self.imageShownWidgetPool = { }
        self.imageSlideshow = None
        self.imageSlideShowPlayFlag = False

    def setAllContainerSignals(self, funcList):
        for container in self.imageShownWidgetPool.values():
            for func in funcList:
                func(container)

    def initLayoutParams(self):
        self.imageShownContainerLayout.getLayout().setContentsMargins(uiConfig.shownContainerMargins)
        self.imageShownContainerLayout.getLayout().setSpacing(uiConfig.shownContainerContentSpace)

    def initWidget(self):
        for col in range(uiConfig.toolsSelectRegionCol):
            for row in range(uiConfig.toolsSelectRegionRow):
                self.imageShownWidgetPool[(row, col)] = SingleImageShownContainer()
        self.reAddImageContainers()

    def addWidget(self, childWidget, row, col, rowSpan = 1, colSpan = 1):
        self.imageShownContainerLayout.getLayout().addWidget(childWidget, row, col, rowSpan, colSpan)

    def updateLayout(self, layoutTuple):
        if layoutTuple == self.curlayout: return
        self.curlayout = deepcopy(layoutTuple)
        self.reAddImageContainers()

    def reAddImageContainers(self):
        topRow, leftCol, bottomRow, rightCol = self.curlayout

        #从Layout移除所有子Widget
        self.imageShownContainerLayout.clearLayout()

        for row in range(topRow, bottomRow + 1):
            for col in range(leftCol, rightCol + 1):
                childWidget = self.imageShownWidgetPool[(row, col)]
                self.addWidget(childWidget, row, col)

    def clearViews(self):
        self.imageShownContainerLayout.mapWidgetsFunc(lambda container,*args:container.close())
        self.imageShownContainerLayout.clearLayout()
        self.imageShownWidgetPool.clear()

    def closeEvent(self, QCloseEvent):
        for col in range(uiConfig.toolsSelectRegionCol):
            for row in range(uiConfig.toolsSelectRegionRow):
                self.imageShownWidgetPool[(row,col)].closeEvent(QCloseEvent)
        if self.imageSlideshow is not None: self.imageSlideshow.closeEvent(QCloseEvent)