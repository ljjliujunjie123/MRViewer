from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon,QColor,QFont
from PyQt5.QtCore import QRect,QSize
from PyQt5 import Qt
from ToolsInterface import ToolsInterface
from Config import uiConfig
class SlideshowButton(QFrame, ToolsInterface):
    def __init__(self, signal):
        super().__init__()

        imgPath = "ui_source/slide_show.png"
        self.slideshowBtn = QPushButton()
        self.slideshowBtn.setIcon(QIcon(imgPath))
        self.slideshowBtn.setIconSize(uiConfig.toolsIconSize)
        #down为开启，up为关闭
        self.slideshowBtn.clicked.connect(signal)

        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.slideshowBtn)

        self.setLayout(layout)
        self.setEnabled(False)

    def init(self):
        self.setEnabled(True)

    def update(self, available):
        self.slideshowBtn.setChecked(False)
        self.setEnabled(available)
