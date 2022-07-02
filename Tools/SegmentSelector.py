from PyQt5.QtGui import QFont,QPainter,QPen,QBrush,QColor
from PyQt5.QtCore import *
from ToolsInterface import ToolsInterface
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Tools.SwitchButton import SwitchButton


class SegmentSelector(QFrame,ToolsInterface):
    def __init__(self, parent=None):
        QFrame.__init__(self, parent)
        self.parent = parent
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.setStyleSheet("border: 1px solid black;")
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
        titleLabel = QLabel("OAR Segmentation")
        titleLabel.setFont(titleFont)
        titleLabel.setStyleSheet('border-width:0px;color:#3894c8')
        cardiacLabel=QLabel("Cardiac")
        cardiacLabel.setFont(switchFont)
        cardiacLabel.setStyleSheet('border-width:0px;color:black')
        aortaLabel=QLabel("Aorta")
        aortaLabel.setFont(switchFont)
        aortaLabel.setStyleSheet('border-width:0px;color:black')
        boneLabel=QLabel("Bone")
        boneLabel.setFont(switchFont)
        boneLabel.setStyleSheet('border-width:0px;color:black')
        #添加开关
        cardiacSwitch = SwitchButton()
        aortalSwitch = SwitchButton()
        boneSwitch = SwitchButton()
        #添加表单布局
        gridlayout = QFormLayout()
        gridlayout.setHorizontalSpacing(100)
        gridlayout.addRow(cardiacLabel,cardiacSwitch)
        gridlayout.addRow(aortaLabel, aortalSwitch)
        gridlayout.addRow(boneLabel, boneSwitch)
        gridlayout.setAlignment(Qt.AlignRight)
        #添加到整体布局
        vlayout=QVBoxLayout()
        vlayout.addWidget(titleLabel)
        vlayout.addLayout(gridlayout)
        self.setLayout(vlayout)