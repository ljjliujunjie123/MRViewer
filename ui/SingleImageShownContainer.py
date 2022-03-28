from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os
from ui.config import uiConfig
from ui.CustomDecoratedLayout import CustomDecoratedLayout
from ui.m2DImageShownWidget import m2DImageShownWidget
from ui.m3DFakeImageShownWidget import m3DFakeImageShownWidget
from ui.m3DImageShownWidget import m3DImageShownWidget
from ui.mRealTimeImageShownWidget import mRealTimeImageShownWidget
from utils.BaseImageData import BaseImageData
from utils.mImage2DShownData import mImage2DShownData
from Model.ImagesDataModel import imageDataModel
from utils.status import Status
import numpy as np
from utils.InteractiveType import InteractiveType

class SingleImageShownContainer(QFrame):

    class SignalCollectionHelper(QObject):
        """
        用来收敛所有和外部通信的signal，并提供简单的set,get方法
        """
        def __init__(self):
            QObject.__init__(self)
            self.selectImageShownContainerSignal = None
            self.updateICrossBoxSignal = None
            self.interactiveSignal = None

        def setSelectImageShownContainerSignal(self, signal):
            self.selectImageShownContainerSignal = signal

        def setICrossBoxSignal(self, signal):
            self.updateICrossBoxSignal = signal

        def setInteractiveSignal(self, signal):
            self.interactiveSignal = signal

    m2DMode = 0
    m3DMode = 1
    m3DFakeMode = 2
    mRTMode = 3
    #这个signal负责SC本身的处理
    selectSignal = pyqtSignal(bool)

    def __init__(self):
        QFrame.__init__(self)
        self.mImageShownWidget = None
        self.mImage2DShownData = mImage2DShownData()
        self.signalCollectionHelper = self.SignalCollectionHelper()
        self.resizeFlag = False
        self.isSelected = False
        self.curMode = self.m2DMode
        self.imageData = BaseImageData()
        self.selectSignal.connect(self.selectSignalHandler)
        #初始化配置
        self.setAcceptDrops(True)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Plain)
        self.setMouseTracking(True)

        #初始化GUI
        self.vBoxLayout = QVBoxLayout()
        self.vBoxLayout.setContentsMargins(0,0,0,0)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setAlignment(Qt.AlignHCenter)
        self.setLayout(self.vBoxLayout)

        #顶部title
        self.title = QFrame()
        self.title.setFrameShape(QFrame.StyledPanel)
        self.title.setFrameShadow(QFrame.Plain)
        self.title.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        self.title.setStyleSheet("background-color:{0};".format(uiConfig.LightColor.Analogous1))
        self.title.setFixedHeight(uiConfig.shownContainerTitleHeight)
        self.hBoxLayout = QHBoxLayout()
        self.hBoxLayout.setContentsMargins(5,5,5,5)
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setAlignment(Qt.AlignLeft)
        self.title.setLayout(self.hBoxLayout)
        self.label = QLabel()
        self.label.setText("This is a image container")
        self.label.setScaledContents(True)
        self.label.setStyleSheet("color:{0};".format(uiConfig.LightColor.Black))
        self.hBoxLayout.addWidget(self.label)

        #底部image
        self.imageContainer = QFrame()
        self.imageContainer.setObjectName("imageContainer")
        self.imageContainer.setStyleSheet("background-color:{0};".format(uiConfig.LightColor.Primary))
        self.imageContainer.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.vImageBoxLayout = CustomDecoratedLayout(QVBoxLayout())
        self.vImageBoxLayout.initParamsForPlain()
        self.vImageBoxLayout.getLayout().setAlignment(Qt.AlignHCenter)
        self.imageContainer.setLayout(self.vImageBoxLayout.getLayout())

        #整体布局垂直
        self.vBoxLayout.addWidget(self.title)
        self.vBoxLayout.addWidget(self.imageContainer)

    def selectSignalHandler(self, isSelected):
        if isSelected:
            self.title.setStyleSheet("background-color:{0};".format(uiConfig.LightColor.Complementary))
        else:
            self.title.setStyleSheet("background-color:{0};".format(uiConfig.LightColor.Analogous1))

    def resetSelectState(self):
        self.isSelected = False
        self.selectSignal.emit(self.isSelected)

    def setTitleText(self, text):
        self.label.setText(text)

    def getDataFromDropEvent(self, imageExtraData):
        self.imageData.studyName = imageExtraData["studyName"]
        self.imageData.seriesName = imageExtraData["seriesName"]
        self.imageData.seriesImageCount = imageExtraData["seriesImageCount"]
        self.imageData.currentIndex = 0
        self.imageData.filePaths = [
            os.path.join(self.imageData.getSeriesPath(), fileName)
            for fileName in imageDataModel.findSeriesItem(self.imageData.studyName, self.imageData.seriesName).keys()
        ]
        self.imageData.curFilePath = self.imageData.filePaths[self.imageData.currentIndex]

    def initImageShownWidget(self):
        self.mImageShownWidget.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.vImageBoxLayout.getLayout().addWidget(self.mImageShownWidget)

    def switchImageContainerMode(self, mode):
        filterRes = self.switchImageContainerModeFilter(mode)
        if filterRes != Status.good:
            print("当前series不能切换到{0}模式，原因是{1}".format(mode,filterRes))
            return

        if self.mImageShownWidget is not None:
            self.vImageBoxLayout.clearLayout()
            self.mImageShownWidget.clearViews()
            del self.mImageShownWidget

        self.setTitleText(self.imageData.getImageTileInfo(self.imageData.currentIndex))
        if mode == self.m2DMode:
            print("m2DMode")
            self.mImageShownWidget = m2DImageShownWidget()
            self.mImageShownWidget.imageShownData = self.mImage2DShownData
            self.mImageShownWidget.updateCrossViewSubSignal.connect(self.tryUpdateCrossViewSignalEmit)
            self.mImageShownWidget.interactiveSubSignal.connect(self.tryInteractiveSignalEmit)
        elif mode == self.m3DMode:
            print("m3DMode")
            self.mImageShownWidget = m3DImageShownWidget()
        elif mode == self.m3DFakeMode:
            print("m3DFakeMode")
            self.mImageShownWidget = m3DFakeImageShownWidget()
        elif mode == self.mRTMode:
            print("mRTMode")
            # self.mImageShownWidget = mRealTimeImageShownWidget()
            self.mImageShownWidget = m2DImageShownWidget()
            self.mImageShownWidget.imageShownData = self.mImage2DShownData
            self.mImageShownWidget.updateCrossViewSubSignal.connect(self.tryUpdateCrossViewSignalEmit)
            self.mImageShownWidget.interactiveSubSignal.connect(self.tryInteractiveSignalEmit)
        self.curMode = mode
        self.initImageShownWidget()
        self.mImageShownWidget.initBaseData(self.imageData)
        self.mImageShownWidget.showAllViews()
        self.tryUpdateCrossViewSignalEmit()

    def switchImageContainerModeFilter(self, mode):
        if mode == self.m3DFakeMode:
            if self.imageData.seriesImageCount != 3:
                return "localizer 必须是3张图片，请检查您的数据是否是三张"

            dcmList = [self.imageData.getDcmDataByIndex(i) for i in range(3)]
            orientations = [np.array(dcmData.ImageOrientationPatient,dtype = float) for dcmData in dcmList]
            nVectors = [np.cross(orientation[:3],orientation[3:]) for orientation in orientations]
            for i in range(len(nVectors) - 1):
                for j in range(i + 1,len(nVectors)):
                    if np.dot(nVectors[i],nVectors[j]) != 0:
                        return "localizer 必须彼此正交，请检查您的数据是否正交"

            return Status.good
        return Status.good

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
            self.signalCollectionHelper.updateICrossBoxSignal.emit(self)
            self.mImageShownWidget.tryHideCrossBoxWidget()

    def tryInteractiveSignalEmit(self, interactiveType: InteractiveType):
        self.signalCollectionHelper.interactiveSignal.emit(interactiveType, self)

    def showSlideShowContainer(self):
        if isinstance(self.mImageShownWidget, m2DImageShownWidget):
            self.mImageShownWidget.showSlideShowContainer()

    def closeSlideShowContainer(self):
        if isinstance(self.mImageShownWidget, m2DImageShownWidget):
            self.mImageShownWidget.closeSlideShowContainer()

    def mousePressEvent(self, QMouseEvent):
        #空状态无法点击 or 已经被选中则无法点击
        if self.mImageShownWidget is None or self.isSelected: return
        #判断点击是否在title上
        point = QMouseEvent.pos()
        if  self.title.y() < point.y() < self.imageContainer.y():
            print("click title")
            self.isSelected = not self.isSelected
            self.selectSignal.emit(self.isSelected)
            self.signalCollectionHelper.selectImageShownContainerSignal.emit(self, self.isSelected)
            self.tryUpdateCrossViewSignalEmit()
        super().mousePressEvent(QMouseEvent)

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
            self.signalCollectionHelper.selectImageShownContainerSignal.emit(self, self.isSelected)
            self.switchImageContainerMode(self.m2DMode)
        else:
            event.ignore()

    def resizeEvent(self, QResizeEvent):
        # print('singleImageShownContainer:', self.geometry())
        # print("imageContainer: ", self.imageContainer.geometry())
        self.tryUpdateCrossBoxWidget()

    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
        print("sc close")
        if self.mImageShownWidget is not None:
            print('vtk close')
            self.mImageShownWidget.closeEvent(QCloseEvent)

    def moveEvent(self, QMoveEvent):
        QFrame.moveEvent(self, QMoveEvent)
        if self.mImageShownWidget is not None:
            self.mImageShownWidget.moveEvent(QMoveEvent)