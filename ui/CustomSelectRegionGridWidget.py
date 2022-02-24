from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from ui.Tools.ToolsInterface import ToolsInterface
from ui.config import uiConfig
from ui.CustomDecoratedLayout import CustomDecoratedLayout

class CustomSelectRegionGridWidget(QDialog):

    def __init__(self, parent, signal):
        QFrame.__init__(self)
        self.updateImageShownLayoutSignal = signal
        self.parent = parent
        self.setWindowFlags(
            Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint
        )# 隐藏标题栏|在主窗口前
        self.setWindowModality(Qt.NonModal)
        width = uiConfig.toolsSelectRegionCol * uiConfig.toolsSelectRegionItemSize.width()
        height = uiConfig.toolsSelectRegionRow * uiConfig.toolsSelectRegionItemSize.height()
        print(width,height)
        self.setFixedSize(width,height)
        self.setContentsMargins(0,0,0,0)
        self.setWindowOpacity(0.7)

        self.vBoxLayout = QVBoxLayout()
        self.vBoxLayout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.vBoxLayout)
        self.hBoxLayout = QHBoxLayout()
        self.hBoxLayout.setContentsMargins(0,0,0,0)
        self.hBoxLayout.setAlignment(Qt.AlignCenter)

        self.innerFrame = QFrame(self)
        self.innerFrame.setFixedSize(self.width()//5 * 4, self.height()//5 * 4)
        self.innerFrame.setMouseTracking(True)
        self.innerFrame.setFrameShape(QFrame.StyledPanel)
        self.innerFrame.setFrameShadow(QFrame.Plain)
        self.hBoxLayout.addWidget(self.innerFrame)
        self.vBoxLayout.addLayout(self.hBoxLayout)

        self.gridLayout = CustomDecoratedLayout(QGridLayout(self.innerFrame))
        self.gridLayout.initParamsForPlain()
        self.gridLayout.setSpacing(2)

        for x in range(5):
            for y in range(5):
                widget = QWidget(self)
                widget.setStyleSheet("background-color:black;")
                widget.setMouseTracking(True)
                self.gridLayout.getLayout().addWidget(widget,x,y,1,1)
        
        self.setMouseTracking(True)
        self.setEnabled(True)

    def mousePressEvent(self, QMouseEvent):
        super().mousePressEvent(QMouseEvent)
        point = QMouseEvent.pos()
        if not self.isInInnerFrame(point): return
        # 注意：从0开始计数
        row,col = -1,-1
        for i in range(uiConfig.toolsSelectRegionCol):
            widget = self.gridLayout.getLayout().itemAt(i).widget()
            if point.x() - widget.size().width()//2 - widget.pos().x() > 0:
                col += 1
        for i in range(0,uiConfig.toolsSelectRegionRow * uiConfig.toolsSelectRegionCol, uiConfig.toolsSelectRegionCol):
            widget = self.gridLayout.getLayout().itemAt(i).widget()
            if point.y() - widget.size().height()//2 - widget.pos().y() > 0:
                row += 1
        self.updateImageShownLayoutSignal.emit((0,0,row,col))

    def mouseMoveEvent(self, QMouseEvent):
        super().mouseMoveEvent(QMouseEvent)
        point = QMouseEvent.pos()
        isInInnerFrame = self.isInInnerFrame(point)
        # print("cur point ", point)
        # print("innerframe ", self.innerFrame.pos())
        for i in range(self.gridLayout.getLayout().count()):
            widget = self.gridLayout.getLayout().itemAt(i).widget()
            if isInInnerFrame and \
                point.x() > self.innerFrame.pos().x() + widget.pos().x() and \
                point.y() > self.innerFrame.pos().y() + widget.pos().y():
                widget.setStyleSheet("background-color:white;")
            else:
                widget.setStyleSheet("background-color:black;")
            widget.show()

    def isInInnerFrame(self, point):
        linMin = self.innerFrame.rect().topLeft()
        linMax = self.innerFrame.rect().bottomRight()

        if point.x() < linMin.x() or point.y() < linMin.y() or \
            point.x() > linMax.x() or point.y() > linMax.y(): return False
        return True

    def eventFilter(self, object: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.WindowDeactivate:
            a=1# self.close()
        return super().eventFilter(object, event)