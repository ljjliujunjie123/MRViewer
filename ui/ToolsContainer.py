from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ui.config import uiConfig
from ui.ToolsFactory import ToolsFactory, ToolNum
from ui.CustomDecoratedLayout import CustomDecoratedLayout

class ToolsContainer(QFrame):

    showInfoSig = pyqtSignal()

    
    updateImageShownLayoutSignal = pyqtSignal(tuple)
    enableImageSlideshowSignal = pyqtSignal(bool)
    imageModeSelectSignal = pyqtSignal(int)
    enableImageExtraInfoSignal = pyqtSignal(bool)
    initToolsContainerStateSignal = pyqtSignal()

    def __init__(self, ParentWidget):
        QFrame.__init__(self, ParentWidget)

        print("ToolsContainer Geometry:")
        print(self.geometry())
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Plain)
        self.setMinimumWidth(uiConfig.toolsContainerHintWidth)
        self.setObjectName("toolsContainer")

        #用竖向ScrollArea收敛所有功能
        self.toolsScrollArea = QScrollArea(self)
        self.toolsScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.toolsScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.toolsScrollArea.setFixedSize(self.size())
        self.toolsScrollArea.setStyleSheet("background-color: {0}".format(uiConfig.LightColor.Primary))

        self.toolsScrollContainer = QFrame(self.toolsScrollArea)
        self.toolsScrollContainer.setFixedSize(self.size())
        self.toolsScrollArea.setWidget(self.toolsScrollContainer)

        self.toolsScrollLayout = CustomDecoratedLayout(QVBoxLayout())
        self.toolsScrollLayout.setMargins(QMargins(10,10,10,10))
        self.toolsScrollLayout.setAlignment(Qt.AlignHCenter)

        #工厂模式
        self.toolFactory = ToolsFactory(self.toolsScrollContainer)

        # 功能1
        # 按钮唤起一个可选择的表格，来调整文件渲染区的布局
        self.selectRegionGridButton = \
            self.toolFactory.createTool(ToolNum.shownLayout, signal = self.updateImageShownLayoutSignal)
        self.toolsScrollLayout.getLayout().addWidget(self.selectRegionGridButton,0,Qt.AlignTop)
        # 功能2 by evermg42
        # 图像的自动轮播开启
        self.enableImageSlideShowWidget = \
            self.toolFactory.createTool(ToolNum.slideShow, signal = self.enableImageSlideshowSignal)
        self.toolsScrollLayout.getLayout().addWidget(self.enableImageSlideShowWidget,0,Qt.AlignTop)

        #功能3
        #图像的模式切换
        self.imageModeSelectWidget = \
            self.toolFactory.createTool(ToolNum.modeSelect, signal = self.imageModeSelectSignal)
        self.toolsScrollLayout.getLayout().addWidget(self.imageModeSelectWidget,0,Qt.AlignTop)

        #功能4
        #图像的附加信息开关
        self.enableImageExtraInfoWidget = \
            self.toolFactory.createTool(ToolNum.extraInfo, signal = self.enableImageExtraInfoSignal)
        self.toolsScrollLayout.getLayout().addWidget(self.enableImageExtraInfoWidget,0,Qt.AlignTop)

        self.toolsScrollLayout.getLayout().addStretch()
        self.toolsScrollContainer.setLayout(self.toolsScrollLayout.getLayout())

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
        self.toolsScrollArea.setFixedSize(self.size())
        self.toolsScrollContainer.setFixedSize(self.size())