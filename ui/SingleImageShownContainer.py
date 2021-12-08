from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QRegion

import os
from ui.CustomDecoratedLayout import CustomDecoratedLayout
from ui.m2DImageShownWidget import m2DImageShownWidget
from ui.m3DFakeImageShownWidget import m3DFakeImageShownWidget
from ui.m3DImageShownWidget import m3DImageShownWidget
from ui.mRealTimeImageShownWidget import mRealTimeImageShownWidget
from utils.BaseImageData import BaseImageData
from utils.util import getImageTileInfoFromDicom

class SingleImageShownContainer(QFrame):

    m2DMode = 0
    m3DMode = 1
    m3DFakeMode = 2
    mRTMode = 3

    selectImageShownContainerSignal = None
    selectSignal = pyqtSignal(bool)

    def __init__(self, selectImageShownContainerSignal):
        QFrame.__init__(self)
        self.mImageShownWidget = None
        self.resizeFlag = False
        self.isSelected = False
        self.imageData = BaseImageData()
        self.selectImageShownContainerSignal = selectImageShownContainerSignal
        self.selectSignal.connect(self.selectSignalHandler)
        #初始化配置
        self.setAcceptDrops(True)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Plain)
        self.setMouseTracking(True)

        #初始化GUI
        vBoxLayout = QVBoxLayout()
        vBoxLayout.setContentsMargins(0,0,0,0)
        vBoxLayout.setSpacing(0)
        vBoxLayout.setAlignment(Qt.AlignHCenter)
        self.setLayout(vBoxLayout)

        #顶部title
        self.title = QFrame()
        self.title.setFrameShape(QFrame.StyledPanel)
        self.title.setFrameShadow(QFrame.Plain)
        self.title.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        self.title.setStyleSheet("background-color:rgb(100,100,100);")
        hBoxLayout = QHBoxLayout()
        hBoxLayout.setContentsMargins(5,5,5,5)
        hBoxLayout.setSpacing(0)
        hBoxLayout.setAlignment(Qt.AlignLeft)
        self.title.setLayout(hBoxLayout)
        self.label = QLabel()
        self.label.setText("this is a image container")
        self.label.setStyleSheet("color:white;")
        hBoxLayout.addWidget(self.label)

        #底部image
        self.imageContainer = QFrame()
        self.imageContainer.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.vImageBoxLayout = CustomDecoratedLayout(QVBoxLayout())
        self.vImageBoxLayout.initParamsForPlain()
        self.vImageBoxLayout.getLayout().setAlignment(Qt.AlignHCenter)
        self.imageContainer.setLayout(self.vImageBoxLayout.getLayout())

        #整体布局垂直
        vBoxLayout.addWidget(self.title)
        vBoxLayout.addWidget(self.imageContainer)

    def selectSignalHandler(self, isSelected):
        if isSelected:
            self.title.setStyleSheet("background-color:rgb(204,102,100);")
        else:
            self.title.setStyleSheet("background-color:rgb(100,100,100);")

    def resetSelectState(self):
        self.isSelected = False
        self.selectSignal.emit(self.isSelected)

    def setTileText(self, text):
        self.label.setText(text)

    def getDataFromDropEvent(self, mimeData):
        self.imageData.seriesPath = mimeData["seriesPath"]
        self.imageData.seriesImageCount = mimeData["seriesImageCount"]
        self.imageData.filePaths = [self.imageData.seriesPath + '/' + fileName for fileName in os.listdir(self.imageData.seriesPath)]
        self.imageData.currentIndex = 0
        self.imageData.curFilePath = self.imageData.filePaths[self.imageData.currentIndex]

    def initImageShownWidget(self):
        self.mImageShownWidget.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.vImageBoxLayout.getLayout().addWidget(self.mImageShownWidget)

    def switchImageContainerMode(self, mode):
        if self.mImageShownWidget is not None:
            self.vImageBoxLayout.clearLayout()
            self.mImageShownWidget.clearViews()
            del self.mImageShownWidget

        self.setTileText(getImageTileInfoFromDicom(self.imageData.curFilePath))
        if mode == self.m2DMode:
            print("m2DMode")
            self.mImageShownWidget = m2DImageShownWidget()
            self.initImageShownWidget()
            self.mImageShownWidget.initBaseData(self.imageData)
            self.mImageShownWidget.showAllView()
        elif mode == self.m3DMode:
            print("m3DMode")
            self.mImageShownWidget = m3DImageShownWidget()
            self.initImageShownWidget()
        elif mode == self.m3DFakeMode:
            print("m3DFakeMode")
            self.mImageShownWidget = m3DFakeImageShownWidget()
            self.initImageShownWidget()
        elif mode == self.mRTMode:
            print("mRTMode")
            self.mImageShownWidget = mRealTimeImageShownWidget()
            self.initImageShownWidget()

    def mousePressEvent(self, QMouseEvent):
        super().mousePressEvent(QMouseEvent)
        point = QMouseEvent.pos()

        #判断点击是否在title上
        if  self.title.y() < point.y() < self.imageContainer.y():
            print("click title")
            self.isSelected = not self.isSelected
            self.selectSignal.emit(self.isSelected)
            self.selectImageShownContainerSignal.emit(self,self.isSelected)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            print("enter")
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            print("drop")
            event.setDropAction(Qt.CopyAction)
            event.accept()
            self.getDataFromDropEvent(event.mimeData().getImageExtraData())
            self.switchImageContainerMode(self.m2DMode)
        else:
            event.ignore()

    def resizeEvent(self, QResizeEvent):
        print('parentWidgetSize:', self.width(), self.height())

    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
        if self.mImageShownWidget is not None: self.mImageShownWidget.closeEvent(QCloseEvent)