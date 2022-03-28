from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import *
from ui.config import uiConfig
from ui.CustomDecoratedLayout import CustomDecoratedLayout

class CustomSelectRegionGridWidget(QWidget):

    def __init__(self, parent, signal):
        QWidget.__init__(self)
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
        self.setWindowIcon(QIcon("ui_source/win_title_icon_color.png"))
        self.setStyleSheet("background-color:{0};".format(uiConfig.LightColor.Primary))
        self.vBoxLayout = CustomDecoratedLayout(QVBoxLayout())
        self.vBoxLayout.initParamsForPlain()
        self.vBoxLayout.setLeftMargin(uiConfig.toolsSelectRegionItemSize.width()//2)
        self.vBoxLayout.setRightMargin(uiConfig.toolsSelectRegionItemSize.width()//2)
        self.vBoxLayout.getLayout().setAlignment(Qt.AlignHCenter)
        self.setLayout(self.vBoxLayout.getLayout())

        self.hBoxLayout = CustomDecoratedLayout(QHBoxLayout())
        self.hBoxLayout.initParamsForPlain()
        self.hBoxLayout.setTopMargin(uiConfig.toolsSelectRegionItemSize.height()//2)
        self.hBoxLayout.setBottomMargin(uiConfig.toolsSelectRegionItemSize.height()//2)
        self.hBoxLayout.getLayout().setAlignment(Qt.AlignVCenter)

        self.innerFrame = QFrame(self)
        self.innerFrame.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.innerFrame.setMouseTracking(True)
        self.innerFrame.setFrameShape(QFrame.StyledPanel)
        self.innerFrame.setFrameShadow(QFrame.Plain)
        self.hBoxLayout.getLayout().addWidget(self.innerFrame)
        self.vBoxLayout.getLayout().addLayout(self.hBoxLayout.getLayout())

        self.gridLayout = CustomDecoratedLayout(QGridLayout())
        self.innerFrame.setLayout(self.gridLayout.getLayout())
        self.gridLayout.initParamsForPlain()
        self.gridLayout.setSpacing(2)

        for x in range(5):
            for y in range(5):
                widget = QWidget(self)
                widget.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
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
        x,y = self.innerFrame.x(), self.innerFrame.y()
        if point.x() < x or point.y() < y or \
            point.x() > x + self.innerFrame.width() or point.y() > y + self.innerFrame.height(): return False
        return True

    def leaveEvent(self, QEvent):
        if self.isVisible():
            self.hide()
        super().leaveEvent(QEvent)