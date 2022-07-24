from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ui.config import uiConfig
from ui.ToolFactory import ToolFactory, ToolNum
class ToolsContainer(QFrame):

    showInfoSig = pyqtSignal()

    updateImageShownLayoutSignal = pyqtSignal(tuple)
    enableImageSlideshowSignal = pyqtSignal(bool)
    imageModeSelectSignal = pyqtSignal(int)
    enableImageExtraInfoSignal = pyqtSignal(bool)

    def __init__(self, ParentWidget):
        QFrame.__init__(self, ParentWidget)

        self.setGeometry(uiConfig.calcToolsContainerGeometry())
        print("ToolsContainer Geometry:")
        print(self.geometry())
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Plain)
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
        self.toolFactory = ToolFactory(self.toolsScrollContainer)

        #功能1
        #一个可选择的表格，来调整文件渲染区的布局
        self.selectImageShownRegionWidget = \
            self.toolFactory.createTool(ToolNum.shownLayout, signal = self.updateImageShownLayoutSignal)
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

    def updateToolsContainerStateHandler(self, case, curMode,showExtraInfoFlag):
        if case == 0:# 情形0：初始化
            print("case==0 初始化")
            for i in range(self.toolsScrollLayout.count()):
                widget = self.toolsScrollLayout.itemAt(i).widget()
                if widget == None:continue
                widget.setEnabled(True)
                layout = widget.layout()
                if layout != None:
                    for j in range(layout.count()):
                        subWidget = layout.itemAt(j).widget()
                        print(i)
                        if subWidget == None:continue
                        subWidget.setEnabled(True)
                if i == 3:
                    widget.setChecked(True)

        if case == 1:# 情形1：选定另一张图片
            print("case==1 选定另一张图片")
            widget = self.toolsScrollLayout.itemAt(1).widget().layout().itemAt(0).widget()
            if curMode == 0:
                widget.setEnabled(True)
            else:
                widget.setEnabled(False)
            if curMode == 0 and widget.checkState() == Qt.Checked:
                widget.setCheckState(Qt.Checked)
            else:
                widget.setCheckState(Qt.Unchecked)

            widget3 = self.toolsScrollLayout.itemAt(3).widget()
            if curMode == 0:
                widget3.setEnabled = True
            else:
                widget3.setEnabled = False
            widget3.setCheckState(showExtraInfoFlag and Qt.Checked or Qt.Unchecked)

        if case == 2:# 情形2：切换2D/3D模式
            print("case==2 切换2D/3D模式")
            widget = self.toolsScrollLayout.itemAt(1).widget()
            widget3 = self.toolsScrollLayout.itemAt(3).widget()

            widget.setChecked(False)
            if curMode == 0:#如果是3D
                widget3.setChecked(True)
                widget3.setEnabled(True)
                widget.setEnabled(True)
            else:
                widget3.setChecked(False)
                widget3.setEnabled(False)
                widget.setEnabled(False)

                
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