from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QSizePolicy, QFrame, QHBoxLayout, QListWidget, QListWidgetItem, QWidget

from ToolsContainer import ToolsContainer

class ControlArea(QFrame):
    def __init__(self, parent):
        QFrame.__init__(self)
        self.parent = parent
        self.InitControlArea()

    def InitControlArea(self):
        self.InitLayout()
        self.InitContent()

    def InitLayout(self):
        self.leftFrame_HLayout = QHBoxLayout(self)
        self.leftFrame_HLayout.setSpacing(5)  
        self.leftFrame_HLayout.setContentsMargins(0,0,0,0) 
        self.leftFrame_HLayout.setAlignment(QtCore.Qt.AlignCenter)  

    def InitContent(self):
        # 实例化两个左侧边栏的组件
        self.operationModeSelector = QListWidget(self)
        self.leftFrame_HLayout.addWidget(self.operationModeSelector)
        self.toolsContainer = ToolsContainer(self)
        self.leftFrame_HLayout.addWidget(self.toolsContainer)

        # 设置展示规则
        self.operationModeSelector.setFrameShape(QListWidget.NoFrame) # 去除边框
        self.operationModeSelector.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # 隐藏垂直滚动条
        self.operationModeSelector.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)# 隐藏水平滚动条
        self.operationModeSelector.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.toolsContainer.setFrameShape(QListWidget.NoFrame) # 去除边框
        self.toolsContainer.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)

        # 设置字体
        font_1 = QtGui.QFont()
        font_1.setFamily("黑体")
        font_1.setPointSize(12)
        font_1.setBold(False)
        self.operationModeSelector.setFont(font_1)


        # 术前按钮
        preIcon = QtGui.QIcon()
        # preIcon.addPixmap(QtGui.QPixmap("./icons/dataView.png"),
        # QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.dataView_item = QListWidgetItem(preIcon,'Pre',self.operationModeSelector)
        self.dataView_item.setSizeHint(QtCore.QSize(30,60))
        self.dataView_item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.preTool = QWidget()
        # self.toolsContainer.addWidget(self.preTool)


        # 术中按钮
        intraIcon = QtGui.QIcon()
        # intraIcon.addPixmap(QtGui.QPixmap("./icons/dataLog.png"),
        # QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.dataLog_item = QListWidgetItem(intraIcon,'Intra',self.operationModeSelector)
        self.dataLog_item.setSizeHint(QtCore.QSize(30,60))
        self.dataLog_item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.intraTool = QWidget()
        # self.toolsContainer.addWidget(self.intraTool)
        
        # 术后按钮
        postIcon = QtGui.QIcon()
        # postIcon.addPixmap(QtGui.QPixmap("./icons/figureParam.png"),
        # QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.param_item = QListWidgetItem(postIcon,'Post',self.operationModeSelector)
        self.param_item.setSizeHint(QtCore.QSize(30,60))
        self.param_item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.postTool = QWidget()
        # self.toolsContainer.addWidget(self.postTool)

        # 为listitem添加点击事件，切换stackedwidget页面
        self.operationModeSelector.itemClicked.connect(self.item_clicked)

    def item_clicked(self):
        # 获取当前选中的item
        item = self.operationModeSelector.selectedItems()[0]
        if item.text() == 'Pre':
            self.switch_dataView()
        elif item.text() == 'Intra':
            self.switch_dataLog()
        elif item.text() == 'Post':
            self.switch_paramWidget()
        else:
            self.switch_export()
    def resizeEvent(self, *args, **kwargs):
        print("cur operationModeSelector Geometry ", self.operationModeSelector.geometry())
        


