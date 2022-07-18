import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import *
from ToolsInterface import ToolsInterface
from enum import Enum
from Config import uiConfig

class LoadButton(QFrame, ToolsInterface):
    def __init__(self, parent, signal):
        super().__init__(parent)
        self.parent = parent
        self.loadBtn = QPushButton("Load Scan")
        self.setObjectName("LoadBtn")
        self.loadBtn.setMinimumSize(100,40)
        self.loadBtn.setEnabled(True)

        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.loadBtn)

        self.setLayout(layout)
        self.setEnabled(True)
        self.loadBtn.clicked.connect(signal)


