from ui.CustomSelectRegionGridWidget import CustomSelectRegionGridWidget
from ui.CustomDecoratedLayout import CustomDecoratedLayout
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon
from ui.config import uiConfig
from ui.SingleImageShownContainer import SingleImageShownContainer
from enum import Enum



class ToolNum(Enum):
    shownLayout = 0
    slideShow = 1
    modeSelect = 2
    extraInfo = 3
    default = -1

class ToolFactory():
    

    iconPaths = {
        SingleImageShownContainer.m2DMode:"ui_source/2d_mode.png",
        SingleImageShownContainer.m3DMode:"ui_source/3d_mode.png",
        SingleImageShownContainer.m3DFakeMode:"ui_source/3d_fake_mode.png",
        SingleImageShownContainer.mRTMode:"ui_source/RT_mode.png"
    }
    def __init__(self, parent):
        print("tool Factory")
        self.parent = parent

    def createTool(self, tag = ToolNum.default, **kwargs):

        if len(kwargs) > 0: signal = kwargs["signal"]

        if tag == ToolNum.shownLayout:
            selectImageShownRegionGridWidget = CustomSelectRegionGridWidget(signal)
            selectImageShownRegionGridWidget.setToolTip("屏幕布局")
            selectImageShownRegionGridWidget.setMouseTracking(True)
            selectImageShownRegionGridWidget.setEnabled(False)
            return selectImageShownRegionGridWidget

        elif tag == ToolNum.slideShow:
            imgPath = "ui_source/slide_show.png"
            enableSlideshow = QPushButton()
            enableSlideshow.setToolTip("跑马灯")
            enableSlideshow.setIcon(QIcon(imgPath))
            enableSlideshow.setIconSize(QSize(80,80))
            enableSlideshow.setEnabled(False) #设置是否启用,可自动变灰色
            enableSlideshow.setCheckable(True)
            enableSlideshow.setChecked(False)
            enableSlideshow.clicked.connect(signal) #打勾就送信
            return enableSlideshow

        elif tag == ToolNum.modeSelect:
            print("imageModeSelect")
            imageModeContainer = QFrame()
            imageModeContainer.setToolTip("模式切换")
            imageVBoxLayout =  CustomDecoratedLayout(QVBoxLayout())
            imageVBoxLayout.initParamsForPlain()
            bt2D = self.createImageModeButton(SingleImageShownContainer.m2DMode, signal)
            bt3D = self.createImageModeButton(SingleImageShownContainer.m3DMode, signal)
            bt3DFake = self.createImageModeButton(SingleImageShownContainer.m3DFakeMode, signal)
            btRT = self.createImageModeButton(SingleImageShownContainer.mRTMode, signal)
            imageVBoxLayout.addWidgets([bt2D,bt3D,bt3DFake,btRT])
            imageModeContainer.setLayout(imageVBoxLayout.getLayout())
            imageModeContainer.setEnabled(False)
            return imageModeContainer

        elif tag == ToolNum.extraInfo:
            imgPath = "ui_source/extra_info.png"
            enableImageExtraInfo = QPushButton()
            enableImageExtraInfo.setToolTip("图像详细信息")
            enableImageExtraInfo.setIcon(QIcon(imgPath))
            enableImageExtraInfo.setIconSize(QSize(80,80))
            
            enableImageExtraInfo.setEnabled(False) #设置是否启用,可自动变灰色
            enableImageExtraInfo.setCheckable(True)
            enableImageExtraInfo.setChecked(False)
            enableImageExtraInfo.clicked.connect(signal) #打勾就送信
            return enableImageExtraInfo
        else:
            pushButton = QPushButton("")
            return pushButton


    def createImageModeButton(self, mode, signal):
        button = QPushButton()
        button.setIcon(QIcon(self.iconPaths[mode]))
        button.setIconSize(uiConfig.imageModeIconSize)
        button.clicked.connect(lambda : signal.emit(mode))
        return button
#     ui->toolButton->setToolButtonStyle(Qt::ToolButtonTextUnderIcon);



