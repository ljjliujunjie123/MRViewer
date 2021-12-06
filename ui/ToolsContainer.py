from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ui.config import uiConfig
from ui.CustomSelectRegionTableWidget import CustomSelectRegionTableWidget

class ToolsContainer(QFrame):

    showInfoSig = pyqtSignal()

    updateImageShownLayoutSignal = pyqtSignal(tuple)
    enableImageSlideshowSignal = pyqtSignal(bool)

    def __init__(self, ParentWidget):
        QFrame.__init__(self, ParentWidget)

        self.setGeometry(uiConfig.calcToolsContainerGeometry())
        print("ToolsContainer Geometry:")
        print(self.geometry())
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Plain)
        self.setObjectName("toolsContainer")

        #功能1
        #一个可选择的表格，来调整文件渲染区的布局
        self.selectImageShownRegionTableWidget = CustomSelectRegionTableWidget()
        self.selectImageShownRegionTableWidget.setParent(self)

        #用来测试各个功能的button
        self.testButton = QPushButton(self)
        self.testButton.setGeometry(0, self.selectImageShownRegionTableWidget.height(), 100, 30)
        self.testButton.clicked.connect(self.updateImageShownLayoutSignalHandler)

        #用来展示信息的button
        self.pushButton = QPushButton(self)
        self.pushButton.setGeometry(0, self.selectImageShownRegionTableWidget.height() + self.testButton.height(), 100, 30)
        self.pushButton.clicked.connect(self.showInfoSig)
    #
    #     self.verticalLayoutWidget = QtWidgets.QWidget(self)
    #     self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 200, 1600))
    #     self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
    #     self.toolsVerticalContainer = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
    #     self.toolsVerticalContainer.setContentsMargins(0, 0, 0, 0)
    #     self.toolsVerticalContainer.setObjectName("toolsVerticalContainer")
    #
    #     self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
    #     self.horizontalLayout_2.setObjectName("horizontalLayout_2")
    #     spacerItem = QtWidgets.QSpacerItem(40, 20)
    #     self.horizontalLayout_2.addItem(spacerItem)
    #
    #     spacerItem1 = QtWidgets.QSpacerItem(40, 20)
    #     self.horizontalLayout_2.addItem(spacerItem1)
    #     self.pushButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
    #     self.pushButton.setObjectName("pushButton")
    #     self.horizontalLayout_2.addWidget(self.pushButton)
    #     spacerItem2 = QtWidgets.QSpacerItem(40, 20)
    #     self.horizontalLayout_2.addItem(spacerItem2)
    #     self.toolsVerticalContainer.addLayout(self.horizontalLayout_2)
    #
    #     self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
    #     self.horizontalLayout_3.setObjectName("horizontalLayout_3")
    #     spacerItem3 = QtWidgets.QSpacerItem(40, 20)
    #     self.horizontalLayout_3.addItem(spacerItem3)
    #
    #     spacerItem4 = QtWidgets.QSpacerItem(40, 20)
    #     self.horizontalLayout_3.addItem(spacerItem4)
    #     self.pushButton_2 = QtWidgets.QPushButton(self.verticalLayoutWidget)
    #     self.pushButton_2.setObjectName("pushButton_2")
    #     self.horizontalLayout_3.addWidget(self.pushButton_2)
    #     spacerItem5 = QtWidgets.QSpacerItem(40, 20)
    #     self.horizontalLayout_3.addItem(spacerItem5)
    #     self.toolsVerticalContainer.addLayout(self.horizontalLayout_3)
    #
    #     self.horizontalLayout = QtWidgets.QHBoxLayout()
    #     self.horizontalLayout.setObjectName("horizontalLayout")
    #     spacerItem6 = QtWidgets.QSpacerItem(40, 20)
    #     self.horizontalLayout.addItem(spacerItem6)
    #
    #     spacerItem7 = QtWidgets.QSpacerItem(40, 20)
    #     self.horizontalLayout.addItem(spacerItem7)
    #     self.pushButton_3 = QtWidgets.QPushButton(self.verticalLayoutWidget)
    #     self.pushButton_3.setObjectName("pushButton_3")
    #     self.horizontalLayout.addWidget(self.pushButton_3)
    #     spacerItem8 = QtWidgets.QSpacerItem(40, 20)
    #     self.horizontalLayout.addItem(spacerItem8)
    #     self.toolsVerticalContainer.addLayout(self.horizontalLayout)
    #
    #     # self.pushButton.clicked.connect(self.showInfoSig)
    #
        #功能2 by evermg42
        #图像的自动轮播开启
        self.enableImageSlideshow = QCheckBox('跑马灯效果',self)
        self.enableImageSlideshow.setGeometry(0, self.selectImageShownRegionTableWidget.height() + self.testButton.height() + self.pushButton.height(), 150, 30)
        self.enableImageSlideshow.setEnabled(True) #设置是否启用,可自动变灰色
        self.enableImageSlideshow.setCheckState(False) #设置初始状态
        self.enableImageSlideshow.stateChanged.connect(self.enableImageSlideshowSignalHandler) #打勾就送信

    def updateImageShownLayoutSignalHandler(self):
        if len(self.selectImageShownRegionTableWidget.selectedRanges()) < 1:
            return
        selectedRegion = self.selectImageShownRegionTableWidget.selectedRanges()[0]
        layout = (
            selectedRegion.topRow(),
            selectedRegion.leftColumn(),
            selectedRegion.bottomRow(),
            selectedRegion.rightColumn()
        )
        print("确认布局", layout)
        self.updateImageShownLayoutSignal.emit(layout)


    def retranslateUi(self):
        _translate = QCoreApplication.translate
        self.pushButton.setText(_translate("MainWindow", "展示信息"))
        # self.pushButton_2.setText(_translate("MainWindow", "功能2"))
        # self.pushButton_3.setText(_translate("MainWindow", "功能3"))
        self.testButton.setText(_translate("MainWindow", "确认布局"))

    def enableImageSlideshowSignalHandler(self):
        self.enableImageSlideshowSignal.emit(self.enableImageSlideshow.isChecked())