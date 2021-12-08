from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from ui.config import uiConfig
from ui.CustomDecoratedLayout import CustomDecoratedLayout

class CustomSelectRegionGridWidget(QFrame):

    def __init__(self, signal):
        QFrame.__init__(self)
        self.updateImageShownLayoutSignal = signal
        width = uiConfig.toolsSelectRegionCol * uiConfig.toolsSelectRegionItemSize.width()
        height = uiConfig.toolsSelectRegionRow * uiConfig.toolsSelectRegionItemSize.height()
        self.setFixedSize(width,height)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Plain)

        self.vBoxLayout = QVBoxLayout()
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

        for rect in [(0,0),(0,1),(1,0),(1,1)]:
            widget = QWidget(self)
            widget.setStyleSheet("background-color:black;")
            widget.setMouseTracking(True)
            self.gridLayout.getLayout().addWidget(widget,rect[0],rect[1],1,1)

    def mousePressEvent(self, QMouseEvent):
        super().mousePressEvent(QMouseEvent)
        point = QMouseEvent.pos()
        if not self.isInInnerFrame(point): return
        #注意：从0开始计数
        row,col = -1,-1
        for i in range(uiConfig.toolsSelectRegionCol):
            widget = self.gridLayout.getLayout().itemAt(i).widget()
            if point.x() - self.innerFrame.pos().x() - widget.pos().x() > 0:
                col += 1
        for i in range(0,uiConfig.toolsSelectRegionRow * uiConfig.toolsSelectRegionCol, uiConfig.toolsSelectRegionCol):
            widget = self.gridLayout.getLayout().itemAt(i).widget()
            if point.y() - self.innerFrame.pos().y() - widget.pos().y() > 0:
                row += 1
        self.updateImageShownLayoutSignal.emit((0,0,row,col))

    def mouseMoveEvent(self, QMouseEvent):
        super().mouseMoveEvent(QMouseEvent)
        point = QMouseEvent.pos()
        isInInnerFrame = self.isInInnerFrame(point)
        print("cur point ", point)
        print("innerframe ", self.innerFrame.pos())
        for i in range(self.gridLayout.getLayout().count()):
            widget = self.gridLayout.getLayout().itemAt(i).widget()
            print(i," widget ", widget.pos())
            if isInInnerFrame and \
                point.x() > self.innerFrame.pos().x() + widget.pos().x() and \
                point.y() > self.innerFrame.pos().y() + widget.pos().y():
                widget.setStyleSheet("background-color:white;")
            else:
                widget.setStyleSheet("background-color:black;")
            widget.show()

    def isInInnerFrame(self, point):
        limMin = self.innerFrame.rect().topLeft()
        limMax = self.innerFrame.rect().bottomRight()
        if point.x() < limMin.x() or point.y() < limMin.y() or \
            point.x() > limMax.x() or point.y() > limMax.y(): return False
        return True

    def setEnabled(self, bool):
        for i in range(self.gridLayout.getLayout().count()):
            widget = self.gridLayout.getLayout().itemAt(i).widget()
            if bool:
                widget.setStyleSheet("background-color:black;")
            else:
                widget.setStyleSheet("background-color:gray;")
        super().setEnabled(bool)