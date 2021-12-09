from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ui.config import uiConfig
from ui.ToolFactory import ToolFactory
class ToolsContainer(QFrame):

    showInfoSig = pyqtSignal()

    updateImageShownLayoutSignal = pyqtSignal(tuple)
    enableImageSlideshowSignal = pyqtSignal(int)
    imageModeSelectSignal = pyqtSignal(int)
    enableImageExtraInfoSignal = pyqtSignal(int)

    def __init__(self, ParentWidget):
        QFrame.__init__(self, ParentWidget)

        self.setGeometry(uiConfig.calcToolsContainerGeometry())
        print("ToolsContainer Geometry:")
        print(self.geometry())
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Plain)
        self.setObjectName("toolsContainer")

        #每一个功能用一个Frame包裹起来，用竖向ScrollArea收敛所有功能
        self.toolsScrollArea = QScrollArea(self)
        self.toolsScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.toolsScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.toolsScrollArea.setFixedSize(self.size())

        self.toolsScrollContainer = QFrame(self.toolsScrollArea)
        self.toolsScrollContainer.setFixedSize(self.size())
        self.toolsScrollArea.setWidget(self.toolsScrollContainer)

        self.toolsScrollLayout = QVBoxLayout()
        self.toolsScrollLayout.setContentsMargins(0,0,0,0)
        self.toolsScrollLayout.setSpacing(5)
        self.toolsScrollLayout.setAlignment(Qt.AlignHCenter)
        self.toolsScrollContainer.setLayout(self.toolsScrollLayout)

        #工厂模式
        self.toolFactory = ToolFactory(self.toolsScrollContainer)

        #功能1
        #一个可选择的表格，来调整文件渲染区的布局
        self.selectImageShownRegionWidget = \
            self.toolFactory.createTool(ToolFactory.imageShownLayout, signal = self.updateImageShownLayoutSignal)
        self.toolsScrollLayout.addWidget(self.selectImageShownRegionWidget)

        # 功能2 by evermg42
        # 图像的自动轮播开启
        self.enableImageSlideShowWidget = \
            self.toolFactory.createTool(ToolFactory.imageSlideShow, signal = self.enableImageSlideshowSignal)
        self.toolsScrollLayout.addWidget(self.enableImageSlideShowWidget)

        #功能3
        #图像的模式切换
        self.imageModeSelectWidget = \
            self.toolFactory.createTool(ToolFactory.imageModeSelect, signal = self.imageModeSelectSignal)
        self.toolsScrollLayout.addWidget(self.imageModeSelectWidget)

        #功能4
        #图像的附加信息开关
        self.enableImageExtraInfoWidget = \
            self.toolFactory.createTool(ToolFactory.imageExtraInfo, signal = self.enableImageExtraInfoSignal)
        self.toolsScrollLayout.addWidget(self.enableImageExtraInfoWidget)

        #占位的功能
        for i in range(4):
            self.toolsScrollLayout.addWidget(self.toolFactory.createTool())

        # #用来测试各个功能的button
        # self.testButton = QPushButton(self)
        # self.testButton.setGeometry(0, self.selectImageShownRegionTableWidget.height(), 100, 30)
        # self.testButton.clicked.connect(self.updateImageShownLayoutSignalHandler)
        #
        # #用来展示信息的button
        # self.pushButton = QPushButton(self)
        # self.pushButton.setGeometry(0, self.selectImageShownRegionTableWidget.height() + self.testButton.height(), 100, 30)
        # self.pushButton.clicked.connect(self.showInfoSig)

    def updateToolsContainerStateHandler(self, state):
        for i in range(self.toolsScrollLayout.count()):
            widget = self.toolsScrollLayout.itemAt(i).widget()
            widget.setEnabled(state)
            layout = widget.layout()
            for i in range(layout.count()):
                subWidget = layout.itemAt(i).widget()
                subWidget.setEnabled(state)

    def retranslateUi(self):
        _translate = QCoreApplication.translate
        # self.pushButton.setText(_translate("MainWindow", "展示信息"))
        # self.testButton.setText(_translate("MainWindow", "确认布局"))

    def enableImageSlideshowSignalHandler(self):
        self.enableImageSlideshowSignal.emit(self.enableImageSlideShowWidget.isChecked())

    def resizeEvent(self, *args, **kwargs):
        print("cur ToolContainer Geometry ", self.geometry())
        self.toolsScrollArea.setFixedSize(self.size())
        self.toolsScrollContainer.setFixedSize(self.size())