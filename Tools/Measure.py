from PyQt5.QtGui import QFont,QPainter,QPen,QBrush,QColor
from PyQt5.QtCore import *
from ToolsInterface import ToolsInterface
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Tools.SwitchButton import SwitchButton


class Measure(QFrame,ToolsInterface):
    def __init__(self, parent=None):
        QFrame.__init__(self, parent)
        self.parent = parent
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.setObjectName("Measure")
        #添加标签
        #设置字体
        titleFont=QFont()
        titleFont.setFamily("SimSun")
        titleFont.setPointSize(12)
        titleFont.setBold(True)
        switchFont = QFont()
        switchFont.setFamily("SimSun")
        switchFont.setPointSize(9)
        switchFont.setBold(True)
        #添加label
        titleLabel = QLabel("Measure")
        titleLabel.setFont(titleFont)
        titleLabel.setStyleSheet('border-width:0px;color:#3894c8')
        cardiacLabel=QLabel("Cardiac")
        cardiacLabel.setFont(switchFont)
        #添加开关
        measureBtn = QPushButton("Measure")
        measureBtn.setFixedSize(100,40)
        text = QLineEdit()
        text.setText("0")
        text.setAlignment(Qt.AlignHCenter)
        text.setFixedSize(40,40)
        #添加表单布局
        gridlayout = QHBoxLayout()
        gridlayout.setAlignment(Qt.AlignLeft)
        gridlayout.setSpacing(130)
        gridlayout.addWidget(measureBtn)
        gridlayout.addWidget(text)
        gridlayout.setStretchFactor(measureBtn,1)
        gridlayout.setStretchFactor(text,1)
        #添加到整体布局
        vlayout=QVBoxLayout()
        vlayout.addWidget(titleLabel)
        vlayout.addLayout(gridlayout)
        self.setLayout(vlayout)