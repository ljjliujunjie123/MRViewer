from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from ToolsContainer import ToolsContainer, ExtraToolsContainer

class ControlArea(QFrame):
    def __init__(self, parent):
        QFrame.__init__(self)
        self.parent = parent
        self.setObjectName("ControlArea")
        self.InitControlArea()

    def InitControlArea(self):
        self.InitLayout()
        self.InitContent()

    def InitLayout(self):
        self.hlayout = QHBoxLayout(self)
        self.hlayout.setSpacing(5)  
        self.hlayout.setContentsMargins(0,0,0,0) 
        self.hlayout.setAlignment(Qt.AlignCenter)  

    def InitContent(self):
        # 实例化两个左侧边栏的组件
        self.operationModeLayout = QVBoxLayout(self)
        self.vlayout = QVBoxLayout(self)
        self.toolsContainer = ToolsContainer(self)
        self.extraToolsContainer = ExtraToolsContainer(self)
        self.hlayout.addLayout(self.operationModeLayout)
        self.hlayout.addLayout(self.vlayout)
        self.hlayout.setStretchFactor(self.operationModeLayout, 1)
        self.hlayout.setStretchFactor(self.vlayout, 4)

        self.vlayout.addWidget(self.toolsContainer)
        self.vlayout.addWidget(self.extraToolsContainer)
        self.vlayout.setStretchFactor(self.toolsContainer, 2)
        self.vlayout.setStretchFactor(self.extraToolsContainer, 1)

        # 设置展示规则
        self.toolsContainer.setFrameShape(QListWidget.NoFrame) # 去除边框
        self.toolsContainer.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.extraToolsContainer.setFrameShape(QListWidget.NoFrame) # 去除边框
        self.extraToolsContainer.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)

        # 设置字体
        font1 = QFont()
        font1.setFamily("Times New Roman")
        font1.setPointSize(9)
        font1.setBold(True)

        self.operationModeLayout.setAlignment(Qt.AlignTop|Qt.AlignHCenter)
        self.operationModeLayout.setSpacing(60)
        self.operationModeLayout.setContentsMargins(0,30,0,0) 
        # 术前按钮
        self.preOprBtn = QPushButton("Pre")
        self.preOprBtn.setFont(font1)
        self.preOprBtn.setObjectName("OprBtn")
        self.preOprBtn.setFixedSize(50,50)
        self.operationModeLayout.addWidget(self.preOprBtn)
        # self.preOprBtn.clicked.connect(signal)#down为开启，up为关闭
        
        # 术中按钮
        self.intraOprBtn = QPushButton("Intra")
        self.intraOprBtn.setFont(font1)
        self.intraOprBtn.setObjectName("OprBtn")
        self.intraOprBtn.setFixedSize(50,50)
        self.operationModeLayout.addWidget(self.intraOprBtn)
        # self.intraOprBtn.clicked.connect(signal)#down为开启，up为关闭

        # 术后按钮
        self.postOprBtn = QPushButton("Post")
        self.postOprBtn.setFont(font1)
        self.postOprBtn.setObjectName("OprBtn")
        self.postOprBtn.setFixedSize(50,50)
        self.operationModeLayout.addWidget(self.postOprBtn)
        # self.postOprBtn.clicked.connect(signal)#down为开启，up为关闭

        # 为listitem添加点击事件，切换stackedwidget页面

    def item_clicked(self):
        # 获取当前选中的item
        item = self.operationModeLayout.selectedItems()[0]
        if item.text() == 'Pre':
            self.switch_dataView()
        elif item.text() == 'Intra':
            self.switch_dataLog()
        elif item.text() == 'Post':
            self.switch_paramWidget()
        else:
            self.switch_export()
    def resizeEvent(self, *args, **kwargs):
        print("cur operationModeLayout Geometry ", self.operationModeLayout.geometry())
        


