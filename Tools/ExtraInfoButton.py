from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import *
from ToolsInterface import ToolsInterface
from PyQt5.Qt import Qt
from Config import uiConfig


class ExtraInfoButton(QFrame, ToolsInterface):
    
    def __init__(self, parent, signal):
        super().__init__(parent)
        imgPath = "ui_source/extra_info.png"
        self.extraInfoBtn = QPushButton()
        self.extraInfoBtn.setToolTip("图像注释")
        self.extraInfoBtn.setIcon(QIcon(imgPath))
        self.extraInfoBtn.setIconSize(uiConfig.toolsIconSize)
        self.extraInfoBtn.setCheckable(True)
        self.extraInfoBtn.setChecked(False)
        self.extraInfoBtn.clicked.connect(signal)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.extraInfoBtn)

        self.setLayout(layout)
        self.setEnabled(False)

    def init(self):
        self.setEnabled(True)
        self.extraInfoBtn.setChecked(True)

    def update(self, available):
        if available:
            self.extraInfoBtn.setChecked(True)
        else:
            self.extraInfoBtn.setChecked(False)
        self.setEnabled(available)
    
        


