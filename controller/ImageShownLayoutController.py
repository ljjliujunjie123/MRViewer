from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
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
        self.mainDisplayer = SingleImageShownContainer()
        self.axialDisplayer = SingleImageShownContainer()#横截面
        self.coronalDisplayer = SingleImageShownContainer()#冠状面
        self.sagittalDisplayer = SingleImageShownContainer()#矢状面
        self.mainDisplayer.switchImageContainerMode(SingleImageShownContainer.m3DFakeMode)
        self.axialDisplayer.switchImageContainerMode(SingleImageShownContainer.mRTMode,path = uiConfig.axialPath)
        self.coronalDisplayer.switchImageContainerMode(SingleImageShownContainer.mRTMode,path = uiConfig.coronalPath)
        self.sagittalDisplayer.switchImageContainerMode(SingleImageShownContainer.mRTMode,path = uiConfig.sagittalPath)
        self.imageSlideshow = None
        self.imageSlideShowPlayFlag = False
        
        self.splitter = QSplitter()
        self.sideSplitter = QSplitter()
        self.sideSplitter.setOrientation(Qt.Vertical)
        self.splitter.addWidget(self.mainDisplayer)
        self.sideSplitter.addWidget(self.axialDisplayer)
        self.sideSplitter.addWidget(self.coronalDisplayer)
        self.sideSplitter.addWidget(self.sagittalDisplayer)
        self.splitter.addWidget(self.sideSplitter)
        self.splitter.setStretchFactor(0,3)
        self.splitter.setStretchFactor(1,1)

    def setAllContainerSignals(self, funcList):
        for container in self.imageShownWidgetPool.values():
            for func in funcList:
                func(container)
        func(self.mainDisplayer)
        func(self.axialDisplayer)
        func(self.coronalDisplayer)
        func(self.sagittalDisplayer)

    def initLayoutParams(self):
        self.imageShownContainerLayout.getLayout().setContentsMargins(uiConfig.shownContainerMargins)
        self.imageShownContainerLayout.getLayout().setSpacing(uiConfig.shownContainerContentSpace)

    def initWidget(self):
        for col in range(uiConfig.toolsSelectRegionCol):
            for row in range(uiConfig.toolsSelectRegionRow):
                self.imageShownWidgetPool[(row, col)] = SingleImageShownContainer()
        self.reAddInPool()

    def addWidget(self, childWidget, row, col, rowSpan = 1, colSpan = 1):
        self.imageShownContainerLayout.getLayout().addWidget(childWidget, row, col, rowSpan, colSpan)

    def updateLayout(self, layoutTuple):
        if layoutTuple == self.curlayout: return
        self.curlayout = deepcopy(layoutTuple)
        self.reAddInPool()
    def switchToIntra(self):
        self.imageShownContainerLayout.clearLayout()
        self.addWidget(self.splitter,0,0)

    def reAddInPool(self):
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