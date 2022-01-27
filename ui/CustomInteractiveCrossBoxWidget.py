from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPen,QPainter
from PyQt5.QtCore import QRectF,Qt
from ui.mGraphicRectItem import mGraphicRectItem

class CustomInteractiveCrossBoxWidget(QGraphicsView):

    def __init__(self, parent = None):
        QGraphicsView.__init__(self, parent)
        self.setMouseTracking(True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground,True)
        self.setStyleSheet("background:transparent;")
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.painter = QPainter(self)

        sceneRect = self.calcSceneRect()
        self.scene = QGraphicsScene(sceneRect)
        self.setScene(self.scene)

        #将border View和CrossView组装入scene
        self.scene.addItem(mGraphicRectItem())
        # self.testItem = QGraphicsTextItem()
        # self.testItem.setPlainText("hello world")
        # self.testItem.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        # self.scene.addItem(self.testItem)
        self.borderItem = QGraphicsRectItem(sceneRect)
        pen = QPen()
        pen.setColor(Qt.white)
        pen.setWidth(10)
        self.borderItem.setPen(pen)
        self.scene.addItem(self.borderItem)

    def calcSceneRect(self):
        width,height = self.width(),self.height()
        return QRectF(-1*width/2,-1*height/2,width,height)

    def mousePressEvent(self, QMouseEvent):
        print("iC View press ", QMouseEvent.pos())
        super().mousePressEvent(QMouseEvent)

    def mouseMoveEvent(self, QMouseEvent):
        print("iC View move ", QMouseEvent.pos())
        super().mouseMoveEvent(QMouseEvent)

    def mouseReleaseEvent(self, QMouseEvent):
        print("iC View release ", QMouseEvent.pos())
        super().mouseReleaseEvent(QMouseEvent)

    def resizeEvent(self, QResizeEvent):
        self.scene.setSceneRect(self.calcSceneRect())
        self.borderItem.setRect(self.calcSceneRect())
        self.scene.update()