from PyQt5.QtGui import QFont,QPainter,QPen,QBrush,QColor
from PyQt5.QtCore import *
from ToolsInterface import ToolsInterface
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Tools.SwitchButton import SwitchButton


class AnnotationSelector(QFrame,ToolsInterface):
    def __init__(self, parent=None):
        QFrame.__init__(self, parent)
        self.parent = parent
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.setObjectName("AnnotationSelector")
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
        titleLabel = QLabel("Annotation")
        titleLabel.setFont(titleFont)
        titleLabel.setStyleSheet('border-width:0px;color:#3894c8')
        cardiacLabel=QLabel("ROI 1")
        cardiacLabel.setFont(switchFont)
        cardiacLabel.setStyleSheet('border-width:0px;color:red')
        aortaLabel=QLabel("ROI 2")
        aortaLabel.setFont(switchFont)
        aortaLabel.setStyleSheet('border-width:0px;color:green')
        boneLabel=QLabel("ROI 3")
        boneLabel.setFont(switchFont)
        boneLabel.setStyleSheet('border-width:0px;color:blue')
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