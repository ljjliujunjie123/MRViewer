from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon,QColor,QFont
from PyQt5.QtCore import QRect,QSize,QPoint
from PyQt5 import Qt
from ui.CustomSelectRegionGridWidget import CustomSelectRegionGridWidget
from ui.Tools.ToolsInterface import ToolsInterface
from ui.config import uiConfig
class SelectRegionGridButton(QFrame, ToolsInterface):
    def __init__(self, signal):
        super().__init__()
        imgPath = "ui_source/select_region_grid.png"
        self.selectRegionGridBtn = QPushButton()
        self.selectRegionGridBtn.setIcon(QIcon(imgPath))
        self.selectRegionGridBtn.setIconSize(uiConfig.toolsIconSize)
        self.selectRegionGridBtn.setCheckable(True)
        self.selectRegionGridBtn.setChecked(False)
        self.selectRegionGridBtn.clicked.connect(lambda:self.createGridWidget(signal))
        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.selectRegionGridBtn)
        self.setLayout(layout)
        self.setEnabled(False)


    def init(self):
        self.setEnabled(True)

    def update(self, available):
        self.selectRegionGridBtn.setChecked(False)
        self.setEnabled(available)

    def createGridWidget(self, signal):
        print(self.geometry)
        self.selectRegionGridWidget = CustomSelectRegionGridWidget(self, signal)
        buttonGlobalPos = self.selectRegionGridBtn.mapToGlobal(QPoint(0,0))
        self.selectRegionGridWidget.setGeometry(buttonGlobalPos.x() - self.selectRegionGridWidget.width(), buttonGlobalPos.y(), self.selectRegionGridWidget.width(), self.selectRegionGridWidget.height())
        print("btn位置", buttonGlobalPos)
        self.installEventFilter(self.selectRegionGridWidget)
        self.selectRegionGridWidget.show()
