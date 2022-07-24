from sys import displayhook
from unittest import case
from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from enum import Enum
from Tools.LoadButton import LoadButton
from Tools.DisplayAdjustor import DisplayAdjustor
from Tools.SegmentSelector import SegmentSelector
from Tools.Measure import Measure
from Tools.AnnotationSelector import AnnotationSelector
from Tools.SelectRegionGridButton import SelectRegionGridButton
from Tools.SlideshowButton import SlideshowButton
from Tools.ExtraInfoButton import ExtraInfoButton
from Tools.ImageModeContainer import ImageModeContainer
from Config import uiConfig
class ToolNum(Enum):
    load     = 0
    display  = 1
    segment  = 2
    measure  = 3
    annotation = 4
    shownLayout = 5
    slideShow = 6
    modeSelect = 7
    extraInfo = 8
    default  = -1

class ToolsFactory():

    def __init__(self, parent):
        print("tool Factory")
        self.parent = parent

    def createTool(self, tag = ToolNum.default, **kwargs):
        if len(kwargs) > 0: signal = kwargs["signal"]

        if tag == ToolNum.load:
            loadButton = LoadButton(self.parent,signal)
            return loadButton

        elif tag == ToolNum.display:
            displayAdjustor = DisplayAdjustor(self.parent)
            return displayAdjustor

        elif tag == ToolNum.segment:
            segmentSelector = SegmentSelector(self.parent)
            return segmentSelector

        elif tag == ToolNum.measure:
            measure = Measure(self.parent)
            return measure

        elif tag == ToolNum.annotation:
            annotationSelector = AnnotationSelector(self.parent)
            return annotationSelector

        elif tag == ToolNum.shownLayout:
            selectRegionGridButton = SelectRegionGridButton(signal)
            return selectRegionGridButton

        elif tag == ToolNum.slideShow:
            enableSlideshow = SlideshowButton(signal)
            return enableSlideshow

        elif tag == ToolNum.modeSelect:
            print("imageModeSelect")
            imageModeContainer = ImageModeContainer(self.parent,signal)
            return imageModeContainer

        elif tag == ToolNum.extraInfo:
            enableImageExtraInfo = ExtraInfoButton(self.parent,signal)
            return enableImageExtraInfo

        else:
            frame = QFrame()
            frame.setContentsMargins(0,0,0,0)
            pushButton = QPushButton("")
            frame.addWidget(pushButton)

class ToolsContainer(QScrollArea):
    loadSignal = pyqtSignal()
    segmentSignal = pyqtSignal(bool,bool,bool)
    def __init__(self, parent):
        QFrame.__init__(self, parent)
        #style
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Plain)
        self.setMinimumWidth(uiConfig.toolsContainerHintWidth)
        self.setContentsMargins(0,0,0,0)
        self.setObjectName("ToolsContainer")

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.toolsScrollContainer = QFrame(self)
        self.setWidget(self.toolsScrollContainer)

        self.toolsScrollLayout = QVBoxLayout()
        self.toolsScrollLayout.setContentsMargins(20,20,20,20)
        self.toolsScrollLayout.setSpacing(40)
        self.toolsScrollLayout.setAlignment(Qt.AlignHCenter)

        #工厂模式
        self.toolFactory = ToolsFactory(self.toolsScrollContainer)

        # 功能1 load files
        self.loadButton = self.toolFactory.createTool(ToolNum.load, signal = self.loadSignal)
        self.toolsScrollLayout.addWidget(self.loadButton,0,Qt.AlignTop)
        # 功能2 Display
        self.displayAdjuster = self.toolFactory.createTool(ToolNum.display, signal = self.loadSignal)
        self.toolsScrollLayout.addWidget(self.displayAdjuster,0,Qt.AlignTop)
        # 功能3 segment
        self.segmentSelector = self.toolFactory.createTool(ToolNum.segment, signal = self.loadSignal)
        self.toolsScrollLayout.addWidget(self.segmentSelector,0,Qt.AlignTop)
        # 功能4 measure
        self.measure = self.toolFactory.createTool(ToolNum.measure, signal = self.loadSignal)
        self.toolsScrollLayout.addWidget(self.measure,0,Qt.AlignTop)

        self.toolsScrollLayout.addStretch()
        self.toolsScrollContainer.setLayout(self.toolsScrollLayout)

    def resizeEvent(self, *args, **kwargs):
        print("cur ToolContainer Geometry ", self.geometry())
        self.setFixedSize(self.size())
        self.toolsScrollContainer.setFixedSize(self.size())

