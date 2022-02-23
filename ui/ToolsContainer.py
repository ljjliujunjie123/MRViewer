from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ui.config import uiConfig
from ui.ToolsFactory import ToolsFactory, ToolNum
class ToolsContainer(QFrame):

    showInfoSig = pyqtSignal()

    
    enableImageShownLayoutSignal = pyqtSignal(bool)
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
        self.toolsScrollArea.setStyleSheet("background-color: grey")

        self.toolsScrollContainer = QFrame(self.toolsScrollArea)
        self.toolsScrollContainer.setFixedSize(self.size())
        self.toolsScrollArea.setWidget(self.toolsScrollContainer)

        self.toolsScrollLayout = QVBoxLayout()
        self.toolsScrollLayout.setContentsMargins(10,10,10,10)
        # self.toolsScrollLayout.setAlignment(Qt.AlignHCenter)

        #工厂模式
        self.toolFactory = ToolsFactory(self.toolsScrollContainer)

        #功能1
        #一个可选择的表格，来调整文件渲染区的布局
        self.selectImageShownRegionWidget = \
            self.toolFactory.createTool(ToolNum.shownLayout, signal = self.enableImageShownLayoutSignal)
        self.toolsScrollLayout.addWidget(self.selectImageShownRegionWidget,0,Qt.AlignTop)
        # 功能2 by evermg42
        # 图像的自动轮播开启
        self.enableImageSlideShowWidget = \
            self.toolFactory.createTool(ToolNum.slideShow, signal = self.enableImageSlideshowSignal)
        self.toolsScrollLayout.addWidget(self.enableImageSlideShowWidget,0,Qt.AlignTop)

        #功能3
        #图像的模式切换
        self.imageModeSelectWidget = \
            self.toolFactory.createTool(ToolNum.modeSelect, signal = self.imageModeSelectSignal)
        self.toolsScrollLayout.addWidget(self.imageModeSelectWidget,0,Qt.AlignTop)

        #功能4
        #图像的附加信息开关
        self.enableImageExtraInfoWidget = \
            self.toolFactory.createTool(ToolNum.extraInfo, signal = self.enableImageExtraInfoSignal)
        self.toolsScrollLayout.addWidget(self.enableImageExtraInfoWidget,0,Qt.AlignTop)

        #占位的功能
        # for i in range(4):
        #     self.toolsScrollLayout.addWidget(self.toolFactory.createTool())

        self.toolsScrollLayout.addStretch()
        self.toolsScrollContainer.setLayout(self.toolsScrollLayout)
        # #用来测试各个功能的button
        # self.testButton = QPushButton(self)
        # self.testButton.setGeometry(0, self.selectImageShownRegionTableWidget.height(), 100, 30)
        # self.testButton.clicked.connect(self.updateImageShownLayoutSignalHandler)
        #
        # #用来展示信息的button
        # self.pushButton = QPushButton(self)
        # self.pushButton.setGeometry(0, self.selectImageShownRegionTableWidget.height() + self.testButton.height(), 100, 30)
        # self.pushButton.clicked.connect(self.showInfoSig)

    def initToolsContainerStateHandler(self):
        self.selectImageShownRegionWidget.init()
        self.enableImageExtraInfoWidget.init()
        self.imageModeSelectWidget.init()
        self.enableImageSlideShowWidget.init()

    def updateToolsContainerStateHandler(self, curMode):
        # self.selectImageShownRegionWidget.update()不需要
        self.enableImageExtraInfoWidget.update(curMode == 0)
        # self.imageModeSelectWidget.update()不需要
        self.enableImageSlideShowWidget.update(curMode == 0)

                
    def retranslateUi(self):
        _translate = QCoreApplication.translate
        # self.pushButton.setText(_translate("MainWindow", "展示信息"))
        # self.testButton.setText(_translate("MainWindow", "确认布局"))

    def resizeEvent(self, *args, **kwargs):
        print("cur ToolContainer Geometry ", self.geometry())
        self.toolsScrollArea.setFixedSize(self.size())
        self.toolsScrollContainer.setFixedSize(self.size())