from PyQt5.QtGui import QFont,QPainter,QPen,QBrush,QColor
from PyQt5.QtCore import *
from ToolsInterface import ToolsInterface
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class DisplayAdjustor(QFrame,ToolsInterface):
    def __init__(self, parent=None):
        QFrame.__init__(self, parent)
        self.parent = parent
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.setObjectName("DisplayAdjustor")
        #添加标签
        #设置字体
        titleFont=QFont()
        titleFont.setFamily("SimSun")
        titleFont.setPointSize(12)
        titleFont.setBold(True)
        sliderFont = QFont()
        sliderFont.setFamily("SimSun")
        sliderFont.setPointSize(9)
        sliderFont.setBold(True)
        #添加label
        titleLabel = QLabel("Display")
        titleLabel.setFont(titleFont)
        titleLabel.setStyleSheet('border-width:0px;color:#3894c8')
        contrastLabel=QLabel("Contrast")
        contrastLabel.setFont(sliderFont)
        opacityLabel=QLabel("Opacity")
        opacityLabel.setFont(sliderFont)
        shiftLabel=QLabel("Shift")
        shiftLabel.setFont(sliderFont)
        #添加开关
        contrastSlider = QSlider(Qt.Horizontal)
        opacitySlider = QSlider(Qt.Horizontal)
        shiftSlider = QSlider(Qt.Horizontal)
        #添加表单布局
        gridlayout = QFormLayout()
        gridlayout.setHorizontalSpacing(100)
        gridlayout.addRow(contrastLabel,contrastSlider)
        gridlayout.addRow(opacityLabel, opacitySlider)
        gridlayout.addRow(shiftLabel, shiftSlider)
        gridlayout.setAlignment(Qt.AlignRight)
        #添加到整体布局
        vlayout=QVBoxLayout()
        vlayout.addWidget(titleLabel)
        vlayout.addLayout(gridlayout)
        self.setLayout(vlayout)