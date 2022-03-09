from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from ui.config import uiConfig

# Thanks to https://blog.csdn.net/gumenghua_com1/article/details/111318926
# https://www.cnblogs.com/ygzhaof/p/10064851.html


class SlideshowContainer(QDialog):

    Btnsize=20

    def __init__(self,
        slowHandler,
        playHandler,
        fastHandler,
        nextSliceHandler,
        prevSliceHandler
    ):
        QDialog.__init__(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        hboxlayout = QHBoxLayout()
        vboxlayout1 = QVBoxLayout()
        vboxlayout2 = QVBoxLayout()
        self.setLayout(hboxlayout)

        prevSliceBtn = QPushButton()
        prevSliceBtn.setIcon(QIcon("ui_source/arrow thin left.png"))
        prevSliceBtn.setIconSize(QSize(Btnsize, Btnsize))
        prevSliceBtn.setStyleSheet("QPushButton{border:none;background:transparent;}")
        playBtn = QPushButton()
        playBtn.setIcon(QIcon("ui_source/play.png"))
        playBtn.setIconSize(QSize(Btnsize, Btnsize))
        playBtn.setStyleSheet("QPushButton{border:none;background:transparent;}")
        nextSliceBtn = QPushButton()
        nextSliceBtn.setIcon(QIcon("ui_source/arrow thin right.png"))
        nextSliceBtn.setIconSize(QSize(Btnsize, Btnsize))
        nextSliceBtn.setStyleSheet("QPushButton{border:none;background:transparent;}")
        slowBtn = QPushButton()
        slowBtn.setMinimumSize(Btnsize, Btnsize/2)
        slowBtn.setIcon(QIcon("ui_source/down.png"))
        slowBtn.setStyleSheet("QPushButton{border:none;background:transparent;}")
        fastBtn = QPushButton()
        fastBtn.setMinimumSize(Btnsize, Btnsize/2)
        fastBtn.setIcon(QIcon("ui_source/up.png"))
        fastBtn.setStyleSheet("QPushButton{border:none;background:transparent;}")
        # 显示FPS文本
        showFpsText = QLineEdit()
        showFpsText.setText("FPS")
        showFpsText.setAlignment(Qt.AlignCenter)
        showFpsText.setStyleSheet("background:transparent;border-width:0;border-style:outset")
        # 显示FPS数字
        showNumber = QLCDNumber()

        hboxlayout.addWidget(prevSliceBtn)
        hboxlayout.addWidget(playBtn)
        hboxlayout.addWidget(nextSliceBtn)
        vboxlayout1.addWidget(showFpsText)
        vboxlayout1.addWidget(showNumber)
        vboxlayout2.addWidget(fastBtn)
        vboxlayout2.addWidget(slowBtn)
        hboxlayout.addLayout(vboxlayout1)
        hboxlayout.addLayout(vboxlayout1)
        hboxlayout.addLayout(vboxlayout2)
        hboxlayout.setSpacing(0)
        vboxlayout1.setSpacing(0)
        vboxlayout2.setSpacing(0)
        # 设置窗口的属性为ApplicationModal模态，用户只有关闭弹窗后，才能关闭主界面
        # self.setWindowModality(Qt.ApplicationModal)
        # self.setGeometry()#未设置初始位置evermg42
        # self.setObjectName("slideshowContainer")
    def mousePressEvent(self, event):
        # 重写鼠标点击的事件
        if (event.button() == Qt.LeftButton):
            self._move_drag = True
            self.move_DragPosition = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        if Qt.LeftButton and self._move_drag:
            # 标题栏拖放窗口位置
            self.move(event.globalPos() - self.move_DragPosition)
            event.accept()

    