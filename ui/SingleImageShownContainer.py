from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QRegion

import os
from ui.config import uiConfig
from ui.CustomDecoratedLayout import CustomDecoratedLayout
from ui.CustomCrossBoxWidget import CustomCrossBoxWidget
from ui.m2DImageShownWidget import m2DImageShownWidget
from ui.m3DFakeImageShownWidget import m3DFakeImageShownWidget
from ui.m3DImageShownWidget import m3DImageShownWidget
from ui.mRealTimeImageShownWidget import mRealTimeImageShownWidget
from utils.BaseImageData import BaseImageData
from utils.util import getImageTileInfoFromDicom
from utils.mImage2DShownData import mImage2DShownData

class SingleImageShownContainer(QFrame):

    m2DMode = 0
    m3DMode = 1
    m3DFakeMode = 2
    mRTMode = 3
    #这个signal负责SC之外的处理
    selectImageShownContainerSignal = None
    updateCrossViewSignal = None
    #这个signal负责SC本身的处理
    selectSignal = pyqtSignal(bool)

    def __init__(self, selectImageShownContainerSignal, updateCrossViewSignal):
        QFrame.__init__(self)
        self.mImageShownWidget = None
        self.mImage2DShownData = mImage2DShownData()
        self.resizeFlag = False
        self.isSelected = False
        self.curMode = self.m2DMode
        self.imageData = BaseImageData()
        self.selectImageShownContainerSignal = selectImageShownContainerSignal
        self.updateCrossViewSignal = updateCrossViewSignal
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
        self.title.setStyleSheet("background-color:grey;")
        hBoxLayout = QHBoxLayout()
        hBoxLayout.setContentsMargins(5,5,5,5)
        hBoxLayout.setSpacing(0)
        hBoxLayout.setAlignment(Qt.AlignLeft)
        self.title.setLayout(hBoxLayout)
        self.label = QLabel()
        self.label.setText("This is a image container")
        self.label.setStyleSheet("color:black;")
        hBoxLayout.addWidget(self.label)

        #底部image
        self.imageContainer = QFrame()
        self.imageContainer.setStyleSheet("background-color:black;")
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
            self.title.setStyleSheet("background-color:#eb9076;")
        else:
            self.title.setStyleSheet("background-color:grey;")

    def resetSelectState(self):
        self.isSelected = False
        self.selectSignal.emit(self.isSelected)

    def setTileText(self, text):
        self.label.setText(text)

    def getDataFromDropEvent(self, mimeData):
        self.imageData.seriesPath = mimeData["seriesPath"]
        self.imageData.seriesImageCount = mimeData["seriesImageCount"]
        self.imageData.filePaths = [os.path.join(self.imageData.seriesPath,fileName) for fileName in os.listdir(self.imageData.seriesPath)]
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
            self.mImageShownWidget.imageShownData = self.mImage2DShownData
            self.mImageShownWidget.updateCrossViewSubSignal.connect(self.tryUpdateCrossViewSignalEmit)
        elif mode == self.m3DMode:
            print("m3DMode")
            self.mImageShownWidget = m3DImageShownWidget()
        elif mode == self.m3DFakeMode:
            print("m3DFakeMode")
            # self.mImageShownWidget = m3DFakeImageShownWidget()
            self.mImageShownWidget = m2DImageShownWidget()
        elif mode == self.mRTMode:
            print("mRTMode")
            self.mImageShownWidget = mRealTimeImageShownWidget()
            # self.mImageShownWidget = m2DImageShownWidget()
        self.curMode = mode
        self.initImageShownWidget()
        self.mImageShownWidget.initBaseData(self.imageData)
        self.mImageShownWidget.showAllViews()
        self.tryUpdateCrossViewSignalEmit()

    def controlImageExtraInfoState(self, isShow):
        self.mImage2DShownData.showExtraInfoFlag = isShow
        if self.curMode is not self.m2DMode or self.mImageShownWidget is None: return
        if isShow:
            self.mImageShownWidget.showImageExtraInfoVtkView()
            self.mImageShownWidget.renderVtkWindow()
        else:
            self.mImageShownWidget.hideImageExtraInfoVtkView()

    def tryUpdateCrossBoxWidget(self):
        if self.mImage2DShownData.showCrossFlag and (self.mImageShownWidget is not None):
            self.mImageShownWidget.updateCrossBoxWidget()

    def tryUpdateCrossViewSignalEmit(self):
        if self.isSelected:
            self.updateCrossViewSignal.emit(self)
            self.mImageShownWidget.tryHideCrossBoxWidget()

    def mousePressEvent(self, QMouseEvent):
        super().mousePressEvent(QMouseEvent)
        point = QMouseEvent.pos()

        #空状态无法点击 or 已经被选中则无法点击
        if self.mImageShownWidget is None or self.isSelected: return
        #判断点击是否在title上
        if  self.title.y() < point.y() < self.imageContainer.y():
            print("click title")
            self.isSelected = not self.isSelected
            self.selectSignal.emit(self.isSelected)
            self.selectImageShownContainerSignal.emit(self, self.isSelected)
            self.tryUpdateCrossViewSignalEmit()

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
            self.isSelected = True
            self.selectSignal.emit(self.isSelected)
            self.selectImageShownContainerSignal.emit(self, self.isSelected)
            self.switchImageContainerMode(self.m2DMode)
        else:
            event.ignore()

    def resizeEvent(self, QResizeEvent):
        print('singleImageShownContainer:', self.geometry())
        self.tryUpdateCrossBoxWidget()

    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
        if self.mImageShownWidget is not None: self.mImageShownWidget.closeEvent(QCloseEvent)