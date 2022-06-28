from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QMouseEvent, QIcon


# Thanks to https://www.cnblogs.com/linuxAndMcu/p/10609182.html
# https://wenku.baidu.com/view/7cfd5ccb0a75f46527d3240c844769eae009a3c1.html
class TitleBar(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self,parent)
        self.parent = parent
        self.setFixedHeight(30)
         
        self.iconLabel = QLabel(self)
        self.titleLabel = QLabel(self)

        self.fileOpener = QMenu(self)
        self.actionopen_study = QAction(self)
        self.actionopen_patient = QAction(self)
        self.fileOpener.setObjectName("fileOpener")
        self.fileOpener.addAction(self.actionopen_study)
        self.fileOpener.addAction(self.actionopen_patient)
        self.minBtn = QPushButton("")
        self.maxBtn = QPushButton("")
        self.closeBtn = QPushButton("")
        # 图标和标题
        self.iconLabel.setFixedSize(20,20)
        self.iconLabel.setScaledContents(True)
        self.titleLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # 文件打开

        # 设置最小化按钮
        self.minBtn.setStyleSheet(
        '''
            QPushButton{background:#6DDF6D;border-radius:5px}
            QPushButton:hover{background:green}
        '''
        )
        self.minBtn.setFixedSize(15,15)
        self.minBtn.clicked.connect(self.parent.showMinimized)
        # 设置最大化按钮
        self.maxBtn.setStyleSheet(
        '''
            QPushButton{background:#F7D674;border-radius:5px}
            QPushButton:hover{background:yellow}
        '''
        )
        self.maxBtn.setFixedSize(15,15)
        self.maxBtn.clicked.connect(self.parent.showMaximized)
        
        # 设置关闭按钮
        self.closeBtn.setStyleSheet(
        '''
            QPushButton{background:#F76677;border-radius:5px}
            QPushButton:hover{background:red}
        '''
        )
        self.closeBtn.setFixedSize(15,15)
        self.closeBtn.clicked.connect(QCoreApplication.instance().quit)

        #标题布局
        pLayout = QHBoxLayout(self)
        pLayout.addWidget(self.iconLabel)
        pLayout.addSpacing(5)
        pLayout.addWidget(self.titleLabel)
        pLayout.addWidget(self.minBtn)
        pLayout.addSpacing(5)
        pLayout.addWidget(self.maxBtn)
        pLayout.addSpacing(5)
        pLayout.addWidget(self.closeBtn)
        pLayout.addSpacing(5)
        pLayout.setContentsMargins(5, 0, 5, 0)
        self.setLayout(pLayout)
    
    