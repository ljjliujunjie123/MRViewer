from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QRegion

class AbstractImageShownWidget(QFrame):

    def __init__(self):
        QFrame.__init__(self)
        self.setAcceptDrops(True)
        self.qvtkWidget = None
        self.resizeFlag = False
        self.isClicked = False

        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Plain)
        self.setMouseTracking(True)

        vBoxLayout = QVBoxLayout()
        vBoxLayout.setContentsMargins(0,0,0,0)
        vBoxLayout.setSpacing(0)
        vBoxLayout.setAlignment(Qt.AlignHCenter)
        self.setLayout(vBoxLayout)

        self.title = QFrame()
        self.title.setFrameShape(QFrame.StyledPanel)
        self.title.setFrameShadow(QFrame.Plain)
        self.title.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        self.title.setStyleSheet("background-color:rgb(100,100,100);")
        hBoxLayout = QHBoxLayout()
        hBoxLayout.setContentsMargins(5,5,5,5)
        hBoxLayout.setSpacing(0)
        hBoxLayout.setAlignment(Qt.AlignLeft)
        self.title.setLayout(hBoxLayout)
        self.label = QLabel()
        self.label.setText("this is a image container")
        self.label.setStyleSheet("color:white;")
        hBoxLayout.addWidget(self.label)

        self.imageContainer = QFrame()
        self.imageContainer.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)

        vBoxLayout.addWidget(self.title)
        vBoxLayout.addWidget(self.imageContainer)

    def setTileText(self, text):
        self.label.setText(text)

    def mousePressEvent(self, QMouseEvent):
        super().mousePressEvent(QMouseEvent)
        point = QMouseEvent.pos()

        #判断点击是否在title上
        if  self.title.y() < point.y() < self.imageContainer.y():
            print("click title")
            self.isClicked = not self.isClicked
            if self.isClicked:
                self.title.setStyleSheet("background-color:rgb(204,102,100);")
            else:
                self.title.setStyleSheet("background-color:rgb(100,100,100);")

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            print("enter")
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            print("drop")
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def resizeEvent(self, QResizeEvent):
        print('parentWidgetSize:', self.width(), self.height())
        if self.qvtkWidget is not None and self.qvtkWidget.size() != self.size():
            self.resizeFlag = True
            self.qvtkWidget.setFixedSize(self.size())
            print('qvtkSize', self.qvtkWidget.size())
        else:
            self.resizeFlag = False

    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
        if self.qvtkWidget is not None: self.qvtkWidget.Finalize()