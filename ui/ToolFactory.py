from ui.CustomSelectRegionGridWidget import CustomSelectRegionGridWidget
from ui.CustomDecoratedLayout import CustomDecoratedLayout
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon
from ui.config import uiConfig
from ui.SingleImageShownContainer import SingleImageShownContainer

class ToolFactory():
    imageShownLayout = 0
    imageSlideShow = 1
    imageModeSelect = 2
    imageExtraInfo = 3
    defaultTool = -1

    iconPaths = {
        SingleImageShownContainer.m2DMode:"ui_source/2d_mode.png",
        SingleImageShownContainer.m3DMode:"ui_source/3d_mode.png",
        SingleImageShownContainer.m3DFakeMode:"ui_source/3d_fake_mode.png",
        SingleImageShownContainer.mRTMode:"ui_source/RT_mode.png"
    }
    def __init__(self, parent):
        print("tool Factory")
        self.parent = parent

    def createTool(self, tag = defaultTool, **kwargs):
        frame = QFrame(self.parent)
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Plain)
        frame.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        frame.setEnabled(False)
        hBoxLayout = QHBoxLayout()
        hBoxLayout.setContentsMargins(0,0,0,0)
        hBoxLayout.setAlignment(Qt.AlignCenter)
        frame.setLayout(hBoxLayout)
        if len(kwargs) > 0: signal = kwargs["signal"]
        if tag == self.imageShownLayout:
            selectImageShownRegionGridWidget = CustomSelectRegionGridWidget(signal)
            selectImageShownRegionGridWidget.setParent(frame)
            selectImageShownRegionGridWidget.setMouseTracking(True)
            selectImageShownRegionGridWidget.setEnabled(False)
            hBoxLayout.addWidget(selectImageShownRegionGridWidget)
        elif tag == self.imageSlideShow:
            enableImageSlideshow = QCheckBox('跑马灯效果',frame)
            enableImageSlideshow.setEnabled(False) #设置是否启用,可自动变灰色
            enableImageSlideshow.setCheckState(False) #设置初始状态
            enableImageSlideshow.setTristate(False)
            enableImageSlideshow.stateChanged.connect(signal) #打勾就送信
            hBoxLayout.addWidget(enableImageSlideshow)
        elif tag == self.imageModeSelect:
            print("imageModeSelect")
            imageModeContainer = QFrame()
            imageHBoxLayout =  CustomDecoratedLayout(QHBoxLayout())
            imageHBoxLayout.initParamsForPlain()
            bt2D = self.createImageModeButton(SingleImageShownContainer.m2DMode, signal)
            bt3D = self.createImageModeButton(SingleImageShownContainer.m3DMode, signal)
            bt3DFake = self.createImageModeButton(SingleImageShownContainer.m3DFakeMode, signal)
            btRT = self.createImageModeButton(SingleImageShownContainer.mRTMode, signal)
            imageHBoxLayout.addWidgets([bt2D,bt3D,bt3DFake,btRT])
            imageModeContainer.setLayout(imageHBoxLayout.getLayout())
            hBoxLayout.addWidget(imageModeContainer)
        elif tag == self.imageExtraInfo:
            print("imageExtraInfo")
            enableImageExtraInfo = QCheckBox('展示附加信息',frame)
            enableImageExtraInfo.setEnabled(False) #设置是否启用,可自动变灰色
            enableImageExtraInfo.setCheckState(Qt.Unchecked) #设置初始状态
            enableImageExtraInfo.setTristate(False)
            enableImageExtraInfo.stateChanged.connect(signal) #打勾就送信
            hBoxLayout.addWidget(enableImageExtraInfo)
        else:
            pushButton = QPushButton(frame)
            hBoxLayout.addWidget(pushButton)

        return frame

    def createImageModeButton(self, mode, signal):
        button = QPushButton()
        button.setIcon(QIcon(self.iconPaths[mode]))
        button.setIconSize(uiConfig.imageModeIconSize)
        button.clicked.connect(lambda : signal.emit(mode))
        return button
#     ui->toolButton->setToolButtonStyle(Qt::ToolButtonTextUnderIcon);