class ExtraToolsContainer(QScrollArea):
    loadSignal = pyqtSignal()
    segmentSignal = pyqtSignal(bool,bool,bool)

    updateImageShownLayoutSignal = pyqtSignal(tuple)
    enableImageSlideshowSignal = pyqtSignal(bool)
    imageModeSelectSignal = pyqtSignal(int)
    enableImageExtraInfoSignal = pyqtSignal(bool)
    initToolsContainerStateSignal = pyqtSignal()

    def __init__(self, parent):
        QFrame.__init__(self, parent)
        #style
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Plain)
        self.setMinimumWidth(uiConfig.toolsContainerHintWidth)
        self.setContentsMargins(0,0,0,0)
        self.setObjectName("ToolsContainer")
        
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.toolsScrollContainer = QFrame(self)

        self.toolsScrollLayout = QVBoxLayout()
        self.toolsScrollLayout.setContentsMargins(20,20,20,20)
        self.toolsScrollLayout.setAlignment(Qt.AlignHCenter)

        #工厂模式
        self.toolFactory = ToolsFactory(self.toolsScrollContainer)

        # 功能1 annotation
        # self.annotationSelector = \
        #     self.toolFactory.createTool(ToolNum.annotation, signal = self.loadSignal)
        # self.toolsScrollLayout.addWidget(self.annotationSelector,0,Qt.AlignTop)

        #! 功能2
        # 按钮唤起一个可选择的表格，来调整文件渲染区的布局
        self.selectRegionGridButton = \
            self.toolFactory.createTool(ToolNum.shownLayout, signal = self.updateImageShownLayoutSignal)
        self.toolsScrollLayout.addWidget(self.selectRegionGridButton,0,Qt.AlignTop)

        #! 功能3 by evermg42
        # 图像的自动轮播开启
        self.enableImageSlideShowWidget = \
            self.toolFactory.createTool(ToolNum.slideShow, signal = self.enableImageSlideshowSignal)
        self.toolsScrollLayout.addWidget(self.enableImageSlideShowWidget,0,Qt.AlignTop)

        #! 功能4
        #图像的模式切换
        self.imageModeSelectWidget = \
            self.toolFactory.createTool(ToolNum.modeSelect, signal = self.imageModeSelectSignal)
        self.toolsScrollLayout.addWidget(self.imageModeSelectWidget,0,Qt.AlignTop)

        #! 功能5
        #图像的附加信息开关
        self.enableImageExtraInfoWidget = \
            self.toolFactory.createTool(ToolNum.extraInfo, signal = self.enableImageExtraInfoSignal)
        self.toolsScrollLayout.addWidget(self.enableImageExtraInfoWidget,0,Qt.AlignTop)


        self.toolsScrollLayout.addStretch()
        self.toolsScrollContainer.setLayout(self.toolsScrollLayout)
        self.setWidget(self.toolsScrollContainer)
    def initToolsContainerStateHandler(self):
        self.selectRegionGridButton.init()
        self.enableImageExtraInfoWidget.init()
        self.imageModeSelectWidget.init()
        self.enableImageSlideShowWidget.init()

    def updateToolsContainerStateHandler(self, curMode):
        # self.selectRegionGridButton.update()不需要
        self.enableImageExtraInfoWidget.update(curMode == 0)
        # self.imageModeSelectWidget.update()不需要
        self.enableImageSlideShowWidget.update(curMode == 0)

    def resizeEvent(self, *args, **kwargs):
        print("cur ToolContainer Geometry ", self.geometry())
        self.setFixedSize(self.size())
        # self.toolsScrollContainer.setFixedSize(self.size())