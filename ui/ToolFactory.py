from ui.CustomSelectRegionGridWidget import CustomSelectRegionGridWidget
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class ToolFactory():
    imageShownLayout = "imageShownLayout"
    imageSlideShow = "imageSlideShow"
    defaultTool = "default"
    def __init__(self, parent):
        print("tool Factory")
        self.parent = parent
        self.tags = {
            self.imageShownLayout: 0,
            self.imageSlideShow: 1,
            self.defaultTool: -1
        }

    def createTool(self, tag = defaultTool, **kwargs):
        frame = QFrame(self.parent)
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Plain)
        frame.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        hBoxLayout = QHBoxLayout()
        hBoxLayout.setContentsMargins(0,0,0,0)
        hBoxLayout.setAlignment(Qt.AlignCenter)
        frame.setLayout(hBoxLayout)
        if len(kwargs) > 0: signal = kwargs["signal"]
        if self.tags[tag] == 0:
            selectImageShownRegionGridWidget = CustomSelectRegionGridWidget(signal)
            selectImageShownRegionGridWidget.setParent(frame)
            selectImageShownRegionGridWidget.setMouseTracking(True)
            hBoxLayout.addWidget(selectImageShownRegionGridWidget)
        elif self.tags[tag] == 1:
            enableImageSlideshow = QCheckBox('跑马灯效果',frame)
            enableImageSlideshow.setEnabled(True) #设置是否启用,可自动变灰色
            enableImageSlideshow.setCheckState(False) #设置初始状态
            enableImageSlideshow.stateChanged.connect(signal) #打勾就送信
            hBoxLayout.addWidget(enableImageSlideshow)
        else:
            pushButton = QPushButton(frame)
            hBoxLayout.addWidget(pushButton)

        return frame

