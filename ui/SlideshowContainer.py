from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from ui.config import uiConfig

# Thanks to https://blog.csdn.net/gumenghua_com1/article/details/111318926
# https://www.cnblogs.com/ygzhaof/p/10064851.html


class SlideshowContainer(QDialog):

    def __init__(self,
        slowHandler,
        playHandler,
        fastHandler
    ):
        QDialog.__init__(self)

        # self.setGeometry()#未设置初始位置evermg42
        print("SlideshowContainer Geometry:")
        print(self.geometry())
        self.setObjectName("slideshowContainer")

        self.resize(uiConfig.shownSlideShowDialogSize)
        self.setStyleSheet("QDialog{background-color:rgb(100,100,100);}")

        self.hBoxLayout = QHBoxLayout(self)
        self.setLayout(self.hBoxLayout)

        #放慢速度的button
        self.slowBtn = QPushButton('-',self)
        self.hBoxLayout.addWidget(self.slowBtn)
        self.slowBtn.clicked.connect(slowHandler)
        
        #暂停播放的button
        self.playBtn = QPushButton('播放',self)
        self.hBoxLayout.addWidget(self.playBtn)
        self.playBtn.clicked.connect(playHandler)

        #加快速度的button
        self.fastBtn = QPushButton('+',self)
        self.hBoxLayout.addWidget(self.fastBtn)
        self.fastBtn.clicked.connect(fastHandler)
    
    def mousePressEvent(self, event):
        # 重写鼠标点击的事件
        if (event.button() == Qt.LeftButton):
            # 鼠标左键点击标题栏区域
            self._move_drag = True
            self.move_DragPosition = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, QMouseEvent):
        self.setCursor(Qt.ArrowCursor)
        if Qt.LeftButton and self._move_drag:
            # 标题栏拖放窗口位置
            self.move(QMouseEvent.globalPos() - self.move_DragPosition)
            QMouseEvent.accept()

    