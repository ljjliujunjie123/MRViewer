from ui.CustomSelectRegionGridWidget import CustomSelectRegionGridWidget
from ui.CustomDecoratedLayout import CustomDecoratedLayout
from ui.Tools.SelectRegionGridButton import SelectRegionGridButton
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from ui.Tools.SlideshowButton import SlideshowButton
from ui.config import uiConfig

from ui.Tools.ExtraInfoButton import ExtraInfoButton
from ui.Tools.ImageModeContainer import ImageModeContainer
from enum import Enum

class ToolNum(Enum):
    shownLayout = 0
    slideShow = 1
    modeSelect = 2
    extraInfo = 3
    default = -1

class ToolsFactory():

    def __init__(self, parent):
        print("tool Factory")
        self.parent = parent

    def createTool(self, tag = ToolNum.default, **kwargs):
        frame = QFrame(self.parent)
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Plain)
        frame.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)

        if len(kwargs) > 0: signal = kwargs["signal"]

        if tag == ToolNum.shownLayout:
            selectRegionGridButton = SelectRegionGridButton(signal)
            return selectRegionGridButton

        elif tag == ToolNum.slideShow:
            imgPath = "ui_source/slide_show.png"
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
            pushButton = QPushButton("")
            layout.addWidget(pushButton)

        frame.setLayout(layout)
        frame.setEnabled(True)
        return frame