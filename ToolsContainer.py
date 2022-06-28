import imp
from sys import displayhook
from unittest import case
from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *#QVBoxLayout, QSizePolicy, QFrame, QHBoxLayout, QPushButton, QListWidget, QListWidgetItem, QWidget,QScrollArea
from enum import Enum
from Tools.LoadButton import LoadButton
# from Tools.DisplayAdjustor import
# from Tools.SegmentSelector import
# from Tools.Measure import
from Config import uiConfig
class ToolNum(Enum):
    load     = 0
    display  = 1
    segment  = 2
    meansure = 3
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
        else:
            frame = QFrame()
            frame.setContentsMargins(0,0,0,0)
            pushButton = QPushButton("")
            frame.addWidget(pushButton)


class ToolsContainer(QScrollArea):
    loadSignal = pyqtSignal()

    def __init__(self, parent):
        QFrame.__init__(self, parent)
        #style
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Plain)
        self.setMinimumWidth(uiConfig.toolsContainerHintWidth)
        self.setContentsMargins(0,0,0,0)
        self.setObjectName("toolsContainer")

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.setFixedSize(self.size())
        # self.setStyleSheet("background-color: {0}".format(uiConfig.LightColor.Primary))

        self.toolsScrollContainer = QFrame(self)
        # self.toolsScrollContainer.setFixedSize(self.size())
        self.setWidget(self.toolsScrollContainer)

        self.toolsScrollLayout = QVBoxLayout()
        self.toolsScrollLayout.setAlignment(Qt.AlignHCenter)

        #工厂模式
        self.toolFactory = ToolsFactory(self.toolsScrollContainer)

        # 功能1 load files
        self.loadButton = self.toolFactory.createTool(ToolNum.load, signal = self.loadSignal)
        self.toolsScrollLayout.addWidget(self.loadButton,0,Qt.AlignTop)

        self.toolsScrollLayout.addStretch()
        self.toolsScrollContainer.setLayout(self.toolsScrollLayout)

    def resizeEvent(self, *args, **kwargs):
        print("cur ToolContainer Geometry ", self.geometry())
        self.setFixedSize(self.size())
        self.toolsScrollContainer.setFixedSize(self.size())