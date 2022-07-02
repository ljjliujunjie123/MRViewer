from PyQt5.QtGui import QFont,QPainter,QPen,QBrush,QColor
from PyQt5.QtCore import *
from ToolsInterface import ToolsInterface
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class SwitchButton(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.parent = parent

        self.setWindowFlags(self.windowFlags()|Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(40, 30)
        self.state = False  # 按钮状态：True表示开，False表示关

    def mousePressEvent(self, event):
        #鼠标点击事件：用于切换按钮状态
        super(SwitchButton, self).mousePressEvent(event)
        self.state = False if self.state else True
        self.update()#向外传递信号可重构此函数

    def paintEvent(self, event):
        #绘制按钮
        super(SwitchButton, self).paintEvent(event)
        # 创建绘制器并设置抗锯齿和图片流畅转换
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        # 开关为开的状态
        if self.state:
            # 绘制背景
            painter.setPen(Qt.NoPen)
            brush = QBrush(QColor('blue'))
            painter.setBrush(brush)
            painter.drawRoundedRect(0,0,50,self.height(),8,8)
            # 绘制圆圈
            painter.setPen(Qt.NoPen)
            brush.setColor(QColor('white'))
            painter.setBrush(brush)
            painter.drawRoundedRect(33, 3, 15, 15, 6, 6)
        # 开关为关的状态
        else:
            # 绘制背景
            painter.setPen(Qt.NoPen)
            brush = QBrush(QColor('#bbb9ba'))
            painter.setBrush(brush)
            painter.drawRoundedRect(0,0,50,self.height(),8,8)
            # 绘制圆圈
            pen = QPen(QColor('white'))
            pen.setWidth(1)
            painter.setPen(pen)
            painter.drawRoundedRect(3, 3, 15, 15, 6, 6)